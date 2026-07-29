import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COLUMN_FILTER = PROJECT_ROOT / "build" / "column-anchor.lua"
EMOJI_FILTER = PROJECT_ROOT / "build" / "emoji-filter.lua"
EPIGRAPH_FILTER = PROJECT_ROOT / "build" / "epigraph.lua"
CROSSREF_FILTER = PROJECT_ROOT / "build" / "fix-crossref.lua"


def _pandoc() -> str:
    executable = shutil.which("pandoc")
    if executable is None:
        pytest.skip("pandoc is required to exercise the column anchor filter")
    return executable


def _convert(
    markdown: str,
    output_format: str,
    filters: tuple[Path, ...] = (COLUMN_FILTER,),
) -> subprocess.CompletedProcess[str]:
    command = [_pandoc(), "-f", "markdown", "-t", output_format]
    command.extend(f"--lua-filter={path}" for path in filters)
    return subprocess.run(
        command,
        input=markdown,
        text=True,
        capture_output=True,
        check=False,
    )


def test_converts_column_anchor_to_latex_target() -> None:
    result = _convert(
        '> <a id="column-ch00-01"></a> **コラム: テスト**\n',
        "latex",
    )

    assert result.returncode == 0, result.stderr
    assert r"\hypertarget{column-ch00-01}{}" in result.stdout
    assert r"\label{column-ch00-01}" in result.stdout
    assert "コラム" in result.stdout


def test_does_not_promote_unrelated_html_anchor() -> None:
    result = _convert(
        '> <a id="other-anchor"></a> **コラム: テスト**\n',
        "latex",
    )

    assert result.returncode == 0, result.stderr
    assert r"\hypertarget{other-anchor}{}" not in result.stdout


def test_anchored_column_is_not_converted_to_epigraph() -> None:
    markdown = (
        '> <a id="column-ch00-01"></a> 🧬 **コラム: テスト**\n'
        "> 説明文\n"
        "> — 出典\n"
    )
    result = _convert(
        markdown,
        "latex",
        (EMOJI_FILTER, EPIGRAPH_FILTER, COLUMN_FILTER),
    )

    assert result.returncode == 0, result.stderr
    assert r"\hypertarget{column-ch00-01}{}" in result.stdout
    assert r"\begin{quote}" in result.stdout
    assert r"\epigraph{" not in result.stdout


def test_inline_anchor_does_not_create_empty_html_paragraph() -> None:
    result = _convert(
        '> <a id="column-ch00-01"></a> **コラム: テスト**\n',
        "html5",
        (),
    )

    assert result.returncode == 0, result.stderr
    assert '<p><a id="column-ch00-01"></a></p>' not in result.stdout
    assert '<p><a id="column-ch00-01"></a> <strong>' in result.stdout


def test_pdf_keeps_column_link_and_target() -> None:
    markdown = (
        "[コラム索引](./00_ai_agent.md#column-ch00-01)\n\n"
        '> <a id="column-ch00-01"></a> **コラム: テスト**\n'
    )
    result = _convert(
        markdown,
        "latex",
        (COLUMN_FILTER, CROSSREF_FILTER),
    )

    assert result.returncode == 0, result.stderr
    valid_links = (
        r"\hyperref[column-ch00-01]{コラム索引}",
        r"\protect\hyperlink{column-ch00-01}{コラム索引}",
    )
    assert any(link in result.stdout for link in valid_links)
    assert r"\hypertarget{column-ch00-01}{}" in result.stdout
    assert r"\label{column-ch00-01}" in result.stdout


def test_epub_html_keeps_column_link_and_target() -> None:
    markdown = (
        "[コラム索引](./00_ai_agent.md#column-ch00-01)\n\n"
        '> <a id="column-ch00-01"></a> **コラム: テスト**\n'
    )
    result = _convert(
        markdown,
        "html5",
        (CROSSREF_FILTER,),
    )

    assert result.returncode == 0, result.stderr
    assert 'href="#column-ch00-01"' in result.stdout
    assert 'id="column-ch00-01"' in result.stdout
