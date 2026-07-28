#!/usr/bin/env python3
"""保存済みコード対応表をソースから独立に再計算して監査する."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.review.e1_remediation import (  # noqa: E402
    git_snapshot_sha256,
    load_fixture,
    source_snapshot_files,
    validate_e1_inventory,
)

FENCE_RE = re.compile(r"^\s*(?:>\s*)*(`{3,}|~{3,})\s*([^\s`]*)")
IGNORED_ASSET_DIRS = {
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}
GOLDSET_STAGES = ("E0", "E1", "E2", "E3", "E5", "EN")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8"))


def _strip_quote(line: str) -> str:
    return re.sub(r"^\s*>\s?", "", line)


def _source_blocks(root: Path) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for path in sorted((root / "chapters").glob("[0-9][0-9]_*.md")):
        chapter = path.name[:2]
        lines = path.read_text(encoding="utf-8").splitlines()
        opener: str | None = None
        start = 0
        language = "none"
        body: list[str] = []
        count = 0
        for line_number, raw in enumerate(lines, 1):
            match = FENCE_RE.match(raw)
            if opener is None:
                if match:
                    opener = match.group(1)[0]
                    start = line_number
                    language = (match.group(2) or "none").lower()
                    body = []
                continue
            if match and match.group(1)[0] == opener:
                count += 1
                code = "\n".join(_strip_quote(line) for line in body)
                blocks.append(
                    {
                        "id": f"B-{chapter}-{count:03d}",
                        "path": str(path.relative_to(root)),
                        "line_start": start,
                        "line_end": line_number,
                        "lang": language,
                        "sha256": _sha256_text(code),
                    }
                )
                opener = None
                continue
            body.append(raw)
        if opener is not None:
            raise ValueError(f"閉じていないコードフェンス: {path}:{start}")
    return blocks


def _asset_paths(root: Path, base_name: str) -> list[Path]:
    return sorted(
        path
        for path in (root / base_name).glob("ch[0-9][0-9]/**/*")
        if path.is_file()
        and not IGNORED_ASSET_DIRS.intersection(path.parts)
        and path.suffix != ".pyc"
    )


def _source_snapshot(root: Path, paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _normalized(code: str) -> str:
    return ast.dump(ast.parse(code), include_attributes=False)


def _negative_normalizer_checks() -> dict[str, bool]:
    base = (
        "def f(x, y):\n"
        "    z = x + y\n"
        "    if z < 10:\n"
        "        return z\n"
        "    raise ValueError(z)\n"
    )
    mutations = {
        "operator": base.replace("x + y", "x - y"),
        "boundary": base.replace("z < 10", "z <= 10"),
        "exception": base.replace("ValueError", "TypeError"),
        "argument_order": base.replace("def f(x, y)", "def f(y, x)"),
        "statement_order": (
            "def f(x, y):\n"
            "    if x + y < 10:\n"
            "        return x + y\n"
            "    z = x + y\n"
            "    raise ValueError(z)\n"
        ),
    }
    original = _normalized(base)
    return {
        name: _normalized(code) != original
        for name, code in mutations.items()
    }


def _populated_goldset_stages(
    correspondence: Counter[str],
) -> tuple[str, ...]:
    """母集団が存在する分類だけを層化監査の対象にする."""

    return tuple(
        stage
        for stage in GOLDSET_STAGES
        if correspondence.get(stage, 0) > 0
    )


def audit(
    root: Path,
    data: dict[str, Any],
    report: str,
) -> dict[str, Any]:
    """全保存則を再計算し、チェック名と成否を返す."""

    source_blocks = _source_blocks(root)
    source_block_by_id = {item["id"]: item for item in source_blocks}
    script_paths = _asset_paths(root, "scripts")
    test_asset_paths = _asset_paths(root, "tests")
    pytest_paths = [
        *sorted((root / "tests").glob("ch[0-9][0-9]/test_*.py")),
        *sorted((root / "tests/review").glob("test_*.py")),
    ]
    source_paths = [root / path for path in data["source_snapshot_files"]]
    checks: dict[str, bool] = {}
    blocks = data["blocks"]
    scripts = data["scripts"]
    test_assets = data["test_assets"]

    checks["schema_version"] = data.get("schema_version") == 4
    checks["method"] = (
        data.get("method")
        == "docs/review/2026-07-28_e1_remediation_plan.md"
    )
    checks["source_snapshot_files"] = data["source_snapshot_files"] == [
        str(path.relative_to(root)) for path in source_snapshot_files(root)
    ]
    checks["chapter_count"] = (
        len(list((root / "chapters").glob("[0-9][0-9]_*.md")))
        == data["summary"]["chapters"]
        == 22
    )
    checks["block_count"] = (
        len(source_blocks)
        == len(blocks)
        == data["summary"]["book_blocks"]
    )
    checks["block_ids_unique"] = len(
        {item["id"] for item in blocks}
    ) == len(blocks)
    checks["block_source_identity"] = all(
        source_block_by_id.get(item["id"])
        == {
            key: item[key]
            for key in (
                "id",
                "path",
                "line_start",
                "line_end",
                "lang",
                "sha256",
            )
        }
        for item in blocks
    )
    checks["script_count"] = (
        len(script_paths)
        == len(scripts)
        == data["summary"]["script_files"]
    )
    checks["script_paths_unique"] = len(
        {item["path"] for item in scripts}
    ) == len(scripts)
    checks["script_source_identity"] = all(
        (root / item["path"]).is_file()
        and _sha256_text(
            (root / item["path"]).read_text(
                encoding="utf-8",
                errors="replace",
            )
        )
        == item["sha256"]
        for item in scripts
    )
    checks["test_asset_count"] = (
        len(test_asset_paths)
        == len(test_assets)
        == data["summary"]["test_files_under_chapters"]
    )
    checks["test_asset_ids_unique"] = len(
        {item["id"] for item in test_assets}
    ) == len(test_assets)
    checks["all_target_ids_unique"] = len(
        {item["id"] for item in [*scripts, *test_assets]}
    ) == len(scripts) + len(test_assets)
    checks["test_asset_source_identity"] = all(
        (root / item["path"]).is_file()
        and _sha256_text(
            (root / item["path"]).read_text(
                encoding="utf-8",
                errors="replace",
            )
        )
        == item["sha256"]
        for item in test_assets
    )
    expected_test_paths = {
        str(path.relative_to(root)) for path in pytest_paths
    }
    checks["pytest_paths_complete"] = expected_test_paths == set(
        data["test_files"]
    )
    checks["source_snapshot"] = (
        _source_snapshot(root, source_paths)
        == data["source_snapshot_sha256"]
    )

    valid_targets = {
        item["path"] for item in [*scripts, *test_assets]
    }
    target_ids = {
        item["path"]: item["id"] for item in [*scripts, *test_assets]
    }
    checks["relation_targets_exist"] = all(
        relation["target_file"] in valid_targets
        for block in blocks
        for relation in block["relations"]
    )
    checks["relation_target_ids_resolve"] = all(
        relation["target_file_id"]
        == target_ids.get(relation["target_file"])
        for block in blocks
        for relation in block["relations"]
    )
    checks["relation_entity_locations_resolve"] = all(
        not relation.get("target_entity")
        or (
            relation["target_entity_locations"]
            and all(
                1
                <= location["line_start"]
                <= location["line_end"]
                <= len(
                    (root / relation["target_file"])
                    .read_text(encoding="utf-8")
                    .splitlines()
                )
                for location in relation["target_entity_locations"]
            )
        )
        for block in blocks
        for relation in block["relations"]
    )
    checks["relation_source_entity_locations_resolve"] = all(
        (
            relation.get("source_entity_id") is None
            and relation.get("source_entity") is None
            and not relation.get("source_entity_locations")
        )
        or (
            relation.get("source_entity_id")
            and relation.get("source_entity")
            and relation.get("source_entity_locations")
            and all(
                location["id"] == relation["source_entity_id"]
                and location["name"] == relation["source_entity"]
                and block["line_start"]
                < location["line_start"]
                <= location["line_end"]
                < block["line_end"]
                for location in relation["source_entity_locations"]
            )
        )
        for block in blocks
        for relation in block["relations"]
    )

    placements = Counter(item["placement"] for item in blocks)
    correspondence = Counter(item["correspondence"] for item in blocks)
    categories = Counter(item["category"] for item in blocks)
    required = [
        item
        for item in blocks
        if item["placement"] in {"required_scripts", "required_tests"}
    ]
    required_correspondence = Counter(
        item["correspondence"] for item in required
    )
    checks["placement_sum"] = sum(placements.values()) == len(blocks)
    checks["correspondence_sum"] = sum(correspondence.values()) == len(blocks)
    checks["required_no_en"] = all(
        item["correspondence"] != "EN" for item in required
    )
    checks["summary_placements"] = (
        dict(placements) == data["summary"]["placements"]
    )
    checks["summary_categories"] = (
        dict(categories) == data["summary"]["categories"]
    )
    checks["summary_correspondence_all"] = (
        dict(correspondence)
        == data["summary"]["correspondence_all"]
    )
    checks["summary_correspondence_required"] = (
        dict(required_correspondence)
        == data["summary"]["correspondence_required"]
    )

    test_totals = {
        "files": len(data["test_files"]),
        "chapter_test_files": sum(
            path.startswith("tests/ch") for path in data["test_files"]
        ),
        "review_test_files": sum(
            path.startswith("tests/review") for path in data["test_files"]
        ),
        "passed": sum(
            int(item["passed"]) for item in data["test_files"].values()
        ),
        "failed": sum(
            int(item["failed"]) for item in data["test_files"].values()
        ),
        "skipped": sum(
            int(item["skipped"]) for item in data["test_files"].values()
        ),
        "errors": sum(
            int(item["errors"]) for item in data["test_files"].values()
        ),
    }
    checks["summary_tests"] = test_totals == data["summary"]["test_run"]
    checks["test_files_passed"] = all(
        int(item["returncode"]) == 0
        and int(item["failed"]) == 0
        and int(item["errors"]) == 0
        for item in data["test_files"].values()
    )
    goldset = data["classification_review"]["goldset"]
    expected_stages = Counter(item["expected"] for item in goldset)
    requires_stratified_goldset = bool(
        data["classification_review"].get("goldset_method")
    )
    populated_stages = _populated_goldset_stages(correspondence)
    checks["goldset"] = (
        all(
            item["matched"]
            and item["expected"] == item["actual"]
            and bool(item["reason"])
            for item in goldset
        )
        and (
            not requires_stratified_goldset
            or all(
                expected_stages[stage] == 2
                for stage in populated_stages
            )
        )
    )
    checks["negative_normalizer"] = all(
        _negative_normalizer_checks().values()
    )
    substitution = Counter(
        item["status"] for item in data["substitution_tests"].values()
    )
    checks["summary_substitution"] = (
        dict(substitution)
        == data["summary"]["substitution_test_status"]
    )
    checks["summary_script_book_status"] = (
        dict(Counter(item["book_status"] for item in scripts))
        == data["summary"]["script_book_status"]
    )
    checks["summary_script_test_status"] = (
        dict(Counter(item["test_result"]["status"] for item in scripts))
        == data["summary"]["script_test_status"]
    )

    if data.get("remediation_scope"):
        try:
            fixture = load_fixture(root)
            batch = int(data["remediation_scope"]["completed_batch"])
            validate_e1_inventory(root, data, fixture, batch)
        except (KeyError, TypeError, ValueError):
            checks["e1_inventory"] = False
        else:
            checks["e1_inventory"] = True
        try:
            checks["source_commit_snapshot"] = (
                git_snapshot_sha256(
                    root,
                    data["source_commit"],
                    data["source_snapshot_files"],
                )
                == data["source_snapshot_sha256"]
            )
        except ValueError:
            checks["source_commit_snapshot"] = False

    markers = [
        "# 本文コード ↔ `scripts/ch*` 対応関係の再監査",
        f"| **合計** | **{len(blocks)}** | 全本文ブロック |",
        f"| テストファイル | {test_totals['files']} |",
        f"| passed | {test_totals['passed']} |",
        f"| failed | {test_totals['failed']} |",
        f"| errors | {test_totals['errors']} |",
    ]
    for stage in GOLDSET_STAGES:
        markers.append(
            f"| {stage} | {correspondence.get(stage, 0)} |"
        )
    checks["markdown_summary"] = all(
        marker in report for marker in markers
    )

    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": "passed" if not failures else "failed",
        "checks": checks,
        "negative_normalizer_checks": _negative_normalizer_checks(),
        "failures": failures,
    }


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent.parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument(
        "--input",
        type=Path,
        default=root / "docs/review/code_correspondence.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=root / "docs/review/code_correspondence.md",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    report = args.report.read_text(encoding="utf-8")
    result = audit(root, data, report)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
