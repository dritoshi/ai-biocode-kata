"""cli_argparse モジュールの個別テスト."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

from scripts.ch11.cli_argparse import main, parse_args

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


def test_parse_args_defaults() -> None:
    """デフォルト引数を検証する."""
    args = parse_args([])
    assert args.input is None
    assert args.output is None
    assert args.min_gc == 0.0
    assert args.max_gc == 1.0
    assert args.verbose is False


def test_parse_args_with_options(tmp_path: Path) -> None:
    """主要オプションを指定してパースできる."""
    input_file = tmp_path / "input.fasta"
    input_file.write_text(FASTA_DATA)
    output_file = tmp_path / "output.fasta"

    args = parse_args(
        [
            str(input_file),
            "-o",
            str(output_file),
            "--min-gc",
            "0.4",
            "--max-gc",
            "0.6",
            "--verbose",
        ]
    )

    assert args.input == input_file
    assert args.output == output_file
    assert args.min_gc == pytest.approx(0.4)
    assert args.max_gc == pytest.approx(0.6)
    assert args.verbose is True


def test_parse_args_version(capsys: pytest.CaptureFixture[str]) -> None:
    """--version が終了コード 0 で表示される."""
    with pytest.raises(SystemExit) as excinfo:
        parse_args(["--version"])

    captured = capsys.readouterr()
    assert excinfo.value.code == 0
    assert "0.1.0" in captured.out


def test_main_filters_to_output_file(tmp_path: Path) -> None:
    """GC条件に合う配列だけをファイルへ出力できる."""
    input_file = tmp_path / "input.fasta"
    input_file.write_text(FASTA_DATA)
    output_file = tmp_path / "output.fasta"

    main([str(input_file), "-o", str(output_file), "--min-gc", "0.6"])

    content = output_file.read_text()
    assert "seq1" in content
    assert "seq2" not in content
    assert "seq3" not in content


def test_main_all_pass(tmp_path: Path) -> None:
    """全配列が通過する条件で全件出力される."""
    input_file = tmp_path / "input.fasta"
    input_file.write_text(FASTA_DATA)
    output_file = tmp_path / "output.fasta"

    main([str(input_file), "-o", str(output_file), "--min-gc", "0.0", "--max-gc", "1.0"])

    content = output_file.read_text()
    assert "seq1" in content
    assert "seq2" in content
    assert "seq3" in content


def test_main_none_pass(tmp_path: Path) -> None:
    """全配列が除外される条件では出力が空になる."""
    input_file = tmp_path / "input.fasta"
    input_file.write_text(FASTA_DATA)
    output_file = tmp_path / "output.fasta"

    main([str(input_file), "-o", str(output_file), "--min-gc", "0.99", "--max-gc", "0.995"])

    assert output_file.read_text() == ""


def test_main_verbose_runs(tmp_path: Path) -> None:
    """--verbose を付けても正常終了する."""
    input_file = tmp_path / "input.fasta"
    input_file.write_text(FASTA_DATA)
    output_file = tmp_path / "output.fasta"

    main([str(input_file), "-o", str(output_file), "--verbose", "--min-gc", "0.4"])

    content = output_file.read_text()
    assert "seq1" in content
    assert "seq3" in content
