"""ベクトル化 vs forループの性能比較棒グラフ (fig-12-01).

NumPyベクトル化演算とforループの処理時間差を視覚化する。
"""

import matplotlib

matplotlib.use("Agg")

import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FIGURES_DIR = Path(__file__).resolve().parents[2] / "figures"


def benchmark_gc_calculation(n_sequences: int = 10_000, seq_length: int = 150) -> dict[str, float]:
    """forループとベクトル化のGC含量計算ベンチマーク."""
    rng = np.random.default_rng(42)
    # ランダムな塩基配列を数値で表現 (A=0, T=1, G=2, C=3)
    sequences = rng.integers(0, 4, size=(n_sequences, seq_length))

    results: dict[str, float] = {}

    # forループ版
    start = time.perf_counter()
    gc_loop = []
    for seq in sequences:
        gc_count = 0
        for base in seq:
            if base == 2 or base == 3:  # G or C
                gc_count += 1
        gc_loop.append(gc_count / seq_length)
    results["for loop"] = time.perf_counter() - start

    # NumPyベクトル化版
    start = time.perf_counter()
    gc_vector = np.mean((sequences == 2) | (sequences == 3), axis=1)
    results["NumPy vectorized"] = time.perf_counter() - start

    return results


def plot_vectorize_bench(output_path: Path | None = None) -> plt.Figure:
    """ベクトル化 vs forループのベンチマーク棒グラフを描画する."""
    results = benchmark_gc_calculation()

    fig, ax = plt.subplots(figsize=(7, 5))

    methods = list(results.keys())
    times = list(results.values())
    colors = ["#e74c3c", "#2ecc71"]

    bars = ax.bar(methods, times, color=colors, edgecolor="black", width=0.4)

    for bar, t in zip(bars, times):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{t:.3f}s",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    speedup = results["for loop"] / results["NumPy vectorized"]
    ax.set_ylabel("Execution time (seconds)", fontsize=12)
    ax.set_title(
        f"GC Content Calculation: for loop vs NumPy\n"
        f"(10,000 sequences × 150 bp, speedup: {speedup:.0f}x)",
        fontsize=13,
    )
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


if __name__ == "__main__":
    output = FIGURES_DIR / "ch12_vectorize_bench.png"
    fig = plot_vectorize_bench(output_path=output)
    print(f"Saved: {output}")
    plt.close(fig)
