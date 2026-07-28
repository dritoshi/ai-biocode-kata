"""E1バッチ0生成と単調遷移を検証する."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from scripts.review.build_e1_batch0_state import build_batch0_state
from scripts.review.check_e1_transition import validate_transition
from scripts.review.e1_remediation import (
    load_fixture,
    pending_comment_record,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _state(fixture: dict[str, Any], batch: int) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for block_id, expectation in fixture["comment_expectations"].items():
        if expectation["scheduled_batch"] <= batch:
            records.append(
                {
                    "block_id": block_id,
                    "status": expectation["terminal_status"],
                    "reason": f"batch {expectation['scheduled_batch']}",
                }
            )
        else:
            records.append(pending_comment_record(block_id, expectation))
    return {
        "remediation_scope": {"completed_batch": batch},
        "comment_sync": records,
    }


def test_batch0_generation_is_deterministic() -> None:
    fixture = load_fixture(PROJECT_ROOT)
    baseline_ref = fixture["baseline_ref"]

    first = build_batch0_state(PROJECT_ROOT, baseline_ref, fixture)
    second = build_batch0_state(PROJECT_ROOT, baseline_ref, fixture)

    assert first == second
    assert first["remediation_scope"]["completed_batch"] == 0
    assert len(first["comment_sync"]) == 45
    assert all(
        set(record) == {
            "block_id",
            "status",
            "scheduled_batch",
            "expected_terminal_status",
        }
        for record in first["comment_sync"]
    )


@pytest.mark.parametrize("batch", range(1, 6))
def test_allows_only_scheduled_batch_transition(batch: int) -> None:
    fixture = load_fixture(PROJECT_ROOT)
    previous = (
        build_batch0_state(PROJECT_ROOT, fixture["baseline_ref"], fixture)
        if batch == 1
        else _state(fixture, batch - 1)
    )
    current = _state(fixture, batch)

    validate_transition(previous, current, fixture, batch)


def test_rejects_rewrite_of_completed_record() -> None:
    fixture = load_fixture(PROJECT_ROOT)
    previous = _state(fixture, 1)
    current = _state(fixture, 2)
    changed = deepcopy(current)
    record = next(
        item
        for item in changed["comment_sync"]
        if item["block_id"] == "B-01-001"
    )
    record["reason"] = "書き換え"

    with pytest.raises(ValueError, match="既完了"):
        validate_transition(previous, changed, fixture, 2)


def test_rejects_extra_pending_field() -> None:
    fixture = load_fixture(PROJECT_ROOT)
    previous = build_batch0_state(
        PROJECT_ROOT,
        fixture["baseline_ref"],
        fixture,
    )
    current = _state(fixture, 1)
    pending = next(
        item
        for item in current["comment_sync"]
        if item["status"] == "pending"
    )
    pending["reason"] = "未着手"

    with pytest.raises(ValueError, match="早期完了"):
        validate_transition(previous, current, fixture, 1)
