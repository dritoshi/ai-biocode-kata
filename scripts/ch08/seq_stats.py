"""配列統計の計算とFASTAフィルタリング — テストの実践デモ."""

from pathlib import Path

from Bio import SeqIO


def gc_content(seq: str) -> float:
    """DNA配列のGC含量を計算する.

    Parameters
    ----------
    seq : str
        DNA配列（A, T, G, C, N などを含む文字列）

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


def filter_fasta_by_gc(
    input_path: Path,
    output_path: Path,
    min_gc: float = 0.0,
    max_gc: float = 1.0,
) -> int:
    """GC含量の範囲でFASTA配列をフィルタリングする.

    Parameters
    ----------
    input_path : Path
        入力FASTAファイルのパス
    output_path : Path
        出力FASTAファイルのパス
    min_gc : float
        GC含量の下限（含む）。デフォルトは0.0
    max_gc : float
        GC含量の上限（含む）。デフォルトは1.0

    Returns
    -------
    int
        書き出した配列の数

    Raises
    ------
    FileNotFoundError
        入力ファイルが存在しない場合
    """
    if not input_path.exists():
        msg = f"入力ファイルが見つかりません: {input_path}"
        raise FileNotFoundError(msg)

    filtered_records = []
    for record in SeqIO.parse(input_path, "fasta"):
        gc = gc_content(str(record.seq))
        if min_gc <= gc <= max_gc:
            filtered_records.append(record)

    count = SeqIO.write(filtered_records, output_path, "fasta")
    return count
