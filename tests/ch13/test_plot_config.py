"""プロジェクト共通プロット設定のテスト."""

import matplotlib as mpl

from scripts.ch13.plot_config import apply_project_style


def test_apply_project_style_updates_rcparams() -> None:
    with mpl.rc_context():
        apply_project_style()

        assert mpl.rcParams["font.size"] == 12
        assert mpl.rcParams["axes.labelsize"] == 14
        assert mpl.rcParams["axes.titlesize"] == 16
        assert mpl.rcParams["figure.dpi"] == 150
        assert mpl.rcParams["savefig.dpi"] == 300
        assert mpl.rcParams["savefig.bbox"] == "tight"
