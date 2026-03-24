"""§13の書籍用図を生成するスクリプト.

テストデータを生成し、各プロット関数を呼び出して figures/ にPNGを保存する。
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FIGURES_DIR = Path(__file__).resolve().parents[2] / "figures"


def generate_gc_histogram() -> None:
    """fig-13-01: GC含量ヒストグラム."""
    from scripts.ch13.matplotlib_bindist import gc_histogram

    rng = np.random.default_rng(42)
    # 大腸菌ゲノム断片のGC含量をシミュレーション（平均0.51、標準偏差0.05）
    gc_values = rng.normal(0.51, 0.05, size=500).clip(0, 1)

    output = FIGURES_DIR / "ch13_gc_histogram.png"
    fig = gc_histogram(gc_values, bins=30, output_path=output)
    plt.close(fig)
    print(f"  -> {output}")


def generate_volcano_plot() -> None:
    """fig-13-02: Volcano plot."""
    from scripts.ch13.bio_plots import volcano_plot

    rng = np.random.default_rng(42)
    n = 2000
    # DEG解析の模擬データ: 大部分は非有意、一部が有意に上昇/減少
    log2fc = rng.normal(0, 1.5, size=n)
    # p値: log2FCが大きいほど小さくなる傾向
    raw_p = 10 ** (-np.abs(log2fc) * rng.uniform(0.5, 3.0, size=n))
    padj = np.minimum(raw_p * n / np.arange(1, n + 1), 1.0)  # BH風の補正

    deg_df = pd.DataFrame(
        {
            "gene": [f"Gene{i}" for i in range(n)],
            "log2FoldChange": log2fc,
            "pvalue": raw_p,
            "padj": padj,
        }
    )

    output = FIGURES_DIR / "ch13_volcano_plot.png"
    fig = volcano_plot(deg_df, output_path=output)
    plt.close(fig)
    print(f"  -> {output}")


def generate_expression_heatmap() -> None:
    """fig-13-03: ヒートマップ+デンドログラム."""
    from scripts.ch13.bio_plots import expression_heatmap

    rng = np.random.default_rng(42)
    n_samples = 8
    # サンプル間距離行列: control群とtreatment群がクラスタを形成
    labels = [f"Ctrl_{i+1}" for i in range(4)] + [
        f"Treat_{i+1}" for i in range(4)
    ]
    # 同群内は距離が小さく、異群間は距離が大きい
    dist = np.zeros((n_samples, n_samples))
    for i in range(n_samples):
        for j in range(i + 1, n_samples):
            same_group = (i < 4 and j < 4) or (i >= 4 and j >= 4)
            base = 0.2 if same_group else 0.7
            d = base + rng.uniform(-0.1, 0.1)
            dist[i, j] = d
            dist[j, i] = d

    g = expression_heatmap(dist, sample_labels=labels)
    output = FIGURES_DIR / "ch13_expression_heatmap.png"
    g.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(g.figure)
    print(f"  -> {output}")


def generate_violin_plot() -> None:
    """fig-13-04: バイオリンプロット."""
    from scripts.ch13.seaborn_biodist import expression_violin

    rng = np.random.default_rng(42)
    n_per_group = 50
    df = pd.DataFrame(
        {
            "category": ["Control"] * n_per_group
            + ["Treatment"] * n_per_group,
            "expression": np.concatenate(
                [
                    rng.normal(10, 2, size=n_per_group),
                    rng.normal(14, 2.5, size=n_per_group),
                ]
            ),
        }
    )

    output = FIGURES_DIR / "ch13_violin_plot.png"
    fig = expression_violin(df, output_path=output)
    plt.close(fig)
    print(f"  -> {output}")


if __name__ == "__main__":
    print("Generating §13 figures...")
    generate_gc_histogram()
    generate_volcano_plot()
    generate_expression_heatmap()
    generate_violin_plot()
    print("Done.")
