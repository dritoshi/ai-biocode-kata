"""第13章のpyGenomeTracks設定例を検証する."""

from configparser import ConfigParser
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2]
TRACKS_PATH = PROJECT_ROOT / "scripts" / "ch13" / "tracks.ini"


def test_tracks_have_required_sections_and_values() -> None:
    """coverage、peaks、genesの必須値を検証する."""
    parser = ConfigParser(interpolation=None)
    loaded = parser.read(TRACKS_PATH, encoding="utf-8")

    assert loaded == [str(TRACKS_PATH)]
    assert parser.sections() == ["coverage", "peaks", "genes"]
    assert parser["coverage"]["file"].endswith(".bw")
    assert parser["coverage"].getfloat("height") == 4
    assert parser["coverage"].getfloat("min_value") == 0
    assert parser["coverage"]["color"] == "#2171b5"
    assert parser["peaks"]["file"].endswith(".bed")
    assert parser["peaks"].getfloat("height") == 1
    assert parser["genes"]["file"].endswith(".gtf")
    assert parser["genes"].getint("fontsize") == 8
