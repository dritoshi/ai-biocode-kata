"""print()デバッグ vs logging.debug() の対比デモ."""

import logging

logger = logging.getLogger(__name__)


def filter_sequences_print_debug(
    sequences: list[str], min_length: int
) -> list[str]:
    """配列リストを長さでフィルタリングする（print版デバッグ付き）.

    本番コードでは print() の代わりに logging を使うべきである。
    ここではアンチパターンとしての print デバッグを示す。

    Parameters
    ----------
    sequences : list[str]
        塩基配列のリスト。
    min_length : int
        最小配列長（この長さ以上の配列を残す）。

    Returns
    -------
    list[str]
        フィルタリング後の配列リスト。
    """
    filtered: list[str] = []
    for seq in sequences:
        if len(seq) >= min_length:
            filtered.append(seq)
    return filtered


def filter_sequences_logging_debug(
    sequences: list[str], min_length: int
) -> list[str]:
    """配列リストを長さでフィルタリングする（logging版デバッグ付き）.

    logging.debug() を使えば、ログレベルの切り替えで
    デバッグ出力を制御できる。

    Parameters
    ----------
    sequences : list[str]
        塩基配列のリスト。
    min_length : int
        最小配列長（この長さ以上の配列を残す）。

    Returns
    -------
    list[str]
        フィルタリング後の配列リスト。
    """
    logger.debug(
        "フィルタ開始: %d 配列, 最小長=%d", len(sequences), min_length
    )
    filtered: list[str] = []
    for seq in sequences:
        if len(seq) >= min_length:
            logger.debug(
                "採用: len=%d, 先頭=%s...", len(seq), seq[:10]
            )
            filtered.append(seq)
        else:
            logger.debug("除外: len=%d < %d", len(seq), min_length)
    logger.debug(
        "フィルタ完了: %d → %d 配列", len(sequences), len(filtered)
    )
    return filtered
