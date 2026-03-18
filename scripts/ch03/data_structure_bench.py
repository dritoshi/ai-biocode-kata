"""データ構造の選択と計算量 — list vs set vs dict の検索性能.

10万件の遺伝子IDを検索する場面を想定し、
データ構造の選択が実行時間にどう影響するかを示す。
"""

import time


def build_gene_ids(n: int) -> list[str]:
    """テスト用の遺伝子IDリストを生成する.

    Parameters
    ----------
    n : int
        生成する遺伝子IDの数

    Returns
    -------
    list[str]
        "GENE_000000" 〜 "GENE_{n-1}" 形式のIDリスト
    """
    return [f"GENE_{i:06d}" for i in range(n)]


def search_in_list(gene_list: list[str], query: str) -> bool:
    """listでの遺伝子ID検索（O(n)）.

    Parameters
    ----------
    gene_list : list[str]
        検索対象のリスト
    query : str
        検索する遺伝子ID

    Returns
    -------
    bool
        見つかれば True
    """
    return query in gene_list


def search_in_set(gene_set: set[str], query: str) -> bool:
    """setでの遺伝子ID検索（O(1) 平均）.

    Parameters
    ----------
    gene_set : set[str]
        検索対象のセット
    query : str
        検索する遺伝子ID

    Returns
    -------
    bool
        見つかれば True
    """
    return query in gene_set


def search_in_dict(gene_dict: dict[str, int], query: str) -> bool:
    """dictでの遺伝子ID検索（O(1) 平均）.

    Parameters
    ----------
    gene_dict : dict[str, int]
        遺伝子ID → インデックスのマッピング
    query : str
        検索する遺伝子ID

    Returns
    -------
    bool
        見つかれば True
    """
    return query in gene_dict


def benchmark_search(n: int = 100_000, n_queries: int = 1000) -> dict[str, float]:
    """list / set / dict の検索時間を計測する.

    Parameters
    ----------
    n : int
        遺伝子IDの総数
    n_queries : int
        検索クエリの回数

    Returns
    -------
    dict[str, float]
        データ構造名 → 合計検索時間（秒）のマッピング
    """
    gene_list = build_gene_ids(n)
    gene_set = set(gene_list)
    gene_dict = {gene_id: i for i, gene_id in enumerate(gene_list)}

    # 検索対象: 末尾付近のID（listでは最も遅いケース）
    queries = [f"GENE_{n - 1 - i:06d}" for i in range(n_queries)]

    results: dict[str, float] = {}

    # list
    start = time.perf_counter()
    for q in queries:
        search_in_list(gene_list, q)
    results["list"] = time.perf_counter() - start

    # set
    start = time.perf_counter()
    for q in queries:
        search_in_set(gene_set, q)
    results["set"] = time.perf_counter() - start

    # dict
    start = time.perf_counter()
    for q in queries:
        search_in_dict(gene_dict, q)
    results["dict"] = time.perf_counter() - start

    return results
