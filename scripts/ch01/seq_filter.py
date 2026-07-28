"""配列フィルタリング — 関心の分離・単一責任原則のデモ.

各関数が1つの責務だけを持つ設計を示す:
- parse_fasta_string(): 入力のパース
- filter_by_length(): 条件によるフィルタリング
- format_as_tsv(): 出力のフォーマット
"""

from dataclasses import dataclass
from io import StringIO

from Bio import SeqIO


@dataclass(frozen=True)
class SequenceRecord:
    """配列レコード."""

    id: str
    sequence: str

    @property
    def length(self) -> int:
        """配列長を返す."""
        return len(self.sequence)


# --- パース（入力の関心） ---


def parse_fasta_string(fasta_text: str) -> list[SequenceRecord]:
    """FASTA形式のテキストをパースする.

    Parameters
    ----------
    fasta_text : str
        FASTA形式の文字列

    Returns
    -------
    list[SequenceRecord]
        パースされた配列レコードのリスト
    """
    if not fasta_text.strip():
        return []

    # FASTAの構文解釈は検証済みのBio.SeqIOへ委譲する
    records = SeqIO.parse(StringIO(fasta_text.strip()), "fasta")
    return [
        SequenceRecord(id=record.description, sequence=str(record.seq))
        for record in records
    ]


# --- フィルタリング（処理の関心） ---


def filter_by_length(
    records: list[SequenceRecord],
    min_length: int = 0,
    max_length: int | None = None,
) -> list[SequenceRecord]:
    """配列長でフィルタリングする.

    Parameters
    ----------
    records : list[SequenceRecord]
        フィルタ対象の配列レコード
    min_length : int
        最小配列長（含む）
    max_length : int | None
        最大配列長（含む）。None の場合は上限なし。

    Returns
    -------
    list[SequenceRecord]
        条件を満たすレコード
    """
    return [
        r
        for r in records
        if r.length >= min_length
        and (max_length is None or r.length <= max_length)
    ]


# --- フォーマット（出力の関心） ---


def format_as_tsv(records: list[SequenceRecord]) -> str:
    """配列レコードをTSV形式の文字列にフォーマットする.

    Parameters
    ----------
    records : list[SequenceRecord]
        出力対象の配列レコード

    Returns
    -------
    str
        TSV形式の文字列（ヘッダー行つき）
    """
    lines = ["id\tsequence\tlength"]
    for r in records:
        lines.append(f"{r.id}\t{r.sequence}\t{r.length}")
    return "\n".join(lines)
