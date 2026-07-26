"""第8章の品質管理設定例を検証する."""

import json
from pathlib import Path

import pytest
import tomllib
import yaml

PROJECT_ROOT = Path(__file__).parents[2]
EXAMPLES_DIR = PROJECT_ROOT / "scripts" / "ch08" / "examples"


def test_pyproject_combines_ruff_and_mypy_settings() -> None:
    """Ruffの3断片とmypy設定を1つのTOMLへ統合する."""
    with (EXAMPLES_DIR / "pyproject.toml").open("rb") as file:
        data = tomllib.load(file)

    ruff = data["tool"]["ruff"]
    assert ruff["target-version"] == "py310"
    assert ruff["line-length"] == 88
    assert ruff["lint"]["select"] == ["E", "W", "F", "I", "N", "D", "UP"]
    assert ruff["lint"]["pydocstyle"]["convention"] == "numpy"
    assert ruff["lint"]["per-file-ignores"]["tests/**"] == ["D"]

    mypy = data["tool"]["mypy"]
    assert mypy == {
        "python_version": "3.10",
        "warn_return_any": True,
        "warn_unused_configs": True,
        "disallow_untyped_defs": True,
    }


def test_pre_commit_has_pinned_quality_hooks() -> None:
    """pre-commit例は実在タグと必要な品質フックを固定する."""
    path = EXAMPLES_DIR / "pre-commit-config.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    repositories = {item["repo"]: item for item in data["repos"]}

    ruff = repositories["https://github.com/astral-sh/ruff-pre-commit"]
    assert ruff["rev"] == "v0.16.0"
    assert ruff["hooks"] == [
        {"id": "ruff-check", "args": ["--fix"]},
        {"id": "ruff-format"},
    ]

    mypy = repositories["https://github.com/pre-commit/mirrors-mypy"]
    assert mypy["rev"] == "v2.3.0"
    assert mypy["hooks"] == [
        {"id": "mypy", "additional_dependencies": ["types-requests"]}
    ]


@pytest.mark.parametrize(
    "filename",
    ["claude-settings.json", "codex-hooks.json"],
)
def test_agent_hook_runs_ruff_after_file_edits(filename: str) -> None:
    """両CLIのPostToolUse例は編集後にRuffを実行する."""
    path = EXAMPLES_DIR / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    groups = data["hooks"]["PostToolUse"]

    assert len(groups) == 1
    assert groups[0]["matcher"] == "Edit|Write"
    assert groups[0]["hooks"] == [{"type": "command", "command": "ruff check --fix ."}]
