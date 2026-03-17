"""GC含量計算のテスト."""

import pytest

from scripts.ch01.gc_content import filter_sequences_by_gc, gc_content


class TestGcContent:
    """gc_content() のテスト."""

    def test_typical_sequence(self) -> None:
        assert gc_content("ATGC") == pytest.approx(0.5)

    def test_all_gc(self) -> None:
        assert gc_content("GGCC") == pytest.approx(1.0)

    def test_no_gc(self) -> None:
        assert gc_content("AATT") == pytest.approx(0.0)

    def test_empty_string(self) -> None:
        assert gc_content("") == 0.0

    def test_case_insensitive(self) -> None:
        assert gc_content("atgc") == pytest.approx(0.5)

    def test_long_sequence(self) -> None:
        seq = "GGGCCC" + "AAAA"  # G=3, C=3, A=4 → 10bp, GC=60%
        assert gc_content(seq) == pytest.approx(0.6)


class TestFilterSequencesByGc:
    """filter_sequences_by_gc() のテスト."""

    @pytest.fixture()
    def sequences(self) -> dict[str, str]:
        return {
            "seq1": "AAAA",  # GC=0.0
            "seq2": "ATGC",  # GC=0.5
            "seq3": "GCGC",  # GC=1.0
        }

    def test_filter_high_gc(self, sequences: dict[str, str]) -> None:
        result = filter_sequences_by_gc(sequences, min_gc=0.5)
        assert set(result.keys()) == {"seq2", "seq3"}

    def test_filter_range(self, sequences: dict[str, str]) -> None:
        result = filter_sequences_by_gc(sequences, min_gc=0.3, max_gc=0.7)
        assert set(result.keys()) == {"seq2"}

    def test_no_filter(self, sequences: dict[str, str]) -> None:
        result = filter_sequences_by_gc(sequences)
        assert len(result) == 3
