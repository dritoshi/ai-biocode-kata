"""§11 プログレスバーとロギングのデモ (fig-11-01 キャプチャ用).

tqdm のプログレスバーと logging のレベル別出力を表示する。
freeze でキャプチャすることで書籍用の図を生成する。

使い方:
    # 実行してターミナル出力を確認
    python3 scripts/ch11/progress_demo.py

    # freeze でキャプチャ
    python3 scripts/ch11/progress_demo.py 2>&1 | freeze -o figures/ch11_progress_logging.png \
        --padding 20 --font.size 14 --window=false --border.radius 8 --language bash
"""

import logging
import sys
import time

from tqdm import tqdm


def setup_logging() -> None:
    """ロギングを設定する."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,
    )


def main() -> None:
    """プログレスバーとロギングのデモを実行する."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Loading reference genome...")
    time.sleep(0.3)
    logger.info("Reference loaded: hg38 (3.1 Gbp)")
    logger.info("Found 6 samples to process")

    # tqdm プログレスバー
    samples = ["SRR001", "SRR002", "SRR003", "SRR004", "SRR005", "SRR006"]
    for i, sample in enumerate(tqdm(samples, desc="Processing samples", file=sys.stderr)):
        time.sleep(0.3)
        if sample == "SRR003":
            logger.warning("Sample %s: low mapping rate (45.2%%)", sample)
        else:
            reads = 12_345_678 - i * 1_000_000
            logger.info("%s: %s reads aligned (%.1f%%)", sample, f"{reads:,}", 98.5 - i * 0.3)

    logger.info("All samples processed successfully")


if __name__ == "__main__":
    main()
