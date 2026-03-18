"""人間向けレイアウトから機械可読形式への変換.

実験ノートの「人間向けExcel」にありがちな問題
（結合セル・空行・不揃いなヘッダ）を検出・正規化し、
機械可読な表形式に変換する方法を示す。
"""

import re


def normalize_sample_sheet(
    messy_rows: list[list[str]],
    header_row_index: int = 0,
) -> list[dict[str, str]]:
    """人間向けレイアウトの表データを機械可読形式に正規化する.

    以下の処理を行う:
    - 指定行をヘッダとして使用
    - 列名の空白・改行をアンダースコアに正規化
    - 空行の除去
    - 結合セル（空セル）を直前の値で前方充填

    Parameters
    ----------
    messy_rows : list[list[str]]
        2次元リスト形式の表データ（ヘッダ行含む）
    header_row_index : int
        ヘッダ行のインデックス（デフォルト: 0）

    Returns
    -------
    list[dict[str, str]]
        列名→値の辞書のリスト（正規化済み）
    """
    if not messy_rows:
        return []

    # ヘッダ行の取得と正規化
    raw_headers = messy_rows[header_row_index]
    headers = [_normalize_column_name(h) for h in raw_headers]

    # データ行の処理（ヘッダ行以降）
    data_rows = messy_rows[header_row_index + 1 :]
    records: list[dict[str, str]] = []

    for row in data_rows:
        # 空行を除去（すべてのセルが空文字列）
        if all(cell.strip() == "" for cell in row):
            continue

        # 列数をヘッダに合わせる（不足分は空文字列で補完）
        padded = row + [""] * max(0, len(headers) - len(row))
        record = {headers[i]: padded[i].strip() for i in range(len(headers))}
        records.append(record)

    # 結合セルの前方充填
    records = _forward_fill(records, headers)

    return records


def _normalize_column_name(name: str) -> str:
    """列名を正規化する.

    空白・改行をアンダースコアに変換し、前後の空白を除去する。

    Parameters
    ----------
    name : str
        正規化前の列名

    Returns
    -------
    str
        正規化後の列名
    """
    name = name.strip()
    # 連続する空白文字（改行含む）をアンダースコアに変換
    name = re.sub(r"\s+", "_", name)
    return name


def _forward_fill(
    records: list[dict[str, str]],
    columns: list[str],
) -> list[dict[str, str]]:
    """空セルを直前の値で前方充填する.

    Parameters
    ----------
    records : list[dict[str, str]]
        辞書のリスト
    columns : list[str]
        前方充填対象の列名リスト

    Returns
    -------
    list[dict[str, str]]
        前方充填後の辞書のリスト
    """
    if not records:
        return records

    for col in columns:
        last_value = ""
        for record in records:
            if record[col] == "":
                record[col] = last_value
            else:
                last_value = record[col]

    return records


def validate_tidy_table(
    records: list[dict[str, str]],
    expected_columns: list[str],
) -> list[str]:
    """機械可読な表形式のバリデーション.

    以下の条件を検証する:
    1. 期待する列がすべて存在する
    2. 空文字列のセルがない
    3. レコード数が1以上

    Parameters
    ----------
    records : list[dict[str, str]]
        検証対象の辞書リスト
    expected_columns : list[str]
        期待する列名のリスト

    Returns
    -------
    list[str]
        エラーメッセージのリスト（空なら合格）
    """
    errors: list[str] = []

    # レコード数の検証
    if not records:
        errors.append("レコードが0件です")
        return errors

    # 列名の検証
    actual_columns = set(records[0].keys())
    for col in expected_columns:
        if col not in actual_columns:
            errors.append(f"列 '{col}' が見つかりません")

    # 空セルの検証
    for i, record in enumerate(records):
        for col, value in record.items():
            if value == "":
                errors.append(f"行 {i + 1}, 列 '{col}' が空です")

    return errors
