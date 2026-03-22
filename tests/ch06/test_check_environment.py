"""check_environment モジュールのテスト."""

from scripts.ch06.check_environment import (
    EnvironmentInfo,
    check_package_installed,
    check_packages,
    format_environment_report,
    get_environment_info,
)


class TestGetEnvironmentInfo:
    """get_environment_info のテスト."""

    def test_returns_environment_info(self) -> None:
        info = get_environment_info()
        assert isinstance(info, EnvironmentInfo)

    def test_python_version_format(self) -> None:
        info = get_environment_info()
        parts = info.python_version.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

    def test_platform_is_nonempty(self) -> None:
        info = get_environment_info()
        assert len(info.platform) > 0

    def test_in_virtualenv_is_bool(self) -> None:
        info = get_environment_info()
        assert isinstance(info.in_virtualenv, bool)


class TestCheckPackageInstalled:
    """check_package_installed のテスト."""

    def test_installed_package_returns_version(self) -> None:
        # pip は必ずインストールされている
        version = check_package_installed("pip")
        assert version is not None
        assert len(version) > 0

    def test_nonexistent_package_returns_none(self) -> None:
        version = check_package_installed("this-package-does-not-exist-xyz-123")
        assert version is None


class TestCheckPackages:
    """check_packages のテスト."""

    def test_returns_dict_for_all_packages(self) -> None:
        names = ["pip", "nonexistent-pkg-xyz"]
        result = check_packages(names)
        assert set(result.keys()) == set(names)

    def test_empty_list_returns_empty_dict(self) -> None:
        result = check_packages([])
        assert result == {}


class TestFormatEnvironmentReport:
    """format_environment_report のテスト."""

    def test_contains_python_version(self) -> None:
        env_info = EnvironmentInfo(
            python_version="3.11.9",
            platform="linux",
            prefix="/home/user/.venv",
            base_prefix="/usr",
            in_virtualenv=True,
        )
        packages: dict[str, str | None] = {"numpy": "1.26.4", "biopython": None}
        report = format_environment_report(env_info, packages)
        assert "3.11.9" in report
        assert "有効" in report

    def test_shows_uninstalled_packages(self) -> None:
        env_info = EnvironmentInfo(
            python_version="3.11.9",
            platform="linux",
            prefix="/usr",
            base_prefix="/usr",
            in_virtualenv=False,
        )
        packages: dict[str, str | None] = {"somepkg": None}
        report = format_environment_report(env_info, packages)
        assert "未インストール" in report
        assert "無効" in report

    def test_shows_installed_version(self) -> None:
        env_info = EnvironmentInfo(
            python_version="3.12.0",
            platform="darwin",
            prefix="/usr",
            base_prefix="/usr",
            in_virtualenv=False,
        )
        packages: dict[str, str | None] = {"numpy": "2.0.1"}
        report = format_environment_report(env_info, packages)
        assert "2.0.1" in report
