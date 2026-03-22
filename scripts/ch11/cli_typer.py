"""typer版 GCフィルタCLI — 型ヒントベースの簡潔な実装."""

import logging
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from Bio import SeqIO

from scripts.ch08.seq_stats import gc_content

logger = logging.getLogger(__name__)

app = typer.Typer(help="FASTA配列をGC含量でフィルタリングする")


@app.command()
def gc_filter(
    input_file: Annotated[
        Path,
        typer.Argument(help="入力FASTAファイル"),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option("-o", "--output", help="出力ファイル（省略時はstdout）"),
    ] = None,
    min_gc: Annotated[
        float,
        typer.Option(help="GC含量の下限", min=0.0, max=1.0),
    ] = 0.0,
    max_gc: Annotated[
        float,
        typer.Option(help="GC含量の上限", min=0.0, max=1.0),
    ] = 1.0,
    verbose: Annotated[
        bool,
        typer.Option("-v", "--verbose", help="デバッグログを表示する"),
    ] = False,
) -> None:
    """FASTA配列をGC含量でフィルタリングする."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stderr,
    )

    logger.info("フィルタ条件: GC含量 %.2f–%.2f", min_gc, max_gc)

    # 入力の読み込み
    records = list(SeqIO.parse(input_file, "fasta"))

    # フィルタリング処理
    filtered = [
        record
        for record in records
        if min_gc <= gc_content(str(record.seq)) <= max_gc
    ]

    # 出力
    if output is not None:
        count = SeqIO.write(filtered, output, "fasta")
    else:
        count = SeqIO.write(filtered, sys.stdout, "fasta")

    typer.echo(f"フィルタ結果: {count} 配列を出力", err=True)


if __name__ == "__main__":
    app()
