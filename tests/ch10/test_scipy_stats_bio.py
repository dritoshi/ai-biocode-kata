"""統計検定・距離行列のテスト."""

import numpy as np
import pytest

from scripts.ch10.scipy_stats_bio import (
    compare_expression,
    correct_pvalues,
    expression_distance_matrix,
)


class TestCompareExpression:
    """compare_expression のテスト."""

    def test_significant_difference(self) -> None:
        """明確に異なる2群は有意差あり."""
        rng = np.random.default_rng(42)
        group1 = rng.normal(loc=10, scale=1, size=50)
        group2 = rng.normal(loc=15, scale=1, size=50)
        t_stat, p_value = compare_expression(group1, group2)
        assert p_value < 0.001
        # group1 < group2 なので t_stat は負
        assert t_stat < 0

    def test_no_significant_difference(self) -> None:
        """同じ分布からの2群は有意差なし."""
        rng = np.random.default_rng(42)
        group1 = rng.normal(loc=10, scale=1, size=50)
        group2 = rng.normal(loc=10, scale=1, size=50)
        _, p_value = compare_expression(group1, group2)
        assert p_value > 0.05

    def test_returns_tuple(self) -> None:
        """戻り値が (t統計量, p値) のタプル."""
        group1 = np.array([1.0, 2.0, 3.0])
        group2 = np.array([4.0, 5.0, 6.0])
        result = compare_expression(group1, group2)
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestCorrectPvalues:
    """correct_pvalues のテスト."""

    def test_basic(self) -> None:
        """BH法で補正されたp値が元のp値以上になる."""
        pvalues = np.array([0.001, 0.01, 0.05, 0.1, 0.5])
        adjusted = correct_pvalues(pvalues)
        # 補正後のp値は元のp値以上
        assert np.all(adjusted >= pvalues)

    def test_monotonicity(self) -> None:
        """ソート済みp値に対して、補正後も単調非減少."""
        pvalues = np.array([0.001, 0.004, 0.01, 0.02, 0.05])
        adjusted = correct_pvalues(pvalues)
        # ソート済みp値に対する補正後は単調非減少
        sorted_idx = np.argsort(pvalues)
        sorted_adjusted = adjusted[sorted_idx]
        assert np.all(sorted_adjusted[1:] >= sorted_adjusted[:-1])

    def test_bounded(self) -> None:
        """補正後のp値は0〜1の範囲."""
        pvalues = np.array([0.5, 0.8, 0.9, 0.95, 0.99])
        adjusted = correct_pvalues(pvalues)
        assert np.all(adjusted >= 0.0)
        assert np.all(adjusted <= 1.0)

    def test_empty(self) -> None:
        """空配列の場合は空配列を返す."""
        result = correct_pvalues(np.array([]))
        assert len(result) == 0

    def test_single(self) -> None:
        """1つのp値の場合、そのまま返る."""
        result = correct_pvalues(np.array([0.03]))
        assert result[0] == pytest.approx(0.03)

    def test_known_values(self) -> None:
        """既知の値で検証."""
        # 5つのp値、n=5
        # rank: 1,2,3,4,5
        # p * n/rank: 0.005*5/1, 0.01*5/2, 0.03*5/3, 0.04*5/4, 0.5*5/5
        #           = 0.025, 0.025, 0.05, 0.05, 0.5
        pvalues = np.array([0.005, 0.01, 0.03, 0.04, 0.5])
        adjusted = correct_pvalues(pvalues)
        expected = np.array([0.025, 0.025, 0.05, 0.05, 0.5])
        np.testing.assert_allclose(adjusted, expected)


class TestExpressionDistanceMatrix:
    """expression_distance_matrix のテスト."""

    def test_symmetric(self) -> None:
        """距離行列は対称行列."""
        rng = np.random.default_rng(42)
        matrix = rng.random((100, 5))
        dist = expression_distance_matrix(matrix)
        np.testing.assert_allclose(dist, dist.T)

    def test_diagonal_zero(self) -> None:
        """対角成分はゼロ."""
        rng = np.random.default_rng(42)
        matrix = rng.random((100, 4))
        dist = expression_distance_matrix(matrix)
        np.testing.assert_allclose(np.diag(dist), 0.0, atol=1e-10)

    def test_shape(self) -> None:
        """出力は (サンプル数 x サンプル数) の正方行列."""
        matrix = np.random.default_rng(42).random((50, 3))
        dist = expression_distance_matrix(matrix)
        assert dist.shape == (3, 3)

    def test_identical_samples(self) -> None:
        """同一のサンプル間の距離は0."""
        # 全列が同じ
        col = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        matrix = np.column_stack([col, col, col])
        dist = expression_distance_matrix(matrix)
        np.testing.assert_allclose(dist, 0.0, atol=1e-10)
