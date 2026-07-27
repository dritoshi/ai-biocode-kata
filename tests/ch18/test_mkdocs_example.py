"""第18章のMkDocs最小サイトを検証する."""

from __future__ import annotations

import runpy
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

PROJECT_ROOT = Path(__file__).parents[2]
EXAMPLE_DIR = PROJECT_ROOT / "scripts" / "ch18" / "mkdocs_example"
CONFIG_PATH = EXAMPLE_DIR / "mkdocs.yml"


def _load_config() -> dict[str, Any]:
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_mkdocs_config_enables_material_and_mkdocstrings() -> None:
    config = _load_config()

    assert config["site_name"] == "My Tool Docs"
    assert config["theme"] == {"name": "material"}
    assert config["plugins"][0] == "search"

    plugin = config["plugins"][1]["mkdocstrings"]
    assert plugin["default_handler"] == "python"
    python_handler = plugin["handlers"]["python"]
    assert python_handler["paths"] == ["src"]
    assert python_handler["options"]["docstring_style"] == "numpy"


def test_navigation_targets_and_python_source_exist() -> None:
    config = _load_config()
    nav_entries = config["nav"]

    for entry in nav_entries:
        assert isinstance(entry, dict)
        relative_path = next(iter(entry.values()))
        assert (EXAMPLE_DIR / "docs" / relative_path).is_file()

    api_page = (EXAMPLE_DIR / "docs" / "api.md").read_text(encoding="utf-8")
    assert "::: my_tool.core" in api_page
    assert (EXAMPLE_DIR / "src" / "my_tool" / "core.py").is_file()


def test_documented_example_function() -> None:
    namespace = runpy.run_path(
        str(EXAMPLE_DIR / "src" / "my_tool" / "core.py"),
    )
    sequence_length = namespace["sequence_length"]

    assert sequence_length("ACGTN") == 5
    assert sequence_length("") == 0


@pytest.mark.skipif(
    shutil.which("mkdocs") is None,
    reason="MkDocsがインストールされていない",
)
def test_mkdocs_build_strict(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    subprocess.run(
        [
            "mkdocs",
            "build",
            "--strict",
            "--config-file",
            str(CONFIG_PATH),
            "--site-dir",
            str(site_dir),
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    assert (site_dir / "index.html").is_file()
    api_html = (site_dir / "api" / "index.html").read_text(encoding="utf-8")
    assert "sequence_length" in api_html
    assert "塩基配列の文字数を返す" in api_html
