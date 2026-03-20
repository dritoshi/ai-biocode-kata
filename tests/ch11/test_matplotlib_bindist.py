"""matplotlib GCヒストグラムのテスト."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from scripts.ch11.matplotlib_bindist import gc_histogram


class TestGcHistogram:
    """gc_histogram のテスト."""

    def test_returns_figure(self) -> None:
        """Figureオブジェクトを返す."""
        rng = np.random.default_rng(42)
        gc_values = rng.uniform(0.3, 0.7, size=100)
        fig = gc_histogram(gc_values)
        assert isinstance(fig, Figure)
        plt.close(fig)

    def test_has_labels(self) -> None:
        """軸ラベルとタイトルが設定されている."""
        rng = np.random.default_rng(42)
        gc_values = rng.uniform(0.3, 0.7, size=100)
        fig = gc_histogram(gc_values)
        ax = fig.axes[0]
        assert ax.get_xlabel() != ""
        assert ax.get_ylabel() != ""
        assert ax.get_title() != ""
        plt.close(fig)

    def test_savefig(self, tmp_path) -> None:
        """ファイルに保存できる."""
        rng = np.random.default_rng(42)
        gc_values = rng.uniform(0.3, 0.7, size=100)
        output = tmp_path / "gc_hist.png"
        fig = gc_histogram(gc_values, output_path=output)
        assert output.exists()
        assert output.stat().st_size > 0
        plt.close(fig)

    def test_empty_data(self) -> None:
        """空データでもエラーにならない."""
        gc_values = np.array([])
        fig = gc_histogram(gc_values)
        assert isinstance(fig, Figure)
        plt.close(fig)

    def test_single_value(self) -> None:
        """単一値でもエラーにならない."""
        gc_values = np.array([0.5])
        fig = gc_histogram(gc_values)
        assert isinstance(fig, Figure)
        plt.close(fig)

    def test_custom_bins(self) -> None:
        """ビン数を変更できる."""
        rng = np.random.default_rng(42)
        gc_values = rng.uniform(0.3, 0.7, size=100)
        fig = gc_histogram(gc_values, bins=10)
        assert isinstance(fig, Figure)
        plt.close(fig)
