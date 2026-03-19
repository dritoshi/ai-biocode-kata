"""polarsによるDEGテーブル処理 — lazy evaluationを活用した高速処理."""

import polars as pl


def filter_significant_genes_lazy(
    lf: pl.LazyFrame,
    padj_threshold: float = 0.05,
    log2fc_threshold: float = 1.0,
) -> pl.LazyFrame:
    """有意な差次的発現遺伝子をlazy evaluationでフィルタリングする.

    polarsのlazy APIを使い、クエリプランを最適化してから実行する。
    数百万行規模のデータで特に効果を発揮する。

    Parameters
    ----------
    lf : pl.LazyFrame
        DEG結果のLazyFrame（padj, log2FoldChange カラムが必要）
    padj_threshold : float
        調整済みp値の閾値（この値未満を有意とする）
    log2fc_threshold : float
        |log2FoldChange| の閾値（この値以上を有意とする）

    Returns
    -------
    pl.LazyFrame
        有意遺伝子のみを含むLazyFrame
    """
    return lf.filter(
        (pl.col("padj") < padj_threshold)
        & (pl.col("log2FoldChange").abs() >= log2fc_threshold)
    )


def summarize_by_category_lazy(
    lf: pl.LazyFrame,
    category_col: str,
    value_col: str,
) -> pl.LazyFrame:
    """カテゴリ別に値をlazy evaluationで集計する.

    Parameters
    ----------
    lf : pl.LazyFrame
        集計対象のLazyFrame
    category_col : str
        グループ化に使うカラム名
    value_col : str
        集計対象の数値カラム名

    Returns
    -------
    pl.LazyFrame
        カテゴリごとの count, mean, median を含むLazyFrame
    """
    return lf.group_by(category_col).agg(
        pl.col(value_col).count().alias("count"),
        pl.col(value_col).mean().alias("mean"),
        pl.col(value_col).median().alias("median"),
    )
