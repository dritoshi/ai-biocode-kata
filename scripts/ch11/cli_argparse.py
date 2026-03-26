"""argparse版 GCフィルタCLI — 既存コードで遭遇するパターンの紹介."""

import argparse
import logging
import sys
from pathlib import Path

from Bio import SeqIO

from scripts.ch08.seq_stats import gc_content

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """コマンドライン引数をパースする."""
    parser = argparse.ArgumentParser(
        description="FASTA配列をGC含量でフィルタリングする",
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=None,
        help="入力FASTAファイル（省略時はstdin）",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="出力ファイル（省略時はstdout）",
    )
    parser.add_argument(
        "--min-gc",
        type=float,
        default=0.0,
        help="GC含量の下限（デフォルト: 0.0）",
    )
    parser.add_argument(
        "--max-gc",
        type=float,
        default=1.0,
        help="GC含量の上限（デフォルト: 1.0）",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="デバッグログを表示する",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """メインエントリポイント."""
    args = parse_args(argv)

    # ロギング設定
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stderr,
    )

    logger.info("フィルタ条件: GC含量 %.2f–%.2f", args.min_gc, args.max_gc)

    input_handle = sys.stdin if args.input is None else args.input.open(encoding="utf-8")
    output_handle = sys.stdout if args.output is None else args.output.open("w", encoding="utf-8")
    try:
        filtered = []
        for record in SeqIO.parse(input_handle, "fasta"):
            gc = gc_content(str(record.seq))
            if args.min_gc <= gc <= args.max_gc:
                filtered.append(record)
                logger.debug("%s: GC=%.3f — 通過", record.id, gc)
            else:
                logger.debug("%s: GC=%.3f — 除外", record.id, gc)

        count = SeqIO.write(filtered, output_handle, "fasta")
        logger.info("結果: %d 配列を出力", count)
    finally:
        if input_handle is not sys.stdin:
            input_handle.close()
        if output_handle is not sys.stdout:
            output_handle.close()


if __name__ == "__main__":
    main()
