"""バイオインフォの定番プロット — Volcano plotとヒートマップ."""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure


def volcano_plot(
    deg_df: pd.DataFrame,
    padj_threshold: float = 0.05,
    log2fc_threshold: float = 1.0,
    output_path: Path | None = None,
) -> Figure:
    """Volcano plotを作成する.

    x軸にlog2FoldChange、y軸に-log10(padj)をプロットし、
    有意な遺伝子を色分けする。

    Parameters
    ----------
    deg_df : pd.DataFrame
        DEG結果テーブル（log2FoldChange, padj カラムが必要）
    padj_threshold : float
        有意水準の閾値
    log2fc_threshold : float
        |log2FoldChange| の閾値
    output_path : Path | None
        保存先パス（Noneなら保存しない）

    Returns
    -------
    Figure
        matplotlib Figureオブジェクト
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    df = deg_df.copy()
    # NaNを含むpadjをクリップしてlog変換
    df["-log10_padj"] = -np.log10(df["padj"].clip(lower=1e-300))

    # 分類: up-regulated, down-regulated, not significant
    is_up = (df["padj"] < padj_threshold) & (
        df["log2FoldChange"] >= log2fc_threshold
    )
    is_down = (df["padj"] < padj_threshold) & (
        df["log2FoldChange"] <= -log2fc_threshold
    )
    df["category"] = np.select([is_up, is_down], ["up", "down"], default="ns")

    colors = {"up": "tab:red", "down": "tab:blue", "ns": "tab:gray"}
    labels = {
        "up": "Up-regulated",
        "down": "Down-regulated",
        "ns": "Not significant",
    }

    for cat in ["ns", "up", "down"]:
        subset = df[df["category"] == cat]
        if subset.empty:
            continue
        ax.scatter(
            subset["log2FoldChange"],
            subset["-log10_padj"],
            c=colors[cat],
            label=labels[cat],
            alpha=0.6,
            s=10,
        )

    # 閾値線
    ax.axhline(
        -np.log10(padj_threshold), color="gray", linestyle="--", linewidth=0.5
    )
    ax.axvline(log2fc_threshold, color="gray", linestyle="--", linewidth=0.5)
    ax.axvline(-log2fc_threshold, color="gray", linestyle="--", linewidth=0.5)

    ax.set_xlabel("$\\log_2$(Fold Change)")
    ax.set_ylabel("$-\\log_{10}$(adjusted p-value)")
    ax.set_title("Volcano Plot")
    ax.legend()

    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


def expression_heatmap(
    distance_matrix: np.ndarray,
    sample_labels: list[str] | None = None,
) -> sns.matrix.ClusterGrid:
    """距離行列のヒートマップと階層クラスタリングを作成する.

    Parameters
    ----------
    distance_matrix : np.ndarray
        正方距離行列（対称、対角ゼロ）
    sample_labels : list[str] | None
        サンプル名ラベル

    Returns
    -------
    sns.matrix.ClusterGrid
        seabornのClusterGridオブジェクト
    """
    if sample_labels is not None:
        df = pd.DataFrame(
            distance_matrix,
            index=sample_labels,
            columns=sample_labels,
        )
    else:
        df = pd.DataFrame(distance_matrix)

    g = sns.clustermap(
        df,
        cmap="viridis",
        figsize=(8, 8),
        linewidths=0.5,
    )
    g.ax_heatmap.set_xlabel("Sample")
    g.ax_heatmap.set_ylabel("Sample")
    g.figure.suptitle("Expression Distance Heatmap", y=1.02)

    return g
