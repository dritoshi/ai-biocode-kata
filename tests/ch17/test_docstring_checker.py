"""docstring_checkerモジュールのテスト."""

import pytest

from scripts.ch17.docstring_checker import (
    CoverageResult,
    ValidationResult,
    check_coverage,
    check_numpy_style,
)

# --- テスト用Pythonソースコード ---

FULLY_DOCUMENTED = '''\
def greet(name: str) -> str:
    """名前を受け取って挨拶文を返す."""
    return f"Hello, {name}"


class Analyzer:
    """データ解析クラス."""

    def run(self) -> None:
        """解析を実行する."""
        pass
'''

PARTIALLY_DOCUMENTED = '''\
def greet(name: str) -> str:
    """名前を受け取って挨拶文を返す."""
    return f"Hello, {name}"


def process(data: list) -> list:
    return [x * 2 for x in data]


class Analyzer:
    """データ解析クラス."""
    pass
'''

NO_DOCSTRINGS = '''\
def greet(name: str) -> str:
    return f"Hello, {name}"


def process(data: list) -> list:
    return [x * 2 for x in data]
'''

PRIVATE_ONLY = '''\
def _helper():
    pass


def _internal_process():
    pass
'''

EMPTY_SOURCE = ""

NUMPY_DOCSTRING_GOOD = '''\
短い要約。

Parameters
----------
x : int
    入力値

Returns
-------
int
    2倍の値
'''

NUMPY_DOCSTRING_NO_UNDERLINE = '''\
短い要約。

Parameters
x : int
    入力値
'''

NUMPY_DOCSTRING_NONE = '''\
短い要約。これはdocstringだが、セクションがない。
'''


# --- check_coverage ---

class TestCheckCoverage:
    """docstringカバレッジの計測テスト."""

    def test_fully_documented(self) -> None:
        result = check_coverage(FULLY_DOCUMENTED)
        assert result.total == 2  # greet + Analyzer（公開のみ）
        assert result.documented == 2
        assert result.missing == []
        assert result.ratio == 1.0

    def test_partially_documented(self) -> None:
        result = check_coverage(PARTIALLY_DOCUMENTED)
        assert result.total == 3  # greet + process + Analyzer
        assert result.documented == 2
        assert result.missing == ["process"]
        assert 0.6 < result.ratio < 0.7

    def test_no_docstrings(self) -> None:
        result = check_coverage(NO_DOCSTRINGS)
        assert result.total == 2
        assert result.documented == 0
        assert result.ratio == 0.0
        assert "greet" in result.missing
        assert "process" in result.missing

    def test_private_skipped(self) -> None:
        """プライベート関数はチェック対象外."""
        result = check_coverage(PRIVATE_ONLY)
        assert result.total == 0
        assert result.ratio == 1.0

    def test_empty_source(self) -> None:
        result = check_coverage(EMPTY_SOURCE)
        assert result.total == 0
        assert result.ratio == 1.0


# --- check_numpy_style ---

class TestCheckNumpyStyle:
    """NumPy style docstring検証テスト."""

    def test_good_numpy_style(self) -> None:
        ok, issues = check_numpy_style(NUMPY_DOCSTRING_GOOD)
        assert ok is True
        assert issues == []

    def test_missing_underline(self) -> None:
        ok, issues = check_numpy_style(NUMPY_DOCSTRING_NO_UNDERLINE)
        assert ok is False
        assert any("アンダーライン" in i for i in issues)

    def test_no_sections(self) -> None:
        ok, issues = check_numpy_style(NUMPY_DOCSTRING_NONE)
        assert ok is False
        assert any("見つからない" in i for i in issues)


# --- CoverageResult ---

class TestCoverageResult:
    """CoverageResultのプロパティテスト."""

    def test_ratio_calculation(self) -> None:
        r = CoverageResult(total=10, documented=7, missing=["a", "b", "c"])
        assert r.ratio == 0.7

    def test_ratio_zero_total(self) -> None:
        """対象が0件ならカバレッジ100%."""
        r = CoverageResult(total=0, documented=0, missing=[])
        assert r.ratio == 1.0

    def test_ratio_zero_documented(self) -> None:
        r = CoverageResult(total=5, documented=0, missing=["a", "b", "c", "d", "e"])
        assert r.ratio == 0.0
