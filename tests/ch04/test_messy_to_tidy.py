"""人間向けレイアウト→機械可読形式変換のテスト."""

from scripts.ch04.messy_to_tidy import (
    normalize_sample_sheet,
    validate_tidy_table,
)


class TestNormalizeSampleSheet:
    """normalize_sample_sheet() のテスト."""

    def test_basic_normalization(self) -> None:
        messy = [
            ["Sample ID", "Condition", "Value"],
            ["S001", "Control", "10.5"],
            ["S002", "Treatment", "20.3"],
        ]
        result = normalize_sample_sheet(messy)
        assert len(result) == 2
        assert result[0]["Sample_ID"] == "S001"
        assert result[1]["Condition"] == "Treatment"

    def test_empty_rows_removed(self) -> None:
        messy = [
            ["gene", "value"],
            ["TP53", "10.5"],
            ["", ""],
            ["BRCA1", "5.2"],
        ]
        result = normalize_sample_sheet(messy)
        assert len(result) == 2
        assert result[0]["gene"] == "TP53"
        assert result[1]["gene"] == "BRCA1"

    def test_whitespace_only_rows_removed(self) -> None:
        messy = [
            ["gene", "value"],
            ["TP53", "10.5"],
            ["  ", " \t "],
            ["BRCA1", "5.2"],
        ]
        result = normalize_sample_sheet(messy)
        assert len(result) == 2

    def test_header_whitespace_normalized(self) -> None:
        messy = [
            ["Sample\nID", "  Condition  ", "Raw Value"],
            ["S001", "Control", "10"],
        ]
        result = normalize_sample_sheet(messy)
        assert "Sample_ID" in result[0]
        assert "Condition" in result[0]
        assert "Raw_Value" in result[0]

    def test_forward_fill_merged_cells(self) -> None:
        # Excelの結合セルを模擬: グループ列が空セル
        messy = [
            ["group", "sample", "value"],
            ["Control", "S001", "10"],
            ["", "S002", "12"],
            ["Treatment", "S003", "20"],
            ["", "S004", "22"],
        ]
        result = normalize_sample_sheet(messy)
        assert result[0]["group"] == "Control"
        assert result[1]["group"] == "Control"  # 前方充填
        assert result[2]["group"] == "Treatment"
        assert result[3]["group"] == "Treatment"  # 前方充填

    def test_custom_header_row(self) -> None:
        messy = [
            ["実験日: 2026-01-15", "", ""],
            ["gene", "condition", "value"],
            ["TP53", "Control", "10.5"],
        ]
        result = normalize_sample_sheet(messy, header_row_index=1)
        assert len(result) == 1
        assert result[0]["gene"] == "TP53"

    def test_short_row_padded(self) -> None:
        messy = [
            ["gene", "value", "note"],
            ["TP53", "10.5"],
        ]
        result = normalize_sample_sheet(messy)
        assert len(result) == 1
        assert result[0]["note"] == ""

    def test_empty_input(self) -> None:
        result = normalize_sample_sheet([])
        assert result == []


class TestValidateTidyTable:
    """validate_tidy_table() のテスト."""

    def test_valid_table(self) -> None:
        records = [
            {"gene": "TP53", "value": "10.5"},
            {"gene": "BRCA1", "value": "5.2"},
        ]
        errors = validate_tidy_table(records, ["gene", "value"])
        assert errors == []

    def test_missing_column(self) -> None:
        records = [{"gene": "TP53"}]
        errors = validate_tidy_table(records, ["gene", "value"])
        assert any("value" in e for e in errors)

    def test_empty_cell(self) -> None:
        records = [{"gene": "TP53", "value": ""}]
        errors = validate_tidy_table(records, ["gene", "value"])
        assert any("空" in e for e in errors)

    def test_empty_records(self) -> None:
        errors = validate_tidy_table([], ["gene"])
        assert any("0件" in e for e in errors)

    def test_multiple_errors(self) -> None:
        records = [
            {"gene": "TP53", "value": ""},
            {"gene": "", "value": "5.2"},
        ]
        errors = validate_tidy_table(records, ["gene", "value", "missing_col"])
        # 列不足 + 空セルのエラーが複数返る
        assert len(errors) >= 3
