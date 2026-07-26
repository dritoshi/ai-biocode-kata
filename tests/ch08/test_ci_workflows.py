"""第8章のGitHub Actionsワークフロー例を検証する."""

from pathlib import Path
from typing import Any

import pytest
import yaml

PROJECT_ROOT = Path(__file__).parents[2]
EXAMPLES_DIR = PROJECT_ROOT / "scripts" / "ch08" / "examples"
SETUP_UV_REF = "astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b"


def _load_workflow(filename: str) -> dict[str, Any]:
    """YAMLのonキーを文字列として保ったまま読み込む."""
    path = EXAMPLES_DIR / filename
    data = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    assert isinstance(data, dict)
    return data


def _steps(workflow: dict[str, Any]) -> list[dict[str, Any]]:
    """testジョブのstepsを返す."""
    steps = workflow["jobs"]["test"]["steps"]
    assert isinstance(steps, list)
    return steps


@pytest.mark.parametrize("filename", ["ci.yml", "ci-matrix.yml"])
def test_workflow_has_safe_triggers_and_permissions(filename: str) -> None:
    workflow = _load_workflow(filename)

    assert workflow["on"]["push"]["branches"] == ["main"]
    assert workflow["on"]["pull_request"]["branches"] == ["main"]
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["jobs"]["test"]["runs-on"] == "ubuntu-latest"


@pytest.mark.parametrize("filename", ["ci.yml", "ci-matrix.yml"])
def test_workflow_pins_current_actions(filename: str) -> None:
    steps = _steps(_load_workflow(filename))
    uses = [step["uses"] for step in steps if "uses" in step]

    assert "actions/checkout@v6" in uses
    assert "actions/setup-python@v6" in uses
    assert SETUP_UV_REF in uses
    assert all("@v7" not in action for action in uses)


@pytest.mark.parametrize("filename", ["ci.yml", "ci-matrix.yml"])
def test_workflow_uses_locked_uv_environment(filename: str) -> None:
    steps = _steps(_load_workflow(filename))
    commands = [step["run"] for step in steps if "run" in step]

    assert "uv sync --frozen" in commands
    assert "uv run ruff check scripts/ tests/" in commands
    assert any(
        "uv run mypy --follow-imports=skip --ignore-missing-imports" in command
        and "scripts/ch08 tests/ch08" in command
        for command in commands
    )
    assert any("--with pytest-cov pytest tests/" in command for command in commands)
    assert all("ruff format --check" not in command for command in commands)
    assert all("requirements.txt" not in command for command in commands)


def test_matrix_workflow_covers_supported_python_versions() -> None:
    workflow = _load_workflow("ci-matrix.yml")
    job = workflow["jobs"]["test"]
    steps = _steps(workflow)
    setup_python = next(
        step for step in steps if step.get("uses") == "actions/setup-python@v6"
    )

    assert job["strategy"]["matrix"]["python-version"] == [
        "3.10",
        "3.11",
        "3.12",
        "3.13",
        "3.14",
    ]
    assert setup_python["with"]["python-version"] == ("${{ matrix.python-version }}")
