"""TSV / CSV の読み書き — 表形式データの基本操作."""

import csv
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
