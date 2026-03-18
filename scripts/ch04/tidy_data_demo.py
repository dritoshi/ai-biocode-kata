"""tidy data の変換 — wide form と long form の相互変換.

Wickham (2014) の tidy data 原則に基づき、
pandas の melt() / pivot_table() を用いた
wide ↔ long 変換を実演する。
"""

import pandas as pd


def wide_to_long(
    records: list[dict[str, str]],
    id_col: str,
    value_cols: list[str],
) -> list[dict[str, str]]:
    """wide form を long form に変換する.

    Parameters
    ----------
    records : list[dict[str, str]]
        wide form の辞書リスト
    id_col : str
        識別子の列名（例: "gene"）
    value_cols : list[str]
        値を持つ列名のリスト（例: ["sample_A", "sample_B"]）

    Returns
    -------
    list[dict[str, str]]
        long form の辞書リスト（variable, value 列が追加される）
    """
    df = pd.DataFrame(records)
    melted = pd.melt(
        df,
        id_vars=[id_col],
        value_vars=value_cols,
        var_name="variable",
        value_name="value",
    )
    return melted.to_dict(orient="records")


def long_to_wide(
    records: list[dict[str, str]],
    id_col: str,
    variable_col: str,
    value_col: str,
) -> list[dict[str, str]]:
    """long form を wide form に変換する.

    Parameters
    ----------
    records : list[dict[str, str]]
        long form の辞書リスト
    id_col : str
        識別子の列名（例: "gene"）
    variable_col : str
        変数名の列名（例: "variable"）
    value_col : str
        値の列名（例: "value"）

    Returns
    -------
    list[dict[str, str]]
        wide form の辞書リスト
    """
    df = pd.DataFrame(records)
    pivoted = df.pivot_table(
        index=id_col,
        columns=variable_col,
        values=value_col,
        aggfunc="first",
    ).reset_index()
    # MultiIndex列名をフラットにする
    pivoted.columns.name = None
    return pivoted.to_dict(orient="records")
