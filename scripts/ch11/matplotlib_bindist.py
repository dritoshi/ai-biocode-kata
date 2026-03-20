"""matplotlibの基礎 — Figure/AxesのオブジェクトAPIによるGC含量ヒストグラム."""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure


def gc_histogram(
    gc_values: np.ndarray,
    bins: int = 30,
    output_path: Path | None = None,
) -> Figure:
    """GC含量のヒストグラムを作成する.

    Parameters
    ----------
    gc_values : np.ndarray
        GC含量の配列（0〜1の範囲）
    bins : int
        ビンの数
    output_path : Path | None
        保存先パス（Noneなら保存しない）

    Returns
    -------
    Figure
        matplotlib Figureオブジェクト
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(gc_values, bins=bins, edgecolor="black", alpha=0.7)
    ax.set_xlabel("GC content")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of GC Content")

    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig
