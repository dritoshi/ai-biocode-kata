"""乱数と再現性デモのテスト."""

import numpy as np
import pytest

from scripts.ch03.random_reproducibility import (
    bootstrap_mean,
    generate_random_sequences,
    subsample_with_seed,
)


class TestSubsampleWithSeed:
    """subsample_with_seed() のテスト."""

    @pytest.fixture()
    def data(self) -> np.ndarray:
        return np.arange(100, dtype=np.float64)

    def test_correct_size(self, data: np.ndarray) -> None:
        result = subsample_with_seed(data, n=10, seed=42)
        assert len(result) == 10

    def test_reproducible(self, data: np.ndarray) -> None:
        # 同じシードなら同じ結果
        result1 = subsample_with_seed(data, n=10, seed=42)
        result2 = subsample_with_seed(data, n=10, seed=42)
        np.testing.assert_array_equal(result1, result2)

    def test_different_seed_different_result(self, data: np.ndarray) -> None:
        # 異なるシードなら異なる結果
        result1 = subsample_with_seed(data, n=10, seed=42)
        result2 = subsample_with_seed(data, n=10, seed=123)
        assert not np.array_equal(result1, result2)

    def test_values_from_original(self, data: np.ndarray) -> None:
        # サブサンプルの値は元データに含まれる
        result = subsample_with_seed(data, n=10, seed=42)
        for val in result:
            assert val in data


class TestBootstrapMean:
    """bootstrap_mean() のテスト."""

    @pytest.fixture()
    def data(self) -> np.ndarray:
        return np.array([1.0, 2.0, 3.0, 4.0, 5.0])

    def test_correct_iterations(self, data: np.ndarray) -> None:
        result = bootstrap_mean(data, n_iterations=100, seed=42)
        assert len(result) == 100

    def test_reproducible(self, data: np.ndarray) -> None:
        result1 = bootstrap_mean(data, n_iterations=50, seed=42)
        result2 = bootstrap_mean(data, n_iterations=50, seed=42)
        np.testing.assert_array_equal(result1, result2)

    def test_means_in_reasonable_range(self, data: np.ndarray) -> None:
        result = bootstrap_mean(data, n_iterations=1000, seed=42)
        # ブートストラップ平均は元データの範囲内に収まるはず
        assert result.min() >= data.min()
        assert result.max() <= data.max()


class TestGenerateRandomSequences:
    """generate_random_sequences() のテスト."""

    def test_correct_count(self) -> None:
        seqs = generate_random_sequences(n=5, length=10, seed=42)
        assert len(seqs) == 5

    def test_correct_length(self) -> None:
        seqs = generate_random_sequences(n=3, length=20, seed=42)
        for seq in seqs:
            assert len(seq) == 20

    def test_valid_bases(self) -> None:
        seqs = generate_random_sequences(n=10, length=50, seed=42)
        valid_bases = set("ATGC")
        for seq in seqs:
            assert set(seq).issubset(valid_bases)

    def test_reproducible(self) -> None:
        seqs1 = generate_random_sequences(n=5, length=10, seed=42)
        seqs2 = generate_random_sequences(n=5, length=10, seed=42)
        assert seqs1 == seqs2

    def test_different_seed(self) -> None:
        seqs1 = generate_random_sequences(n=5, length=10, seed=42)
        seqs2 = generate_random_sequences(n=5, length=10, seed=123)
        assert seqs1 != seqs2
