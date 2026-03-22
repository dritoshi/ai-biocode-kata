"""コア機能: 配列操作の基本関数."""


def gc_content(seq: str) -> float:
    """DNA配列のGC含量を計算する.

    Parameters
    ----------
    seq : str
        DNA配列（A, T, G, C）

    Returns
    -------
    float
        GC含量（0.0〜1.0）
    """
    if len(seq) == 0:
        return 0.0
    seq_upper = seq.upper()
    gc_count = seq_upper.count("G") + seq_upper.count("C")
    return gc_count / len(seq_upper)


def reverse_complement(seq: str) -> str:
    """DNA配列の逆相補鎖を返す.

    Parameters
    ----------
    seq : str
        DNA配列

    Returns
    -------
    str
        逆相補鎖
    """
    complement = {"A": "T", "T": "A", "G": "C", "C": "G"}
    return "".join(complement.get(base, "N") for base in reversed(seq.upper()))
