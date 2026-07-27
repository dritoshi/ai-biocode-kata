"""配列処理ツールの基本関数."""


def sequence_length(sequence: str) -> int:
    """塩基配列の文字数を返す.

    Parameters
    ----------
    sequence : str
        長さを数える塩基配列

    Returns
    -------
    int
        塩基配列の文字数
    """
    return len(sequence)
