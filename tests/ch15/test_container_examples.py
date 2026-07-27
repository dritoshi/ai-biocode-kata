"""第15章のコンテナとlockファイルの実例を検証する."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import tomllib
import yaml

from scripts.ch15.validate_dockerfile import validate_file

PROJECT_ROOT = Path(__file__).parents[2]
CHAPTER_DIR = PROJECT_ROOT / "scripts" / "ch15"
VERSION_PINNING_DIR = CHAPTER_DIR / "version_pinning"

DOCKERFILES = [
    CHAPTER_DIR / "Dockerfile.gpu",
    CHAPTER_DIR / "Dockerfile.conda-lock",
    VERSION_PINNING_DIR / "conda_lock" / "Dockerfile",
    VERSION_PINNING_DIR / "requirements" / "Dockerfile",
    VERSION_PINNING_DIR / "uv" / "Dockerfile",
]


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_samtools_rule_is_complete() -> None:
    snakefile = (CHAPTER_DIR / "samtools_sort.smk").read_text(encoding="utf-8")

    assert "rule samtools_sort:" in snakefile
    assert 'input:\n        "results/{sample}.bam"' in snakefile
    assert 'output:\n        "results/{sample}.sorted.bam"' in snakefile
    assert (
        '"docker://quay.io/biocontainers/'
        'samtools:1.20--h50ea8bc_0"'
    ) in snakefile
    assert '"samtools sort -o {output} {input}"' in snakefile
    assert "..." not in snakefile


def test_all_new_dockerfiles_pass_validator() -> None:
    for path in DOCKERFILES:
        result = validate_file(path)
        assert result.ok, f"{path}: {result.warnings}"


def test_gpu_dockerfile_uses_real_multiarch_digest() -> None:
    text = (CHAPTER_DIR / "Dockerfile.gpu").read_text(encoding="utf-8")

    assert (
        "nvidia/cuda:12.3.2-base-ubuntu22.04"
        "@sha256:8cecfe099315f73127d6d5cc43fce32c7ffff4ea0460eefac48f2b7d811ce857"
    ) in text
    assert 'CMD ["bash", "-lc", "echo CUDA_VERSION=${CUDA_VERSION}"]' in text
    assert "abc123" not in text


@pytest.mark.parametrize(
    "lock_path",
    [
        CHAPTER_DIR / "rnaseq.conda-lock.yml",
        VERSION_PINNING_DIR / "conda_lock" / "rnaseq.conda-lock.yml",
    ],
)
def test_conda_lock_covers_x86_and_arm(lock_path: Path) -> None:
    lock = _load_yaml(lock_path)

    assert lock["version"] == 1
    assert lock["metadata"]["platforms"] == ["linux-64", "linux-aarch64"]
    packages = lock["package"]
    biopython = [
        package for package in packages if package["name"] == "biopython"
    ]
    assert {package["platform"] for package in biopython} == {
        "linux-64",
        "linux-aarch64",
    }
    assert {package["version"] for package in biopython} == {"1.85"}
    assert all(
        re.fullmatch(r"[0-9a-f]{64}", item["hash"]["sha256"])
        for item in packages
    )


def test_version_pinning_methods_are_separate() -> None:
    conda_text = (
        VERSION_PINNING_DIR / "conda_lock" / "Dockerfile"
    ).read_text(encoding="utf-8")
    requirements_text = (
        VERSION_PINNING_DIR / "requirements" / "Dockerfile"
    ).read_text(encoding="utf-8")
    uv_text = (VERSION_PINNING_DIR / "uv" / "Dockerfile").read_text(
        encoding="utf-8"
    )

    assert "conda-lock install" in conda_text
    assert "requirements.txt" not in conda_text
    assert "uv sync" not in conda_text

    assert "--require-hashes" in requirements_text
    assert "conda-lock" not in requirements_text
    assert "uv sync" not in requirements_text

    assert "uv sync --frozen" in uv_text
    assert "conda-lock" not in uv_text
    assert "requirements.txt" not in uv_text


def test_requirements_are_pinned_with_hashes() -> None:
    text = (
        VERSION_PINNING_DIR / "requirements" / "requirements.txt"
    ).read_text(encoding="utf-8")

    assert "biopython==1.85" in text
    assert "numpy==2.5.1" in text
    assert text.count("--hash=sha256:") >= 2


def test_uv_lock_matches_project() -> None:
    directory = VERSION_PINNING_DIR / "uv"
    project = tomllib.loads(
        (directory / "pyproject.toml").read_text(encoding="utf-8")
    )
    lock_text = (directory / "uv.lock").read_text(encoding="utf-8")

    assert project["project"]["dependencies"] == ["biopython==1.85"]
    assert 'name = "biopython"' in lock_text
    assert 'version = "1.85"' in lock_text
    assert 'name = "numpy"' in lock_text
    assert 'version = "2.5.1"' in lock_text


CONTAINER_CASES = [
    pytest.param(
        CHAPTER_DIR,
        "Dockerfile.gpu",
        "ai-biocode-ch15-gpu",
        "CUDA_VERSION=12.3.2",
        id="gpu",
    ),
    pytest.param(
        CHAPTER_DIR,
        "Dockerfile.conda-lock",
        "ai-biocode-ch15-conda-lock",
        "1.85",
        id="conda-lock",
    ),
    pytest.param(
        VERSION_PINNING_DIR / "conda_lock",
        "Dockerfile",
        "ai-biocode-ch15-pin-conda",
        "1.85",
        id="pin-conda",
    ),
    pytest.param(
        VERSION_PINNING_DIR / "requirements",
        "Dockerfile",
        "ai-biocode-ch15-pin-requirements",
        "1.85",
        id="pin-requirements",
    ),
    pytest.param(
        VERSION_PINNING_DIR / "uv",
        "Dockerfile",
        "ai-biocode-ch15-pin-uv",
        "1.85",
        id="pin-uv",
    ),
]


@pytest.mark.skipif(
    os.environ.get("RUN_CONTAINER_BUILDS") != "1"
    or shutil.which("podman") is None,
    reason="Podman実ビルドはRUN_CONTAINER_BUILDS=1で実行する",
)
@pytest.mark.parametrize(
    ("context", "dockerfile", "tag", "expected"),
    CONTAINER_CASES,
)
def test_podman_build_and_run(
    context: Path,
    dockerfile: str,
    tag: str,
    expected: str,
) -> None:
    subprocess.run(
        [
            "podman",
            "build",
            "--file",
            dockerfile,
            "--tag",
            tag,
            ".",
        ],
        cwd=context,
        check=True,
        text=True,
    )
    completed = subprocess.run(
        ["podman", "run", "--rm", tag],
        check=True,
        capture_output=True,
        text=True,
    )

    assert expected in completed.stdout
