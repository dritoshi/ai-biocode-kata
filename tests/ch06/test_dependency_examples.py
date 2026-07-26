"""第6章の依存関係設定例を検証する."""

import re
from pathlib import Path

import tomllib
import yaml

PROJECT_ROOT = Path(__file__).parents[2]
EXAMPLES_DIR = PROJECT_ROOT / "scripts" / "ch06" / "examples"


def test_requirements_have_parseable_bounds() -> None:
    """requirements例はパッケージ名とバージョン制約を持つ."""
    path = EXAMPLES_DIR / "requirements.txt"
    requirements = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    ]

    assert requirements == [
        "biopython>=1.83",
        "numpy>=1.26,<2.0",
        "pandas>=2.0",
    ]
    assert all(
        re.fullmatch(r"[A-Za-z0-9_.-]+(?:[<>=!~].+)", item) for item in requirements
    )


def test_pyproject_has_required_metadata_and_dependencies() -> None:
    """pyproject例はPEP 621の主要メタデータを持つ."""
    with (EXAMPLES_DIR / "pyproject.toml").open("rb") as file:
        data = tomllib.load(file)

    project = data["project"]
    assert project["name"] == "my-bioinfo-tool"
    assert project["version"] == "0.1.0"
    assert project["requires-python"] == ">=3.10"
    assert project["dependencies"] == [
        "biopython>=1.83",
        "numpy>=1.26",
    ]


def test_environment_has_channel_order_and_pip_section() -> None:
    """Conda環境例は推奨チャネル順とpip依存を保持する."""
    path = EXAMPLES_DIR / "environment.yml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    assert data["name"] == "rnaseq-env"
    assert data["channels"] == ["conda-forge", "bioconda"]
    assert "defaults" not in data["channels"]
    assert "python=3.11" in data["dependencies"]
    assert "samtools=1.19" in data["dependencies"]
    pip_section = next(
        item["pip"]
        for item in data["dependencies"]
        if isinstance(item, dict) and "pip" in item
    )
    assert pip_section == ["scanpy>=1.10"]


def test_condarc_uses_strict_channel_priority() -> None:
    """condarc例はBioconda推奨のチャネル順とstrictを使う."""
    path = EXAMPLES_DIR / "condarc.example"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    assert data == {
        "channels": ["conda-forge", "bioconda"],
        "channel_priority": "strict",
    }
