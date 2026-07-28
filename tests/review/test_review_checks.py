"""レビュー補助チェックの回帰テスト."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.review import check_xref
from scripts.review.check_structure import find_new_issues, issue_key
from scripts.review.e1_remediation import (
    load_fixture,
    normalized_evidence_bytes,
)
from scripts.review.run_e1_batch_gates import command_for

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def test_extracts_artifact_links_outside_code_blocks(tmp_path: Path) -> None:
    """scripts/testsリンクだけを本文から抽出する."""
    chapter = tmp_path / "chapter.md"
    chapter.write_text(
        "[実装](../scripts/ch01/example.py)\n"
        "[テスト](../tests/ch01/test_example.py)\n"
        "```text\n"
        "[コード内](../scripts/ch01/ignored.py)\n"
        "```\n",
        encoding="utf-8",
    )

    links = check_xref.extract_links(chapter)

    assert [link["type"] for link in links] == [
        "artifact_link",
        "artifact_link",
    ]


def test_checks_artifact_link_existence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """実在する成果物リンクと壊れたリンクを区別する."""
    root = tmp_path / "repo"
    chapter = root / "chapters/01_example.md"
    target = root / "scripts/ch01/example.py"
    chapter.parent.mkdir(parents=True)
    target.parent.mkdir(parents=True)
    chapter.write_text("# 章\n", encoding="utf-8")
    target.write_text("value = 1\n", encoding="utf-8")
    monkeypatch.setattr(check_xref, "PROJECT_ROOT", root)

    valid = {
        "line": 1,
        "raw_link": "../scripts/ch01/example.py",
    }
    missing = {
        "line": 2,
        "raw_link": "../tests/ch01/test_example.py",
    }

    assert check_xref.check_artifact_link(chapter, valid) is None
    issue = check_xref.check_artifact_link(chapter, missing)
    assert issue is not None
    assert issue["type"] == "broken_artifact_link"


def test_structure_baseline_ignores_line_number_changes() -> None:
    """既知問題は行番号が移動しても新規問題として扱わない."""
    baseline = [
        {
            "file": "chapters/01_example.md",
            "line": 10,
            "type": "bold_bracket",
            "message": "既知の問題",
        }
    ]
    current = [
        {
            "file": "chapters/01_example.md",
            "line": 20,
            "type": "bold_bracket",
            "message": "既知の問題",
        },
        {
            "file": "chapters/03_example.md",
            "line": 5,
            "type": "missing_section",
            "message": "新規の問題",
        },
    ]

    assert issue_key(baseline[0]) == issue_key(current[0])
    assert find_new_issues(current, baseline) == [current[1]]


def test_e1_fixture_keeps_all_normative_anchors() -> None:
    """計画で固定した45 ID・56関係・バッチ件数を保持する."""
    fixture = load_fixture(PROJECT_ROOT)

    assert len(fixture["comment_expectations"]) == 45
    assert len(fixture["final_relations"]) == 56
    assert [
        len(fixture["batches"][str(batch)]["completed_ids"])
        for batch in range(6)
    ] == [0, 4, 18, 32, 41, 45]


def test_normalizes_comment_evidence() -> None:
    """行末空白だけを除き、インデントと#を保持する."""
    assert normalized_evidence_bytes(["  # 理由  ", "本文\t"]) == (
        b"  # \xe7\x90\x86\xe7\x94\xb1\n\xe6\x9c\xac\xe6\x96\x87\n"
    )


def test_batch_gate_selects_one_chapter_group() -> None:
    """対象バッチ以外の章をコマンドへ混在させない."""
    command = command_for(PROJECT_ROOT, 4, "target-pytest")

    assert "tests/ch02" in command
    assert "tests/ch13" in command
    assert "tests/ch17" in command
    assert "tests/ch12" not in command


def test_batch_gate_rejects_unknown_values() -> None:
    with pytest.raises(ValueError, match="batch"):
        command_for(PROJECT_ROOT, 0, "mypy")
    with pytest.raises(ValueError, match="未知"):
        command_for(PROJECT_ROOT, 1, "unknown")
