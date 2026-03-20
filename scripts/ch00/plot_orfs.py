"""ORFマップの可視化 — 全ORF・HMM予測結果・GenBankアノテーションの比較."""

import matplotlib

matplotlib.use("Agg")

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from scripts.ch00.find_orfs import ORF


@dataclass(frozen=True)
class KnownGene:
    """GenBankアノテーションの既知遺伝子."""

    name: str
    start: int
    end: int
    frame: int


# E. coli K-12 MG1655 (U00096.3) の 1–20,000 bp 領域に含まれるCDS遺伝子
KNOWN_GENES: list[KnownGene] = [
    KnownGene("thrL", 189, 255, +1),
    KnownGene("thrA", 336, 2799, +1),
    KnownGene("thrB", 2800, 3733, +2),
    KnownGene("thrC", 3733, 5020, +2),
    KnownGene("yaaX", 5233, 5530, +2),
    KnownGene("yaaA", 5682, 6459, -3),
    KnownGene("yaaJ", 6528, 7959, -3),
    KnownGene("talB", 8237, 9191, +3),
    KnownGene("mog", 9305, 9893, +3),
    KnownGene("satP", 9927, 10494, -3),
    KnownGene("yaaW", 10642, 11356, -2),
    KnownGene("mbiA", 10829, 11315, +2),
    KnownGene("yaaI", 11381, 11786, -1),
    KnownGene("dnaK", 12162, 14079, +1),
    KnownGene("dnaJ", 14167, 15298, +2),
    KnownGene("insL1", 15444, 16557, +1),
    KnownGene("mokC", 16750, 16960, -2),
    KnownGene("hokC", 16750, 16903, -2),
    KnownGene("sokC", 16951, 17010, +3),
    KnownGene("nhaA", 17488, 18655, +2),
    KnownGene("nhaR", 18714, 19620, +1),
]


def plot_orf_comparison(
    all_orfs: list[ORF],
    predicted: list[ORF],
    genome_length: int,
    output_path: Path | None = None,
    known_genes: list[KnownGene] | None = None,
) -> Figure:
    """全ORFとHMM予測結果を比較するゲノムマップを作成する.

    上段: 全ORF（グレー）、中段: HMM予測後（赤）。
    known_genesを指定すると下段にGenBankアノテーション（青）を追加。
    横軸はゲノム座標、フレーム別に段を変える。

    Parameters
    ----------
    all_orfs : list[ORF]
        find_all_orfs()で検出された全ORF
    predicted : list[ORF]
        predict_genes()で絞り込まれた遺伝子候補
    genome_length : int
        ゲノム配列の塩基長
    output_path : Path | None
        保存先パス（Noneなら保存しない）
    known_genes : list[KnownGene] | None
        GenBankアノテーションの既知遺伝子（Noneなら2パネル）

    Returns
    -------
    Figure
        matplotlib Figureオブジェクト
    """
    if known_genes is not None:
        fig, (ax1, ax2, ax3) = plt.subplots(
            3, 1, figsize=(12, 8), sharex=True,
        )
    else:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

    _draw_orf_map(ax1, all_orfs, genome_length, color="gray", alpha=0.5)
    ax1.set_title(f"All ORFs ({len(all_orfs)})")
    ax1.set_ylabel("Frame")

    _draw_orf_map(ax2, predicted, genome_length, color="tab:red", alpha=0.8)
    ax2.set_title(f"HMM-predicted genes ({len(predicted)})")
    ax2.set_ylabel("Frame")

    if known_genes is not None:
        _draw_known_genes(ax3, known_genes, genome_length)
        ax3.set_title(f"GenBank annotation ({len(known_genes)})")
        ax3.set_xlabel("Genome position (bp)")
        ax3.set_ylabel("Frame")
    else:
        ax2.set_xlabel("Genome position (bp)")

    plt.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")

    return fig


def _draw_orf_map(
    ax: plt.Axes,
    orfs: list[ORF],
    genome_length: int,
    color: str,
    alpha: float,
) -> None:
    """ORFをゲノムマップとして描画する."""
    frame_y = {+1: 3, +2: 2, +3: 1, -1: -1, -2: -2, -3: -3}

    for orf in orfs:
        y = frame_y.get(orf.frame, 0)
        ax.barh(
            y, orf.end - orf.start, left=orf.start,
            height=0.6, color=color, alpha=alpha, edgecolor="none",
        )

    ax.set_yticks([-3, -2, -1, 1, 2, 3])
    ax.set_yticklabels(["-3", "-2", "-1", "+1", "+2", "+3"])
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlim(0, genome_length)
    ax.set_ylim(-4, 4)


def _draw_known_genes(
    ax: plt.Axes,
    genes: list[KnownGene],
    genome_length: int,
) -> None:
    """GenBankアノテーションの既知遺伝子をゲノムマップとして描画する."""
    frame_y = {+1: 3, +2: 2, +3: 1, -1: -1, -2: -2, -3: -3}

    for gene in genes:
        y = frame_y.get(gene.frame, 0)
        ax.barh(
            y, gene.end - gene.start, left=gene.start,
            height=0.6, color="tab:blue", alpha=0.8, edgecolor="none",
        )
        ax.text(
            (gene.start + gene.end) / 2, y + 0.45, gene.name,
            ha="center", va="bottom", fontsize=6,
        )

    ax.set_yticks([-3, -2, -1, 1, 2, 3])
    ax.set_yticklabels(["-3", "-2", "-1", "+1", "+2", "+3"])
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlim(0, genome_length)
    ax.set_ylim(-4, 4)
