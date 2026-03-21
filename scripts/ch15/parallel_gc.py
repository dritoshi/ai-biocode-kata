"""concurrent.futuresによる並列GC含量計算."""

from concurrent.futures import ProcessPoolExecutor


def gc_content_single(sequence: str) -> float:
    """単一DNA配列のGC含量を計算する.

    GC含量はDNA配列中のグアニン（G）とシトシン（C）の割合で、
    配列の物理化学的性質を反映する基本的な指標である。

    Parameters
    ----------
    sequence : str
        DNA配列（A, T, G, C を含む文字列）

    Returns
    -------
    float
        GC含量（0.0〜1.0）。空文字列の場合は 0.0。
    """
    if not sequence:
        return 0.0
    seq_upper = sequence.upper()
    gc_count = seq_upper.count("G") + seq_upper.count("C")
    return gc_count / len(seq_upper)


def gc_content_sequential(sequences: list[str]) -> list[float]:
    """複数のDNA配列のGC含量を逐次的に計算する.

    Parameters
    ----------
    sequences : list[str]
        DNA配列のリスト

    Returns
    -------
    list[float]
        各配列のGC含量のリスト
    """
    return [gc_content_single(seq) for seq in sequences]


def gc_content_parallel(
    sequences: list[str], n_workers: int = 2
) -> list[float]:
    """ProcessPoolExecutorで複数DNA配列のGC含量を並列計算する.

    CPUバウンドな処理では、GIL（Global Interpreter Lock）の制約により
    スレッド並列では高速化できない。ProcessPoolExecutor は別プロセスを
    起動するため、GILの制約を回避できる。

    Parameters
    ----------
    sequences : list[str]
        DNA配列のリスト
    n_workers : int
        並列ワーカー数（デフォルト: 2）

    Returns
    -------
    list[float]
        各配列のGC含量のリスト（入力順序を保持）
    """
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        # map() は入力順序を保持して結果を返す
        results = list(executor.map(gc_content_single, sequences))
    return results
