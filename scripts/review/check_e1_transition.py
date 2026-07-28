#!/usr/bin/env python3
"""E1コメント同期状態が予定バッチだけ単調遷移したか検査する."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.review.build_e1_batch0_state import (  # noqa: E402
    build_batch0_state,
)
from scripts.review.e1_remediation import (  # noqa: E402
    load_fixture,
    pending_comment_record,
)


def validate_transition(
    previous: dict[str, Any],
    current: dict[str, Any],
    fixture: dict[str, Any],
    batch: int,
) -> None:
    """既完了不変・予定IDだけのpending解除を検証する."""
    if batch not in range(1, 6):
        raise ValueError("batchは1〜5でなければならない")
    if previous.get("remediation_scope", {}).get("completed_batch") != batch - 1:
        raise ValueError("比較元のcompleted_batchが直前バッチではない")
    if current.get("remediation_scope", {}).get("completed_batch") != batch:
        raise ValueError("比較先のcompleted_batchが対象バッチではない")

    expectations = fixture["comment_expectations"]
    previous_records = {
        record.get("block_id"): record
        for record in previous.get("comment_sync", [])
    }
    current_records = {
        record.get("block_id"): record
        for record in current.get("comment_sync", [])
    }
    if set(previous_records) != set(expectations):
        raise ValueError("比較元comment_syncのID集合が不正")
    if set(current_records) != set(expectations):
        raise ValueError("比較先comment_syncのID集合が不正")

    for block_id, expectation in expectations.items():
        scheduled = int(expectation["scheduled_batch"])
        pending = pending_comment_record(block_id, expectation)
        before = previous_records[block_id]
        after = current_records[block_id]
        if scheduled < batch:
            if before != after:
                raise ValueError(f"既完了レコードが変更された: {block_id}")
        elif scheduled == batch:
            if before != pending:
                raise ValueError(f"遷移前がpendingではない: {block_id}")
            if after.get("status") != expectation["terminal_status"]:
                raise ValueError(f"予定終端状態へ遷移していない: {block_id}")
            if after == pending:
                raise ValueError(f"予定IDがpendingのまま: {block_id}")
        elif before != pending or after != pending:
            raise ValueError(f"後続バッチIDが早期完了した: {block_id}")


def _load_previous(
    root: Path,
    batch: int,
    fixture: dict[str, Any],
    transition_baseline_ref: str,
    previous_ref: str,
) -> dict[str, Any]:
    if batch == 1:
        return build_batch0_state(root, transition_baseline_ref, fixture)
    result = subprocess.run(
        [
            "git",
            "show",
            f"{previous_ref}:docs/review/code_correspondence.json",
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(
            f"直前対応表を読めない: {result.stderr.strip()}"
        )
    return json.loads(result.stdout)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--batch", type=int, required=True)
    parser.add_argument("--transition-baseline-ref", required=True)
    parser.add_argument("--previous-ref", required=True)
    parser.add_argument("--current", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    fixture = load_fixture(root)
    previous = _load_previous(
        root,
        args.batch,
        fixture,
        args.transition_baseline_ref,
        args.previous_ref,
    )
    current = json.loads(args.current.read_text(encoding="utf-8"))
    validate_transition(previous, current, fixture, args.batch)
    print(f"E1バッチ{args.batch}の単調遷移を確認しました")


if __name__ == "__main__":
    main()
