"""コラム索引と本文アンカーの同期を検証する."""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHAPTERS_DIR = PROJECT_ROOT / "chapters"
INDEX_PATH = CHAPTERS_DIR / "appendix_e_column_index.md"

COLUMN_RE = re.compile(
    r'^> <a id="(?P<id>column-ch\d{2}-\d{2})"></a>\s+(?P<title>.+)$',
    re.MULTILINE,
)
INDEX_LINK_RE = re.compile(
    r"^- \[(?P<title>.+)\]\(\./(?P<file>[^#)]+)"
    r"#(?P<id>column-ch\d{2}-\d{2})\)$",
    re.MULTILINE,
)


def normalized_title(title: str) -> str:
    """コラム見出しと索引ラベルを比較できる形にそろえる."""
    return title.removeprefix("#### ").removeprefix("### ").replace("**", "")


def source_columns() -> dict[tuple[str, str], str]:
    """本文のコラムをファイル名・IDからタイトルへ対応付ける."""
    columns: dict[tuple[str, str], str] = {}
    for path in sorted(CHAPTERS_DIR.glob("*.md")):
        if path == INDEX_PATH:
            continue
        for match in COLUMN_RE.finditer(path.read_text(encoding="utf-8")):
            key = (path.name, match.group("id"))
            assert key not in columns, f"コラムIDが重複している: {key}"
            columns[key] = normalized_title(match.group("title"))
    return columns


def indexed_columns() -> tuple[dict[tuple[str, str], str], int]:
    """索引のリンクをファイル名・IDからラベルへ対応付ける."""
    text = INDEX_PATH.read_text(encoding="utf-8")
    matches = list(INDEX_LINK_RE.finditer(text))
    columns = {
        (match.group("file"), match.group("id")): match.group("title")
        for match in matches
    }
    return columns, len(matches)


def test_column_index_covers_every_column_once() -> None:
    indexed, link_count = indexed_columns()
    source = source_columns()

    assert len(source) == 69
    assert link_count == len(indexed), "索引に同じコラムへのリンクが重複している"
    assert indexed.keys() == source.keys()


def test_column_index_labels_match_column_titles() -> None:
    indexed, _ = indexed_columns()

    assert indexed == source_columns()
