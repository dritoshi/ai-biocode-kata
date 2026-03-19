"""SciPyライブラリ関数の活用 — AIが再発明しがちな処理をライブラリに任せる."""

import numpy as np
from scipy import stats
from scipy.spatial.distance import pdist, squareform


def compare_expression(
    group1: np.ndarray,
    group2: np.ndarray,
) -> tuple[float, float]:
    """2群の発現量をt検定で比較する.

    Welchのt検定（等分散を仮定しない）を使用する。
    バイオインフォマティクスでは群間の分散が異なることが多いため、
    等分散を仮定するStudentのt検定よりもWelchのt検定が推奨される。

    Parameters
    ----------
    group1 : np.ndarray
        群1の発現量（1次元配列）
    group2 : np.ndarray
        群2の発現量（1次元配列）

    Returns
    -------
    tuple[float, float]
        (t統計量, p値) のタプル
    """
    result = stats.ttest_ind(group1, group2, equal_var=False)
    return float(result.statistic), float(result.pvalue)


def correct_pvalues(pvalues: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg法（BH法）による多重検定補正を行う.

    数千〜数万の遺伝子を同時に検定する場合、多重検定補正が必須である。
    BH法はFDR（偽発見率）を制御する標準的な方法である。

    Parameters
    ----------
    pvalues : np.ndarray
        補正前のp値の配列（1次元）

    Returns
    -------
    np.ndarray
        BH法で補正されたp値（adjusted p-values）の配列
    """
    n = len(pvalues)
    if n == 0:
        return np.array([], dtype=np.float64)

    # BH法の手順:
    # 1. p値を昇順にソートし、ランクを付ける
    sorted_indices = np.argsort(pvalues)
    sorted_pvalues = pvalues[sorted_indices]
    ranks = np.arange(1, n + 1)

    # 2. 補正: p_adj = p * n / rank
    adjusted = sorted_pvalues * n / ranks

    # 3. 単調性を保証（後ろから累積最小値を取る）
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]

    # 4. [0, 1] にクリップ
    adjusted = np.clip(adjusted, 0.0, 1.0)

    # 5. 元の順序に戻す
    result = np.empty(n, dtype=np.float64)
    result[sorted_indices] = adjusted
    return result


def expression_distance_matrix(matrix: np.ndarray) -> np.ndarray:
    """発現プロファイルの相関距離行列を計算する.

    サンプル間の相関距離（1 - ピアソン相関係数）を計算し、
    正方距離行列を返す。ヒートマップや階層クラスタリングの入力に使う。

    Parameters
    ----------
    matrix : np.ndarray
        発現量行列（行: 遺伝子、列: サンプル）

    Returns
    -------
    np.ndarray
        サンプル間の相関距離行列（正方行列）
    """
    # 列（サンプル）を観測ベクトルとして扱うため転置
    distances = pdist(matrix.T, metric="correlation")
    return squareform(distances)


def correct_pvalues_scipy(pvalues: np.ndarray) -> np.ndarray:
    """SciPyのライブラリ関数によるBH法の多重検定補正.

    correct_pvalues() の手動実装（約25行）と同じ結果を
    scipy.stats.false_discovery_control() の2行で得られる。

    Parameters
    ----------
    pvalues : np.ndarray
        補正前のp値の配列（1次元）

    Returns
    -------
    np.ndarray
        BH法で補正されたp値（adjusted p-values）の配列
    """
    if len(pvalues) == 0:
        return np.array([], dtype=np.float64)
    return stats.false_discovery_control(pvalues, method="bh")


def distance_matrix_naive(matrix: np.ndarray) -> np.ndarray:
    """二重forループによるサンプル間相関距離行列の計算（非推奨）.

    AIが生成しがちなナイーブ実装の例。
    expression_distance_matrix() のように scipy.spatial.distance.pdist() を
    使えば、高速かつ簡潔に書ける。

    Parameters
    ----------
    matrix : np.ndarray
        発現量行列（行: 遺伝子、列: サンプル）

    Returns
    -------
    np.ndarray
        サンプル間の相関距離行列（正方行列）
    """
    n_samples = matrix.shape[1]
    dist = np.zeros((n_samples, n_samples))
    for i in range(n_samples):
        for j in range(i + 1, n_samples):
            # ピアソン相関係数を手計算
            corr = np.corrcoef(matrix[:, i], matrix[:, j])[0, 1]
            dist[i, j] = 1.0 - corr
            dist[j, i] = dist[i, j]
    return dist
