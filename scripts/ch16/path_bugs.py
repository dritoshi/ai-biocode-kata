"""パス関連バグの再現と修正デモ."""

from pathlib import Path


def read_config_relative_buggy(name: str) -> str:
    """設定ファイルを相対パスで読み込む（バグあり版）.

    カレントディレクトリ（cwd）依存のため、
    スクリプトの実行場所によって結果が変わる。

    Parameters
    ----------
    name : str
        設定ファイル名（例: "config.ini"）。

    Returns
    -------
    str
        ファイルの内容。
    """
    # バグ: cwd に依存するため、実行場所が変わると壊れる
    path = Path(name)
    return path.read_text()


def read_config_relative_fixed(name: str) -> str:
    """設定ファイルをスクリプト基準のパスで読み込む（修正版）.

    __file__ を基準にした相対パスでファイルを探すため、
    どのディレクトリから実行しても同じ結果になる。

    Parameters
    ----------
    name : str
        設定ファイル名（例: "config.ini"）。

    Returns
    -------
    str
        ファイルの内容。
    """
    # 修正: このスクリプトの場所を基準にパスを構築
    script_dir = Path(__file__).resolve().parent
    path = script_dir / name
    return path.read_text()


def resolve_data_path(path_str: str) -> Path:
    """ユーザ入力のパス文字列を安全に解決する.

    チルダ展開・絶対パス化・シンボリックリンク解決を行う。

    Parameters
    ----------
    path_str : str
        ユーザが入力したパス文字列（例: "~/data/input.csv"）。

    Returns
    -------
    Path
        解決済みの絶対パス。

    Raises
    ------
    FileNotFoundError
        解決後のパスが存在しない場合。
    """
    path = Path(path_str).expanduser().resolve()
    if not path.exists():
        msg = f"ファイルが見つかりません: {path}"
        raise FileNotFoundError(msg)
    return path
