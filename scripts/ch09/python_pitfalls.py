"""Python固有の落とし穴デモ — バグ版と修正版のペア."""

import copy

import numpy as np
import pandas as pd


def add_gene_buggy(name: str, gene_list: list[str] = []) -> list[str]:  # noqa: B006
    """ミュータブルデフォルト引数バグ版.

    デフォルト引数のリストが全呼び出しで共有されるため、
    呼び出しごとに状態が蓄積される。

    Parameters
    ----------
    name : str
        追加する遺伝子名。
    gene_list : list[str]
        遺伝子リスト（デフォルト引数がミュータブル — バグ）。

    Returns
    -------
    list[str]
        遺伝子名が追加されたリスト。
    """
    gene_list.append(name)
    return gene_list


def add_gene_fixed(name: str, gene_list: list[str] | None = None) -> list[str]:
    """ミュータブルデフォルト引数修正版.

    None をデフォルトにし、関数内で新しいリストを作る。

    Parameters
    ----------
    name : str
        追加する遺伝子名。
    gene_list : list[str] | None
        遺伝子リスト。None の場合は新しいリストを作成する。

    Returns
    -------
    list[str]
        遺伝子名が追加されたリスト。
    """
    if gene_list is None:
        gene_list = []
    gene_list.append(name)
    return gene_list


def shallow_copy_demo() -> tuple[dict, dict]:
    """浅いコピーでネストデータが共有される例.

    ``dict.copy()`` は最上位の要素だけをコピーするため、
    ネストされたリストは元のオブジェクトと共有される。

    Returns
    -------
    tuple[dict, dict]
        (original, shallow) — shallow["genes"] への変更が
        original["genes"] にも反映されている状態。
    """
    original: dict[str, list[str]] = {"genes": ["BRCA1", "TP53"]}
    shallow = original.copy()
    shallow["genes"].append("EGFR")
    return original, shallow


def deep_copy_demo() -> tuple[dict, dict]:
    """深いコピーでネストデータが独立する例.

    ``copy.deepcopy()`` はネストされたオブジェクトも再帰的にコピーする。

    Returns
    -------
    tuple[dict, dict]
        (original, deep) — deep["genes"] への変更が
        original["genes"] に反映されない状態。
    """
    original: dict[str, list[str]] = {"genes": ["BRCA1", "TP53"]}
    deep = copy.deepcopy(original)
    deep["genes"].append("MYC")
    return original, deep


def remove_n_buggy(sequence: str) -> str:
    """文字列不変性バグ版（戻り値を捨てる）.

    ``str.replace()`` は新しい文字列を返すが、
    戻り値を変数に代入しなければ元の文字列は変わらない。

    Parameters
    ----------
    sequence : str
        塩基配列文字列。

    Returns
    -------
    str
        元の文字列（N を含んだまま）。
    """
    sequence.replace("N", "")  # 戻り値を捨てている
    return sequence


def remove_n_fixed(sequence: str) -> str:
    """文字列不変性修正版（戻り値を変数に代入）.

    Parameters
    ----------
    sequence : str
        塩基配列文字列。

    Returns
    -------
    str
        N を除去した文字列。
    """
    sequence = sequence.replace("N", "")
    return sequence


def filter_with_loc(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """.loc[] を使ったSettingWithCopyWarning回避版.

    チェーンインデックスの代わりに ``.loc[]`` で明示的にアクセスし、
    条件を満たす行の ``"gene"`` 列を ``"HIGH"`` に更新する。

    Parameters
    ----------
    df : pd.DataFrame
        ``"gene"`` 列と ``"score"`` 列を持つ DataFrame。
    threshold : float
        score の閾値。

    Returns
    -------
    pd.DataFrame
        更新後の DataFrame。
    """
    df = df.copy()
    df.loc[df["score"] > threshold, "gene"] = "HIGH"
    return df


def demonstrate_numpy_view() -> tuple[np.ndarray, np.ndarray, bool]:
    """NumPyスライスのビュー挙動デモ.

    通常のスライス（``arr[::2]``）はビューを返し、
    元の配列とメモリを共有する。

    Returns
    -------
    tuple[np.ndarray, np.ndarray, bool]
        (arr, view, shares_memory) — ビューへの変更が
        元配列に反映された状態。
    """
    arr = np.array([10, 20, 30, 40, 50])
    view = arr[::2]
    shares_memory = bool(np.shares_memory(arr, view))
    return arr, view, shares_memory


def demonstrate_numpy_copy() -> tuple[np.ndarray, np.ndarray, bool]:
    """NumPyファンシーインデックスのコピー挙動デモ.

    ファンシーインデックス（``arr[[0, 2, 4]]``）はコピーを返し、
    元の配列とメモリを共有しない。

    Returns
    -------
    tuple[np.ndarray, np.ndarray, bool]
        (arr, copy_arr, shares_memory) — コピーへの変更が
        元配列に反映されない状態。
    """
    arr = np.array([10, 20, 30, 40, 50])
    copy_arr = arr[[0, 2, 4]]
    shares_memory = bool(np.shares_memory(arr, copy_arr))
    return arr, copy_arr, shares_memory
