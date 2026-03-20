"""モジュールシステムのデモ: sys.pathの確認と共有ライブラリの依存確認."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def show_sys_path() -> list[str]:
    """現在のsys.pathを返す.

    Returns
    -------
    list[str]
        Pythonがモジュールを検索するディレクトリのリスト
    """
    return list(sys.path)


def find_site_packages() -> Path | None:
    """現在の環境のsite-packagesディレクトリを返す.

    Returns
    -------
    Path | None
        site-packagesのパス。見つからなければNone
    """
    for p in sys.path:
        path = Path(p)
        if path.name == "site-packages" and path.is_dir():
            return path
    return None


def check_shared_libs(binary_path: str) -> list[str] | None:
    """実行ファイルの共有ライブラリ依存を表示する（Linux: ldd, macOS: otool -L）.

    Parameters
    ----------
    binary_path : str
        確認したい実行ファイルのパス

    Returns
    -------
    list[str] | None
        依存ライブラリのリスト。ツールが見つからなければNone
    """
    path = Path(binary_path)
    if not path.exists():
        return None

    if sys.platform == "linux":
        tool = "ldd"
    elif sys.platform == "darwin":
        tool = "otool"
    else:
        return None

    if shutil.which(tool) is None:
        return None

    try:
        if sys.platform == "linux":
            result = subprocess.run(
                ["ldd", str(path)],
                capture_output=True,
                text=True,
                timeout=10,
            )
        else:
            result = subprocess.run(
                ["otool", "-L", str(path)],
                capture_output=True,
                text=True,
                timeout=10,
            )

        if result.returncode != 0:
            return None

        lines = result.stdout.strip().splitlines()
        # 1行目はファイル名（otool）なので除外
        libs = [line.strip() for line in lines[1:] if line.strip()]
        return libs

    except (subprocess.TimeoutExpired, OSError):
        return None
