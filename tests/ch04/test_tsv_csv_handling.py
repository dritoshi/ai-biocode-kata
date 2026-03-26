"""TSV / CSV 読み書きデモのテスト."""

from pathlib import Path

from scripts.ch04.tsv_csv_handling import (
    read_expression_tsv,
    write_expression_csv,
)


class TestReadExpressionTsv:
    """read_expression_tsv() のテスト."""

    def test_basic_read(self, tmp_path: Path) -> None:
        tsv_file = tmp_path / "expr.tsv"
        tsv_file.write_text(
            "gene\tsample_A\tsample_B\n"
            "TP53\t10.5\t20.3\n"
            "BRCA1\t5.2\t8.1\n",
            encoding="utf-8",
        )
        records = read_expression_tsv(tsv_file)
        assert len(records) == 2
        assert records[0]["gene"] == "TP53"
        assert records[0]["sample_A"] == "10.5"
        assert records[1]["gene"] == "BRCA1"

    def test_empty_file(self, tmp_path: Path) -> None:
        tsv_file = tmp_path / "empty.tsv"
        tsv_file.write_text("gene\tsample_A\n", encoding="utf-8")
        records = read_expression_tsv(tsv_file)
        assert records == []

    def test_single_column(self, tmp_path: Path) -> None:
        tsv_file = tmp_path / "single.tsv"
        tsv_file.write_text("gene\nTP53\nBRCA1\n", encoding="utf-8")
        records = read_expression_tsv(tsv_file)
        assert len(records) == 2
        assert records[0]["gene"] == "TP53"


class TestWriteExpressionCsv:
    """write_expression_csv() のテスト."""

    def test_basic_write(self, tmp_path: Path) -> None:
        records = [
            {"gene": "TP53", "value": "10.5"},
            {"gene": "BRCA1", "value": "5.2"},
        ]
        csv_file = tmp_path / "out.csv"
        write_expression_csv(records, csv_file)
        content = csv_file.read_text(encoding="utf-8")
        lines = content.strip().split("\n")
        assert lines[0] == "gene,value"
        assert lines[1] == "TP53,10.5"
        assert lines[2] == "BRCA1,5.2"

    def test_empty_records(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "empty.csv"
        write_expression_csv([], csv_file)
        assert csv_file.read_text(encoding="utf-8") == ""

    def test_roundtrip_tsv_to_csv(self, tmp_path: Path) -> None:
        # TSV → read → write CSV → 内容が保持される
        tsv_file = tmp_path / "expr.tsv"
        tsv_file.write_text(
            "gene\tvalue\nTP53\t10.5\n",
            encoding="utf-8",
        )
        records = read_expression_tsv(tsv_file)
        csv_file = tmp_path / "expr.csv"
        write_expression_csv(records, csv_file)
        content = csv_file.read_text(encoding="utf-8")
        assert "TP53" in content
        assert "10.5" in content
