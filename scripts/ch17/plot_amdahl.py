"""Amdahlの法則グラフ (fig-17-01).

ボトルネック関数の割合pと高速化率sから全体の高速化率をプロットし、
並列化の限界を視覚化する。
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FIGURES_DIR = Path(__file__).resolve().parents[2] / "figures"


def plot_amdahl(output_path: Path | None = None) -> plt.Figure:
    """Amdahlの法則をプロットする.

    全体の高速化率 = 1 / ((1 - p) + p/s)
    p: 高速化可能な部分の割合
    s: その部分の高速化率
    """
    s = np.linspace(1, 64, 200)  # 高速化率（1〜64倍）

    fig, ax = plt.subplots(figsize=(8, 6))

    p_values = [0.5, 0.75, 0.9, 0.95, 0.99]
    colors = ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#3498db"]

    for p, color in zip(p_values, colors):
        speedup = 1 / ((1 - p) + p / s)
        ax.plot(s, speedup, label=f"p = {p:.0%}", linewidth=2, color=color)

    ax.set_xlabel("Speedup of parallelized portion ($s$)", fontsize=12)
    ax.set_ylabel("Overall speedup", fontsize=12)
    ax.set_title("Amdahl's Law: Diminishing Returns of Parallelization", fontsize=14)
    ax.legend(title="Parallelizable\nfraction ($p$)", fontsize=10, title_fontsize=10)
    ax.set_xlim(1, 64)
    ax.set_ylim(1, 30)
    ax.grid(True, alpha=0.3)

    # アノテーション
    ax.annotate(
        "p=50% → max 2x\nregardless of cores",
        xy=(50, 2.0),
        xytext=(35, 8),
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color="#e74c3c"),
        color="#e74c3c",
    )

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


if __name__ == "__main__":
    output = FIGURES_DIR / "ch17_amdahl.png"
    fig = plot_amdahl(output_path=output)
    print(f"Saved: {output}")
    plt.close(fig)
