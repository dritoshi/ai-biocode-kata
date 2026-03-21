"""traceback_demo.py のテスト."""

import pytest

from scripts.ch16.traceback_demo import (
    lookup_gene_annotation,
    parse_gene_expression,
    read_fasta_records,
    safe_parse_gene_expression,
)


class TestReadFastaRecords:
    """read_fasta_records のテスト."""

    def test_normal_fasta(self, tmp_path):
        """正常なFASTAファイルを正しく読み込めることを確認."""
        fasta = tmp_path / "test.fasta"
        fasta.write_text(">gene1\nATCG\nGCTA\n>gene2\nAAAA\n")
        records = read_fasta_records(fasta)
        assert len(records) == 2
        assert records[0] == {"header": "gene1", "sequence": "ATCGGCTA"}
        assert records[1] == {"header": "gene2", "sequence": "AAAA"}

    def test_file_not_found(self, tmp_path):
        """存在しないファイルで FileNotFoundError が発生."""
        with pytest.raises(FileNotFoundError):
            read_fasta_records(tmp_path / "missing.fasta")

    def test_empty_file(self, tmp_path):
        """空ファイルで ValueError が発生."""
        fasta = tmp_path / "empty.fasta"
        fasta.write_text("")
        with pytest.raises(ValueError, match="空です"):
            read_fasta_records(fasta)

    def test_single_record(self, tmp_path):
        """レコードが1つのFASTAファイルを正しく読み込める."""
        fasta = tmp_path / "single.fasta"
        fasta.write_text(">seq1\nACGTACGT\n")
        records = read_fasta_records(fasta)
        assert len(records) == 1
        assert records[0]["sequence"] == "ACGTACGT"


class TestParseGeneExpression:
    """parse_gene_expression のテスト."""

    def test_normal_values(self):
        """正常な数値文字列リストを変換できる."""
        result = parse_gene_expression(["1.5", "2.3", "0.8"])
        assert result == pytest.approx([1.5, 2.3, 0.8])

    def test_invalid_value(self):
        """変換不能な値で ValueError が発生."""
        with pytest.raises(ValueError, match="インデックス 1"):
            parse_gene_expression(["1.0", "N/A", "2.0"])

    def test_empty_list(self):
        """空リストは空リストを返す."""
        assert parse_gene_expression([]) == []


class TestLookupGeneAnnotation:
    """lookup_gene_annotation のテスト."""

    def test_found(self):
        """存在する遺伝子IDでアノテーションを取得できる."""
        db = {"BRCA1": {"name": "Breast cancer 1", "chr": "17"}}
        result = lookup_gene_annotation("BRCA1", db)
        assert result["name"] == "Breast cancer 1"

    def test_not_found(self):
        """存在しない遺伝子IDで KeyError が発生."""
        db = {"BRCA1": {"name": "Breast cancer 1"}}
        with pytest.raises(KeyError, match="TP53"):
            lookup_gene_annotation("TP53", db)


class TestSafeParseGeneExpression:
    """safe_parse_gene_expression のテスト."""

    def test_mixed_values(self):
        """正常値と異常値が混在するデータを分離できる."""
        values, errors = safe_parse_gene_expression(
            ["1.5", "N/A", "2.0", "???"]
        )
        assert values == pytest.approx([1.5, 2.0])
        assert errors == [(1, "N/A"), (3, "???")]

    def test_all_valid(self):
        """全て正常値の場合、エラーリストが空."""
        values, errors = safe_parse_gene_expression(["1.0", "2.0"])
        assert values == pytest.approx([1.0, 2.0])
        assert errors == []

    def test_all_invalid(self):
        """全て異常値の場合、正常値リストが空."""
        values, errors = safe_parse_gene_expression(["abc", "def"])
        assert values == []
        assert len(errors) == 2
