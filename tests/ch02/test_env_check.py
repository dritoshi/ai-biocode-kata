"""環境チェック関数のテスト."""

import os
from unittest.mock import patch

from scripts.ch02.env_check import (
    check_command_available,
    check_required_commands,
    find_broken_path_entries,
    get_command_path,
    get_path_entries,
)


class TestCheckCommandAvailable:
    """check_command_available() のテスト."""

    def test_python3_exists(self) -> None:
        # python3 はテスト環境に必ず存在する
        assert check_command_available("python3") is True

    def test_nonexistent_command(self) -> None:
        assert check_command_available("this_command_does_not_exist_xyz") is False


class TestGetCommandPath:
    """get_command_path() のテスト."""

    def test_python3_path(self) -> None:
        path = get_command_path("python3")
        assert path is not None
        assert "python3" in path

    def test_nonexistent_returns_none(self) -> None:
        assert get_command_path("this_command_does_not_exist_xyz") is None


class TestGetPathEntries:
    """get_path_entries() のテスト."""

    def test_returns_list(self) -> None:
        entries = get_path_entries()
        assert isinstance(entries, list)
        assert len(entries) > 0

    def test_entries_are_strings(self) -> None:
        entries = get_path_entries()
        for entry in entries:
            assert isinstance(entry, str)

    def test_with_custom_path(self) -> None:
        with patch.dict(os.environ, {"PATH": "/usr/bin:/usr/local/bin"}):
            entries = get_path_entries()
            assert "/usr/bin" in entries
            assert "/usr/local/bin" in entries

    def test_empty_path(self) -> None:
        with patch.dict(os.environ, {"PATH": ""}):
            entries = get_path_entries()
            assert entries == []


class TestFindBrokenPathEntries:
    """find_broken_path_entries() のテスト."""

    def test_with_broken_entry(self) -> None:
        fake_path = "/nonexistent/directory/abc123:/usr/bin"
        with patch.dict(os.environ, {"PATH": fake_path}):
            broken = find_broken_path_entries()
            assert "/nonexistent/directory/abc123" in broken

    def test_with_valid_entries(self) -> None:
        with patch.dict(os.environ, {"PATH": "/usr/bin:/bin"}):
            broken = find_broken_path_entries()
            assert broken == []


class TestCheckRequiredCommands:
    """check_required_commands() のテスト."""

    def test_mixed_commands(self) -> None:
        result = check_required_commands(
            ["python3", "this_command_does_not_exist_xyz"]
        )
        assert result["python3"] is True
        assert result["this_command_does_not_exist_xyz"] is False

    def test_empty_list(self) -> None:
        result = check_required_commands([])
        assert result == {}
