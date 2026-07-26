"""第4章の設定ファイル例を検証する."""

from pathlib import Path

import tomllib
import yaml

PROJECT_ROOT = Path(__file__).parents[2]
YAML_PATH = PROJECT_ROOT / "scripts" / "ch04" / "config_example.yaml"
TOML_PATH = PROJECT_ROOT / "scripts" / "ch04" / "pyproject_example.toml"


def test_yaml_config_has_required_values_and_relative_paths() -> None:
    """YAML例は必須値を持ち、環境固有の絶対パスを含まない."""
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))

    assert data["samples"] == ["sample_A", "sample_B"]
    assert data["threads"] == 8
    assert set(data["reference"]) == {"genome", "annotation"}
    assert Path(data["reference"]["genome"]).is_absolute() is False
    assert Path(data["reference"]["annotation"]).is_absolute() is False


def test_pyproject_dependencies_are_pep621_array() -> None:
    """PEP 621のdependenciesは文字列配列として定義する."""
    with TOML_PATH.open("rb") as file:
        data = tomllib.load(file)

    project = data["project"]
    assert project["name"] == "my-bioinfo-tool"
    assert project["requires-python"] == ">=3.10"
    assert project["dependencies"] == [
        "biopython>=1.83",
        "numpy>=1.26",
    ]
