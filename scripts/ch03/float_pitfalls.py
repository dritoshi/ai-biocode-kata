"""浮動小数点の罠 — 精度・比較・特殊値のデモ.

IEEE 754 浮動小数点数の挙動を理解し、
バイオインフォマティクスで陥りやすい罠を回避する方法を示す。
"""

import math


def naive_float_equal(a: float, b: float) -> bool:
    """== による浮動小数点の比較（危険）.

    Parameters
    ----------
    a : float
        比較する値
    b : float
        比較する値

    Returns
    -------
    bool
        a == b の結果
    """
    return a == b


def safe_float_equal(a: float, b: float, rel_tol: float = 1e-9) -> bool:
    """math.isclose() による安全な浮動小数点の比較.

    Parameters
    ----------
    a : float
        比較する値
    b : float
        比較する値
    rel_tol : float
        相対許容誤差（デフォルト: 1e-9）

    Returns
    -------
    bool
        a と b が十分近ければ True
    """
    return math.isclose(a, b, rel_tol=rel_tol)


def naive_sum(values: list[float]) -> float:
    """組み込みsum()による合計（丸め誤差が蓄積する）.

    Parameters
    ----------
    values : list[float]
        合計する値のリスト

    Returns
    -------
    float
        合計値
    """
    return sum(values)


def accurate_sum(values: list[float]) -> float:
    """math.fsum()による高精度な合計.

    Parameters
    ----------
    values : list[float]
        合計する値のリスト

    Returns
    -------
    float
        高精度な合計値
    """
    return math.fsum(values)


def safe_log_pvalue(pvalue: float) -> float:
    """p値の安全な対数変換（アンダーフロー対策）.

    極小のp値（1e-300付近）はアンダーフローで 0.0 になりうる。
    0以下の場合は -inf を返すことで、下流の計算を破綻させない。

    Parameters
    ----------
    pvalue : float
        p値（0 < pvalue <= 1 を想定）

    Returns
    -------
    float
        log10(pvalue)。pvalue <= 0 の場合は -inf。
    """
    if pvalue <= 0.0:
        return float("-inf")
    return math.log10(pvalue)


def demonstrate_nan_behavior() -> dict[str, bool]:
    """NaN の特殊な振る舞いを示す.

    Returns
    -------
    dict[str, bool]
        NaN に関する各種比較の結果
    """
    nan = float("nan")
    return {
        "nan == nan": nan == nan,
        "nan != nan": nan != nan,
        "nan < 0": nan < 0,
        "nan > 0": nan > 0,
        "math.isnan(nan)": math.isnan(nan),
    }
