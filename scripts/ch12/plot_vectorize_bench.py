"""GC含量計算の実測ベンチマーク棒グラフ (fig-12-01).

本文（§12-1）が示す4つの実装を実際に計測して比較する。ポイントは
「NumPyを使えば速い」ではなく「配列ごとのPythonループを残すと、
NumPyを使っても str.count より遅くなる」ことを可視化する点にある。

- per-base loop : 1塩基ずつPythonのforループでGCを数える（最も遅い）
- str.count     : 文字列組み込みメソッド（内部がC実装。既に速い）
- per-seq NumPy : 配列ごとに np.frombuffer するループ版（罠。遅い）
- batch NumPy   : 全配列を連結して1回で処理する真のベクトル化（速い）

図と本文がずれないよう、batch NumPy は本文と同じ
``scripts.ch12.numpy_vectorize.gc_content_vectorized`` を計測する。
"""

import matplotlib

matplotlib.use("Agg")

import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.ch12.numpy_vectorize import gc_content_vectorized

FIGURES_DIR = Path(__file__).resolve().parents[2] / "figures"


def _gc_per_base_loop(sequences: list[str]) -> list[float]:
    """1塩基ずつのネストしたPythonループ（最も遅い）."""
    results = []
    for seq in sequences:
        gc = 0
        for base in seq:
            if base in ("G", "C"):
                gc += 1
        results.append(gc / len(seq))
    return results


def _gc_str_count(sequences: list[str]) -> list[float]:
    """str.count（内部がC実装のため、配列ごとのPythonループでも速い）."""
    return [(s.count("G") + s.count("C")) / len(s) for s in sequences]


def _gc_per_seq_numpy(sequences: list[str]) -> np.ndarray:
    """配列ごとに np.frombuffer するループ版（ベクトル化に見えるが遅い）."""
    results = np.empty(len(sequences), dtype=np.float64)
    for i, seq in enumerate(sequences):
        arr = np.frombuffer(seq.upper().encode("ascii"), dtype=np.uint8)
        results[i] = ((arr == ord("G")) | (arr == ord("C"))).mean()
    return results


def _timed(fn, arg) -> float:
    start = time.perf_counter()
    fn(arg)
    return time.perf_counter() - start


def _best_ms(fn, arg, reps: int = 5) -> float:
    """ベンチマーク: 数回計測して最小値（ミリ秒）を返す."""
    fn(arg)  # ウォームアップ
    return min(_timed(fn, arg) for _ in range(reps)) * 1000.0


def benchmark_gc_calculation(
    n_sequences: int = 50_000, seq_length: int = 150
) -> dict[str, float]:
    """4つのGC含量実装の処理時間（ミリ秒）を計測する."""
    rng = np.random.default_rng(42)
    bases = np.array(list("ATGC"))
    sequences = [
        "".join(bases[rng.integers(0, 4, size=seq_length)]) for _ in range(n_sequences)
    ]
    return {
        "per-base\nloop": _best_ms(_gc_per_base_loop, sequences),
        "str.count": _best_ms(_gc_str_count, sequences),
        "per-seq\nNumPy": _best_ms(_gc_per_seq_numpy, sequences),
        "batch\nNumPy": _best_ms(gc_content_vectorized, sequences),
    }


def plot_vectorize_bench(output_path: Path | None = None) -> plt.Figure:
    """GC含量計算の4実装のベンチマーク棒グラフを描画する."""
    n_sequences, seq_length = 50_000, 150
    results = benchmark_gc_calculation(n_sequences, seq_length)

    fig, ax = plt.subplots(figsize=(7.5, 5))

    methods = list(results.keys())
    times = list(results.values())
    # 遅い実装は赤系、速い実装は緑系
    colors = ["#e74c3c", "#2ecc71", "#e67e22", "#27ae60"]

    bars = ax.bar(methods, times, color=colors, edgecolor="black", width=0.55)

    for bar, t in zip(bars, times):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{t:.1f} ms",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    ax.set_ylabel("Execution time (ms, lower is better)", fontsize=12)
    ax.set_title(
        f"GC content of {n_sequences:,} sequences x {seq_length} bp\n"
        "A per-sequence NumPy loop is slower than the C-level str.count; "
        "true batch NumPy wins",
        fontsize=11,
    )
    ax.grid(axis="y", alpha=0.3)
    ax.margins(y=0.15)

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


if __name__ == "__main__":
    output = FIGURES_DIR / "ch12_vectorize_bench.png"
    fig = plot_vectorize_bench(output_path=output)
    print(f"Saved: {output}")
    plt.close(fig)
