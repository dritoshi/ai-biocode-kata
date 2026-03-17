"""GC含量の計算 — KISS原則・DRY原則のデモ."""


def gc_content(seq: str) -> float:
    """DNA配列のGC含量を計算する.

    Parameters
    ----------
    seq : str
        DNA配列（A, T, G, C からなる文字列）

    Returns
    -------
    float
        GC含量（0.0〜1.0）。空文字列の場合は 0.0。
    """
    if not seq:
        return 0.0
    seq_upper = seq.upper()
    gc_count = seq_upper.count("G") + seq_upper.count("C")
    return gc_count / len(seq_upper)


def filter_sequences_by_gc(
    sequences: dict[str, str],
    min_gc: float = 0.0,
    max_gc: float = 1.0,
) -> dict[str, str]:
    """GC含量の範囲で配列をフィルタリングする.

    Parameters
    ----------
    sequences : dict[str, str]
        配列ID → 配列のマッピング
    min_gc : float
        GC含量の下限（含む）
    max_gc : float
        GC含量の上限（含む）

    Returns
    -------
    dict[str, str]
        条件を満たす配列のサブセット
    """
    # gc_content() を再利用する（DRY原則）
    return {
        seq_id: seq
        for seq_id, seq in sequences.items()
        if min_gc <= gc_content(seq) <= max_gc
    }
