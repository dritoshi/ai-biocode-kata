"""ORFマップ可視化のテスト."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure

from scripts.ch00.find_orfs import ORF
from scripts.ch00.plot_orfs import KnownGene, plot_orf_comparison


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


@pytest.fixture()
def sample_known_genes() -> list[KnownGene]:
    """テスト用GenBankアノテーション."""
    return [
        KnownGene("geneA", 100, 400, +1),
        KnownGene("geneB", 500, 900, -2),
    ]


class TestThreePanelPlot:
    """3パネル表示（GenBankアノテーション付き）のテスト."""

    def test_three_panels_with_known_genes(
        self, sample_orfs, predicted_orfs, sample_known_genes,
    ) -> None:
        """known_genesを渡すと3つのサブプロットが存在する."""
        fig = plot_orf_comparison(
            sample_orfs, predicted_orfs, 1000,
            known_genes=sample_known_genes,
        )
        assert len(fig.axes) == 3
        plt.close(fig)

    def test_known_gene_labels(
        self, sample_orfs, predicted_orfs, sample_known_genes,
    ) -> None:
        """3パネル時に下段にテキスト要素（遺伝子名）が存在する."""
        fig = plot_orf_comparison(
            sample_orfs, predicted_orfs, 1000,
            known_genes=sample_known_genes,
        )
        ax3 = fig.axes[2]
        texts = [t.get_text() for t in ax3.texts]
        assert "geneA" in texts
        assert "geneB" in texts
        plt.close(fig)

    def test_savefig_three_panels(
        self, sample_orfs, predicted_orfs, sample_known_genes, tmp_path,
    ) -> None:
        """3パネル図のファイル保存ができる."""
        output = tmp_path / "test_three_panel.png"
        fig = plot_orf_comparison(
            sample_orfs, predicted_orfs, 1000,
            output_path=output,
            known_genes=sample_known_genes,
        )
        assert output.exists()
        assert output.stat().st_size > 0
        plt.close(fig)
