"""乱数と再現性 — シード固定による結果の再現.

擬似乱数生成器のシードを固定することで、
ランダムな処理でも結果を完全に再現できることを示す。
"""

import numpy as np
from numpy.typing import NDArray


def subsample_with_seed(
    data: NDArray[np.float64],
    n: int,
    seed: int,
) -> NDArray[np.float64]:
    """シード固定でランダムサブサンプリングする.

    Parameters
    ----------
    data : NDArray[np.float64]
        サンプリング対象の配列
    n : int
        サンプル数
    seed : int
        乱数シード

    Returns
    -------
    NDArray[np.float64]
        サブサンプル
    """
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(data), size=n, replace=False)
    return data[indices]


def bootstrap_mean(
    data: NDArray[np.float64],
    n_iterations: int,
    seed: int,
) -> NDArray[np.float64]:
    """ブートストラップ法で平均値の分布を推定する.

    Parameters
    ----------
    data : NDArray[np.float64]
        元データ
    n_iterations : int
        ブートストラップの反復回数
    seed : int
        乱数シード

    Returns
    -------
    NDArray[np.float64]
        各反復の平均値の配列
    """
    rng = np.random.default_rng(seed)
    means = np.empty(n_iterations)
    for i in range(n_iterations):
        sample = rng.choice(data, size=len(data), replace=True)
        means[i] = sample.mean()
    return means


def generate_random_sequences(
    n: int,
    length: int,
    seed: int,
) -> list[str]:
    """ランダムなDNA配列を生成する.

    Parameters
    ----------
    n : int
        生成する配列の数
    length : int
        各配列の長さ
    seed : int
        乱数シード

    Returns
    -------
    list[str]
        DNA配列のリスト
    """
    rng = np.random.default_rng(seed)
    bases = np.array(["A", "T", "G", "C"])
    sequences: list[str] = []
    for _ in range(n):
        indices = rng.integers(0, 4, size=length)
        sequences.append("".join(bases[indices]))
    return sequences
