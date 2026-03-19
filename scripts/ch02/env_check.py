"""環境変数とPATHの検証ユーティリティ — 環境チェックのデモ."""

import os
import shutil
from pathlib import Path


def check_command_available(command: str) -> bool:
    """コマンドがPATH上に存在するか確認する.

    シェルの ``which command`` に相当する。

    Parameters
    ----------
    command : str
        確認するコマンド名

    Returns
    -------
    bool
        コマンドが見つかれば True
    """
    return shutil.which(command) is not None


def get_command_path(command: str) -> str | None:
    """コマンドのフルパスを取得する.

    シェルの ``which command`` の出力に相当する。

    Parameters
    ----------
    command : str
        確認するコマンド名

    Returns
    -------
    str | None
        コマンドのフルパス。見つからなければ None
    """
    return shutil.which(command)


def get_path_entries() -> list[str]:
    """PATH環境変数をリストとして取得する.

    シェルの ``echo $PATH | tr ':' '\\n'`` に相当する。

    Returns
    -------
    list[str]
        PATHに含まれるディレクトリのリスト
    """
    path_var = os.environ.get("PATH", "")
    return [entry for entry in path_var.split(os.pathsep) if entry]


def find_broken_path_entries() -> list[str]:
    """PATH内の存在しないディレクトリを検出する.

    PATHに古い環境のディレクトリが残っていると、
    コマンドの検索が遅くなったり予期しない動作を引き起こしたりする。

    Returns
    -------
    list[str]
        存在しないディレクトリのリスト
    """
    broken: list[str] = []
    for entry in get_path_entries():
        if not Path(entry).is_dir():
            broken.append(entry)
    return broken


def check_required_commands(commands: list[str]) -> dict[str, bool]:
    """複数のコマンドの存在を一括確認する.

    Parameters
    ----------
    commands : list[str]
        確認するコマンド名のリスト

    Returns
    -------
    dict[str, bool]
        コマンド名 → 存在するか のマッピング
    """
    return {cmd: check_command_available(cmd) for cmd in commands}
