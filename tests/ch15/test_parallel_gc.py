"""並列GC含量計算のテスト — 逐次版と並列版の結果一致を検証."""

import pytest

from scripts.ch15.parallel_gc import (
    gc_content_parallel,
    gc_content_sequential,
    gc_content_single,
)


class TestGcContentSingle:
    """gc_content_single のテスト."""

    def test_basic(self) -> None:
        """基本的なGC含量計算."""
        assert gc_content_single("ATGC") == pytest.approx(0.5)

    def test_all_gc(self) -> None:
        """全てGCの場合は1.0."""
        assert gc_content_single("GGCC") == pytest.approx(1.0)

    def test_no_gc(self) -> None:
        """GCが含まれない場合は0.0."""
        assert gc_content_single("AATT") == pytest.approx(0.0)

    def test_empty(self) -> None:
        """空文字列の場合は0.0."""
        assert gc_content_single("") == pytest.approx(0.0)

    def test_case_insensitive(self) -> None:
        """小文字でも正しく計算する."""
        assert gc_content_single("atgc") == pytest.approx(0.5)


class TestGcContentSequential:
    """gc_content_sequential のテスト."""

    def test_multiple_sequences(self) -> None:
        """複数配列のGC含量を逐次計算."""
        sequences = ["ATGC", "GGGG", "AAAA", ""]
        result = gc_content_sequential(sequences)
        expected = [0.5, 1.0, 0.0, 0.0]
        assert result == pytest.approx(expected)


class TestGcContentParallel:
    """gc_content_parallel のテスト."""

    def test_matches_sequential(self) -> None:
        """並列版と逐次版の計算結果が一致する."""
        sequences = [
            "ATGCATGC",
            "GGGGCCCC",
            "AATTAATT",
            "GCGCGCGC",
            "ATATATAT",
        ]
        sequential = gc_content_sequential(sequences)
        parallel = gc_content_parallel(sequences, n_workers=2)
        assert parallel == pytest.approx(sequential)

    def test_empty_list(self) -> None:
        """空リストの場合は空リストを返す."""
        result = gc_content_parallel([], n_workers=2)
        assert result == []

    def test_preserves_order(self) -> None:
        """入力順序が保持される."""
        sequences = ["GC", "AT", "GCGC", "ATAT"]
        result = gc_content_parallel(sequences, n_workers=2)
        expected = [1.0, 0.0, 1.0, 0.0]
        assert result == pytest.approx(expected)
