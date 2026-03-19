"""日本語環境のエンコーディング罠 — BOM付きCSV読み込みとNFCファイル名正規化.

Windows ExcelからエクスポートされたCSV（BOM付きUTF-8）の安全な読み込みと、
macOSのNFDファイル名正規化への対処を実演する。
"""

import csv
import unicodedata
from pathlib import Path


def read_csv_with_bom_handling(path: Path) -> list[dict[str, str]]:
    """BOM付きUTF-8に対応したCSV読み込み.

    Windows Excelが「UTF-8でCSV保存」すると、ファイル先頭に
    BOM（U+FEFF）が付与される。encoding="utf-8-sig" を使うことで
    BOMがあれば自動除去し、なければ通常のUTF-8として読み込む。

    Parameters
    ----------
    path : Path
        CSVファイルのパス

    Returns
    -------
    list[dict[str, str]]
        各行をヘッダ名→値の辞書にしたリスト
    """
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def normalize_filename_nfc(name: str) -> str:
    """ファイル名をNFC（合成形）に正規化する.

    macOS（APFS）は日本語ファイル名をNFD（分解形）で格納するため、
    濁点・半濁点が独立コードポイントに分離される。
    Linux/WindowsのNFC（合成形）と比較すると不一致になる。
    NFC正規化により、OS間の差異を吸収する。

    Parameters
    ----------
    name : str
        正規化対象のファイル名

    Returns
    -------
    str
        NFC正規化済みのファイル名
    """
    return unicodedata.normalize("NFC", name)


def safe_path_match(path_a: str, path_b: str) -> bool:
    """NFC正規化後にパス文字列を比較する.

    macOS由来（NFD）とLinux/Windows由来（NFC）のパスを
    安全に比較するためのユーティリティ。

    Parameters
    ----------
    path_a : str
        比較対象のパス文字列
    path_b : str
        比較対象のパス文字列

    Returns
    -------
    bool
        NFC正規化後に一致すればTrue
    """
    return normalize_filename_nfc(path_a) == normalize_filename_nfc(path_b)
