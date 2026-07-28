"""E1解消バッチで共有するfixture・遷移・snapshot検証."""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

PLAN_PATH = "docs/review/2026-07-28_e1_remediation_plan.md"
FIXTURE_PATH = "tests/review/fixtures/e1_expected_relations.json"
GENERATED_ARTIFACTS = {
    "docs/review/code_correspondence.json",
    "docs/review/code_correspondence.md",
    "docs/review/structure_check.json",
    "docs/review/xref_check.json",
}
PENDING_FIELDS = {
    "block_id",
    "status",
    "scheduled_batch",
    "expected_terminal_status",
}
TERMINAL_STATUSES = {
    "added",
    "satisfied_existing",
    "body_only",
    "not_applicable",
}
SEMANTIC_CATEGORIES = {
    "biological_data_assumption",
    "unit_shape_boundary",
    "implementation_decision",
    "performance_intent",
    "chapter_context",
    "none",
}
IGNORED_PARTS = {
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}


def _run_git(root: Path, *args: str) -> str:
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


def load_fixture(root: Path) -> dict[str, Any]:
    """固定fixtureを読み、主要な保存則を検証する."""
    path = root / FIXTURE_PATH
    data = json.loads(path.read_text(encoding="utf-8"))
    comments = data.get("comment_expectations", {})
    placements = data.get("placements", {})
    final_relations = data.get("final_relations", [])
    if data.get("schema_version") != 1:
        raise ValueError("E1 fixture schema_versionは1でなければならない")
    if len(comments) != 45 or set(comments) != set(placements):
        raise ValueError("E1 fixtureは同じ45 IDのコメントとplacementが必要")
    if len(final_relations) != 56:
        raise ValueError("E1 fixtureの最終関係は56件でなければならない")
    ids = sorted(comments)
    digest = hashlib.sha256(("\n".join(ids) + "\n").encode()).hexdigest()
    if digest != data.get("baseline_e1_sha256"):
        raise ValueError("E1 fixtureの基準IDハッシュが一致しない")
    for batch in range(6):
        if str(batch) not in data.get("batches", {}):
            raise ValueError(f"E1 fixtureにバッチ{batch}がない")
    return data


def baseline_e1_ids(fixture: dict[str, Any]) -> list[str]:
    """固定した基準E1 IDを昇順で返す."""
    return sorted(fixture["comment_expectations"])


def pending_comment_record(
    block_id: str,
    expectation: dict[str, Any],
) -> dict[str, Any]:
    """規範アンカーから4フィールドだけのpendingを作る."""
    return {
        "block_id": block_id,
        "status": "pending",
        "scheduled_batch": expectation["scheduled_batch"],
        "expected_terminal_status": expectation["terminal_status"],
    }


def normalized_evidence_bytes(lines: Iterable[str]) -> bytes:
    """証拠行をLF・行末空白・末尾LFの規則で正規化する."""
    normalized = "\n".join(line.rstrip() for line in lines) + "\n"
    return normalized.encode("utf-8")


