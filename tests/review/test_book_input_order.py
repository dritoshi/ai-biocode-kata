"""統計と各ビルド経路の入力ファイル順を検証する."""

from __future__ import annotations

import re
from pathlib import Path

from scripts.count_chars import (
    CHAPTER_LABELS,
    READING_SPEEDS,
    count_chars,
    estimate_reading_time,
    format_time,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHAPTERS_DIR = PROJECT_ROOT / "chapters"


def _shell_chapter_order(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r"^CHAPTER_ORDER=\(\n(?P<body>.*?)^\)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert match is not None
    return [
        line.strip()
        for line in match.group("body").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _vivliostyle_chapter_order(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r"^\s*entry: \[\n(?P<body>.*?)^\s*\],",
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert match is not None
    return re.findall(r"'chapters/([^']+)'", match.group("body"))


def test_statistics_cover_every_manuscript_file() -> None:
    expected = {path.name for path in CHAPTERS_DIR.glob("*.md")}

    assert set(CHAPTER_LABELS) == expected
    assert len(count_chars(CHAPTERS_DIR)) == len(expected)


def test_build_inputs_match_statistics_order() -> None:
    expected = list(CHAPTER_LABELS)

    assert _shell_chapter_order(PROJECT_ROOT / "build" / "build_pdf.sh") == expected
    assert _shell_chapter_order(PROJECT_ROOT / "build" / "build_epub.sh") == expected
    assert (
        _vivliostyle_chapter_order(PROJECT_ROOT / "vivliostyle.config.js")
        == expected
    )


def test_chapter_stats_match_current_manuscript() -> None:
    results = count_chars(CHAPTERS_DIR)
    stats = (PROJECT_ROOT / "docs" / "chapter_stats.md").read_text(encoding="utf-8")
    totals = [sum(row[index] for row in results) for index in range(1, 6)]

    for label, raw, body, code, body_z, code_z in results:
        count_row = (
            f"| {label} | {raw:,} | {body:,} | {code:,} | "
            f"{body_z:,} | {code_z:,} |"
        )
        assert count_row in stats

        times = [
            format_time(estimate_reading_time(body_z, code_z, speed))
            for speed in READING_SPEEDS.values()
        ]
        assert f"| {label} | {' | '.join(times)} |" in stats

    total_row = (
        f"| **合計** | **{totals[0]:,}** | **{totals[1]:,}** | "
        f"**{totals[2]:,}** | **{totals[3]:,}** | **{totals[4]:,}** |"
    )
    assert total_row in stats
