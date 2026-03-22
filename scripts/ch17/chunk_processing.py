"""pandasチャンク処理で大規模発現量テーブルの統計量を計算する."""

from pathlib import Path

import numpy as np
import pandas as pd


def compute_stats_naive(path: Path) -> dict[str, pd.Series]:
    """CSVファイル全体を一括読み込みして統計量を計算する.

    全データをメモリに載せるため、ファイルサイズが大きいとメモリ不足になる。

    Parameters
    ----------
    path : Path
        CSV ファイルのパス。行=サンプル、列=遺伝子の発現量テーブル。
        1列目がサンプルID。

    Returns
    -------
    dict[str, pd.Series]
        "mean"（遺伝子ごとの平均発現量）と "var"（不偏分散）を含む辞書
    """
    df = pd.read_csv(path, index_col=0)
    return {
        "mean": df.mean(axis=0),
        "var": df.var(axis=0, ddof=1),
    }


def compute_stats_chunked(
    path: Path, chunksize: int = 1000
) -> dict[str, pd.Series]:
    """チャンク処理で統計量を逐次集約する.

    Welfordのオンラインアルゴリズムのバッチ版を用いて、チャンクごとに
    平均と分散を逐次更新する。メモリ使用量はチャンクサイズに比例し、
    ファイル全体のサイズに依存しない。

    行=サンプル、列=遺伝子の形式を前提とする。チャンクはサンプル方向
    （行方向）に分割され、遺伝子ごとの統計量をサンプル間で集約する。

    Parameters
    ----------
    path : Path
        CSV ファイルのパス。行=サンプル、列=遺伝子の発現量テーブル。
    chunksize : int
        一度に読み込む行数（サンプル数）。デフォルト: 1000

    Returns
    -------
    dict[str, pd.Series]
        "mean"（遺伝子ごとの平均発現量）と "var"（不偏分散）を含む辞書
    """
    n_total = 0
    running_mean: pd.Series | None = None
    running_m2: pd.Series | None = None

    reader = pd.read_csv(path, index_col=0, chunksize=chunksize)
    for chunk in reader:
        batch_count = len(chunk)
        batch_mean = chunk.mean(axis=0).astype(np.float64)
        # 母分散（ddof=0）× サンプル数 = 偏差平方和
        batch_m2 = chunk.var(axis=0, ddof=0).astype(np.float64) * batch_count

        if running_mean is None:
            n_total = batch_count
            running_mean = batch_mean
            running_m2 = batch_m2
        else:
            # Welford のバッチ更新（並列結合公式）
            delta = batch_mean - running_mean
            new_count = n_total + batch_count
            running_mean = running_mean + delta * batch_count / new_count
            running_m2 = (
                running_m2
                + batch_m2
                + delta**2 * n_total * batch_count / new_count
            )
            n_total = new_count

    if running_mean is None or n_total < 2:
        raise ValueError("統計量の計算には2サンプル以上が必要です")

    variance = running_m2 / (n_total - 1)

    return {
        "mean": running_mean,
        "var": variance,
    }
