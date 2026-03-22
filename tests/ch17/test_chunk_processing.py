"""チャンク処理と一括処理の統計量一致テスト."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts.ch17.chunk_processing import compute_stats_chunked, compute_stats_naive


def _create_expression_csv(path: Path, n_genes: int, n_samples: int) -> None:
    """テスト用の発現量CSVファイルを生成するヘルパー.

    行=サンプル、列=遺伝子の形式で作成する。

    Parameters
    ----------
    path : Path
        出力先パス
    n_genes : int
        遺伝子数（列数）
    n_samples : int
        サンプル数（行数）
    """
    rng = np.random.default_rng(42)
    data = rng.integers(0, 10000, size=(n_samples, n_genes))
    sample_ids = [f"SAMPLE_{i:03d}" for i in range(n_samples)]
    gene_ids = [f"GENE_{j:04d}" for j in range(n_genes)]
    df = pd.DataFrame(data, index=sample_ids, columns=gene_ids)
    df.to_csv(path)


class TestComputeStatsNaive:
    """compute_stats_naive のテスト."""

    def test_basic_stats(self, tmp_path: Path) -> None:
        """基本的な統計量計算."""
        csv_path = tmp_path / "expr.csv"
        _create_expression_csv(csv_path, n_genes=10, n_samples=5)
        result = compute_stats_naive(csv_path)
        assert "mean" in result
        assert "var" in result
        assert len(result["mean"]) == 10
        assert len(result["var"]) == 10


class TestComputeStatsChunked:
    """compute_stats_chunked のテスト."""

    def test_matches_naive(self, tmp_path: Path) -> None:
        """チャンク版と一括版の統計量が一致する."""
        csv_path = tmp_path / "expr.csv"
        _create_expression_csv(csv_path, n_genes=50, n_samples=20)
        naive = compute_stats_naive(csv_path)
        chunked = compute_stats_chunked(csv_path, chunksize=3)
        pd.testing.assert_series_equal(
            chunked["mean"], naive["mean"], rtol=1e-10
        )
        pd.testing.assert_series_equal(
            chunked["var"], naive["var"], rtol=1e-10
        )

    def test_small_chunksize(self, tmp_path: Path) -> None:
        """チャンクサイズが非常に小さくても正しい結果を返す."""
        csv_path = tmp_path / "expr.csv"
        _create_expression_csv(csv_path, n_genes=20, n_samples=8)
        naive = compute_stats_naive(csv_path)
        chunked = compute_stats_chunked(csv_path, chunksize=1)
        pd.testing.assert_series_equal(
            chunked["mean"], naive["mean"], rtol=1e-10
        )
        pd.testing.assert_series_equal(
            chunked["var"], naive["var"], rtol=1e-10
        )

    def test_too_few_samples(self, tmp_path: Path) -> None:
        """サンプル数が1の場合はエラーを返す."""
        csv_path = tmp_path / "expr.csv"
        _create_expression_csv(csv_path, n_genes=5, n_samples=1)
        with pytest.raises(ValueError, match="2サンプル以上"):
            compute_stats_chunked(csv_path, chunksize=5)
