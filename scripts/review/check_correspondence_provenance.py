#!/usr/bin/env python3
"""E1対応表の2コミット構造・到達可能性・PR記録を検査する."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.review.e1_remediation import GENERATED_ARTIFACTS  # noqa: E402

MARKER_RE = re.compile(r"<!-- e1-provenance: (\{[^\n]*\}) -->")


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ValueError(f"git {' '.join(args)} に失敗: {detail}")
    return result.stdout.strip()


def artifact_changes(
    root: Path,
    source_commit: str,
    artifact_commit: str,
) -> set[str]:
    """source→artifact間の変更が許可生成物だけか検査して返す."""
    parent = _git(root, "rev-parse", f"{artifact_commit}^")
    if parent != source_commit:
        raise ValueError("生成物コミットの直接の親がsourceコミットではない")
    changed = set(
        _git(
            root,
            "diff",
            "--name-only",
            source_commit,
            artifact_commit,
        ).splitlines()
    )
    required = {
        "docs/review/code_correspondence.json",
        "docs/review/code_correspondence.md",
    }
    if not required.issubset(changed):
        raise ValueError("対応表JSON・Markdownが生成物コミットにない")
    if not changed.issubset(GENERATED_ARTIFACTS):
        raise ValueError(
            "生成物コミットに許可外の変更がある: "
            + ", ".join(sorted(changed - GENERATED_ARTIFACTS))
        )
    return changed


def find_artifact_commit(root: Path, source_commit: str) -> str:
    """全refから条件を満たすsourceの直接の子を一意に発見する."""
    children_line = _git(
        root,
        "rev-list",
        "--all",
        "--children",
    ).splitlines()
    candidates: list[str] = []
    for line in children_line:
        fields = line.split()
        if fields and fields[0] == source_commit:
            for child in fields[1:]:
                try:
                    artifact_changes(root, source_commit, child)
                except ValueError:
                    continue
                candidates.append(child)
    unique = sorted(set(candidates))
    if len(unique) != 1:
        raise ValueError(
            f"生成物コミット候補は1件必要（実測{len(unique)}件）"
        )
    return unique[0]


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=root,
        check=False,
    )
    return result.returncode == 0


def validate_pr_json(
    root: Path,
    pr_data: dict[str, Any],
    source_commit: str,
    artifact_commit: str,
    expected_state: str,
    main_ref: str | None,
) -> None:
    """PR JSONと本文中の固定provenanceマーカーを照合する."""
    if pr_data.get("state") != expected_state:
        raise ValueError("PR状態が期待値と異なる")
    if pr_data.get("headRefOid") != artifact_commit:
        raise ValueError("PR headRefOidが生成物コミットと異なる")
    markers = MARKER_RE.findall(str(pr_data.get("body", "")))
    if len(markers) != 1:
        raise ValueError("provenanceマーカーはちょうど1件必要")
    try:
        marker = json.loads(markers[0])
    except json.JSONDecodeError as exc:
        raise ValueError("provenanceマーカーのJSONが不正") from exc
    expected_marker = {
        "pr_number": pr_data.get("number"),
        "source_commit": source_commit,
        "artifact_commit": artifact_commit,
    }
    if marker != expected_marker:
        raise ValueError("provenanceマーカーの内容が一致しない")
    if expected_state == "MERGED":
        merge_commit = (pr_data.get("mergeCommit") or {}).get("oid")
        if not merge_commit:
            raise ValueError("MERGED PRにmerge commitがない")
        if main_ref and not _is_ancestor(root, merge_commit, main_ref):
            raise ValueError("merge commitがmain refから到達不能")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--artifact-commit", required=True)
    parser.add_argument("--main-ref")
    parser.add_argument("--require-reachable", action="store_true")
    parser.add_argument("--expected-pr-json")
    parser.add_argument(
        "--expected-pr-state",
        choices=("OPEN", "MERGED"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    artifact_commit = (
        find_artifact_commit(root, args.source_commit)
        if args.artifact_commit == "auto"
        else args.artifact_commit
    )
    artifact_changes(root, args.source_commit, artifact_commit)
    if args.require_reachable:
        if not args.main_ref:
            raise SystemExit("--require-reachableには--main-refが必要")
        for commit in (args.source_commit, artifact_commit):
            if not _is_ancestor(root, commit, args.main_ref):
                raise SystemExit(f"{commit} が {args.main_ref} から到達不能")
    if bool(args.expected_pr_json) != bool(args.expected_pr_state):
        raise SystemExit(
            "--expected-pr-jsonと--expected-pr-stateは併用してください"
        )
    if args.expected_pr_json:
        validate_pr_json(
            root,
            json.loads(args.expected_pr_json),
            args.source_commit,
            artifact_commit,
            args.expected_pr_state,
            args.main_ref,
        )
    print(
        json.dumps(
            {
                "source_commit": args.source_commit,
                "artifact_commit": artifact_commit,
            }
        )
    )


if __name__ == "__main__":
    main()
