"""ユーティリティ: 入力の検証など."""

from __future__ import annotations

VALID_BASES = set("ATGCatgc")


def validate_sequence(seq: str) -> tuple[bool, list[str]]:
    """DNA配列が有効な塩基のみで構成されているか検証する.

    Parameters
    ----------
    seq : str
        DNA配列

    Returns
    -------
    tuple[bool, list[str]]
        (有効か, 無効な文字のリスト)
    """
    invalid_chars: list[str] = []
    for char in seq:
        if char not in VALID_BASES and char not in invalid_chars:
            invalid_chars.append(char)
    return len(invalid_chars) == 0, invalid_chars
