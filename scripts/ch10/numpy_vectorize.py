"""NumPyによるベクトル化演算 — バイオインフォデータの高速処理."""

import numpy as np


def gc_content_vectorized(sequences: list[str]) -> np.ndarray:
    """複数のDNA配列のGC含量をNumPyで一括計算する.

    forループで1配列ずつ処理する代わりに、バイト配列への変換と
    ベクトル比較により高速に計算する。

    Parameters
    ----------
    sequences : list[str]
        DNA配列のリスト（A, T, G, C を含む文字列）

    Returns
    -------
    np.ndarray
        各配列のGC含量（0.0〜1.0）。空配列の場合は 0.0。
    """
    results = np.empty(len(sequences), dtype=np.float64)
    for i, seq in enumerate(sequences):
        if not seq:
            results[i] = 0.0
            continue
        # バイト配列に変換してベクトル比較
        arr = np.frombuffer(seq.upper().encode("ascii"), dtype=np.uint8)
        gc_mask = (arr == ord("G")) | (arr == ord("C"))
        results[i] = gc_mask.sum() / len(arr)
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
