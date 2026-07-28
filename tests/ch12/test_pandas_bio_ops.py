"""pandasテーブル操作のテスト."""

from pathlib import Path

import pandas as pd
import pytest

from scripts.ch12.pandas_bio_ops import (
    filter_significant_genes,
    load_deg_results,
    merge_with_metadata,
    summarize_by_category,
)


@pytest.fixture()
def deg_df() -> pd.DataFrame:
    """テスト用DEG結果DataFrame."""
    return pd.DataFrame(
        {
            "gene": ["BRCA1", "TP53", "EGFR", "MYC", "GAPDH"],
            "baseMean": [1500.0, 800.0, 2200.0, 3000.0, 5000.0],
            "log2FoldChange": [2.5, -1.8, 0.3, 1.5, -0.1],
            "pvalue": [1e-10, 1e-6, 0.2, 1e-4, 0.8],
            "padj": [1e-8, 1e-4, 0.4, 0.01, 0.95],
        }
    )


@pytest.fixture()
def metadata_df() -> pd.DataFrame:
    """テスト用メタデータDataFrame."""
    return pd.DataFrame(
        {
            "gene": ["BRCA1", "TP53", "EGFR", "MYC", "GAPDH"],
            "category": [
                "tumor_suppressor",
                "tumor_suppressor",
                "oncogene",
                "oncogene",
                "housekeeping",
            ],
            "chromosome": ["17", "17", "7", "8", "12"],
        }
    )


class TestLoadDegResults:
    """load_deg_results のテスト."""

    def test_csv(self, tmp_path) -> None:
        """CSVファイルを正しく読み込める."""
        csv_path = tmp_path / "deg.csv"
        csv_path.write_text(
            "gene,baseMean,log2FoldChange,pvalue,padj\n"
            "BRCA1,1500,2.5,1e-10,1e-8\n"
            "TP53,800,-1.8,1e-6,1e-4\n"
        )
        df = load_deg_results(csv_path)
        assert len(df) == 2
        assert df["gene"].iloc[0] == "BRCA1"

    def test_tsv(self, tmp_path) -> None:
        """TSVファイルを正しく読み込める."""
        tsv_path = tmp_path / "deg.tsv"
        tsv_path.write_text(
            "gene\tbaseMean\tlog2FoldChange\tpvalue\tpadj\n"
            "BRCA1\t1500\t2.5\t1e-10\t1e-8\n"
        )
        df = load_deg_results(tsv_path)
        assert len(df) == 1
        assert df["gene"].iloc[0] == "BRCA1"

    def test_na_handling(self, tmp_path) -> None:
        """NAやna文字列がNaNとして読み込まれる."""
        csv_path = tmp_path / "deg.csv"
        csv_path.write_text(
            "gene,baseMean,log2FoldChange,pvalue,padj\n"
            "BRCA1,1500,2.5,1e-10,NA\n"
            "TP53,800,-1.8,na,\n"
        )
        df = load_deg_results(csv_path)
        assert pd.isna(df["padj"].iloc[0])
        assert pd.isna(df["pvalue"].iloc[1])
        assert pd.api.types.is_string_dtype(df["gene"].dtype)
        assert pd.api.types.is_float_dtype(df["pvalue"].dtype)
        assert pd.api.types.is_float_dtype(df["padj"].dtype)

    def test_missing_required_column(self, tmp_path: Path) -> None:
        """必須列が欠けたDEG結果を明示的に拒否する."""
        csv_path = tmp_path / "missing_padj.csv"
        csv_path.write_text(
            "gene,baseMean,log2FoldChange,pvalue\n"
            "BRCA1,1500,2.5,1e-10\n",
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="padj"):
            load_deg_results(csv_path)


