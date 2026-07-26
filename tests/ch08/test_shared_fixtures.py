"""共有フィクスチャのテスト."""

from pathlib import Path

from Bio import SeqIO


def test_data_dir_fixture(test_data_dir: Path) -> None:
    assert test_data_dir.is_dir()


def test_sample_fasta_fixture(sample_fasta: Path) -> None:
    records = list(SeqIO.parse(sample_fasta, "fasta"))
    assert [record.id for record in records] == ["seq1", "seq2"]
    assert [str(record.seq) for record in records] == ["ATGCGCAT", "GGCCGGCC"]
