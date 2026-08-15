"""依存性逆転原則のサンプル実装を検証する。"""

from pathlib import Path

from scripts.ch05.dependency_inversion import (
    FastaSequenceSource,
    mean_sequence_length,
)


class InMemorySequenceSource:
    """テスト用にメモリ上の配列を供給する。"""

    def __init__(self, sequences: list[str]) -> None:
        self._sequences = sequences

    def load(self) -> list[str]:
        """保持している配列を返す。"""
        return self._sequences


def test_mean_sequence_length_accepts_in_memory_source() -> None:
    source = InMemorySequenceSource(["ACGT", "AA"])

    assert mean_sequence_length(source) == 3.0


def test_mean_sequence_length_returns_zero_for_empty_source() -> None:
    source = InMemorySequenceSource([])

    assert mean_sequence_length(source) == 0.0


def test_fasta_sequence_source_uses_seqio(tmp_path: Path) -> None:
    fasta_path = tmp_path / "sequences.fasta"
    fasta_path.write_text(">seq1\nACGT\n>seq2\nAAAAAA\n", encoding="utf-8")

    source = FastaSequenceSource(fasta_path)

    assert source.load() == ["ACGT", "AAAAAA"]
    assert mean_sequence_length(source) == 5.0
