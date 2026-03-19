"""seqtool モジュールのテスト."""

from click.testing import CliRunner

from scripts.ch09.seqtool import cli

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
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "配列解析ツール" in result.output


def test_version() -> None:
    """--version がバージョン番号を表示する."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_stats_table(tmp_path) -> None:
    """stats サブコマンドがtable形式で統計を表示する."""
    input_file = tmp_path / "input.fasta"
    input_file.write_text(FASTA_DATA)

    runner = CliRunner()
    result = runner.invoke(cli, ["stats", str(input_file)])
    assert result.exit_code == 0


def test_stats_plain(tmp_path) -> None:
    """stats サブコマンドがplain形式でTSVを出力する."""
    input_file = tmp_path / "input.fasta"
    input_file.write_text(FASTA_DATA)

    runner = CliRunner()
    result = runner.invoke(
        cli, ["stats", str(input_file), "--format", "plain"]
    )
    assert result.exit_code == 0
    assert "配列数\t3" in result.output
    assert "平均GC含量" in result.output


def test_stats_stdin() -> None:
    """stats サブコマンドがstdinから読み込める."""
    runner = CliRunner()
    result = runner.invoke(cli, ["stats", "--format", "plain"], input=FASTA_DATA)
    assert result.exit_code == 0
    assert "配列数\t3" in result.output


def test_filter_basic(tmp_path) -> None:
    """filter サブコマンドがGCフィルタリングを行う."""
    input_file = tmp_path / "input.fasta"
    input_file.write_text(FASTA_DATA)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["filter", str(input_file), "--min-gc", "0.6", "--no-progress"],
    )
    assert result.exit_code == 0
    assert "seq1" in result.output
    assert "seq2" not in result.output


def test_filter_stdin() -> None:
    """filter サブコマンドがstdinから読み込める."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["filter", "--min-gc", "0.4", "--max-gc", "0.6", "--no-progress"],
        input=FASTA_DATA,
    )
    assert result.exit_code == 0
    assert "seq3" in result.output


def test_filter_with_output(tmp_path) -> None:
    """filter サブコマンドがファイルに出力する."""
    input_file = tmp_path / "input.fasta"
    input_file.write_text(FASTA_DATA)
    output_file = tmp_path / "output.fasta"

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "filter",
            str(input_file),
            "-o",
            str(output_file),
            "--min-gc",
            "0.4",
            "--no-progress",
        ],
    )
    assert result.exit_code == 0
    content = output_file.read_text()
    assert "seq1" in content
    assert "seq3" in content


def test_convert_to_tab(tmp_path) -> None:
    """convert サブコマンドがTSV形式に変換する."""
    input_file = tmp_path / "input.fasta"
    input_file.write_text(FASTA_DATA)

    runner = CliRunner()
    result = runner.invoke(cli, ["convert", str(input_file), "--to", "tab"])
    assert result.exit_code == 0
    assert "seq1\tGCGCGCGCGC" in result.output
    assert "seq2\tATATATATAT" in result.output


def test_convert_to_fasta(tmp_path) -> None:
    """convert サブコマンドがFASTA形式で出力する."""
    input_file = tmp_path / "input.fasta"
    input_file.write_text(FASTA_DATA)

    runner = CliRunner()
    result = runner.invoke(cli, ["convert", str(input_file), "--to", "fasta"])
    assert result.exit_code == 0
    assert ">seq1" in result.output


def test_convert_stdin() -> None:
    """convert サブコマンドがstdinから読み込める."""
    runner = CliRunner()
    result = runner.invoke(
        cli, ["convert", "--to", "tab"], input=FASTA_DATA
    )
    assert result.exit_code == 0
    assert "seq1\tGCGCGCGCGC" in result.output


def test_verbose_flag(tmp_path) -> None:
    """--verbose フラグがグループレベルで機能する."""
    input_file = tmp_path / "input.fasta"
    input_file.write_text(FASTA_DATA)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["--verbose", "stats", str(input_file), "--format", "plain"],
    )
    assert result.exit_code == 0


def test_log_level_option(tmp_path) -> None:
    """--log-level オプションがグループレベルで機能する."""
    input_file = tmp_path / "input.fasta"
    input_file.write_text(FASTA_DATA)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--log-level",
            "DEBUG",
            "stats",
            str(input_file),
            "--format",
            "plain",
        ],
    )
    assert result.exit_code == 0
