"""配列フィルタリング（関心の分離デモ）のテスト."""

from scripts.ch01.seq_filter import (
    SequenceRecord,
    filter_by_length,
    format_as_tsv,
    parse_fasta_string,
)

SAMPLE_FASTA = """\
>seq1 short sequence
ATGC
>seq2 medium sequence
ATGCATGCATGC
>seq3 long sequence
ATGCATGCATGCATGCATGCATGCATGCATGC
"""


class TestParseFastaString:
    """parse_fasta_string() のテスト."""

    def test_parse_count(self) -> None:
        records = parse_fasta_string(SAMPLE_FASTA)
        assert len(records) == 3

    def test_parse_ids(self) -> None:
        records = parse_fasta_string(SAMPLE_FASTA)
        ids = [r.id for r in records]
        assert ids == ["seq1 short sequence", "seq2 medium sequence", "seq3 long sequence"]

    def test_parse_sequences(self) -> None:
        records = parse_fasta_string(SAMPLE_FASTA)
        assert records[0].sequence == "ATGC"
        assert records[1].sequence == "ATGCATGCATGC"

    def test_empty_input(self) -> None:
        assert parse_fasta_string("") == []

    def test_multiline_sequence(self) -> None:
        fasta = ">seq1\nATGC\nATGC\n"
        records = parse_fasta_string(fasta)
        assert records[0].sequence == "ATGCATGC"


class TestFilterByLength:
    """filter_by_length() のテスト."""

    def test_min_length(self) -> None:
        records = parse_fasta_string(SAMPLE_FASTA)
        result = filter_by_length(records, min_length=10)
        assert len(result) == 2
        assert all(r.length >= 10 for r in result)

    def test_max_length(self) -> None:
        records = parse_fasta_string(SAMPLE_FASTA)
        result = filter_by_length(records, max_length=5)
        assert len(result) == 1
        assert result[0].sequence == "ATGC"

    def test_range(self) -> None:
        records = parse_fasta_string(SAMPLE_FASTA)
        result = filter_by_length(records, min_length=5, max_length=20)
        assert len(result) == 1

    def test_no_filter(self) -> None:
        records = parse_fasta_string(SAMPLE_FASTA)
        result = filter_by_length(records)
        assert len(result) == 3


class TestFormatAsTsv:
    """format_as_tsv() のテスト."""

    def test_header(self) -> None:
        tsv = format_as_tsv([])
        assert tsv == "id\tsequence\tlength"

    def test_format(self) -> None:
        records = [SequenceRecord(id="seq1", sequence="ATGC")]
        tsv = format_as_tsv(records)
        lines = tsv.splitlines()
        assert len(lines) == 2
        assert lines[1] == "seq1\tATGC\t4"
