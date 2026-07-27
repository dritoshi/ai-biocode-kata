"""cProfileによるプロファイリングデモ — TPM正規化の遅い版と速い版."""

import builtins
import cProfile
import pstats
from collections.abc import Callable
from io import StringIO
from typing import ParamSpec, Protocol, TypeVar, cast

import numpy as np

_P = ParamSpec("_P")
_R = TypeVar("_R")


class _ProfileDecorator(Protocol):
    """関数の型を保つプロファイリング用デコレータ."""

    def __call__(
        self, func: Callable[_P, _R]
    ) -> Callable[_P, _R]:
        """関数をプロファイル対象として登録する."""
        ...


def _identity_profile(func: Callable[_P, _R]) -> Callable[_P, _R]:
    """kernprof外では関数を変更せずに返す."""
    return func


# kernprofは実行時にbuiltins.profileを注入する。通常import時はno-opを使う。
profile = cast(
    _ProfileDecorator,
    getattr(builtins, "profile", _identity_profile),
)


def normalize_tpm_slow(
    counts: np.ndarray, gene_lengths: np.ndarray
) -> np.ndarray:
    """forループによるTPM正規化（遅い版）.

    TPM（Transcripts Per Million）は遺伝子長で補正した発現量指標である。
    計算手順:
      1. 各遺伝子のカウントを遺伝子長（kb）で割り、RPK を求める
      2. サンプルごとのRPK合計で割り、100万を掛ける

    Parameters
    ----------
    counts : np.ndarray
        発現量カウント行列（行: 遺伝子、列: サンプル）。shape = (n_genes, n_samples)
    gene_lengths : np.ndarray
        遺伝子長の配列（bp単位）。shape = (n_genes,)

    Returns
    -------
    np.ndarray
        TPM正規化後の行列。各サンプルの列合計は約 1,000,000 になる。
    """
    n_genes, n_samples = counts.shape
    # 遺伝子長をキロベース（kb）に変換
    lengths_kb = gene_lengths / 1000.0

    # RPK（Reads Per Kilobase）を計算
    rpk = np.empty_like(counts, dtype=np.float64)
    for i in range(n_genes):
        for j in range(n_samples):
            rpk[i, j] = counts[i, j] / lengths_kb[i]

    # サンプルごとのスケーリングファクタを計算
    tpm = np.empty_like(rpk)
    for j in range(n_samples):
        col_sum = 0.0
        for i in range(n_genes):
            col_sum += rpk[i, j]
        scaling_factor = col_sum / 1_000_000
        for i in range(n_genes):
            tpm[i, j] = rpk[i, j] / scaling_factor

    return tpm


# @profile構文と同じデコレータ呼び出しで、既存関数を計測対象に登録する。
profiled_normalize_tpm_slow = profile(normalize_tpm_slow)


def normalize_tpm_fast(
    counts: np.ndarray, gene_lengths: np.ndarray
) -> np.ndarray:
    """NumPyベクトル化によるTPM正規化（速い版）.

    forループを排除し、ブロードキャスティングで一括計算する。
    計算結果は normalize_tpm_slow と同一だが、大幅に高速。

    Parameters
    ----------
    counts : np.ndarray
        発現量カウント行列（行: 遺伝子、列: サンプル）。shape = (n_genes, n_samples)
    gene_lengths : np.ndarray
        遺伝子長の配列（bp単位）。shape = (n_genes,)

    Returns
    -------
    np.ndarray
        TPM正規化後の行列
    """
    # 遺伝子長をキロベース（kb）に変換し、列ベクトルに整形
    lengths_kb = gene_lengths[:, np.newaxis] / 1000.0

    # RPK をブロードキャスティングで一括計算
    rpk = counts / lengths_kb

    # サンプルごとのスケーリングファクタ
    scaling_factors = rpk.sum(axis=0) / 1_000_000

    # TPM を一括計算
    return rpk / scaling_factors


def profile_pipeline(
    func: Callable[..., object], *args: object
) -> pstats.Stats:
    """指定した関数を cProfile で計測し、結果を返す.

    Parameters
    ----------
    func : callable
        プロファイル対象の関数
    *args : object
        関数に渡す引数

    Returns
    -------
    pstats.Stats
        プロファイル結果の統計オブジェクト。
        print_stats() で上位関数の実行時間を確認できる。
    """
    profiler = cProfile.Profile()
    profiler.enable()
    func(*args)
    profiler.disable()

    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative")
    return stats


def main() -> None:
    """小規模データでline_profilerの計測対象を実行する."""
    counts = np.array([[100, 200], [300, 400]], dtype=np.float64)
    gene_lengths = np.array([1000, 2000], dtype=np.float64)
    profiled_normalize_tpm_slow(counts, gene_lengths)


if __name__ == "__main__":
    main()
