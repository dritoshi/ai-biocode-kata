#!/usr/bin/env python3
"""E1バッチのsource変更が固定許可パス内だけか検査する."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.review.e1_remediation import (  # noqa: E402
    GENERATED_ARTIFACTS,
    load_fixture,
)


def _git_lines(root: Path, *args: str) -> list[str]:
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
    return [line for line in result.stdout.splitlines() if line]


def _is_source_path(path: str) -> bool:
    return (
        path.startswith(("chapters/", "scripts/", "tests/"))
        or path == "docs/review/2026-07-28_e1_remediation_plan.md"
    ) and path not in GENERATED_ARTIFACTS


def _worktree_paths(root: Path) -> set[str]:
    result = subprocess.run(
        [
            "git",
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "-z",
        ],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError("git statusに失敗")
    fields = result.stdout.decode(errors="replace").split("\0")
    paths: set[str] = set()
    index = 0
    while index < len(fields):
        entry = fields[index]
        if not entry:
            break
        status = entry[:2]
        path = entry[3:]
        paths.add(path)
        index += 1
        if "R" in status or "C" in status:
            if index < len(fields) and fields[index]:
                paths.add(fields[index])
                index += 1
    return paths


def validate_source_scope(
    root: Path,
    fixture: dict,
    batch: int,
    baseline_ref: str,
    source_commit: str,
    *,
    check_worktree: bool,
    require_clean: bool,
) -> None:
    """コミット差分と必要に応じ作業ツリー差分を検査する."""
    if str(batch) not in fixture["batches"] or batch == 0:
        raise ValueError("batchは1〜5でなければならない")
    allowed = set(
        fixture["batches"][str(batch)]["allowed_source_paths"]
    )
    committed = set(
        _git_lines(
            root,
            "diff",
            "--name-only",
            "--diff-filter=ACMRT",
            f"{baseline_ref}..{source_commit}",
        )
    )
    unexpected_committed = sorted(
        path for path in committed if _is_source_path(path) and path not in allowed
    )
    if unexpected_committed:
        raise ValueError(
            "バッチ外のsourceコミット差分: "
            + ", ".join(unexpected_committed)
        )

    if check_worktree:
        worktree = {path for path in _worktree_paths(root) if _is_source_path(path)}
        unexpected_worktree = sorted(worktree - allowed)
        if unexpected_worktree:
            raise ValueError(
                "バッチ外のsource作業ツリー差分: "
                + ", ".join(unexpected_worktree)
            )
        if require_clean and worktree:
            raise ValueError(
                "source対象に未コミット差分がある: "
                + ", ".join(sorted(worktree))
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--batch", type=int, required=True)
    parser.add_argument("--baseline-ref", required=True)
    parser.add_argument("--source-commit")
    parser.add_argument("--worktree", action="store_true")
    parser.add_argument("--require-clean", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    source_commit = args.source_commit or "HEAD"
    validate_source_scope(
        root,
        load_fixture(root),
        args.batch,
        args.baseline_ref,
        source_commit,
        check_worktree=args.worktree,
        require_clean=args.require_clean,
    )
    print(f"E1バッチ{args.batch}のsource変更範囲を確認しました")


if __name__ == "__main__":
    main()
