"""validate_dockerfileモジュールのテスト."""

import pytest

from scripts.ch13.validate_dockerfile import (
    ValidationResult,
    check_apt_cache_cleanup,
    check_base_image_tag,
    check_layer_cache_order,
    check_run_consolidation,
    validate,
)

# --- テスト用Dockerfileテキスト ---

GOOD_DOCKERFILE = """\
FROM condaforge/mambaforge:24.3.0-0

RUN apt-get update && \\
    apt-get install -y --no-install-recommends \\
        procps \\
        curl \\
    && rm -rf /var/lib/apt/lists/*

COPY environment.yml /tmp/environment.yml

RUN mamba env create -f /tmp/environment.yml && \\
    mamba clean --all --yes

ENV PATH="/opt/conda/envs/rnaseq/bin:$PATH"

WORKDIR /workspace
COPY . /workspace

ENTRYPOINT ["snakemake"]
"""

BAD_TAG_DOCKERFILE = """\
FROM python:latest

RUN pip install numpy pandas

COPY . /app
WORKDIR /app
"""

NO_TAG_DOCKERFILE = """\
FROM python

RUN pip install numpy pandas

COPY . /app
WORKDIR /app
"""

DIGEST_DOCKERFILE = """\
FROM python:3.11-slim@sha256:abc123def456

RUN pip install numpy pandas

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app
WORKDIR /app
"""

BAD_ORDER_DOCKERFILE = """\
FROM condaforge/mambaforge:24.3.0-0

COPY . /workspace

RUN mamba install -y numpy pandas

WORKDIR /workspace
"""

BAD_APT_DOCKERFILE = """\
FROM ubuntu:22.04

RUN apt-get update && \\
    apt-get install -y python3 python3-pip

COPY . /app
WORKDIR /app
"""

SPLIT_APT_DOCKERFILE = """\
FROM ubuntu:22.04

RUN apt-get update
RUN apt-get install -y python3 python3-pip

COPY . /app
WORKDIR /app
"""

MULTISTAGE_DOCKERFILE = """\
FROM condaforge/mambaforge:24.3.0-0 AS builder

COPY environment.yml /tmp/environment.yml
RUN mamba env create -f /tmp/environment.yml

FROM debian:bookworm-slim AS runtime

RUN apt-get update && \\
    apt-get install -y --no-install-recommends libgomp1 \\
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/conda/envs/rnaseq /opt/env
ENV PATH="/opt/env/bin:$PATH"

COPY . /workspace
WORKDIR /workspace
"""


# --- check_base_image_tag ---

class TestCheckBaseImageTag:
    """ベースイメージタグ固定の検証テスト."""

    def test_tagged_image(self) -> None:
        ok, problematic, has_digest = check_base_image_tag(GOOD_DOCKERFILE)
        assert ok is True
        assert problematic == []

    def test_latest_tag(self) -> None:
        ok, problematic, has_digest = check_base_image_tag(BAD_TAG_DOCKERFILE)
        assert ok is False
        assert "python:latest" in problematic

    def test_no_tag(self) -> None:
        ok, problematic, has_digest = check_base_image_tag(NO_TAG_DOCKERFILE)
        assert ok is False
        assert "python" in problematic

    def test_digest_image(self) -> None:
        ok, problematic, has_digest = check_base_image_tag(DIGEST_DOCKERFILE)
        assert ok is True
        assert has_digest is True

    def test_multistage_all_tagged(self) -> None:
        ok, problematic, has_digest = check_base_image_tag(MULTISTAGE_DOCKERFILE)
        assert ok is True
        assert problematic == []


# --- check_layer_cache_order ---

class TestCheckLayerCacheOrder:
    """レイヤーキャッシュ順序の検証テスト."""

    def test_good_order(self) -> None:
        ok, issues = check_layer_cache_order(GOOD_DOCKERFILE)
        assert ok is True
        assert issues == []

    def test_bad_order(self) -> None:
        ok, issues = check_layer_cache_order(BAD_ORDER_DOCKERFILE)
        assert ok is False
        assert len(issues) >= 1
        assert "COPY . ." in issues[0]

    def test_multistage_resets(self) -> None:
        """マルチステージビルドではFROMごとにリセットされる."""
        ok, issues = check_layer_cache_order(MULTISTAGE_DOCKERFILE)
        assert ok is True


# --- check_run_consolidation ---

class TestCheckRunConsolidation:
    """RUN命令統合の検証テスト."""

    def test_consolidated(self) -> None:
        ok, issues = check_run_consolidation(GOOD_DOCKERFILE)
        assert ok is True
        assert issues == []

    def test_split_apt(self) -> None:
        ok, issues = check_run_consolidation(SPLIT_APT_DOCKERFILE)
        assert ok is False
        assert len(issues) >= 1
        assert "apt-get update" in issues[0]


# --- check_apt_cache_cleanup ---

class TestCheckAptCacheCleanup:
    """apt-getキャッシュ削除の検証テスト."""

    def test_cleaned(self) -> None:
        ok, issues = check_apt_cache_cleanup(GOOD_DOCKERFILE)
        assert ok is True
        assert issues == []

    def test_not_cleaned(self) -> None:
        ok, issues = check_apt_cache_cleanup(BAD_APT_DOCKERFILE)
        assert ok is False
        assert len(issues) >= 1
        assert "キャッシュ削除" in issues[0]

    def test_no_apt(self) -> None:
        """apt-getを使っていなければチェック対象外."""
        dockerfile = """\
FROM python:3.11-slim
RUN pip install numpy
"""
        ok, issues = check_apt_cache_cleanup(dockerfile)
        assert ok is True
        assert issues == []


# --- validate ---

class TestValidate:
    """一括検証のテスト."""

    def test_good_dockerfile(self) -> None:
        result = validate(GOOD_DOCKERFILE)
        assert result.ok is True
        assert len(result.passed) >= 3
        assert result.warnings == []

    def test_bad_tag_warnings(self) -> None:
        result = validate(BAD_TAG_DOCKERFILE)
        assert result.ok is False
        assert any("タグが未固定" in w for w in result.warnings)

    def test_bad_order_warnings(self) -> None:
        result = validate(BAD_ORDER_DOCKERFILE)
        assert result.ok is False
        assert any("COPY . ." in w for w in result.warnings)

    def test_bad_apt_warnings(self) -> None:
        result = validate(BAD_APT_DOCKERFILE)
        assert result.ok is False
        assert any("キャッシュ削除" in w for w in result.warnings)

    def test_digest_info(self) -> None:
        result = validate(DIGEST_DOCKERFILE)
        assert len(result.info) >= 1
        assert any("ダイジェスト" in i for i in result.info)

    def test_split_apt_warnings(self) -> None:
        result = validate(SPLIT_APT_DOCKERFILE)
        assert result.ok is False
        assert any("apt-get update" in w for w in result.warnings)


# --- ValidationResult ---

class TestValidationResult:
    """ValidationResultのプロパティテスト."""

    def test_ok_when_no_warnings(self) -> None:
        r = ValidationResult(passed=["check1"], warnings=[], info=["info1"])
        assert r.ok is True

    def test_not_ok_when_warnings(self) -> None:
        r = ValidationResult(passed=[], warnings=["warn1"], info=[])
        assert r.ok is False

    def test_info_does_not_affect_ok(self) -> None:
        """infoフィールドはokに影響しない."""
        r = ValidationResult(passed=[], warnings=[], info=["info1", "info2"])
        assert r.ok is True
