"""NumPyによるベクトル化演算 — バイオインフォデータの高速処理."""

import numpy as np


def gc_content_vectorized(sequences: list[str]) -> np.ndarray:
    """複数のDNA配列のGC含量を、全配列を一括してNumPyで計算する.

    配列を1つずつNumPy配列に変換する（配列ごとのPythonループが残る）と、
    短い配列では変換の固定コストが支配的になり、かえって遅くなる。
    ここでは全配列を1本のバイト列に連結し、GC判定を一度だけ行い、
    ``np.add.reduceat`` で配列の境界ごとに合計を区切る。配列ごとの
    Pythonループを持たない、真のベクトル化である。

    Parameters
    ----------
    sequences : list[str]
        DNA配列のリスト（A, T, G, C を含む文字列）

    Returns
    -------
    np.ndarray
        各配列のGC含量（0.0〜1.0）。空配列の場合は 0.0。
    """
    n = len(sequences)
    results = np.zeros(n, dtype=np.float64)
    lengths = np.fromiter((len(s) for s in sequences), dtype=np.int64, count=n)
    if n == 0 or lengths.sum() == 0:
        return results
    # 全配列を連結して1つのバイト配列にし、GCを一度だけベクトル判定する
    buffer = np.frombuffer("".join(sequences).upper().encode("ascii"), dtype=np.uint8)
    is_gc = ((buffer == ord("G")) | (buffer == ord("C"))).astype(np.int64)
    # 各配列の開始位置（空配列は境界が重複するため除外）で合計を区切る
    nonempty = lengths > 0
    starts = np.concatenate(([0], np.cumsum(lengths)[:-1]))
    counts = np.add.reduceat(is_gc, starts[nonempty])
    results[nonempty] = counts / lengths[nonempty]
    return results


def normalize_cpm(counts: np.ndarray) -> np.ndarray:
    """発現量カウント行列をCPM（Counts Per Million）に正規化する.

    ブロードキャスティングを活用し、サンプルごとの総カウント数で
    各遺伝子のカウントを正規化する。

    Parameters
    ----------
    counts : np.ndarray
        発現量カウント行列（行: 遺伝子、列: サンプル）。
        値は非負整数を想定。

    Returns
    -------
    np.ndarray
        CPM正規化後の行列（float64）
    """
    # 列（サンプル）ごとの合計を計算
    col_sums = counts.sum(axis=0)
    # ゼロ除算を防ぐ
    col_sums = np.where(col_sums == 0, 1, col_sums)
    # ブロードキャスティングで一括正規化
    return (counts / col_sums) * 1_000_000


def filter_by_quality(scores: np.ndarray, threshold: int = 20) -> np.ndarray:
    """Quality scoreが閾値以上の要素だけを抽出する.

    ファンシーインデックス（ブーリアンマスク）を使い、
    閾値未満のスコアを除外する。

    Parameters
    ----------
    scores : np.ndarray
        Quality scoreの配列（整数値）
    threshold : int
        フィルタリングの閾値（この値以上を残す）。デフォルトは20。

    Returns
    -------
    np.ndarray
        閾値以上のスコアだけを含む配列
    """
    mask = scores >= threshold
    return scores[mask]
