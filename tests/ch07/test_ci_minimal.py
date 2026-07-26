"""第7章の最小GitHub Actionsワークフローを検証する."""

from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).parents[2]
WORKFLOW_PATH = PROJECT_ROOT / "scripts" / "ch07" / "ci_minimal.yml"
SETUP_UV_REF = "astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b"


def _load_workflow() -> dict[str, Any]:
    """YAMLのonキーを文字列として保ったまま読み込む."""
    data = yaml.load(WORKFLOW_PATH.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    assert isinstance(data, dict)
    return data


def _steps(workflow: dict[str, Any]) -> list[dict[str, Any]]:
    """testジョブのstepsを返す."""
    steps = workflow["jobs"]["test"]["steps"]
    assert isinstance(steps, list)
    return steps


def test_workflow_has_safe_triggers_and_permissions() -> None:
    workflow = _load_workflow()

    assert workflow["on"] == ["push", "pull_request"]
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["jobs"]["test"]["runs-on"] == "ubuntu-latest"


def test_workflow_pins_current_actions() -> None:
    steps = _steps(_load_workflow())
    uses = [step["uses"] for step in steps if "uses" in step]

    assert uses == [
        "actions/checkout@v6",
        "actions/setup-python@v6",
        SETUP_UV_REF,
    ]
    assert all("@v7" not in action for action in uses)


def test_workflow_uses_locked_uv_environment() -> None:
    steps = _steps(_load_workflow())
    commands = [step["run"] for step in steps if "run" in step]

    assert commands == ["uv sync --frozen", "uv run pytest tests/"]
    assert all("requirements.txt" not in command for command in commands)


def test_workflow_configures_python_and_uv_cache() -> None:
    steps = _steps(_load_workflow())
    setup_python = next(
        step for step in steps if step.get("uses") == "actions/setup-python@v6"
    )
    setup_uv = next(step for step in steps if step.get("uses") == SETUP_UV_REF)

    assert setup_python["with"]["python-version"] == "3.12"
    assert setup_uv["with"]["enable-cache"] == "true"
