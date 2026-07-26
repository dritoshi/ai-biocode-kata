"""FASTAストリーミング処理のテスト."""

from pathlib import Path

from scripts.ch17.streaming_fasta import count_long_sequences


def test_count_long_sequences_includes_boundary(tmp_path: Path) -> None:
    fasta_path = tmp_path / "sequences.fasta"
    fasta_path.write_text(
        ">short\nACGT\n>boundary\nACGTAC\n>long\nACGTACGT\n",
        encoding="utf-8",
    )

    assert count_long_sequences(fasta_path, min_length=6) == 2


def test_count_long_sequences_handles_empty_fasta(tmp_path: Path) -> None:
    fasta_path = tmp_path / "empty.fasta"
    fasta_path.write_text("", encoding="utf-8")

    assert count_long_sequences(fasta_path, min_length=1) == 0
