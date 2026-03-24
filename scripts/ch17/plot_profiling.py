"""プロファイリング結果の可視化 (fig-17-02).

関数別処理時間の棒グラフでボトルネックを特定する様子を示す。
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FIGURES_DIR = Path(__file__).resolve().parents[2] / "figures"


def plot_profiling_result(output_path: Path | None = None) -> plt.Figure:
    """模擬的なプロファイリング結果を棒グラフで描画する."""
    # 模擬データ: RNA-seqパイプラインの各ステップの処理時間
    functions = [
        "align_reads()",
        "build_index()",
        "count_features()",
        "load_genome()",
        "write_output()",
        "parse_gtf()",
        "quality_check()",
    ]
    times = [45.2, 18.5, 12.3, 8.1, 3.2, 2.8, 1.5]  # 秒

    fig, ax = plt.subplots(figsize=(9, 5))

    colors = ["#e74c3c" if t == max(times) else "#3498db" for t in times]

    bars = ax.barh(functions, times, color=colors, edgecolor="black", height=0.6)

    # ボトルネック表示
    for bar, t in zip(bars, times):
        ax.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{t:.1f}s ({t / sum(times) * 100:.0f}%)",
            ha="left",
            va="center",
            fontsize=10,
        )

    ax.set_xlabel("Execution time (seconds)", fontsize=12)
    ax.set_title(
        "Profiling Result: Identify the Bottleneck\n"
        f"(Total: {sum(times):.1f}s — align_reads() is {times[0] / sum(times) * 100:.0f}% of total)",
        fontsize=13,
    )
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.3)

    # ボトルネックにラベル
    ax.annotate(
        "Bottleneck!\nOptimize here first",
        xy=(times[0], 0),
        xytext=(times[0] + 10, 1.5),
        fontsize=10,
        fontweight="bold",
        color="#e74c3c",
        arrowprops=dict(arrowstyle="->", color="#e74c3c"),
    )

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


if __name__ == "__main__":
    output = FIGURES_DIR / "ch17_profiling_result.png"
    fig = plot_profiling_result(output_path=output)
    print(f"Saved: {output}")
    plt.close(fig)
