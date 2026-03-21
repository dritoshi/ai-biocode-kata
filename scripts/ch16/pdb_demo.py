"""breakpoint()/pdb 実演用の関数群."""


def calculate_gc_stats(
    sequences: list[str],
) -> dict[str, float]:
    """複数の塩基配列のGC含量統計を計算する.

    Parameters
    ----------
    sequences : list[str]
        塩基配列のリスト（A, T, G, C で構成）。

    Returns
    -------
    dict[str, float]
        "mean_gc", "min_gc", "max_gc" をキーとする統計値辞書。
        空リストの場合は全て 0.0 を返す。
    """
    if not sequences:
        return {"mean_gc": 0.0, "min_gc": 0.0, "max_gc": 0.0}

    gc_ratios: list[float] = []
    for seq in sequences:
        upper = seq.upper()
        gc_count = upper.count("G") + upper.count("C")
        gc_ratio = gc_count / len(upper) if upper else 0.0
        gc_ratios.append(gc_ratio)

    return {
        "mean_gc": sum(gc_ratios) / len(gc_ratios),
        "min_gc": min(gc_ratios),
        "max_gc": max(gc_ratios),
    }


def find_motif_positions(sequence: str, motif: str) -> list[int]:
    """配列中のモチーフの出現位置をすべて返す.

    Parameters
    ----------
    sequence : str
        検索対象の塩基配列。
    motif : str
        検索するモチーフ（部分文字列）。

    Returns
    -------
    list[int]
        モチーフが見つかった開始位置のリスト（0-based）。
        見つからない場合は空リスト。
    """
    positions: list[int] = []
    start = 0
    upper_seq = sequence.upper()
    upper_motif = motif.upper()
    while start <= len(upper_seq) - len(upper_motif):
        idx = upper_seq.find(upper_motif, start)
        if idx == -1:
            break
        positions.append(idx)
        # 重複ありで次の位置から検索
        start = idx + 1
    return positions
