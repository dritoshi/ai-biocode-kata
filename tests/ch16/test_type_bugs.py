"""type_bugs.py のテスト."""

import math

import pandas as pd
import pytest

from scripts.ch16.type_bugs import (
    detect_nan_in_dataframe,
    safe_mean,
    sum_expression_values_buggy,
    sum_expression_values_fixed,
)


class TestSumExpressionValuesBuggy:
    """バグ版が文字列連結を行うことを実証するテスト."""

    def test_demonstrates_string_concatenation(self):
        """数値のつもりが文字列連結になるバグを実証."""
        result = sum_expression_values_buggy(["1.5", "2.3", "0.8"])
        # バグ版は文字列連結する
        assert result == "1.52.30.8"
        assert isinstance(result, str)


class TestSumExpressionValuesFixed:
    """修正版 sum_expression_values_fixed のテスト."""

    def test_normal_sum(self):
        """正常な合計計算."""
        result = sum_expression_values_fixed(["1.5", "2.3", "0.8"])
        assert result == pytest.approx(4.6)

    def test_empty_list(self):
        """空リストは 0.0 を返す."""
        result = sum_expression_values_fixed([])
        assert result == pytest.approx(0.0)

    def test_invalid_value(self):
        """数値変換不能な値で ValueError."""
        with pytest.raises(ValueError):
            sum_expression_values_fixed(["1.0", "abc"])


class TestSafeMean:
    """safe_mean のテスト."""

    def test_normal_values(self):
        """正常な値の平均."""
        result = safe_mean([1.0, 2.0, 3.0])
        assert result == pytest.approx(2.0)

    def test_with_none(self):
        """None混在でNoneを除外して平均."""
        result = safe_mean([1.0, None, 3.0])
        assert result == pytest.approx(2.0)

    def test_with_nan(self):
        """NaN混在でNaNを除外して平均."""
        result = safe_mean([1.0, float("nan"), 3.0])
        assert result == pytest.approx(2.0)

    def test_all_none(self):
        """全て None の場合は None を返す."""
        result = safe_mean([None, None])
        assert result is None

    def test_empty(self):
        """空リストは None を返す."""
        result = safe_mean([])
        assert result is None


class TestDetectNanInDataframe:
    """detect_nan_in_dataframe のテスト."""

    def test_with_nan(self):
        """NaN含有列を正しく検出する."""
        df = pd.DataFrame({
            "gene": ["A", "B", "C"],
            "expr1": [1.0, float("nan"), 3.0],
            "expr2": [4.0, 5.0, 6.0],
        })
        result = detect_nan_in_dataframe(df)
        assert result["expr1"] == 1
        assert result["expr2"] == 0
        assert result["gene"] == 0

    def test_no_nan(self):
        """NaNがない場合は全て0."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        result = detect_nan_in_dataframe(df)
        assert result["a"] == 0
        assert result["b"] == 0
