"""mylib.core モジュールの個別テスト."""

import pytest

from scripts.ch05.mylib.core import gc_content, reverse_complement


@pytest.mark.parametrize(
    ("sequence", "expected"),
    [
        ("GGCC", 1.0),
        ("AATT", 0.0),
        ("ATGC", 0.5),
        ("", 0.0),
        ("atgc", 0.5),
    ],
)
def test_gc_content(sequence: str, expected: float) -> None:
    """GC含量を個別に検証する."""
    assert gc_content(sequence) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("sequence", "expected"),
    [
        ("ATGC", "GCAT"),
        ("AATT", "AATT"),
        ("ATXG", "CNAT"),
        ("", ""),
        ("atgc", "GCAT"),
    ],
)
def test_reverse_complement(sequence: str, expected: str) -> None:
    """逆相補鎖を個別に検証する."""
    assert reverse_complement(sequence) == expected
