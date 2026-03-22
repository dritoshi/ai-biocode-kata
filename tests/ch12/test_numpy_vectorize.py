"""NumPyベクトル化演算のテスト."""

import numpy as np
import pytest

from scripts.ch12.numpy_vectorize import (
    filter_by_quality,
    gc_content_vectorized,
    normalize_cpm,
)


class TestGcContentVectorized:
    """gc_content_vectorized のテスト."""

    def test_basic(self) -> None:
        """基本的なGC含量計算."""
        sequences = ["ATGC", "GGGG", "AAAA"]
        result = gc_content_vectorized(sequences)
        expected = np.array([0.5, 1.0, 0.0])
        np.testing.assert_allclose(result, expected)

    def test_empty_sequence(self) -> None:
        """空文字列のGC含量は0.0."""
        result = gc_content_vectorized(["", "ATGC"])
        assert result[0] == 0.0
        assert result[1] == pytest.approx(0.5)

    def test_case_insensitive(self) -> None:
        """大文字・小文字を区別しない."""
        result = gc_content_vectorized(["atgc", "ATGC"])
        np.testing.assert_allclose(result[0], result[1])

    def test_empty_list(self) -> None:
        """空リストの場合は空配列を返す."""
        result = gc_content_vectorized([])
        assert len(result) == 0

    def test_long_sequences(self) -> None:
        """長い配列でも正しく計算される."""
        seq = "GC" * 500 + "AT" * 500
        result = gc_content_vectorized([seq])
        assert result[0] == pytest.approx(0.5)


class TestNormalizeCpm:
    """normalize_cpm のテスト."""

    def test_basic(self) -> None:
        """基本的なCPM正規化."""
        counts = np.array([[10, 20], [30, 40], [60, 40]], dtype=np.float64)
        result = normalize_cpm(counts)
        # 列の合計: [100, 100]
        # CPM = counts / col_sum * 1e6
        expected = np.array(
            [[100_000, 200_000], [300_000, 400_000], [600_000, 400_000]],
            dtype=np.float64,
        )
        np.testing.assert_allclose(result, expected)

    def test_column_sums_to_million(self) -> None:
        """各列の合計がほぼ1,000,000になる."""
        counts = np.array([[5, 15], [10, 25], [85, 60]], dtype=np.float64)
        result = normalize_cpm(counts)
        col_sums = result.sum(axis=0)
        np.testing.assert_allclose(col_sums, [1_000_000, 1_000_000])

    def test_zero_column(self) -> None:
        """全てゼロの列でもゼロ除算が起きない."""
        counts = np.array([[10, 0], [20, 0]], dtype=np.float64)
        result = normalize_cpm(counts)
        assert np.all(np.isfinite(result))
        np.testing.assert_allclose(result[:, 1], [0.0, 0.0])

    def test_single_gene(self) -> None:
        """遺伝子1つの場合、CPMは1,000,000になる."""
        counts = np.array([[42]], dtype=np.float64)
        result = normalize_cpm(counts)
        assert result[0, 0] == pytest.approx(1_000_000)


class TestFilterByQuality:
    """filter_by_quality のテスト."""

    def test_basic(self) -> None:
        """閾値以上のスコアだけ残る."""
        scores = np.array([10, 25, 5, 30, 15, 20])
        result = filter_by_quality(scores, threshold=20)
        np.testing.assert_array_equal(result, [25, 30, 20])

    def test_all_pass(self) -> None:
        """全てのスコアが閾値以上の場合、全て残る."""
        scores = np.array([30, 40, 50])
        result = filter_by_quality(scores, threshold=20)
        np.testing.assert_array_equal(result, [30, 40, 50])

    def test_none_pass(self) -> None:
        """全てのスコアが閾値未満の場合、空配列を返す."""
        scores = np.array([5, 10, 15])
        result = filter_by_quality(scores, threshold=20)
        assert len(result) == 0

    def test_default_threshold(self) -> None:
        """デフォルト閾値は20."""
        scores = np.array([19, 20, 21])
        result = filter_by_quality(scores)
        np.testing.assert_array_equal(result, [20, 21])
