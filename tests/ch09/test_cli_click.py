"""cli_click モジュールのテスト."""

from click.testing import CliRunner

from scripts.ch09.cli_click import gc_filter

# テスト用FASTAデータ
FASTA_DATA = """\
>seq1 high GC
GCGCGCGCGC
>seq2 low GC
ATATATATAT
>seq3 medium GC
ATGCATGCAT
"""


def test_help() -> None:
    """--help が正常に表示される."""
    runner = CliRunner()
    result = runner.invoke(gc_filter, ["--help"])
    assert result.exit_code == 0
    assert "GC含量" in result.output


def test_version() -> None:
    """--version がバージョン番号を表示する."""
    runner = CliRunner()
    result = runner.invoke(gc_filter, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_gc_filter_basic() -> None:
    """基本的なGCフィルタリングが動作する."""
    runner = CliRunner()
    result = runner.invoke(
        gc_filter,
        ["--min-gc", "0.6", "--max-gc", "1.0"],
        input=FASTA_DATA,
    )
    assert result.exit_code == 0
    # GC含量100%のseq1のみ通過
    assert "seq1" in result.output
    assert "seq2" not in result.output


def test_gc_filter_all_pass() -> None:
    """全配列が通過する条件で全配列が出力される."""
    runner = CliRunner()
    result = runner.invoke(
        gc_filter,
        ["--min-gc", "0.0", "--max-gc", "1.0"],
        input=FASTA_DATA,
    )
    assert result.exit_code == 0
    assert "seq1" in result.output
    assert "seq2" in result.output
    assert "seq3" in result.output


def test_gc_filter_none_pass() -> None:
    """全配列が除外される条件で出力が空になる."""
    runner = CliRunner()
    result = runner.invoke(
        gc_filter,
        ["--min-gc", "0.99", "--max-gc", "0.995"],
        input=FASTA_DATA,
    )
    assert result.exit_code == 0
    # 配列データがstdoutに出ない
    assert "seq1" not in result.output
    assert "seq2" not in result.output


def test_gc_filter_stdin() -> None:
    """stdinからの入力を処理できる."""
    runner = CliRunner()
    result = runner.invoke(
        gc_filter,
        ["--min-gc", "0.4", "--max-gc", "0.6"],
        input=FASTA_DATA,
    )
    assert result.exit_code == 0
    # GC含量50%のseq3が通過
    assert "seq3" in result.output


def test_gc_filter_verbose() -> None:
    """--verbose でデバッグ情報が出力される."""
    runner = CliRunner()
    result = runner.invoke(
        gc_filter,
        ["--verbose"],
        input=FASTA_DATA,
    )
    assert result.exit_code == 0


def test_gc_filter_with_file(tmp_path) -> None:
    """ファイル入力が正常に動作する."""
    input_file = tmp_path / "input.fasta"
    input_file.write_text(FASTA_DATA)
    output_file = tmp_path / "output.fasta"

    runner = CliRunner()
    result = runner.invoke(
        gc_filter,
        [str(input_file), "-o", str(output_file), "--min-gc", "0.4"],
    )
    assert result.exit_code == 0
    content = output_file.read_text()
    assert "seq1" in content
    assert "seq3" in content


def test_gc_filter_invalid_range() -> None:
    """不正なGC含量範囲でエラーになる."""
    runner = CliRunner()
    result = runner.invoke(
        gc_filter,
        ["--min-gc", "1.5"],
        input=FASTA_DATA,
    )
    assert result.exit_code != 0
