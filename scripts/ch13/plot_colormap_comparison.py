"""カラーマップ比較図 (fig-13-07).

viridis/cividis/jet/rainbow を並べて比較し、
色覚多様性への配慮の重要性を視覚化する。
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FIGURES_DIR = Path(__file__).resolve().parents[2] / "figures"


def plot_colormap_comparison(output_path: Path | None = None) -> plt.Figure:
    """推奨・非推奨カラーマップの比較図を描画する."""
    rng = np.random.default_rng(42)
    data = rng.normal(0, 1, size=(20, 20))

    cmaps = {
        "viridis (recommended)": "viridis",
        "cividis (recommended)": "cividis",
        "jet (avoid)": "jet",
        "rainbow (avoid)": "rainbow",
    }

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))

    for ax, (label, cmap_name) in zip(axes, cmaps.items()):
        im = ax.imshow(data, cmap=cmap_name, aspect="auto")
        ax.set_title(label, fontsize=12, fontweight="bold")
        ax.set_xticks([])
        ax.set_yticks([])
        fig.colorbar(im, ax=ax, shrink=0.8)

    fig.suptitle(
        "Colormap Comparison: viridis/cividis are perceptually uniform and colorblind-safe",
        fontsize=13,
        y=1.02,
    )
    fig.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


if __name__ == "__main__":
    output = FIGURES_DIR / "ch13_colormap_comparison.png"
    fig = plot_colormap_comparison(output_path=output)
    print(f"Saved: {output}")
    plt.close(fig)
