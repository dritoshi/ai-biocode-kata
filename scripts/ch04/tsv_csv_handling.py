"""TSV / CSV の読み書き — 表形式データの基本操作.

区切り文字の違い、ヘッダ行の扱い、
CSV round-trip による浮動小数点の精度劣化を実演する。
"""

import csv
import io
from pathlib import Path


def read_expression_tsv(path: Path) -> list[dict[str, str]]:
    """TSVファイルから発現量データを読み込む.

    ヘッダ行をキーとした辞書のリストを返す。

    Parameters
    ----------
    path : Path
        TSVファイルのパス

    Returns
    -------
    list[dict[str, str]]
        各行をヘッダ名→値の辞書にしたリスト
    """
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return list(reader)


def write_expression_csv(records: list[dict[str, str]], path: Path) -> None:
    """発現量データをCSVファイルに書き出す.

    Parameters
    ----------
    records : list[dict[str, str]]
        ヘッダ名→値の辞書のリスト
    path : Path
        出力先CSVファイルのパス
    """
    if not records:
        # 空リストの場合はヘッダなしの空ファイルを作成
        path.write_text("", encoding="utf-8")
        return

    fieldnames = list(records[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def csv_roundtrip_precision(values: list[float], n_trips: int) -> list[float]:
    """CSV round-trip を繰り返して精度劣化を観察する.

    浮動小数点数をCSVに書き出し→読み込みを n_trips 回繰り返し、
    各tripの最初の値の変化を追跡する。

    Parameters
    ----------
    values : list[float]
        round-trip させる浮動小数点数のリスト
    n_trips : int
        round-trip の回数

    Returns
    -------
    list[float]
        各trip後の最初の値（初期値含めて n_trips+1 要素）
    """
    tracking: list[float] = [values[0]]
    current = values

    for _ in range(n_trips):
        # CSVに書き出し（文字列化）
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(current)
        csv_text = buf.getvalue()

        # CSVから読み込み（文字列→float変換）
        buf = io.StringIO(csv_text)
        reader = csv.reader(buf)
        row = next(reader)
        current = [float(v) for v in row]
        tracking.append(current[0])

    return tracking
