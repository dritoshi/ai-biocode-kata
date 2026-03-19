"""polarsテーブル操作のテスト."""

import polars as pl

from scripts.ch10.polars_bio_ops import (
    filter_significant_genes_lazy,
    summarize_by_category_lazy,
)


def _make_deg_lazyframe() -> pl.LazyFrame:
    """テスト用DEG結果のLazyFrameを作成する."""
    return pl.DataFrame(
        {
            "gene": ["BRCA1", "TP53", "EGFR", "MYC", "GAPDH"],
            "baseMean": [1500.0, 800.0, 2200.0, 3000.0, 5000.0],
            "log2FoldChange": [2.5, -1.8, 0.3, 1.5, -0.1],
            "pvalue": [1e-10, 1e-6, 0.2, 1e-4, 0.8],
            "padj": [1e-8, 1e-4, 0.4, 0.01, 0.95],
        }
    ).lazy()


class TestFilterSignificantGenesLazy:
    """filter_significant_genes_lazy のテスト."""

    def test_default_thresholds(self) -> None:
        """デフォルト閾値でフィルタし、collect()で実体化."""
        lf = _make_deg_lazyframe()
        result = filter_significant_genes_lazy(lf).collect()
        assert len(result) == 3
        assert set(result["gene"].to_list()) == {"BRCA1", "TP53", "MYC"}

    def test_strict_thresholds(self) -> None:
        """厳しい閾値でフィルタ."""
        lf = _make_deg_lazyframe()
        result = filter_significant_genes_lazy(
            lf, padj_threshold=1e-5, log2fc_threshold=2.0
        ).collect()
        assert len(result) == 1
        assert result["gene"][0] == "BRCA1"

    def test_returns_lazyframe(self) -> None:
        """戻り値がLazyFrameである（まだ実行されていない）."""
        lf = _make_deg_lazyframe()
        result = filter_significant_genes_lazy(lf)
        assert isinstance(result, pl.LazyFrame)

    def test_no_significant(self) -> None:
        """有意な遺伝子がない場合."""
        lf = _make_deg_lazyframe()
        result = filter_significant_genes_lazy(
            lf, padj_threshold=1e-20, log2fc_threshold=10.0
        ).collect()
        assert len(result) == 0


class TestSummarizeByCategoryLazy:
    """summarize_by_category_lazy のテスト."""

    def test_basic(self) -> None:
        """カテゴリ別集計."""
        lf = pl.DataFrame(
            {
                "gene": ["BRCA1", "TP53", "EGFR", "MYC", "GAPDH"],
                "category": [
                    "tumor_suppressor",
                    "tumor_suppressor",
                    "oncogene",
                    "oncogene",
                    "housekeeping",
                ],
                "log2FoldChange": [2.5, -1.8, 0.3, 1.5, -0.1],
            }
        ).lazy()
        result = summarize_by_category_lazy(
            lf, "category", "log2FoldChange"
        ).collect()
        assert len(result) == 3
        assert "count" in result.columns
        assert "mean" in result.columns
        assert "median" in result.columns

    def test_returns_lazyframe(self) -> None:
        """戻り値がLazyFrameである."""
        lf = pl.DataFrame(
            {
                "gene": ["A", "B"],
                "cat": ["x", "x"],
                "val": [1.0, 2.0],
            }
        ).lazy()
        result = summarize_by_category_lazy(lf, "cat", "val")
        assert isinstance(result, pl.LazyFrame)
