"""第10章のパッケージ・設定例を検証する."""

import importlib
import sys
from pathlib import Path

import pytest
import tomllib
from click.testing import CliRunner

from scripts.ch10.config_example import load_config

PROJECT_ROOT = Path(__file__).parents[2]
PACKAGE_DIR = PROJECT_ROOT / "scripts" / "ch10" / "package_example"
CONFIG_PATH = PROJECT_ROOT / "scripts" / "ch10" / "config.yaml"


def test_package_metadata_and_entry_point_resolve() -> None:
    """PEP 621、build backend、CLI entry pointが整合する."""
    with (PACKAGE_DIR / "pyproject.toml").open("rb") as file:
        data = tomllib.load(file)

    project = data["project"]
    assert project["name"] == "my-tool"
    assert project["requires-python"] == ">=3.10"
    assert project["dependencies"] == [
        "biopython>=1.80",
        "pysam>=0.22",
        "click>=8.0",
    ]
    assert data["build-system"] == {
        "requires": ["hatchling"],
        "build-backend": "hatchling.build",
    }

    entry_point = project["scripts"]["my-tool"]
    module_name, function_name = entry_point.split(":")
    module_path = PACKAGE_DIR / "src" / Path(*module_name.split("."))
    assert module_path.with_suffix(".py").is_file()
    assert function_name == "main"


def test_package_cli_runs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """登録先のCLIが最小入力で実行できる."""
    monkeypatch.syspath_prepend(str(PACKAGE_DIR / "src"))
    sys.modules.pop("my_tool.cli", None)
    module = importlib.import_module("my_tool.cli")
    input_path = tmp_path / "reads.fastq"
    input_path.write_text("@read1\nACGT\n+\n!!!!\n", encoding="utf-8")

    result = CliRunner().invoke(
        module.main,
        ["align", "--input", str(input_path)],
    )

    assert result.exit_code == 0
    assert "入力を確認: reads.fastq" in result.output


def test_real_config_is_loaded_and_merged() -> None:
    """本文対応の実ファイルを既存load_configで読み込む."""
    config = load_config(CONFIG_PATH)

    assert config["filtering"] == {
        "min_qual": 30,
        "min_depth": 10,
        "max_missing_rate": 0.1,
    }
    assert config["output"] == {
        "directory": "results",
        "format": "vcf",
    }
