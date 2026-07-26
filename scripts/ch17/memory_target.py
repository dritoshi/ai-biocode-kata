"""memrayで計測するメモリ割り当て例."""

import numpy as np


def load_large_data(
    n_rows: int = 100_000,
    n_columns: int = 100,
    seed: int = 42,
) -> np.ndarray:
    """乱数行列を生成し、列ごとの平均を返す."""
    # 既定では10万行 × 100列の行列を生成（約80 MB）
    data = np.random.default_rng(seed).random((n_rows, n_columns))
    # 平均を計算（追加メモリはほぼ不要）
    means = data.mean(axis=0)
    return means


if __name__ == "__main__":
    load_large_data()
