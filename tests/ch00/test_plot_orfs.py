"""ORFマップ可視化のテスト."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure

from scripts.ch00.find_orfs import ORF
from scripts.ch00.plot_orfs import plot_orf_comparison


@pytest.fixture()
def sample_orfs() -> list[ORF]:
    """テスト用ORFリスト."""
    return [
        ORF(start=100, end=400, frame=1, protein="M" + "A" * 99),
        ORF(start=500, end=800, frame=2, protein="M" + "G" * 99),
        ORF(start=200, end=600, frame=-1, protein="M" + "L" * 132),
    ]


@pytest.fixture()
def predicted_orfs() -> list[ORF]:
    """テスト用予測ORFリスト."""
    return [
        ORF(start=100, end=400, frame=1, protein="M" + "A" * 99),
    ]


class TestPlotOrfComparison:
    """plot_orf_comparison() のテスト."""

    def test_returns_figure(self, sample_orfs, predicted_orfs) -> None:
        """Figureオブジェクトを返す."""
        fig = plot_orf_comparison(sample_orfs, predicted_orfs, 1000)
        assert isinstance(fig, Figure)
        plt.close(fig)

    def test_has_two_subplots(self, sample_orfs, predicted_orfs) -> None:
        """2つのサブプロットが存在する."""
        fig = plot_orf_comparison(sample_orfs, predicted_orfs, 1000)
        assert len(fig.axes) == 2
        plt.close(fig)

    def test_savefig(self, sample_orfs, predicted_orfs, tmp_path) -> None:
        """ファイルに保存できる."""
        output = tmp_path / "test_orf_map.png"
        fig = plot_orf_comparison(
            sample_orfs, predicted_orfs, 1000, output_path=output,
        )
        assert output.exists()
        assert output.stat().st_size > 0
        plt.close(fig)

    def test_empty_orfs(self) -> None:
        """ORFが空でもエラーにならない."""
        fig = plot_orf_comparison([], [], 1000)
        assert isinstance(fig, Figure)
        plt.close(fig)

    def test_axes_have_labels(self, sample_orfs, predicted_orfs) -> None:
        """軸ラベルが設定されている."""
        fig = plot_orf_comparison(sample_orfs, predicted_orfs, 1000)
        ax1, ax2 = fig.axes
        assert ax1.get_title() != ""
        assert ax2.get_title() != ""
        assert ax2.get_xlabel() != ""
        plt.close(fig)
