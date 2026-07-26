"""プロジェクト共通のMatplotlibスタイル設定."""

import matplotlib.pyplot as plt


def apply_project_style() -> None:
    """プロジェクト共通のMatplotlibスタイルを適用する."""
    plt.rcParams.update(
        {
            "font.size": 12,
            "axes.labelsize": 14,
            "axes.titlesize": 16,
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
        }
    )
