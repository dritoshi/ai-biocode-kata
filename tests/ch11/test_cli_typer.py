"""cli_typer モジュールの直接CLIテスト."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
from click.utils import strip_ansi
from typer.testing import CliRunner

from scripts.ch11.cli_typer import app

FASTA_DATA = """\
>seq1 high GC
GCGCGCGCGC
>seq2 low GC
ATATATATAT
>seq3 medium GC
ATGCATGCAT
"""


@pytest.fixture(autouse=True)
def _reset_logging() -> None:
    """各テスト後にルートロガー設定を戻す."""
    yield
    root = logging.getLogger()
    for handler in root.handlers[:]:
        handler.close()
        root.removeHandler(handler)
    root.setLevel(logging.WARNING)


def _input_file(tmp_path: Path) -> Path:
    """テスト用FASTAファイルを作成する."""
    path = tmp_path / "input.fasta"
    path.write_text(FASTA_DATA, encoding="utf-8")
    return path


def test_help() -> None:
    """--helpが入力とオプションを説明する."""
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    help_text = strip_ansi(result.stdout)
    assert "入力FASTAファイル" in help_text
    assert "--min-gc" in help_text


def test_filters_to_stdout(tmp_path: Path) -> None:
    """正常入力をフィルタしてstdoutへ出力する."""
    result = CliRunner().invoke(
        app,
        [str(_input_file(tmp_path)), "--min-gc", "0.6"],
    )

    assert result.exit_code == 0
    assert "seq1" in result.stdout
    assert "seq2" not in result.stdout


def test_writes_output_file(tmp_path: Path) -> None:
    """-o指定時はFASTA結果をファイルへ出力する."""
    output_path = tmp_path / "output.fasta"
    result = CliRunner().invoke(
        app,
        [
            str(_input_file(tmp_path)),
            "--min-gc",
            "0.4",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    content = output_path.read_text(encoding="utf-8")
    assert "seq1" in content
    assert "seq3" in content


def test_rejects_out_of_range_value(tmp_path: Path) -> None:
    """範囲外のGC含量は終了コード2で拒否する."""
    result = CliRunner().invoke(
        app,
        [str(_input_file(tmp_path)), "--min-gc", "1.5"],
    )

    assert result.exit_code == 2
    assert "Invalid value" in result.stderr
