"""浮動小数点の罠デモのテスト."""

import math

import pytest

from scripts.ch03.float_pitfalls import (
    accurate_sum,
    demonstrate_nan_behavior,
    naive_float_equal,
    naive_sum,
    safe_float_equal,
    safe_log_pvalue,
)


class TestNaiveFloatEqual:
    """naive_float_equal() のテスト."""

    def test_exact_match(self) -> None:
        assert naive_float_equal(1.0, 1.0) is True

    def test_classic_trap(self) -> None:
        # 0.1 + 0.2 != 0.3 が再現されること
        assert naive_float_equal(0.1 + 0.2, 0.3) is False


class TestSafeFloatEqual:
    """safe_float_equal() のテスト."""

    def test_classic_trap_resolved(self) -> None:
        # math.isclose() なら 0.1 + 0.2 ≈ 0.3
        assert safe_float_equal(0.1 + 0.2, 0.3) is True

    def test_exact_match(self) -> None:
        assert safe_float_equal(1.0, 1.0) is True

    def test_clearly_different(self) -> None:
        assert safe_float_equal(1.0, 2.0) is False


class TestNaiveSum:
    """naive_sum() のテスト."""

    def test_simple_sum(self) -> None:
        assert naive_sum([1.0, 2.0, 3.0]) == pytest.approx(6.0)

    def test_empty(self) -> None:
        assert naive_sum([]) == 0.0


class TestAccurateSum:
    """accurate_sum() のテスト."""

    def test_simple_sum(self) -> None:
        assert accurate_sum([1.0, 2.0, 3.0]) == pytest.approx(6.0)

    def test_many_small_values(self) -> None:
        # 0.1 を10回足すと、sum()では誤差が出るが fsum()は正確
        values = [0.1] * 10
        assert accurate_sum(values) == 1.0

    def test_empty(self) -> None:
        assert accurate_sum([]) == 0.0


class TestSafeLogPvalue:
    """safe_log_pvalue() のテスト."""

    def test_normal_pvalue(self) -> None:
        assert safe_log_pvalue(0.01) == pytest.approx(-2.0)

    def test_very_small_pvalue(self) -> None:
        assert safe_log_pvalue(1e-300) == pytest.approx(-300.0)

    def test_zero_pvalue(self) -> None:
        assert safe_log_pvalue(0.0) == float("-inf")

    def test_negative_pvalue(self) -> None:
        assert safe_log_pvalue(-0.01) == float("-inf")

    def test_pvalue_one(self) -> None:
        assert safe_log_pvalue(1.0) == pytest.approx(0.0)


class TestDemonstrateNanBehavior:
    """demonstrate_nan_behavior() のテスト."""

    def test_nan_properties(self) -> None:
        result = demonstrate_nan_behavior()
        # NaN は自分自身と等しくない
        assert result["nan == nan"] is False
        assert result["nan != nan"] is True
        # NaN は比較で常に False
        assert result["nan < 0"] is False
        assert result["nan > 0"] is False
        # math.isnan() でのみ判定可能
        assert result["math.isnan(nan)"] is True
