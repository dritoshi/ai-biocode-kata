"""O記法の成長曲線を描画するスクリプト (fig-03-01).

$O(1)$, $O(\\log n)$, $O(n)$, $O(n \\log n)$, $O(n^2)$ の成長を
1つのグラフに重ねてプロットし、計算量の違いを視覚化する。
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FIGURES_DIR = Path(__file__).resolve().parents[2] / "figures"


def plot_complexity_growth(output_path: Path | None = None) -> plt.Figure:
    """計算量の成長曲線を描画する.

    Parameters
    ----------
    output_path : Path | None
        保存先パス（Noneなら保存しない）

    Returns
    -------
    Figure
        matplotlib Figureオブジェクト
    """
    n = np.arange(1, 101)

    complexities = {
        "$O(1)$": np.ones_like(n, dtype=float),
        "$O(\\log n)$": np.log2(n),
        "$O(n)$": n.astype(float),
        "$O(n \\log n)$": n * np.log2(n),
        "$O(n^2)$": n**2,
    }

    colors = ["#2ca02c", "#1f77b4", "#ff7f0e", "#d62728", "#9467bd"]

    fig, ax = plt.subplots(figsize=(8, 6))

    for (label, y), color in zip(complexities.items(), colors):
        ax.plot(n, y, label=label, linewidth=2, color=color)

    ax.set_xlabel("Input size ($n$)", fontsize=12)
    ax.set_ylabel("Operations", fontsize=12)
    ax.set_title("Growth of Common Time Complexities", fontsize=14)
    ax.legend(fontsize=11, loc="upper left")
    ax.set_xlim(1, 100)
    ax.set_ylim(0, 5000)

    # グリッドを薄く表示
    ax.grid(True, alpha=0.3)

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


if __name__ == "__main__":
    output = FIGURES_DIR / "ch03_complexity_growth.png"
    fig = plot_complexity_growth(output_path=output)
    print(f"Saved: {output}")
    plt.close(fig)
