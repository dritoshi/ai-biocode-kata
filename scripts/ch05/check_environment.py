"""開発環境の状態を確認するユーティリティ.

Pythonバージョン、仮想環境の有無、主要パッケージのインストール状況を
プログラムから確認する方法を示す。
"""

import importlib.metadata
import logging
import sys
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EnvironmentInfo:
    """Python実行環境の情報."""

    python_version: str
    platform: str
    prefix: str
    base_prefix: str
    in_virtualenv: bool


def get_environment_info() -> EnvironmentInfo:
    """現在のPython実行環境の情報を取得する.

    Returns
    -------
    EnvironmentInfo
        Pythonバージョン、プラットフォーム、仮想環境の状態を含む情報
    """
    return EnvironmentInfo(
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        platform=sys.platform,
        prefix=sys.prefix,
        base_prefix=sys.base_prefix,
        in_virtualenv=sys.prefix != sys.base_prefix,
    )


def check_package_installed(package_name: str) -> str | None:
    """指定したパッケージがインストールされているか確認する.

    Parameters
    ----------
    package_name : str
        確認するパッケージ名

    Returns
    -------
    str | None
        インストールされていればバージョン文字列、なければ None
    """
    try:
        version = importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        logger.debug("パッケージ '%s' が見つからない", package_name)
        return None
    else:
        return version


def check_packages(package_names: list[str]) -> dict[str, str | None]:
    """複数パッケージのインストール状況を一括確認する.

    Parameters
    ----------
    package_names : list[str]
        確認するパッケージ名のリスト

    Returns
    -------
    dict[str, str | None]
        パッケージ名をキー、バージョン文字列（未インストールなら None）を値とする辞書
    """
    return {name: check_package_installed(name) for name in package_names}


def format_environment_report(
    env_info: EnvironmentInfo,
    packages: dict[str, str | None],
) -> str:
    """環境情報とパッケージ状況を人間可読な文字列にフォーマットする.

    Parameters
    ----------
    env_info : EnvironmentInfo
        Python実行環境の情報
    packages : dict[str, str | None]
        パッケージ名とバージョンの辞書

    Returns
    -------
    str
        フォーマット済みのレポート文字列
    """
    lines: list[str] = [
        "=== Python環境レポート ===",
        f"Pythonバージョン: {env_info.python_version}",
        f"プラットフォーム: {env_info.platform}",
        f"仮想環境: {'有効' if env_info.in_virtualenv else '無効'}",
        f"  prefix:      {env_info.prefix}",
        f"  base_prefix: {env_info.base_prefix}",
        "",
        "=== パッケージ状況 ===",
    ]
    for name, version in packages.items():
        status = version if version is not None else "未インストール"
        lines.append(f"  {name}: {status}")

    return "\n".join(lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # バイオインフォマティクスでよく使うパッケージ
    target_packages = [
        "numpy",
        "pandas",
        "biopython",
        "scikit-learn",
        "matplotlib",
    ]

    env_info = get_environment_info()
    packages = check_packages(target_packages)
    report = format_environment_report(env_info, packages)
    logger.info("\n%s", report)
