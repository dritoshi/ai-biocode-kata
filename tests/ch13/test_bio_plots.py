"""Volcano plotとヒートマップのテスト."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import seaborn as sns
from matplotlib.figure import Figure

from scripts.ch13.bio_plots import expression_heatmap, volcano_plot


@pytest.fixture()
def deg_df() -> pd.DataFrame:
    """テスト用DEG結果DataFrame."""
    rng = np.random.default_rng(42)
    n = 100
    return pd.DataFrame(
        {
            "gene": [f"Gene{i}" for i in range(n)],
            "log2FoldChange": rng.normal(0, 2, size=n),
            "pvalue": rng.uniform(0, 1, size=n),
            "padj": rng.uniform(0, 1, size=n),
        }
    )


@pytest.fixture()
def distance_matrix() -> np.ndarray:
    """テスト用距離行列（対称、対角ゼロ）."""
    rng = np.random.default_rng(42)
    n = 6
    raw = rng.uniform(0, 1, size=(n, n))
    sym = (raw + raw.T) / 2
    np.fill_diagonal(sym, 0)
    return sym


class TestVolcanoPlot:
    """volcano_plot のテスト."""

    def test_returns_figure(self, deg_df) -> None:
        """Figureオブジェクトを返す."""
        fig = volcano_plot(deg_df)
        assert isinstance(fig, Figure)
        plt.close(fig)

    def test_has_labels(self, deg_df) -> None:
        """軸ラベルとタイトルが設定されている."""
        fig = volcano_plot(deg_df)
        ax = fig.axes[0]
        assert ax.get_xlabel() != ""
        assert ax.get_ylabel() != ""
        assert ax.get_title() != ""
        plt.close(fig)

    def test_has_legend(self, deg_df) -> None:
        """凡例が存在する."""
        fig = volcano_plot(deg_df)
        ax = fig.axes[0]
        legend = ax.get_legend()
        assert legend is not None
        plt.close(fig)

    def test_savefig(self, deg_df, tmp_path) -> None:
        """ファイルに保存できる."""
        output = tmp_path / "volcano.png"
        fig = volcano_plot(deg_df, output_path=output)
        assert output.exists()
        assert output.stat().st_size > 0
        plt.close(fig)

    def test_nan_padj(self) -> None:
        """NaN含有データでもエラーにならない."""
        df = pd.DataFrame(
            {
                "gene": ["A", "B", "C"],
                "log2FoldChange": [2.0, -1.5, 0.3],
                "pvalue": [0.001, 0.01, 0.5],
                "padj": [0.01, float("nan"), 0.8],
            }
        )
        fig = volcano_plot(df)
        assert isinstance(fig, Figure)
        plt.close(fig)

    def test_all_nonsignificant(self) -> None:
        """全遺伝子が非有意でもエラーにならない."""
        df = pd.DataFrame(
            {
                "gene": ["A", "B"],
                "log2FoldChange": [0.1, -0.2],
                "pvalue": [0.5, 0.8],
                "padj": [0.9, 0.95],
            }
        )
        fig = volcano_plot(df)
        assert isinstance(fig, Figure)
        plt.close(fig)


class TestExpressionHeatmap:
    """expression_heatmap のテスト."""

    def test_returns_clustergrid(self, distance_matrix) -> None:
        """ClusterGridオブジェクトを返す."""
        g = expression_heatmap(distance_matrix)
        assert isinstance(g, sns.matrix.ClusterGrid)
        plt.close(g.figure)

    def test_with_labels(self, distance_matrix) -> None:
        """ラベル付きで動作する."""
        labels = [f"Sample{i}" for i in range(len(distance_matrix))]
        g = expression_heatmap(distance_matrix, sample_labels=labels)
        assert isinstance(g, sns.matrix.ClusterGrid)
        plt.close(g.figure)

    def test_heatmap_has_xlabel(self, distance_matrix) -> None:
        """ヒートマップ軸にラベルが設定されている."""
        g = expression_heatmap(distance_matrix)
        assert g.ax_heatmap.get_xlabel() != ""
        assert g.ax_heatmap.get_ylabel() != ""
        plt.close(g.figure)

    def test_small_matrix(self) -> None:
        """2x2の最小行列でも動作する."""
        mat = np.array([[0.0, 0.5], [0.5, 0.0]])
        g = expression_heatmap(mat, sample_labels=["A", "B"])
        assert isinstance(g, sns.matrix.ClusterGrid)
        plt.close(g.figure)
