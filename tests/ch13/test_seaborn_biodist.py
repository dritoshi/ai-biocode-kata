"""seabornバイオリンプロットのテスト."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from scripts.ch13.seaborn_biodist import expression_violin


class TestExpressionViolin:
    """expression_violin のテスト."""

    def test_returns_figure(self) -> None:
        """Figureオブジェクトを返す."""
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {
                "category": ["control"] * 30 + ["treatment"] * 30,
                "expression": np.concatenate(
                    [
                        rng.normal(10, 2, size=30),
                        rng.normal(15, 2, size=30),
                    ]
                ),
            }
        )
        fig = expression_violin(df)
        assert isinstance(fig, Figure)
        plt.close(fig)

    def test_has_labels(self) -> None:
        """軸ラベルとタイトルが設定されている."""
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {
                "category": ["control"] * 30 + ["treatment"] * 30,
                "expression": np.concatenate(
                    [
                        rng.normal(10, 2, size=30),
                        rng.normal(15, 2, size=30),
                    ]
                ),
            }
        )
        fig = expression_violin(df)
        ax = fig.axes[0]
        assert ax.get_xlabel() != ""
        assert ax.get_ylabel() != ""
        assert ax.get_title() != ""
        plt.close(fig)

    def test_custom_columns(self) -> None:
        """カスタムカラム名でも動作する."""
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {
                "group": ["A"] * 20 + ["B"] * 20,
                "value": rng.normal(0, 1, size=40),
            }
        )
        fig = expression_violin(df, category_col="group", value_col="value")
        assert isinstance(fig, Figure)
        plt.close(fig)

    def test_single_category(self) -> None:
        """カテゴリが1つでもエラーにならない."""
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {
                "category": ["control"] * 20,
                "expression": rng.normal(10, 2, size=20),
            }
        )
        fig = expression_violin(df)
        assert isinstance(fig, Figure)
        plt.close(fig)

    def test_three_categories(self) -> None:
        """3カテゴリで正しくプロットされる."""
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {
                "category": ["A"] * 20 + ["B"] * 20 + ["C"] * 20,
                "expression": rng.normal(10, 2, size=60),
            }
        )
        fig = expression_violin(df)
        assert isinstance(fig, Figure)
        plt.close(fig)
