"""seabornによる統計的可視化 — バイオリンプロット."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure


def expression_violin(
    expression_df: pd.DataFrame,
    category_col: str = "category",
    value_col: str = "expression",
    output_path: "Path | None" = None,
) -> Figure:
    """カテゴリ別発現量のバイオリンプロットを作成する.

    tidy data（long form）形式のDataFrameを受け取り、
    カテゴリごとの分布をバイオリンプロットで表示する。

    Parameters
    ----------
    expression_df : pd.DataFrame
        tidy format のDataFrame（カテゴリ列と値列を含む）
    category_col : str
        カテゴリのカラム名
    value_col : str
        値のカラム名
    output_path : Path | None
        保存先パス（Noneなら保存しない）

    Returns
    -------
    Figure
        matplotlib Figureオブジェクト
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    sns.violinplot(
        data=expression_df,
        x=category_col,
        y=value_col,
        hue=category_col,
        ax=ax,
        palette="cividis",
        inner="box",
        legend=False,
    )

    ax.set_xlabel(category_col.replace("_", " ").title())
    ax.set_ylabel(value_col.replace("_", " ").title())
    ax.set_title("Expression Distribution by Category")

    if output_path is not None:
        from pathlib import Path

        fig.savefig(Path(output_path), dpi=300, bbox_inches="tight")

    return fig
