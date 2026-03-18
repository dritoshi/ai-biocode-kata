"""tidy data 変換デモのテスト."""

import pytest

from scripts.ch04.tidy_data_demo import (
    long_to_wide,
    wide_to_long,
)


class TestWideToLong:
    """wide_to_long() のテスト."""

    @pytest.fixture()
    def wide_records(self) -> list[dict[str, str]]:
        return [
            {"gene": "TP53", "sample_A": "10.5", "sample_B": "20.3"},
            {"gene": "BRCA1", "sample_A": "5.2", "sample_B": "8.1"},
        ]

    def test_basic_melt(self, wide_records: list[dict[str, str]]) -> None:
        result = wide_to_long(
            wide_records,
            id_col="gene",
            value_cols=["sample_A", "sample_B"],
        )
        # 2遺伝子 × 2サンプル = 4行
        assert len(result) == 4

    def test_columns_present(self, wide_records: list[dict[str, str]]) -> None:
        result = wide_to_long(
            wide_records,
            id_col="gene",
            value_cols=["sample_A", "sample_B"],
        )
        assert "gene" in result[0]
        assert "variable" in result[0]
        assert "value" in result[0]

    def test_values_preserved(self, wide_records: list[dict[str, str]]) -> None:
        result = wide_to_long(
            wide_records,
            id_col="gene",
            value_cols=["sample_A", "sample_B"],
        )
        values = {(r["gene"], r["variable"]): r["value"] for r in result}
        assert values[("TP53", "sample_A")] == "10.5"
        assert values[("BRCA1", "sample_B")] == "8.1"

    def test_single_value_col(self) -> None:
        records = [{"gene": "TP53", "expr": "10.5"}]
        result = wide_to_long(records, id_col="gene", value_cols=["expr"])
        assert len(result) == 1
        assert result[0]["variable"] == "expr"


class TestLongToWide:
    """long_to_wide() のテスト."""

    @pytest.fixture()
    def long_records(self) -> list[dict[str, str]]:
        return [
            {"gene": "TP53", "variable": "sample_A", "value": "10.5"},
            {"gene": "TP53", "variable": "sample_B", "value": "20.3"},
            {"gene": "BRCA1", "variable": "sample_A", "value": "5.2"},
            {"gene": "BRCA1", "variable": "sample_B", "value": "8.1"},
        ]

    def test_basic_pivot(self, long_records: list[dict[str, str]]) -> None:
        result = long_to_wide(
            long_records,
            id_col="gene",
            variable_col="variable",
            value_col="value",
        )
        # 2遺伝子 = 2行
        assert len(result) == 2

    def test_columns_present(self, long_records: list[dict[str, str]]) -> None:
        result = long_to_wide(
            long_records,
            id_col="gene",
            variable_col="variable",
            value_col="value",
        )
        assert "gene" in result[0]
        assert "sample_A" in result[0]
        assert "sample_B" in result[0]

    def test_values_preserved(self, long_records: list[dict[str, str]]) -> None:
        result = long_to_wide(
            long_records,
            id_col="gene",
            variable_col="variable",
            value_col="value",
        )
        tp53 = next(r for r in result if r["gene"] == "TP53")
        assert tp53["sample_A"] == "10.5"
        assert tp53["sample_B"] == "20.3"


class TestRoundtrip:
    """wide → long → wide の往復変換テスト."""

    def test_wide_long_wide(self) -> None:
        original = [
            {"gene": "TP53", "sample_A": "10.5", "sample_B": "20.3"},
            {"gene": "BRCA1", "sample_A": "5.2", "sample_B": "8.1"},
        ]
        long_form = wide_to_long(
            original,
            id_col="gene",
            value_cols=["sample_A", "sample_B"],
        )
        restored = long_to_wide(
            long_form,
            id_col="gene",
            variable_col="variable",
            value_col="value",
        )
        # 元の形に戻ること
        assert len(restored) == 2
        tp53 = next(r for r in restored if r["gene"] == "TP53")
        assert tp53["sample_A"] == "10.5"
        assert tp53["sample_B"] == "20.3"
