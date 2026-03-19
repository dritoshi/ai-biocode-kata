"""サブコマンド統合CLI — stats / filter / convert の3コマンド構成."""

import logging
import sys

import click
from Bio import SeqIO

from scripts.ch07.seq_stats import gc_content
from scripts.ch09.logging_setup import setup_logging

logger = logging.getLogger(__name__)


@click.group()
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="デバッグログを表示する",
)
@click.option(
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        case_sensitive=False,
    ),
    default=None,
    help="ログレベルを指定する（--verboseより優先）",
)
@click.option(
    "--log-file",
    type=click.Path(),
    default=None,
    help="ログの出力先ファイル",
)
@click.version_option("0.1.0", prog_name="seqtool")
@click.pass_context
def cli(
    ctx: click.Context,
    verbose: bool,
    log_level: str | None,
    log_file: str | None,
) -> None:
    """配列解析ツール — FASTA配列の統計・フィルタリング・変換."""
    # ログレベルの3層構造: CLI引数 > デフォルト値
    if log_level is not None:
        effective_level = log_level.upper()
    elif verbose:
        effective_level = "DEBUG"
    else:
        effective_level = "WARNING"

    setup_logging(level=effective_level, log_file=log_file)
    ctx.ensure_object(dict)
    ctx.obj["log_level"] = effective_level


@cli.command()
@click.argument("input_file", type=click.File("r"), default="-")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "plain"], case_sensitive=False),
    default="table",
    show_default=True,
    help="出力形式（tableはrich表示、plainはTSV）",
)
def stats(input_file: click.utils.LazyFile, output_format: str) -> None:
    """配列の統計情報を表示する."""
    logger.info("統計情報の計算を開始")

    records = list(SeqIO.parse(input_file, "fasta"))
    if not records:
        click.echo("配列が見つかりません", err=True)
        sys.exit(1)

    # 統計計算
    lengths = [len(record.seq) for record in records]
    gc_values = [gc_content(str(record.seq)) for record in records]
    total = len(records)
    avg_length = sum(lengths) / total
    avg_gc = sum(gc_values) / total

    if output_format == "table":
        try:
            from rich.console import Console
            from rich.table import Table

            table = Table(title="配列統計")
            table.add_column("項目", style="cyan")
            table.add_column("値", style="green", justify="right")
            table.add_row("配列数", str(total))
            table.add_row("平均長", f"{avg_length:.1f}")
            table.add_row("最短", str(min(lengths)))
            table.add_row("最長", str(max(lengths)))
            table.add_row("平均GC含量", f"{avg_gc:.3f}")

            console = Console(stderr=True)
            console.print(table)
        except ImportError:
            # richが利用できない場合はplain出力にフォールバック
            output_format = "plain"

    if output_format == "plain":
        click.echo("項目\t値")
        click.echo(f"配列数\t{total}")
        click.echo(f"平均長\t{avg_length:.1f}")
        click.echo(f"最短\t{min(lengths)}")
        click.echo(f"最長\t{max(lengths)}")
        click.echo(f"平均GC含量\t{avg_gc:.3f}")

    logger.info("統計情報の計算完了: %d 配列", total)


@cli.command(name="filter")
@click.argument("input_file", type=click.File("r"), default="-")
@click.option(
    "-o",
    "--output",
    type=click.File("w"),
    default="-",
    help="出力ファイル（省略時はstdout）",
)
@click.option(
    "--min-gc",
    type=click.FloatRange(0.0, 1.0),
    default=0.0,
    show_default=True,
    help="GC含量の下限",
)
@click.option(
    "--max-gc",
    type=click.FloatRange(0.0, 1.0),
    default=1.0,
    show_default=True,
    help="GC含量の上限",
)
@click.option(
    "--progress/--no-progress",
    default=True,
    show_default=True,
    help="プログレスバーを表示する",
)
def filter_cmd(
    input_file: click.utils.LazyFile,
    output: click.utils.LazyFile,
    min_gc: float,
    max_gc: float,
    progress: bool,
) -> None:
    """GC含量で配列をフィルタリングする."""
    logger.info("フィルタ条件: GC含量 %.2f–%.2f", min_gc, max_gc)

    records = list(SeqIO.parse(input_file, "fasta"))

    # プログレスバー付きフィルタリング
    filtered = []
    iterator = records
    if progress and sys.stderr.isatty():
        try:
            from tqdm import tqdm

            iterator = tqdm(records, desc="フィルタリング", file=sys.stderr)
        except ImportError:
            pass

    for record in iterator:
        gc = gc_content(str(record.seq))
        if min_gc <= gc <= max_gc:
            filtered.append(record)

    count = SeqIO.write(filtered, output, "fasta")
    click.echo(
        f"フィルタ結果: {len(records)} 配列中 {count} 配列を出力",
        err=True,
    )


@cli.command()
@click.argument("input_file", type=click.File("r"), default="-")
@click.option(
    "-o",
    "--output",
    type=click.File("w"),
    default="-",
    help="出力ファイル（省略時はstdout）",
)
@click.option(
    "--to",
    "to_format",
    type=click.Choice(["fasta", "tab"], case_sensitive=False),
    default="tab",
    show_default=True,
    help="出力形式（fasta: FASTA, tab: TSV）",
)
def convert(
    input_file: click.utils.LazyFile,
    output: click.utils.LazyFile,
    to_format: str,
) -> None:
    """配列のフォーマットを変換する."""
    logger.info("変換先フォーマット: %s", to_format)

    records = list(SeqIO.parse(input_file, "fasta"))
    if not records:
        click.echo("配列が見つかりません", err=True)
        sys.exit(1)

    if to_format == "tab":
        for record in records:
            output.write(f"{record.id}\t{record.seq}\n")
        click.echo(f"変換完了: {len(records)} 配列をTSVに変換", err=True)
    else:
        count = SeqIO.write(records, output, "fasta")
        click.echo(f"変換完了: {count} 配列をFASTAに出力", err=True)

    logger.info("変換完了: %d 配列", len(records))


def main() -> None:
    """エントリポイント."""
    cli()


if __name__ == "__main__":
    main()
