#!/usr/bin/env python3
"""E1実装PRを重複なく作成しprovenanceマーカーを設定する."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MARKER_RE = re.compile(r"<!-- e1-provenance: (\{[^\n]*\}) -->")
PR_URL_RE = re.compile(r"/pull/(\d+)(?:\D|$)")


def _run(root: Path, command: list[str]) -> str:
    result = subprocess.run(
        command,
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ValueError(f"{' '.join(command)} に失敗: {detail}")
    return result.stdout.strip()


def _write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=path.parent,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def _load_state(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") not in {"prepared", "created", "completed"}:
        raise ValueError("PR状態ファイルのstatusが不正")
    return data


def provenance_marker(
    pr_number: int,
    source_commit: str,
    artifact_commit: str,
) -> str:
    """PR本文へ置く固定形式マーカーを返す."""
    payload = json.dumps(
        {
            "pr_number": pr_number,
            "source_commit": source_commit,
            "artifact_commit": artifact_commit,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f"<!-- e1-provenance: {payload} -->"


def body_with_marker(body: str, marker: str) -> tuple[str, bool]:
    """既存本文を保持し、同一マーカーがなければ末尾へ1件追加する."""
    matches = MARKER_RE.findall(body)
    if len(matches) > 1:
        raise ValueError("provenanceマーカーが重複している")
    if matches:
        existing = f"<!-- e1-provenance: {matches[0]} -->"
        if existing != marker:
            raise ValueError("既存provenanceマーカーが期待値と異なる")
        return body, False
    separator = "\n\n" if body and not body.endswith("\n\n") else ""
    return f"{body}{separator}{marker}\n", True


def _view_pr(root: Path, number: int) -> dict[str, Any]:
    raw = _run(
        root,
        [
            "gh",
            "pr",
            "view",
            str(number),
            "--json",
            "number,state,body,baseRefName,headRefName,headRefOid",
        ],
    )
    return json.loads(raw)


def _validate_pr(
    data: dict[str, Any],
    state: dict[str, Any],
    number: int,
) -> None:
    expected = {
        "number": number,
        "state": "OPEN",
        "baseRefName": state["base"],
        "headRefName": state["head"],
        "headRefOid": state["artifact_commit"],
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValueError(f"PR {key}が期待値と異なる")


def resume(
    root: Path,
    state_path: Path,
    *,
    pr_number: int | None,
) -> int:
    """明示番号または保存済み番号だけでPR本文設定を再開する."""
    state = _load_state(state_path)
    number = pr_number or state.get("pr_number")
    if not isinstance(number, int):
        raise ValueError("resumeには明示PR番号が必要")
    data = _view_pr(root, number)
    _validate_pr(data, state, number)
    marker = provenance_marker(
        number,
        state["source_commit"],
        state["artifact_commit"],
    )
    updated, changed = body_with_marker(str(data.get("body", "")), marker)
    if changed:
        _run(
            root,
            ["gh", "pr", "edit", str(number), "--body", updated],
        )
    state["pr_number"] = number
    state["status"] = "completed"
    _write_state(state_path, state)
    return number


def _matching_open_prs(
    root: Path,
    state: dict[str, Any],
) -> list[int]:
    raw = _run(
        root,
        [
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--base",
            state["base"],
            "--head",
            state["head"],
            "--json",
            "number,baseRefName,headRefName,headRefOid",
        ],
    )
    rows = json.loads(raw)
    return [
        int(row["number"])
        for row in rows
        if row.get("baseRefName") == state["base"]
        and row.get("headRefName") == state["head"]
        and row.get("headRefOid") == state["artifact_commit"]
    ]


def create(
    root: Path,
    state_path: Path,
    *,
    base: str,
    head: str,
    title: str,
    body_file: Path,
    source_commit: str,
    artifact_commit: str,
) -> int:
    """push・remote照合後にPRを1件だけ作り、resumeへ進む."""
    current = _run(root, ["git", "symbolic-ref", "--quiet", "--short", "HEAD"])
    if current == "main" or current != head:
        raise ValueError("現在ブランチは指定した非main headでなければならない")
    if _run(root, ["git", "rev-parse", "HEAD"]) != artifact_commit:
        raise ValueError("HEADがartifact_commitと一致しない")

    expected_state = {
        "status": "prepared",
        "base": base,
        "head": head,
        "source_commit": source_commit,
        "artifact_commit": artifact_commit,
    }
    if state_path.exists():
        state = _load_state(state_path)
        for key in ("base", "head", "source_commit", "artifact_commit"):
            if state.get(key) != expected_state[key]:
                raise ValueError("既存PR状態ファイルが今回の入力と一致しない")
        if isinstance(state.get("pr_number"), int):
            return resume(root, state_path, pr_number=None)
    else:
        state = expected_state
        _write_state(state_path, state)

    _run(root, ["git", "push", "--set-upstream", "origin", "HEAD"])
    remote = _run(
        root,
        [
            "git",
            "ls-remote",
            "--heads",
            "origin",
            f"refs/heads/{head}",
        ],
    )
    remote_oid = remote.split(maxsplit=1)[0] if remote else ""
    if remote_oid != artifact_commit:
        raise ValueError("remote head OIDがartifact_commitと一致しない")

    matches = _matching_open_prs(root, state)
    if len(matches) > 1:
        raise ValueError("完全一致するOPEN PRが複数ある")
    if matches:
        number = matches[0]
    else:
        url = _run(
            root,
            [
                "gh",
                "pr",
                "create",
                "--base",
                base,
                "--head",
                head,
                "--title",
                title,
                "--body-file",
                str(body_file),
            ],
        )
        match = PR_URL_RE.search(url)
        if not match:
            raise ValueError("gh pr createの返却URLからPR番号を読めない")
        number = int(match.group(1))
    print(f"E1_PR_NUMBER={number}", file=sys.stderr)
    state["status"] = "created"
    state["pr_number"] = number
    _write_state(state_path, state)
    return resume(root, state_path, pr_number=number)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="mode", required=True)
    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("--base", required=True)
    create_parser.add_argument("--head", required=True)
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--body-file", type=Path, required=True)
    create_parser.add_argument("--source-commit", required=True)
    create_parser.add_argument("--artifact-commit", required=True)
    create_parser.add_argument("--state-file", type=Path, required=True)
    create_parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    resume_parser = subparsers.add_parser("resume")
    resume_parser.add_argument("--body-file", type=Path, required=True)
    resume_parser.add_argument("--state-file", type=Path, required=True)
    resume_parser.add_argument("--pr-number", type=int)
    resume_parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    if args.mode == "create":
        number = create(
            root,
            args.state_file,
            base=args.base,
            head=args.head,
            title=args.title,
            body_file=args.body_file,
            source_commit=args.source_commit,
            artifact_commit=args.artifact_commit,
        )
    else:
        number = resume(
            root,
            args.state_file,
            pr_number=args.pr_number,
        )
    print(f"https://github.com/pull/{number}")


if __name__ == "__main__":
    main()
