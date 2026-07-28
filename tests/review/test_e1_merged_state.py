"""E1マージ後監査のref固定を検証する."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.review.check_e1_merged_state import check_merged_state


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def test_rejects_worktree_not_at_expected_ref(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    (root / "first.txt").write_text("first\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "first")
    first = _git(root, "rev-parse", "HEAD")
    (root / "second.txt").write_text("second\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "second")

    with pytest.raises(ValueError, match="expected ref"):
        check_merged_state(
            root,
            batch=1,
            transition_baseline_ref=first,
            previous_ref=first,
            expected_ref=first,
        )
