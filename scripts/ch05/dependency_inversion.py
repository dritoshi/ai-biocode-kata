"""依存性逆転原則を示す配列長解析の例。"""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from Bio import SeqIO


class SequenceSource(Protocol):
    """配列を供給するオブジェクトが満たすインターフェース。"""

    def load(self) -> list[str]:
        """配列文字列のリストを返す。"""
        ...


def mean_sequence_length(source: SequenceSource) -> float:
    """抽象的な配列供給元から配列を読み、平均配列長を返す。"""
    sequences = source.load()
    if not sequences:
        return 0.0
    return sum(len(sequence) for sequence in sequences) / len(sequences)


@dataclass(frozen=True)
class FastaSequenceSource:
    """Bio.SeqIOを使ってFASTAファイルから配列を供給する。"""

    path: Path

    def load(self) -> list[str]:
        """FASTAファイル内の配列を文字列として返す。"""
        return [str(record.seq) for record in SeqIO.parse(self.path, "fasta")]
