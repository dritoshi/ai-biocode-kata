"""BED（0-based half-open）と GFF（1-based closed）の座標変換ユーティリティ."""

from __future__ import annotations


def bed_to_gff(start: int, end: int) -> tuple[int, int]:
    """BED座標（0-based half-open）をGFF座標（1-based closed）に変換する.

    Args:
        start: 0-based開始位置
        end: 0-basedの終了位置（含まない）

    Returns:
        (gff_start, gff_end): 1-based closed区間
    """
    # 0-based → 1-based: startに+1、endはそのまま（half-open→closedで相殺）
    return start + 1, end


def gff_to_bed(start: int, end: int) -> tuple[int, int]:
    """GFF座標（1-based closed）をBED座標（0-based half-open）に変換する.

    Args:
        start: 1-based開始位置
        end: 1-basedの終了位置（含む）

    Returns:
        (bed_start, bed_end): 0-based half-open区間
    """
    # 1-based → 0-based: startから-1、endはそのまま（closed→half-openで相殺）
    return start - 1, end


def interval_length_bed(start: int, end: int) -> int:
    """BED座標系での区間長を計算する."""
    # half-open区間なので引き算だけで長さが出る
    return end - start


def interval_length_gff(start: int, end: int) -> int:
    """GFF座標系での区間長を計算する."""
    # closed区間なので+1が必要
    return end - start + 1
