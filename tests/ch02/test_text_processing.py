"""テキスト処理関数のテスト."""

from pathlib import Path

import pytest

from scripts.ch02.text_processing import (
    count_fasta_records,
    count_lines,
    extract_column,
    grep_lines,
    sort_unique,
)


@pytest.fixture()
def fasta_file(tmp_path: Path) -> Path:
    """テスト用FASTAファイルを作成する."""
    content = """>seq1 Homo sapiens BRCA1
ATGCGATCGATCG
>seq2 Mus musculus TP53
GCTAGCTAGCTAG
>seq3 Homo sapiens BRCA2
TTAACCGGTTAACC
"""
    p = tmp_path / "test.fasta"
    p.write_text(content)
    return p


@pytest.fixture()
def tsv_file(tmp_path: Path) -> Path:
    """テスト用TSVファイルを作成する."""
    content = "gene\tsample_A\tsample_B\nBRCA1\t10.5\t12.3\nTP53\t8.2\t9.1\nEGFR\t15.0\t14.8\n"
    p = tmp_path / "expression.tsv"
    p.write_text(content)
    return p


class TestGrepLines:
    """grep_lines() のテスト."""

    def test_match_fasta_headers(self, fasta_file: Path) -> None:
        result = grep_lines(fasta_file, pattern=r"^>")
        assert len(result) == 3
        assert result[0] == ">seq1 Homo sapiens BRCA1"

    def test_match_species(self, fasta_file: Path) -> None:
        result = grep_lines(fasta_file, pattern="Homo sapiens")
        assert len(result) == 2

    def test_no_match(self, fasta_file: Path) -> None:
        result = grep_lines(fasta_file, pattern="NONEXISTENT")
        assert result == []

    def test_regex_pattern(self, fasta_file: Path) -> None:
        result = grep_lines(fasta_file, pattern=r"BRCA\d")
        assert len(result) == 2


class TestCountFastaRecords:
    """count_fasta_records() のテスト."""

    def test_count(self, fasta_file: Path) -> None:
        assert count_fasta_records(fasta_file) == 3

    def test_empty_file(self, tmp_path: Path) -> None:
        p = tmp_path / "empty.fasta"
        p.write_text("")
        assert count_fasta_records(p) == 0

    def test_no_records(self, tmp_path: Path) -> None:
        p = tmp_path / "no_header.fasta"
        p.write_text("ATGCGATCG\nGCTAGCTAG\n")
        assert count_fasta_records(p) == 0


class TestExtractColumn:
    """extract_column() のテスト."""

    def test_first_column(self, tsv_file: Path) -> None:
        result = extract_column(tsv_file, column=0, skip_header=True)
        assert result == ["BRCA1", "TP53", "EGFR"]

    def test_second_column(self, tsv_file: Path) -> None:
        result = extract_column(tsv_file, column=1, skip_header=True)
        assert result == ["10.5", "8.2", "15.0"]

    def test_with_header(self, tsv_file: Path) -> None:
        result = extract_column(tsv_file, column=0, skip_header=False)
        assert result[0] == "gene"
        assert len(result) == 4

    def test_column_out_of_range(self, tmp_path: Path) -> None:
        p = tmp_path / "single_col.tsv"
        p.write_text("a\nb\nc\n")
        result = extract_column(p, column=5)
        assert result == []


class TestSortUnique:
    """sort_unique() のテスト."""

    def test_duplicates_removed(self) -> None:
        assert sort_unique(["chr1", "chr2", "chr1", "chr3", "chr2"]) == [
            "chr1",
            "chr2",
            "chr3",
        ]

    def test_already_unique(self) -> None:
        assert sort_unique(["a", "b", "c"]) == ["a", "b", "c"]

    def test_empty_list(self) -> None:
        assert sort_unique([]) == []

    def test_single_element(self) -> None:
        assert sort_unique(["x"]) == ["x"]


class TestCountLines:
    """count_lines() のテスト."""

    def test_count(self, fasta_file: Path) -> None:
        # FASTAファイル: 3ヘッダ + 3配列 = 6行
        assert count_lines(fasta_file) == 6

    def test_empty_file(self, tmp_path: Path) -> None:
        p = tmp_path / "empty.txt"
        p.write_text("")
        assert count_lines(p) == 0

    def test_single_line(self, tmp_path: Path) -> None:
        p = tmp_path / "single.txt"
        p.write_text("hello\n")
        assert count_lines(p) == 1
