"""テキスト処理のPython実装 — シェルコマンドとの対比デモ."""

import re
from pathlib import Path


def grep_lines(file_path: Path, pattern: str) -> list[str]:
    """ファイルからパターンに一致する行を抽出する.

    シェルの ``grep PATTERN file`` に相当する。

    Parameters
    ----------
    file_path : Path
        検索対象のファイルパス
    pattern : str
        正規表現パターン

    Returns
    -------
    list[str]
        パターンに一致した行のリスト（改行なし）
    """
    compiled = re.compile(pattern)
    matched: list[str] = []
    with file_path.open() as f:
        for line in f:
            if compiled.search(line):
                matched.append(line.rstrip("\n"))
    return matched


def count_fasta_records(file_path: Path) -> int:
    """FASTAファイルのレコード数をカウントする.

    シェルの ``grep -c "^>" file.fasta`` に相当する。

    Parameters
    ----------
    file_path : Path
        FASTAファイルのパス

    Returns
    -------
    int
        レコード数（">" で始まる行の数）
    """
    count = 0
    with file_path.open() as f:
        for line in f:
            if line.startswith(">"):
                count += 1
    return count


def extract_column(
    file_path: Path,
    column: int,
    delimiter: str = "\t",
    skip_header: bool = False,
) -> list[str]:
    """ファイルから指定列を抽出する.

    シェルの ``cut -f N -d DELIM file`` に相当する。

    Parameters
    ----------
    file_path : Path
        対象ファイルのパス
    column : int
        抽出する列のインデックス（0始まり）
    delimiter : str
        列の区切り文字（デフォルト: タブ）
    skip_header : bool
        先頭行をスキップするか

    Returns
    -------
    list[str]
        指定列の値のリスト
    """
    values: list[str] = []
    with file_path.open() as f:
        for i, line in enumerate(f):
            if skip_header and i == 0:
                continue
            fields = line.rstrip("\n").split(delimiter)
            if column < len(fields):
                values.append(fields[column])
    return values


def sort_unique(items: list[str]) -> list[str]:
    """リストをソートして重複を除去する.

    シェルの ``sort | uniq`` に相当する。

    Parameters
    ----------
    items : list[str]
        文字列のリスト

    Returns
    -------
    list[str]
        ソート済み・重複除去済みのリスト
    """
    return sorted(set(items))


def count_lines(file_path: Path) -> int:
    """ファイルの行数をカウントする.

    シェルの ``wc -l file`` に相当する。

    Parameters
    ----------
    file_path : Path
        対象ファイルのパス

    Returns
    -------
    int
        行数
    """
    count = 0
    with file_path.open() as f:
        for _line in f:
            count += 1
    return count
