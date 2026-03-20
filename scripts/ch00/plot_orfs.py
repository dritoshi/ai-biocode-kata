"""ORFマップの可視化 — 全ORFとHMM予測結果の比較."""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from scripts.ch00.find_orfs import ORF


def plot_orf_comparison(
    all_orfs: list[ORF],
    predicted: list[ORF],
    genome_length: int,
    output_path: Path | None = None,
) -> Figure:
    """全ORFとHMM予測結果を比較するゲノムマップを作成する.

    上段: 全ORF（グレー）、下段: HMM予測後（赤）。
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

    Returns
    -------
    Figure
        matplotlib Figureオブジェクト
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

    _draw_orf_map(ax1, all_orfs, genome_length, color="gray", alpha=0.5)
    ax1.set_title(f"All ORFs ({len(all_orfs)})")
    ax1.set_ylabel("Frame")

    _draw_orf_map(ax2, predicted, genome_length, color="tab:red", alpha=0.8)
    ax2.set_title(f"HMM-predicted genes ({len(predicted)})")
    ax2.set_xlabel("Genome position (bp)")
    ax2.set_ylabel("Frame")

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
