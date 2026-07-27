import pytest

from scripts.ch01.gc_content import filter_sequences_by_gc


@pytest.fixture()
def sample_sequences() -> dict[str, str]:
    """テスト用のサンプル配列."""
    return {
        "high_gc": "GCGCGCGC",   # GC=100%
        "low_gc": "AAAATTTT",    # GC=0%
        "mixed": "ATGCATGC",     # GC=50%
    }


def test_filter_high_gc(sample_sequences: dict[str, str]) -> None:
    result = filter_sequences_by_gc(sample_sequences, min_gc=0.8)
    assert set(result.keys()) == {"high_gc"}


def test_filter_all(sample_sequences: dict[str, str]) -> None:
    result = filter_sequences_by_gc(sample_sequences)
    assert len(result) == 3
