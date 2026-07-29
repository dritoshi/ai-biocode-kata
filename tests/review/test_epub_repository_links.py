import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FILTER_PATH = PROJECT_ROOT / "build" / "fix-repository-links.lua"
COMMIT_SHA = "a" * 40
REPOSITORY_URL = "https://github.com/dritoshi/ai-biocode-kata"


def _pandoc() -> str:
    executable = shutil.which("pandoc")
    if executable is None:
        pytest.skip("pandoc is required to exercise the EPUB Lua filter")
    return executable


def _run_filter(markdown: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            _pandoc(),
            "-f",
            "markdown",
            "-t",
            "json",
            f"--lua-filter={FILTER_PATH}",
        ],
        input=markdown,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def _link_targets(node: Any) -> list[str]:
    targets: list[str] = []
    if isinstance(node, dict):
        if node.get("t") == "Link":
            targets.append(node["c"][2][0])
        for value in node.values():
            targets.extend(_link_targets(value))
    elif isinstance(node, list):
        for value in node:
            targets.extend(_link_targets(value))
    return targets


def _filter_env() -> dict[str, str]:
    env = os.environ.copy()
    env["EPUB_REPOSITORY_URL"] = REPOSITORY_URL
    env["EPUB_SOURCE_COMMIT"] = COMMIT_SHA
    return env


def test_rewrites_files_directories_and_suffixes() -> None:
    markdown = """
[script](../scripts/ch01/gc_content.py)
[test](../tests/ch01/test_gc_content.py#L10)
[directory](../scripts/ch15/version_pinning/uv/)
[mutable](https://github.com/dritoshi/ai-biocode-kata/blob/main/scripts/ch04/coordinate_convert.py)
[mutable-directory](https://github.com/dritoshi/ai-biocode-kata/tree/main/scripts/ch15/version_pinning/uv)
[tagged](https://github.com/dritoshi/ai-biocode-kata/blob/v0.4.0/scripts/ch04/coordinate_convert.py)
[chapter](./01_design.md)
[external](https://example.com/scripts/example.py)
"""

    result = _run_filter(markdown, _filter_env())

    assert result.returncode == 0, result.stderr
    targets = _link_targets(json.loads(result.stdout))
    assert targets == [
        f"{REPOSITORY_URL}/blob/{COMMIT_SHA}/scripts/ch01/gc_content.py",
        f"{REPOSITORY_URL}/blob/{COMMIT_SHA}/tests/ch01/test_gc_content.py#L10",
        f"{REPOSITORY_URL}/tree/{COMMIT_SHA}/scripts/ch15/version_pinning/uv",
        f"{REPOSITORY_URL}/blob/{COMMIT_SHA}/scripts/ch04/coordinate_convert.py",
        f"{REPOSITORY_URL}/tree/{COMMIT_SHA}/scripts/ch15/version_pinning/uv",
        f"{REPOSITORY_URL}/blob/v0.4.0/scripts/ch04/coordinate_convert.py",
        "./01_design.md",
        "https://example.com/scripts/example.py",
    ]


@pytest.mark.parametrize(
    ("variable", "value", "message"),
    [
        ("EPUB_REPOSITORY_URL", "", "EPUB_REPOSITORY_URL is required"),
        (
            "EPUB_REPOSITORY_URL",
            "https://example.com/owner/repository",
            "must be a GitHub repository URL",
        ),
        ("EPUB_SOURCE_COMMIT", "main", "must be a 40-character lowercase"),
    ],
)
def test_rejects_invalid_permalink_configuration(
    variable: str,
    value: str,
    message: str,
) -> None:
    env = _filter_env()
    env[variable] = value

    result = _run_filter("[script](../scripts/ch01/gc_content.py)", env)

    assert result.returncode != 0
    assert message in result.stderr
