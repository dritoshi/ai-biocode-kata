"""型不一致バグのデモ — str vs int, NaN vs None."""

import math

import pandas as pd


def sum_expression_values_buggy(values: list[str]) -> str:
    """発現量の合計を計算する（バグあり版）.

    CSVから読み込んだ値が文字列のまま + で結合される典型的バグ。
    型ヒントは str だが、呼び出し側は数値を期待している。

    Parameters
    ----------
    values : list[str]
        文字列としての発現量（例: ["1.5", "2.3", "0.8"]）。

    Returns
    -------
    str
        文字列連結された結果（バグ: "1.52.30.8" のようになる）。
    """
    # バグ: float に変換せずに + で連結 → 文字列結合になる
    total = ""
    for v in values:
        total = total + v
    return total


def sum_expression_values_fixed(values: list[str]) -> float:
    """発現量の合計を正しく計算する（修正版）.

    文字列を float に変換してから合計する。

    Parameters
    ----------
    values : list[str]
        文字列としての発現量（例: ["1.5", "2.3", "0.8"]）。

    Returns
    -------
    float
        合計値。

    Raises
    ------
    ValueError
        数値に変換できない文字列が含まれている場合。
    """
    total = 0.0
    for v in values:
        total += float(v)
    return total


def safe_mean(values: list[float | None]) -> float | None:
    """None を除外して平均値を計算する.

    Parameters
    ----------
    values : list[float | None]
        数値と None が混在する可能性のあるリスト。

    Returns
    -------
    float | None
        有効な数値の平均。全て None の場合は None を返す。
    """
    valid = [v for v in values if v is not None and not math.isnan(v)]
    if not valid:
        return None
    return sum(valid) / len(valid)


def detect_nan_in_dataframe(df: pd.DataFrame) -> dict[str, int]:
    """DataFrameの各列に含まれるNaN数を返す.

    Parameters
    ----------
    df : pd.DataFrame
        検査対象のDataFrame。

    Returns
    -------
    dict[str, int]
        列名をキー、NaN数を値とする辞書。NaN が 0 の列も含む。
    """
    return dict(df.isna().sum())
