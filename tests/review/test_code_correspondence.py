"""精密コード対応表の生成・override・独立監査を検証する."""

from __future__ import annotations

import json
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from scripts.review.audit_code_correspondence import audit
from scripts.review.code_correspondence import (
    add_relations,
    apply_category_overrides,
    build_inventory,
    extract_all_blocks,
    extract_source_blocks,
    load_overrides,
    normalized_for_determinism,
    render_report,
    sha256_text,
    summarize_test_results,
    validate_test_results,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OVERRIDES_PATH = (
    PROJECT_ROOT / "scripts/review/code_correspondence_overrides.json"
)


def _test_results() -> dict[str, dict[str, Any]]:
    return {
        "tests/ch01/test_add.py": {
            "returncode": 0,
            "passed": 1,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "duration_seconds": 0.01,
            "summary": "1 passed in 0.01s",
        }
    }


def _minimal_repository(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "chapters").mkdir(parents=True)
    (root / "scripts/ch01").mkdir(parents=True)
    (root / "tests/ch01").mkdir(parents=True)
    for number in range(22):
        body = "# 章\n"
        if number == 1:
            body += (
                "\n## 加算\n\n"
                "```python\n"
                "def add(left: int, right: int) -> int:\n"
                "    return left + right\n"
                "```\n"
            )
        (root / f"chapters/{number:02d}_chapter.md").write_text(
            body,
            encoding="utf-8",
        )
    (root / "scripts/ch01/add.py").write_text(
        '"""加算の実体."""\n\n'
        "def add(left: int, right: int) -> int:\n"
        '    """2値を加算する."""\n'
        "    return left + right\n",
        encoding="utf-8",
    )
    (root / "tests/ch01/test_add.py").write_text(
        "from scripts.ch01.add import add\n\n"
        "def test_add() -> None:\n"
        "    assert add(1, 2) == 3\n",
        encoding="utf-8",
    )
    return root


def _minimal_overrides(
    *,
    block_sha256: str | None = None,
    relations: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    relation_overrides: dict[str, Any] = {}
    if relations is not None:
        relation_overrides["B-01-001"] = {
            "block_sha256": block_sha256,
            "relations": relations,
        }
    return {
        "schema_version": 1,
        "category_overrides": {},
        "relation_overrides": relation_overrides,
        "goldset": [],
        "substitution_tests": {},
        "review_metadata": {},
    }


class TestExtraction:
    """全件抽出の境界を検証する."""

    def test_keeps_short_tilde_and_quoted_blocks(self, tmp_path: Path) -> None:
        chapter = tmp_path / "01_example.md"
        chapter.write_text(
            "# 章\n\n"
            "~~~text\n"
            "短い\n"
            "~~~\n\n"
            "> ```python\n"
            "> x = 1\n"
            "> ```\n",
            encoding="utf-8",
        )
        blocks, _ = extract_source_blocks(chapter, root=tmp_path)
        assert [block.id for block in blocks] == ["B-01-001", "B-01-002"]
        assert [block.lang for block in blocks] == ["text", "python"]
        assert blocks[1].code == "x = 1"

    def test_rejects_unclosed_fence(self, tmp_path: Path) -> None:
        chapter = tmp_path / "01_example.md"
        chapter.write_text("```python\nx = 1\n", encoding="utf-8")
        with pytest.raises(ValueError, match="閉じていない"):
            extract_source_blocks(chapter, root=tmp_path)


class TestOverrides:
    """人手判断台帳の安全性を検証する."""

    def test_rejects_unknown_schema(self, tmp_path: Path) -> None:
        path = tmp_path / "overrides.json"
        path.write_text('{"schema_version": 99}', encoding="utf-8")
        with pytest.raises(ValueError, match="schema_version"):
            load_overrides(path)

    def test_rejects_stale_block_hash(self, tmp_path: Path) -> None:
        root = _minimal_repository(tmp_path)
        blocks, _ = extract_all_blocks(root)
        overrides = _minimal_overrides()
        overrides["category_overrides"]["B-01-001"] = {
            "block_sha256": "stale",
            "category": "implementation",
            "placement": "required_scripts",
            "reason": "人手確認",
        }
        with pytest.raises(ValueError, match="ハッシュが古い"):
            apply_category_overrides(blocks, overrides)

    def test_rejects_missing_relation_target(self, tmp_path: Path) -> None:
        root = _minimal_repository(tmp_path)
        blocks, _ = extract_all_blocks(root)
        overrides = _minimal_overrides(
            block_sha256=blocks[0].sha256,
            relations=[
                {
                    "target_file": "scripts/ch01/missing.py",
                    "target_entity": None,
                    "equivalence": "E0",
                    "kind": "excerpt",
                    "evidence": "存在しない",
                    "verification": "manual",
                }
            ],
        )
        with pytest.raises(ValueError, match="target_fileが存在しない"):
            build_inventory(
                root,
                overrides,
                _test_results(),
                generated_at="2026-07-26T00:00:00+09:00",
                include_history=False,
            )

    def test_repository_override_counts_and_hashes(self) -> None:
        overrides = load_overrides(OVERRIDES_PATH)
        blocks, _ = extract_all_blocks(PROJECT_ROOT)
        apply_category_overrides(blocks, overrides)
        relations = add_relations(PROJECT_ROOT, blocks, overrides)
        assert len(overrides["category_overrides"]) == 26
        assert len(overrides["relation_overrides"]) == 83
        assert len(overrides["substitution_tests"]) == 28
        assert len(relations) == 529

    def test_rejects_stale_substitution_test_hash(self, tmp_path: Path) -> None:
        root = _minimal_repository(tmp_path)
        blocks, _ = extract_all_blocks(root)
        overrides = _minimal_overrides()
        target = (root / "scripts/ch01/add.py").read_text(encoding="utf-8")
        overrides["substitution_tests"] = {
            "B-01-001::scripts/ch01/add.py": {
                "status": "passed",
                "block_id": "B-01-001",
                "target_file": "scripts/ch01/add.py",
                "test_files": ["tests/ch01/test_add.py"],
                "block_sha256": blocks[0].sha256,
                "target_sha256": sha256_text(target),
                "test_file_sha256": {
                    "tests/ch01/test_add.py": "stale",
                },
            }
        }
        with pytest.raises(ValueError, match="テストハッシュが古い"):
            build_inventory(
                root,
                overrides,
                _test_results(),
                generated_at="2026-07-26T00:00:00+09:00",
                include_history=False,
            )


class TestBuildAndAudit:
    """小さなリポジトリで生成から独立監査まで通す."""

    def test_builds_e1_relation_and_test_mapping(self, tmp_path: Path) -> None:
        root = _minimal_repository(tmp_path)
        data = build_inventory(
            root,
            _minimal_overrides(),
            _test_results(),
            generated_at="2026-07-26T00:00:00+09:00",
            include_history=False,
        )
        block = data["blocks"][0]
        assert block["correspondence"] == "E1"
        assert block["relations"][0]["target_file"] == "scripts/ch01/add.py"
        assert block["tests"]["files"] == ["tests/ch01/test_add.py"]
        assert data["summary"]["book_blocks"] == 1
        assert data["summary"]["script_files"] == 1

    def test_rejects_missing_test_result(self, tmp_path: Path) -> None:
        root = _minimal_repository(tmp_path)
        with pytest.raises(ValueError, match="対象が一致しない"):
            validate_test_results(root, {})

    def test_non_pytest_asset_is_not_reported_as_passed(self) -> None:
        summary = summarize_test_results(
            ["tests/ch08/conftest.py"],
            _test_results(),
        )
        assert summary["status"] == "no_direct_test"
        assert summary["files"] == []

    def test_empty_relation_override_forces_e5(self, tmp_path: Path) -> None:
        root = _minimal_repository(tmp_path)
        blocks, _ = extract_all_blocks(root)
        data = build_inventory(
            root,
            _minimal_overrides(
                block_sha256=blocks[0].sha256,
                relations=[],
            ),
            _test_results(),
            generated_at="2026-07-26T00:00:00+09:00",
            include_history=False,
        )
        assert data["blocks"][0]["correspondence"] == "E5"

    def test_independent_audit_detects_source_tampering(
        self,
        tmp_path: Path,
    ) -> None:
        root = _minimal_repository(tmp_path)
        data = build_inventory(
            root,
            _minimal_overrides(),
            _test_results(),
            generated_at="2026-07-26T00:00:00+09:00",
            include_history=False,
        )
        report = render_report(data)
        assert audit(root, data, report)["status"] == "passed"
        tampered = deepcopy(data)
        tampered["blocks"][0]["sha256"] = "tampered"
        result = audit(root, tampered, report)
        assert result["status"] == "failed"
        assert "block_source_identity" in result["failures"]

    def test_determinism_normalization_removes_times(
        self,
        tmp_path: Path,
    ) -> None:
        root = _minimal_repository(tmp_path)
        first = build_inventory(
            root,
            _minimal_overrides(),
            _test_results(),
            generated_at="2026-07-26T00:00:00+09:00",
            include_history=False,
        )
        second = deepcopy(first)
        second["generated_at"] = "2026-07-27T00:00:00+09:00"
        second["source_commit"] = "different"
        second["test_files"]["tests/ch01/test_add.py"][
            "duration_seconds"
        ] = 99.0
        second["test_files"]["tests/ch01/test_add.py"][
            "summary"
        ] = "1 passed in 99.0s"
        assert normalized_for_determinism(
            first
        ) == normalized_for_determinism(second)


def test_override_file_is_valid_json() -> None:
    data = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1


def test_compatibility_cli_keeps_list_and_limit_flags(tmp_path: Path) -> None:
    output = tmp_path / "legacy.json"
    completed = subprocess.run(
        [
            str(PROJECT_ROOT / ".venv/bin/python"),
            "scripts/review/check_code_sync.py",
            "--output",
            str(output),
            "--list",
            "--max-unsynced",
            "1000",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["metric"] == "legacy_line_set_similarity"
    assert data["authoritative_report"] == "docs/review/code_correspondence.json"
