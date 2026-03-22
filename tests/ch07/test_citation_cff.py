"""CITATION.cff テンプレートのバリデーションテスト。

cffconvert を使って CITATION.cff の形式が正しいことを検証する。
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

# テンプレートファイルのパス
TEMPLATE_PATH = Path(__file__).resolve().parent.parent.parent / "scripts" / "ch07" / "CITATION.cff.template"


def test_template_exists() -> None:
    """テンプレートファイルが存在する。"""
    assert TEMPLATE_PATH.exists(), f"テンプレートが見つからない: {TEMPLATE_PATH}"


def test_template_is_valid_yaml() -> None:
    """テンプレートが有効な YAML として読み込める。"""
    content = TEMPLATE_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    assert isinstance(data, dict), "YAMLのトップレベルが辞書でない"


def test_template_has_required_fields() -> None:
    """CFF 1.2.0 の必須フィールドが含まれている。"""
    content = TEMPLATE_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(content)

    required_fields = ["cff-version", "message", "title", "authors"]
    for field in required_fields:
        assert field in data, f"必須フィールドが不足: {field}"


def test_template_cff_version() -> None:
    """cff-version が 1.2.0 である。"""
    content = TEMPLATE_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    assert data["cff-version"] == "1.2.0", f"cff-version が 1.2.0 でない: {data['cff-version']}"


def test_template_authors_structure() -> None:
    """authors フィールドがリスト形式で、各要素に必須キーがある。"""
    content = TEMPLATE_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(content)

    authors = data["authors"]
    assert isinstance(authors, list), "authors がリストでない"
    assert len(authors) > 0, "authors が空"

    for author in authors:
        assert "family-names" in author or "name" in author, (
            "著者に family-names または name が必要"
        )


def _cffconvert_available() -> bool:
    """cffconvert コマンドが利用可能か確認する。"""
    try:
        result = subprocess.run(
            ["cffconvert", "--version"],
            capture_output=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


@pytest.mark.skipif(
    not _cffconvert_available(),
    reason="cffconvert がインストールされていない",
)
def test_template_validates_with_cffconvert() -> None:
    """cffconvert によるバリデーションが通る。"""
    result = subprocess.run(
        ["cffconvert", "--validate", "-i", str(TEMPLATE_PATH)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"cffconvert バリデーション失敗: {result.stderr}"