class TestFilterSignificantGenes:
    """filter_significant_genes のテスト."""

    def test_default_thresholds(self, deg_df) -> None:
        """デフォルト閾値（padj < 0.05, |log2FC| >= 1）でフィルタ."""
        result = filter_significant_genes(deg_df)
        # BRCA1: padj=1e-8, |log2FC|=2.5 → 有意
        # TP53: padj=1e-4, |log2FC|=1.8 → 有意
        # MYC: padj=0.01, |log2FC|=1.5 → 有意
        # EGFR: |log2FC|=0.3 → 非有意
        # GAPDH: padj=0.95 → 非有意
        assert len(result) == 3
        assert set(result["gene"].tolist()) == {"BRCA1", "TP53", "MYC"}

    def test_strict_thresholds(self, deg_df) -> None:
        """厳しい閾値でフィルタ."""
        result = filter_significant_genes(
            deg_df, padj_threshold=1e-5, log2fc_threshold=2.0
        )
        assert len(result) == 1
        assert result["gene"].iloc[0] == "BRCA1"

    def test_no_significant(self, deg_df) -> None:
        """有意な遺伝子がない場合は空DataFrame."""
        result = filter_significant_genes(
            deg_df, padj_threshold=1e-20, log2fc_threshold=10.0
        )
        assert len(result) == 0

    def test_threshold_boundaries_and_na(self) -> None:
        """p値・効果量の包含境界とNA除外を確認する."""
        df = pd.DataFrame(
            {
                "gene": ["padj_equal", "fc_positive", "fc_negative", "na"],
                "padj": [0.05, 0.049, 0.049, pd.NA],
                "log2FoldChange": [2.0, 1.0, -1.0, 2.0],
            }
        )
        result = filter_significant_genes(df)
        assert result["gene"].tolist() == ["fc_positive", "fc_negative"]


class TestMergeWithMetadata:
    """merge_with_metadata のテスト."""

    def test_basic(self, deg_df, metadata_df) -> None:
        """メタデータとの結合."""
        result = merge_with_metadata(deg_df, metadata_df)
        assert "category" in result.columns
        assert "chromosome" in result.columns
        assert len(result) == 5

    def test_left_join(self, deg_df) -> None:
        """左結合: メタデータにない遺伝子はNaNになる."""
        partial_metadata = pd.DataFrame(
            {
                "gene": ["BRCA1", "TP53"],
                "category": ["tumor_suppressor", "tumor_suppressor"],
            }
        )
        result = merge_with_metadata(deg_df, partial_metadata)
        assert len(result) == 5
        # メタデータにない遺伝子のcategoryはNaN
        egfr_row = result[result["gene"] == "EGFR"]
        assert pd.isna(egfr_row["category"].iloc[0])

    def test_duplicate_metadata_keys_expand_matching_rows(self) -> None:
        """メタデータ側の重複キーが一致行を複製することを確認する."""
        deg = pd.DataFrame({"gene": ["BRCA1", "TP53"], "value": [1, 2]})
        metadata = pd.DataFrame(
            {
                "gene": ["BRCA1", "BRCA1"],
                "category": ["a", "b"],
            }
        )
        result = merge_with_metadata(deg, metadata)
        assert len(result) == 3
        assert (result["gene"] == "BRCA1").sum() == 2
        assert pd.isna(result.loc[result["gene"] == "TP53", "category"]).all()


class TestSummarizeByCategory:
    """summarize_by_category のテスト."""

    def test_basic(self, deg_df, metadata_df) -> None:
        """カテゴリ別集計."""
        merged = merge_with_metadata(deg_df, metadata_df)
        result = summarize_by_category(merged, "category", "log2FoldChange")
        assert "count" in result.columns
        assert "mean" in result.columns
        assert "median" in result.columns
        # 3カテゴリ: housekeeping, oncogene, tumor_suppressor
        assert len(result) == 3

    def test_single_group_and_missing_category(self) -> None:
        """単一カテゴリを集計し、欠損カテゴリは既定どおり除外する."""
        df = pd.DataFrame(
            {
                "category": ["a", "a", pd.NA],
                "value": [1.0, 3.0, 100.0],
            }
        )
        result = summarize_by_category(df, "category", "value")
        assert result["category"].tolist() == ["a"]
        assert result["count"].tolist() == [2]
        assert result["mean"].iloc[0] == pytest.approx(2.0)
        assert result["median"].iloc[0] == pytest.approx(2.0)
