"""E1 PR helperの純粋な本文更新規則を検証する."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.review import create_e1_pr
from scripts.review.create_e1_pr import (
    body_with_marker,
    create,
    provenance_marker,
)


def test_adds_one_marker_without_replacing_body() -> None:
    marker = provenance_marker(7, "source", "artifact")

    body, changed = body_with_marker("変更内容", marker)

    assert changed is True
    assert body.startswith("変更内容\n\n")
    assert body.count("<!-- e1-provenance:") == 1


def test_same_marker_is_idempotent() -> None:
    marker = provenance_marker(7, "source", "artifact")
    original = f"変更内容\n\n{marker}\n"

    body, changed = body_with_marker(original, marker)

    assert changed is False
    assert body == original


def test_rejects_different_marker() -> None:
    existing = provenance_marker(7, "source", "artifact")
    expected = provenance_marker(8, "source", "artifact")

    with pytest.raises(ValueError, match="期待値と異なる"):
        body_with_marker(existing, expected)


def test_create_pushes_and_verifies_remote_before_pr(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []
    artifact = "a" * 40

    def fake_run(root: Path, command: list[str]) -> str:
        del root
        calls.append(command)
        if command[:3] == ["git", "symbolic-ref", "--quiet"]:
            return "revise/e1-ch01-ch03"
        if command[:2] == ["git", "rev-parse"]:
            return artifact
        if command[:2] == ["git", "ls-remote"]:
            return f"{artifact}\trefs/heads/revise/e1-ch01-ch03"
        if command[:3] == ["gh", "pr", "list"]:
            return "[]"
        if command[:3] == ["gh", "pr", "create"]:
            return "https://github.com/example/repo/pull/42"
        if command[:3] == ["gh", "pr", "view"]:
            return json.dumps(
                {
                    "number": 42,
                    "state": "OPEN",
                    "body": "説明",
                    "baseRefName": "main",
                    "headRefName": "revise/e1-ch01-ch03",
                    "headRefOid": artifact,
                }
            )
        return ""

    monkeypatch.setattr(create_e1_pr, "_run", fake_run)
    state_path = tmp_path / "state.json"
    body_file = tmp_path / "body.md"
    body_file.write_text("説明\n", encoding="utf-8")

    number = create(
        tmp_path,
        state_path,
        base="main",
        head="revise/e1-ch01-ch03",
        title="E1 batch 1",
        body_file=body_file,
        source_commit="s" * 40,
        artifact_commit=artifact,
    )

    assert number == 42
    push_index = next(
        index for index, command in enumerate(calls) if command[:2] == ["git", "push"]
    )
    create_index = next(
        index
        for index, command in enumerate(calls)
        if command[:3] == ["gh", "pr", "create"]
    )
    assert push_index < create_index
    pr_create = calls[create_index]
    assert pr_create[pr_create.index("--head") + 1] == "revise/e1-ch01-ch03"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["status"] == "completed"
    assert state["pr_number"] == 42


def test_push_failure_does_not_create_pr(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []
    artifact = "a" * 40

    def fake_run(root: Path, command: list[str]) -> str:
        del root
        calls.append(command)
        if command[:3] == ["git", "symbolic-ref", "--quiet"]:
            return "revise/e1-ch01-ch03"
        if command[:2] == ["git", "rev-parse"]:
            return artifact
        if command[:2] == ["git", "push"]:
            raise ValueError("push failed")
        return ""

    monkeypatch.setattr(create_e1_pr, "_run", fake_run)
    body_file = tmp_path / "body.md"
    body_file.write_text("説明\n", encoding="utf-8")

    with pytest.raises(ValueError, match="push failed"):
        create(
            tmp_path,
            tmp_path / "state.json",
            base="main",
            head="revise/e1-ch01-ch03",
            title="E1 batch 1",
            body_file=body_file,
            source_commit="s" * 40,
            artifact_commit=artifact,
        )

    assert not any(command[:3] == ["gh", "pr", "create"] for command in calls)
