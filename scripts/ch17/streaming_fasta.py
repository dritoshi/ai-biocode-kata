"""FASTAを全件保持せずに逐次処理する例."""

from pathlib import Path

from Bio import SeqIO


def count_long_sequences(fasta_path: Path, min_length: int) -> int:
    """FASTAファイルから指定長以上の配列数をカウントする.

    Bio.SeqIO.parse() はイテレータを返すため、
    ファイル全体をメモリに載せずに1レコードずつ処理する。
    """
    count = 0
    for record in SeqIO.parse(fasta_path, "fasta"):
        if len(record.seq) >= min_length:
            count += 1
    return count
