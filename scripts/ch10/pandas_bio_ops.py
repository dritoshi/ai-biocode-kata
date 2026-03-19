"""pandasによるDEGテーブル処理 — バイオインフォデータのテーブル操作."""

from pathlib import Path

import pandas as pd


def load_deg_results(path: Path) -> pd.DataFrame:
    """DEG（差次的発現遺伝子）解析結果のCSV/TSVを読み込む.

    NA値の明示的指定とカラムの型指定により、
    読み込み時の型推論の罠を回避する。

    Parameters
    ----------
    path : Path
        DEG結果ファイルのパス（CSV or TSV）

    Returns
    -------
    pd.DataFrame
        カラム: gene, baseMean, log2FoldChange, pvalue, padj
    """
    sep = "\t" if path.suffix in (".tsv", ".txt") else ","
    return pd.read_csv(
        path,
        sep=sep,
        na_values=["NA", "na", ""],
        dtype={"gene": str},
    )


def filter_significant_genes(
    df: pd.DataFrame,
    padj_threshold: float = 0.05,
    log2fc_threshold: float = 1.0,
) -> pd.DataFrame:
    """有意な差次的発現遺伝子をフィルタリングする.

    調整済みp値と対数変化量の両方の閾値で絞り込む。

    Parameters
    ----------
    df : pd.DataFrame
        DEG結果テーブル（padj, log2FoldChange カラムが必要）
    padj_threshold : float
        調整済みp値の閾値（この値未満を有意とする）
    log2fc_threshold : float
        |log2FoldChange| の閾値（この値以上を有意とする）

    Returns
    -------
    pd.DataFrame
        有意遺伝子のみを含むDataFrame
    """
    return df.query(
        "padj < @padj_threshold and abs(log2FoldChange) >= @log2fc_threshold"
    ).copy()


def merge_with_metadata(
    deg_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    on: str = "gene",
) -> pd.DataFrame:
    """DEG結果にメタデータ（遺伝子アノテーション等）を結合する.

    Parameters
    ----------
    deg_df : pd.DataFrame
        DEG結果テーブル
    metadata_df : pd.DataFrame
        メタデータテーブル（gene カラムを含む）
    on : str
        結合キーのカラム名。デフォルトは "gene"

    Returns
    -------
    pd.DataFrame
        結合後のDataFrame（左結合）
    """
    return pd.merge(deg_df, metadata_df, on=on, how="left")


def summarize_by_category(
    df: pd.DataFrame,
    category_col: str,
    value_col: str,
) -> pd.DataFrame:
    """カテゴリ別に値を集計する.

    groupbyとaggを使って、カテゴリごとの件数・平均・中央値を算出する。

    Parameters
    ----------
    df : pd.DataFrame
        集計対象のDataFrame
    category_col : str
        グループ化に使うカラム名
    value_col : str
        集計対象の数値カラム名

    Returns
    -------
    pd.DataFrame
        カテゴリごとの count, mean, median を含むDataFrame
    """
    return (
        df.groupby(category_col)[value_col]
        .agg(["count", "mean", "median"])
        .reset_index()
    )
