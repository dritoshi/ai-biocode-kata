"""DNA配列の逆相補鎖を求める — TDDのデモ."""

COMPLEMENT: dict[str, str] = {
    "A": "T",
    "T": "A",
    "G": "C",
    "C": "G",
}


def reverse_complement(seq: str) -> str:
    """DNA配列の逆相補鎖を返す.

    Parameters
    ----------
    seq : str
        DNA配列（A, T, G, C からなる文字列）

    Returns
    -------
    str
        逆相補鎖。空文字列の場合は空文字列を返す。
    """
    if not seq:
        return ""
    return "".join(COMPLEMENT[base] for base in reversed(seq.upper()))
