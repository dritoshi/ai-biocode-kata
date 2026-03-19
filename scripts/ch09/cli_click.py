"""click版 GCフィルタCLI — 本書の標準推奨ライブラリによる実装."""

import logging
import sys

import click
from Bio import SeqIO

from scripts.ch07.seq_stats import gc_content
from scripts.ch09.logging_setup import setup_logging

logger = logging.getLogger(__name__)


@click.command()
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
    "-v",
    "--verbose",
    is_flag=True,
    help="デバッグログを表示する",
)
@click.version_option("0.1.0", prog_name="gc-filter")
def gc_filter(
    input_file: click.utils.LazyFile,
    output: click.utils.LazyFile,
    min_gc: float,
    max_gc: float,
    verbose: bool,
) -> None:
    """FASTA配列をGC含量でフィルタリングする.

    INPUT_FILE を読み込み、GC含量が指定範囲内の配列のみを出力する。
    INPUT_FILE を省略するとstdinから読み込む。
    """
    setup_logging(level="DEBUG" if verbose else "WARNING")
    logger.info("フィルタ条件: GC含量 %.2f–%.2f", min_gc, max_gc)

    # フィルタリング処理
    filtered = []
    for record in SeqIO.parse(input_file, "fasta"):
        gc = gc_content(str(record.seq))
        if min_gc <= gc <= max_gc:
            filtered.append(record)
            logger.debug("%s: GC=%.3f — 通過", record.id, gc)
        else:
            logger.debug("%s: GC=%.3f — 除外", record.id, gc)

    count = SeqIO.write(filtered, output, "fasta")
    # ログはstderrに出力し、結果のstdout出力を汚さない
    click.echo(f"フィルタ結果: {count} 配列を出力", err=True)


def main() -> None:
    """エントリポイント."""
    gc_filter()


if __name__ == "__main__":
    main()
