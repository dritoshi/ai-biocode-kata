"""module_demoモジュールとmylibパッケージのテスト."""

import sys

from scripts.ch05.module_demo import (
    check_shared_libs,
    find_site_packages,
    show_sys_path,
)
from scripts.ch05.mylib import gc_content, reverse_complement, validate_sequence
from scripts.ch05.mylib.core import gc_content as gc_content_direct
from scripts.ch05.mylib.utils import validate_sequence as validate_direct


# --- show_sys_path ---


class TestShowSysPath:
    """sys.path表示のテスト."""

    def test_returns_list(self) -> None:
        result = show_sys_path()
        assert isinstance(result, list)

    def test_contains_strings(self) -> None:
        result = show_sys_path()
        assert all(isinstance(p, str) for p in result)

    def test_matches_sys_path(self) -> None:
        result = show_sys_path()
        assert result == sys.path


# --- find_site_packages ---


class TestFindSitePackages:
    """site-packages検索のテスト."""

    def test_returns_path_or_none(self) -> None:
        result = find_site_packages()
        assert result is None or hasattr(result, "name")

    def test_if_found_name_is_site_packages(self) -> None:
        result = find_site_packages()
        if result is not None:
            assert result.name == "site-packages"


# --- check_shared_libs ---


class TestCheckSharedLibs:
    """共有ライブラリ依存確認のテスト."""

    def test_nonexistent_binary(self) -> None:
        result = check_shared_libs("/nonexistent/binary")
        assert result is None

    def test_python_binary(self) -> None:
        """Python実行ファイル自体の依存を確認."""
        result = check_shared_libs(sys.executable)
        # ツールがなければNone、あればリスト
        if result is not None:
            assert isinstance(result, list)


# --- mylib パッケージのimportテスト ---


class TestMylibImport:
    """mylibパッケージのimportとモジュール構造のテスト."""

    def test_import_from_package(self) -> None:
        """パッケージ経由のimport."""
        assert callable(gc_content)
        assert callable(reverse_complement)
        assert callable(validate_sequence)

    def test_import_from_module(self) -> None:
        """モジュール直接のimport."""
        assert gc_content_direct is gc_content
        assert validate_direct is validate_sequence


# --- mylib.core ---


class TestGcContent:
    """GC含量計算のテスト."""

    def test_all_gc(self) -> None:
        assert gc_content("GGCC") == 1.0

    def test_all_at(self) -> None:
        assert gc_content("AATT") == 0.0

    def test_mixed(self) -> None:
        assert gc_content("ATGC") == 0.5

    def test_empty(self) -> None:
        assert gc_content("") == 0.0

    def test_case_insensitive(self) -> None:
        assert gc_content("atgc") == 0.5


class TestReverseComplement:
    """逆相補鎖のテスト."""

    def test_simple(self) -> None:
        assert reverse_complement("ATGC") == "GCAT"

    def test_palindrome(self) -> None:
        assert reverse_complement("AATT") == "AATT"

    def test_unknown_base(self) -> None:
        assert reverse_complement("ATXG") == "CNAT"


# --- mylib.utils ---


class TestValidateSequence:
    """配列検証のテスト."""

    def test_valid(self) -> None:
        ok, invalid = validate_sequence("ATGCATGC")
        assert ok is True
        assert invalid == []

    def test_invalid(self) -> None:
        ok, invalid = validate_sequence("ATXGCY")
        assert ok is False
        assert "X" in invalid
        assert "Y" in invalid

    def test_empty(self) -> None:
        ok, invalid = validate_sequence("")
        assert ok is True
        assert invalid == []

    def test_lowercase(self) -> None:
        ok, invalid = validate_sequence("atgc")
        assert ok is True
