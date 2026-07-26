"""第8章で共有するpytestフィクスチャ."""

from pathlib import Path

import pytest


@pytest.fixture()
def test_data_dir() -> Path:
    """テストデータディレクトリのパスを返す."""
    return Path(__file__).parent / "data"


@pytest.fixture()
def sample_fasta(test_data_dir: Path) -> Path:
    """テスト用FASTAファイルのパスを返す."""
    return test_data_dir / "sample.fasta"
