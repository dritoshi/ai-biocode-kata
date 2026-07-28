#!/usr/bin/env python3
"""origin/main相当の一時worktreeでE1バッチ成果物を独立監査する."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.review.audit_code_correspondence import audit  # noqa: E402
from scripts.review.build_e1_batch0_state import (  # noqa: E402
    build_batch0_state,
)
from scripts.review.check_e1_transition import (  # noqa: E402
    validate_transition,
)
from scripts.review.e1_remediation import (  # noqa: E402
    load_fixture,
    validate_e1_inventory,
)


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def check_merged_state(
    root: Path,
    *,
    batch: int,
    transition_baseline_ref: str,
    previous_ref: str,
    expected_ref: str,
) -> None:
    """HEAD、対応表、前バッチ遷移を一時worktree内で検査する."""
    if _git(root, "rev-parse", "HEAD") != _git(
        root,
        "rev-parse",
        expected_ref,
    ):
        raise ValueError("一時worktreeのHEADがexpected refと一致しない")
    fixture = load_fixture(root)
    inventory_path = root / "docs/review/code_correspondence.json"
    report_path = root / "docs/review/code_correspondence.md"
    current = json.loads(inventory_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")
    result = audit(root, current, report)
    if result["status"] != "passed":
        raise ValueError(
            "対応表の独立監査に失敗: " + ", ".join(result["failures"])
        )
    validate_e1_inventory(root, current, fixture, batch)
    if batch == 1:
        previous = build_batch0_state(
            root,
            transition_baseline_ref,
            fixture,
        )
    else:
        previous = json.loads(
            _git(
                root,
                "show",
                f"{previous_ref}:docs/review/code_correspondence.json",
            )
        )
    validate_transition(previous, current, fixture, batch)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--batch", type=int, required=True)
    parser.add_argument("--transition-baseline-ref", required=True)
    parser.add_argument("--previous-ref", required=True)
    parser.add_argument("--expected-ref", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    check_merged_state(
        args.root.resolve(),
        batch=args.batch,
        transition_baseline_ref=args.transition_baseline_ref,
        previous_ref=args.previous_ref,
        expected_ref=args.expected_ref,
    )
    print(f"E1バッチ{args.batch}のマージ後状態を確認しました")


if __name__ == "__main__":
    main()