def evidence_sha256(path: Path, line_start: int, line_end: int) -> str:
    """1始まりの行範囲から正規化済み証拠ハッシュを返す."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not (1 <= line_start <= line_end <= len(lines)):
        raise ValueError(
            f"証拠行範囲が不正: {path}:{line_start}-{line_end}"
        )
    return hashlib.sha256(
        normalized_evidence_bytes(lines[line_start - 1 : line_end])
    ).hexdigest()


def _review_paths(root: Path, directory: str) -> list[Path]:
    base = root / directory
    if not base.exists():
        return []
    return sorted(
        path
        for path in base.rglob("*")
        if path.is_file()
        and not IGNORED_PARTS.intersection(path.parts)
        and path.suffix != ".pyc"
    )


def _chapter_asset_paths(root: Path, directory: str) -> list[Path]:
    return sorted(
        path
        for path in (root / directory).glob("ch[0-9][0-9]/**/*")
        if path.is_file()
        and not IGNORED_PARTS.intersection(path.parts)
        and path.suffix != ".pyc"
    )


def source_snapshot_files(root: Path) -> list[Path]:
    """スキーマ4のsource provenance対象を固定順で返す."""
    paths = [
        *sorted((root / "chapters").glob("[0-9][0-9]_*.md")),
        *_chapter_asset_paths(root, "scripts"),
        *_chapter_asset_paths(root, "tests"),
        *_review_paths(root, "scripts/review"),
        *_review_paths(root, "tests/review"),
    ]
    plan = root / PLAN_PATH
    if plan.is_file():
        paths.append(plan)
    return sorted(set(paths))


def snapshot_sha256(root: Path, paths: Iterable[Path]) -> str:
    """作業ツリーの指定ファイルからsnapshotを計算する."""
    digest = hashlib.sha256()
    for path in sorted(paths):
        relative = str(path.relative_to(root))
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def git_snapshot_sha256(
    root: Path,
    commit: str,
    relative_paths: Iterable[str],
) -> str:
    """Git treeのblobだけからsnapshotを再計算する."""
    digest = hashlib.sha256()
    for relative in sorted(relative_paths):
        result = subprocess.run(
            ["git", "show", f"{commit}:{relative}"],
            cwd=root,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            detail = result.stderr.decode(errors="replace").strip()
            raise ValueError(
                f"Git treeにsnapshot対象がない: {relative}: {detail}"
            )
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(result.stdout)
        digest.update(b"\0")
    return digest.hexdigest()


def assert_worktree_matches_head(
    root: Path,
    relative_paths: Iterable[str],
) -> str:
    """snapshot対象がHEADのGit treeとバイト一致することを保証する."""
    head = _run_git(root, "rev-parse", "HEAD")
    paths = sorted(relative_paths)
    worktree = snapshot_sha256(root, [root / path for path in paths])
    committed = git_snapshot_sha256(root, head, paths)
    if worktree != committed:
        raise ValueError(
            "snapshot対象に未コミット変更があるため対応表を生成できない"
        )
    return head


def relation_signature(
    block_id: str,
    relation: dict[str, Any],
) -> tuple[str, str | None, str | None, str, str | None, str]:
    """fixtureと比較する定義単位の関係署名を返す."""
    return (
        block_id,
        relation.get("source_entity_id"),
        relation.get("source_entity"),
        relation["target_file"],
        relation.get("target_entity"),
        relation["equivalence"],
    )


def relation_summaries(
    blocks: list[dict[str, Any]],
    tracked_ids: set[str],
) -> tuple[dict[str, int], dict[str, int], int]:
    """基準45 IDの関係を親判定別・関係判定別に集計する."""
    by_parent: Counter[str] = Counter()
    by_equivalence: Counter[str] = Counter()
    total = 0
    for block in blocks:
        if block["id"] not in tracked_ids:
            continue
        for relation in block["relations"]:
            by_parent[block["correspondence"]] += 1
            by_equivalence[relation["equivalence"]] += 1
            total += 1
    stages = ("E0", "E1", "E2")
    return (
        {stage: by_parent.get(stage, 0) for stage in stages},
        {stage: by_equivalence.get(stage, 0) for stage in stages},
        total,
    )


def _qualified_ranges(path: Path) -> dict[str, tuple[int, int]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: dict[str, tuple[int, int]] = {}

    def walk(body: list[ast.stmt], prefix: str = "") -> None:
        for node in body:
            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
            ):
                name = f"{prefix}.{node.name}" if prefix else node.name
                found[name] = (
                    int(node.lineno),
                    int(node.end_lineno or node.lineno),
                )
                walk(node.body, name)

    walk(tree.body)
    return found


def _validate_evidence(
    root: Path,
    evidence: dict[str, Any],
    *,
    expected_file: str,
    entity: str | None = None,
) -> None:
    if evidence.get("file") != expected_file:
        raise ValueError(f"証拠ファイルが規範と異なる: {evidence}")
    line_start = int(evidence.get("line_start", 0))
    line_end = int(evidence.get("line_end", 0))
    actual = evidence_sha256(root / expected_file, line_start, line_end)
    if evidence.get("sha256") != actual:
        raise ValueError(f"証拠ハッシュが一致しない: {evidence}")
    if entity is not None:
        ranges = _qualified_ranges(root / expected_file)
        if entity not in ranges:
            raise ValueError(f"証拠entityが解決できない: {entity}")
        entity_start, entity_end = ranges[entity]
        if not (
            entity_start <= line_start <= line_end <= entity_end
        ):
            raise ValueError(f"証拠がentity範囲外: {evidence}")


def validate_comment_sync(
    root: Path,
    records: list[dict[str, Any]],
    fixture: dict[str, Any],
    batch: int,
) -> None:
    """45件のpending/終端状態、列挙値、証拠位置を検証する."""
    expectations = fixture["comment_expectations"]
    if len(records) != 45:
        raise ValueError("comment_syncは45件でなければならない")
    by_id = {record.get("block_id"): record for record in records}
    if set(by_id) != set(expectations):
        raise ValueError("comment_syncのID集合が固定45 IDと異なる")
    expected_completed = set(
        fixture["batches"][str(batch)]["completed_ids"]
    )
    for block_id, expectation in expectations.items():
        record = by_id[block_id]
        if block_id not in expected_completed:
            expected = pending_comment_record(block_id, expectation)
            if record != expected:
                raise ValueError(f"pendingレコードが不正: {block_id}")
            continue
        if record.get("status") != expectation["terminal_status"]:
            raise ValueError(f"終端状態が規範と異なる: {block_id}")
        if record.get("semantic_category") not in SEMANTIC_CATEGORIES:
            raise ValueError(f"意味分類が不正: {block_id}")
        for key in (
            "source_evidence_type",
            "semantic_category",
        ):
            expected_key = (
                "source_evidence"
                if key == "source_evidence_type"
                else key
            )
            if record.get(key) != expectation[expected_key]:
                raise ValueError(f"{key}が規範と異なる: {block_id}")
        if not str(record.get("reason", "")).strip():
            raise ValueError(f"終端理由がない: {block_id}")
        source_evidence = record.get("source_evidence", [])
        target_evidence = record.get("target_evidence", [])
        status = record["status"]
        if status in {"added", "satisfied_existing"}:
            if not source_evidence or not target_evidence:
                raise ValueError(f"両側の証拠が必要: {block_id}")
        elif status == "body_only":
            if not source_evidence or target_evidence:
                raise ValueError(f"body_onlyの証拠が不正: {block_id}")
        elif status == "not_applicable":
            if source_evidence or target_evidence:
                raise ValueError(f"not_applicableに証拠は置けない: {block_id}")
        if not isinstance(source_evidence, list) or not isinstance(
            target_evidence,
            list,
        ):
            raise ValueError(f"証拠は配列でなければならない: {block_id}")
        for evidence in source_evidence:
            _validate_evidence(
                root,
                evidence,
                expected_file=expectation["source_file"],
            )
        for evidence in target_evidence:
            if evidence.get("scope") != expectation["target_scope"]:
                raise ValueError(f"target scopeが規範と異なる: {block_id}")
            if evidence.get("entity") != expectation["target_entity"]:
                raise ValueError(f"target entityが規範と異なる: {block_id}")
            _validate_evidence(
                root,
                evidence,
                expected_file=expectation["target_file"],
                entity=(
                    expectation["target_entity"]
                    if expectation["target_scope"] == "entity"
                    else None
                ),
            )


def validate_e1_inventory(
    root: Path,
    data: dict[str, Any],
    fixture: dict[str, Any],
    batch: int,
) -> None:
    """成果物のE1バッチ保存則をfixtureから独立検査する."""
    if data.get("schema_version") != 4:
        raise ValueError("対応表schema_versionは4でなければならない")
    scope = data.get("remediation_scope", {})
    if scope.get("completed_batch") != batch:
        raise ValueError("completed_batchが期待値と異なる")
    ids = baseline_e1_ids(fixture)
    if scope.get("baseline_commit") != fixture["baseline_ref"]:
        raise ValueError("基準コミットがfixtureと異なる")
    if scope.get("baseline_e1_ids") != ids:
        raise ValueError("基準E1 IDがfixtureと異なる")
    if scope.get("baseline_e1_sha256") != fixture["baseline_e1_sha256"]:
        raise ValueError("基準E1 IDハッシュがfixtureと異なる")

    blocks = data["blocks"]
    block_by_id = {block["id"]: block for block in blocks}
    placements = {
        block_id: block_by_id[block_id]["placement"] for block_id in ids
    }
    if placements != fixture["placements"]:
        raise ValueError("基準45 IDのplacementがfixtureと異なる")
    expected_batch = fixture["batches"][str(batch)]
    if data["summary"]["correspondence_all"] != expected_batch["correspondence"]:
        raise ValueError("E判定件数がバッチ期待値と異なる")

    by_parent, by_equivalence, total = relation_summaries(blocks, set(ids))
    if total != expected_batch["relation_count"]:
        raise ValueError("基準45 IDの関係件数が期待値と異なる")
    if by_parent != expected_batch["relations_by_parent_block_correspondence"]:
        raise ValueError("親ブロック判定別関係件数が期待値と異なる")
    if by_equivalence != expected_batch["relations_by_equivalence"]:
        raise ValueError("関係自身の判定別件数が期待値と異なる")

    completed_ids = set(expected_batch["completed_ids"])
    expected_relations = {
        tuple(item)
        for item in fixture["final_relations"]
        if item[0] in completed_ids
    }
    actual_relations = {
        relation_signature(block_id, relation)
        for block_id in completed_ids
        for relation in block_by_id[block_id]["relations"]
    }
    if actual_relations != expected_relations:
        raise ValueError("完了済みIDの定義単位関係がfixtureと異なる")
    validate_comment_sync(
        root,
        data.get("comment_sync", []),
        fixture,
        batch,
    )

    relative_paths = data.get("source_snapshot_files", [])
    expected_paths = [
        str(path.relative_to(root)) for path in source_snapshot_files(root)
    ]
    if relative_paths != expected_paths:
        raise ValueError("source_snapshot_filesが固定対象集合と異なる")
    if snapshot_sha256(
        root,
        [root / path for path in relative_paths],
    ) != data.get("source_snapshot_sha256"):
        raise ValueError("作業ツリーのsource snapshotが一致しない")
    source_commit = data.get("source_commit")
    if source_commit:
        committed = git_snapshot_sha256(root, source_commit, relative_paths)
        if committed != data.get("source_snapshot_sha256"):
            raise ValueError("Git treeのsource snapshotが一致しない")
