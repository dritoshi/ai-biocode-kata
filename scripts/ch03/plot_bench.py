"""list vs set vs dict のベンチマーク棒グラフ (fig-03-02).

10万件の遺伝子IDに対する検索速度の違いを棒グラフで視覚化する。
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import matplotlib.pyplot as plt

from scripts.ch03.data_structure_bench import benchmark_search

FIGURES_DIR = Path(__file__).resolve().parents[2] / "figures"


def plot_benchmark(output_path: Path | None = None) -> plt.Figure:
    """データ構造別の検索時間を棒グラフで描画する."""
    results = benchmark_search(n=100_000, n_queries=1000)

    fig, ax = plt.subplots(figsize=(7, 5))

    structures = list(results.keys())
    times = list(results.values())
    colors = ["#e74c3c", "#2ecc71", "#3498db"]

    bars = ax.bar(structures, times, color=colors, edgecolor="black", width=0.5)

    # 値をバーの上に表示
    for bar, t in zip(bars, times):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{t:.4f}s",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    ax.set_ylabel("Search time (seconds, 1000 queries)", fontsize=12)
    ax.set_title(
        "Search Performance: list vs set vs dict\n"
        "(n = 100,000 gene IDs)",
        fontsize=13,
    )
    ax.set_yscale("log")
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


if __name__ == "__main__":
    output = FIGURES_DIR / "ch03_list_vs_set_bench.png"
    fig = plot_benchmark(output_path=output)
    print(f"Saved: {output}")
    plt.close(fig)
