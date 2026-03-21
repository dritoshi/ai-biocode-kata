"""TPM正規化の正確性テスト."""

import numpy as np
import pytest

from scripts.ch15.profiling_demo import (
    normalize_tpm_fast,
    normalize_tpm_slow,
    profile_pipeline,
)


class TestNormalizeTpmSlow:
    """normalize_tpm_slow のテスト."""

    def test_basic_tpm(self) -> None:
        """基本的なTPM正規化の計算結果が正しい."""
        counts = np.array([[100, 200], [300, 400]], dtype=np.float64)
        gene_lengths = np.array([1000, 2000], dtype=np.float64)
        result = normalize_tpm_slow(counts, gene_lengths)
        # 各サンプルの列合計が約100万になることを確認
        col_sums = result.sum(axis=0)
        np.testing.assert_allclose(col_sums, [1_000_000, 1_000_000], rtol=1e-6)

    def test_single_gene(self) -> None:
        """遺伝子が1つだけの場合、TPMは全サンプルで100万."""
        counts = np.array([[50, 100]], dtype=np.float64)
        gene_lengths = np.array([500], dtype=np.float64)
        result = normalize_tpm_slow(counts, gene_lengths)
        np.testing.assert_allclose(result, [[1_000_000, 1_000_000]], rtol=1e-6)

    def test_proportional_distribution(self) -> None:
        """同じ遺伝子長の場合、TPMはカウントの比率を反映する."""
        counts = np.array([[100], [300]], dtype=np.float64)
        gene_lengths = np.array([1000, 1000], dtype=np.float64)
        result = normalize_tpm_slow(counts, gene_lengths)
        # 1:3 の比率が保たれる
        np.testing.assert_allclose(result[0, 0] / result[1, 0], 1 / 3, rtol=1e-6)


class TestNormalizeTpmFast:
    """normalize_tpm_fast のテスト."""

    def test_basic_tpm(self) -> None:
        """基本的なTPM正規化の計算結果が正しい."""
        counts = np.array([[100, 200], [300, 400]], dtype=np.float64)
        gene_lengths = np.array([1000, 2000], dtype=np.float64)
        result = normalize_tpm_fast(counts, gene_lengths)
        col_sums = result.sum(axis=0)
        np.testing.assert_allclose(col_sums, [1_000_000, 1_000_000], rtol=1e-6)

    def test_matches_slow_version(self) -> None:
        """速い版と遅い版の計算結果が一致する."""
        rng = np.random.default_rng(42)
        counts = rng.integers(0, 1000, size=(50, 10)).astype(np.float64)
        gene_lengths = rng.integers(500, 5000, size=50).astype(np.float64)
        slow = normalize_tpm_slow(counts, gene_lengths)
        fast = normalize_tpm_fast(counts, gene_lengths)
        np.testing.assert_allclose(fast, slow, rtol=1e-10)


class TestProfilePipeline:
    """profile_pipeline のテスト."""

    def test_returns_stats(self) -> None:
        """pstats.Stats オブジェクトを返す."""
        import pstats

        counts = np.array([[100, 200]], dtype=np.float64)
        gene_lengths = np.array([1000], dtype=np.float64)
        stats = profile_pipeline(normalize_tpm_fast, counts, gene_lengths)
        assert isinstance(stats, pstats.Stats)
