"""TPM正規化の正確性テスト."""

import builtins
import importlib.util
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import numpy as np

from scripts.ch17.profiling_demo import (
    main,
    normalize_tpm_fast,
    normalize_tpm_slow,
    profile,
    profile_pipeline,
    profiled_normalize_tpm_slow,
)


class TestNormalizeTpmSlow:
    """normalize_tpm_slow のテスト."""

    def test_basic_tpm(self) -> None:
        """基本的なTPM正規化の計算結果が正しい."""
        counts = np.array([[100, 200], [300, 400]], dtype=np.float64)
        gene_lengths = np.array([1000, 2000], dtype=np.float64)
        result = normalize_tpm_slow(counts, gene_lengths)
        # 各サンプルの列合計が約100万になることを確認
        col_sums = result.sum(axis=0)
        np.testing.assert_allclose(col_sums, [1_000_000, 1_000_000], rtol=1e-6)

    def test_single_gene(self) -> None:
        """遺伝子が1つだけの場合、TPMは全サンプルで100万."""
        counts = np.array([[50, 100]], dtype=np.float64)
        gene_lengths = np.array([500], dtype=np.float64)
        result = normalize_tpm_slow(counts, gene_lengths)
        np.testing.assert_allclose(result, [[1_000_000, 1_000_000]], rtol=1e-6)

    def test_proportional_distribution(self) -> None:
        """同じ遺伝子長の場合、TPMはカウントの比率を反映する."""
        counts = np.array([[100], [300]], dtype=np.float64)
        gene_lengths = np.array([1000, 1000], dtype=np.float64)
        result = normalize_tpm_slow(counts, gene_lengths)
        # 1:3 の比率が保たれる
        np.testing.assert_allclose(result[0, 0] / result[1, 0], 1 / 3, rtol=1e-6)

    def test_empty_gene_axis_preserves_shape(self) -> None:
        """遺伝子が0件でもサンプル軸を保った空行列を返す."""
        counts: np.ndarray = np.empty((0, 2), dtype=np.float64)
        gene_lengths: np.ndarray = np.empty(0, dtype=np.float64)
        result = normalize_tpm_slow(counts, gene_lengths)
        assert result.shape == (0, 2)
        assert result.dtype == np.float64


class TestLineProfilerIntegration:
    """line_profiler用デコレータの切り替えを検証する."""

    def test_fallback_is_no_op(self) -> None:
        """通常import時のfallbackは関数を変更しない."""

        def identity(value: int) -> int:
            return value

        assert profile(identity) is identity
        assert profiled_normalize_tpm_slow is normalize_tpm_slow

    def test_uses_kernprof_injected_decorator(
        self, monkeypatch
    ) -> None:
        """builtinsへ注入されたデコレータを利用する."""
        decorated: list[str] = []

        def injected_profile(
            func: Callable[..., object],
        ) -> Callable[..., object]:
            decorated.append(func.__name__)
            return func

        monkeypatch.setattr(
            builtins,
            "profile",
            injected_profile,
            raising=False,
        )
        module_path = (
            Path(__file__).parents[2]
            / "scripts"
            / "ch17"
            / "profiling_demo.py"
        )
        spec = importlib.util.spec_from_file_location(
            "profiling_demo_with_kernprof",
            module_path,
        )
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        assert isinstance(module, ModuleType)
        spec.loader.exec_module(module)

        assert decorated == ["normalize_tpm_slow"]

    def test_main_runs_profiled_calculation(self) -> None:
        """最小main入口が計算を完了する."""
        main()


class TestNormalizeTpmFast:
    """normalize_tpm_fast のテスト."""

    def test_basic_tpm(self) -> None:
        """基本的なTPM正規化の計算結果が正しい."""
        counts = np.array([[100, 200], [300, 400]], dtype=np.float64)
        gene_lengths = np.array([1000, 2000], dtype=np.float64)
        result = normalize_tpm_fast(counts, gene_lengths)
        col_sums = result.sum(axis=0)
        np.testing.assert_allclose(col_sums, [1_000_000, 1_000_000], rtol=1e-6)

    def test_matches_slow_version(self) -> None:
        """速い版と遅い版の計算結果が一致する."""
        rng = np.random.default_rng(42)
        counts = rng.integers(0, 1000, size=(50, 10)).astype(np.float64)
        gene_lengths = rng.integers(500, 5000, size=50).astype(np.float64)
        slow = normalize_tpm_slow(counts, gene_lengths)
        fast = normalize_tpm_fast(counts, gene_lengths)
        np.testing.assert_allclose(fast, slow, rtol=1e-10)

    def test_preserves_shape(self) -> None:
        """ベクトル化後も遺伝子×サンプルの形状を保つ."""
        counts: np.ndarray = np.ones((3, 2), dtype=np.float64)
        gene_lengths = np.array([500, 1000, 2000], dtype=np.float64)
        result = normalize_tpm_fast(counts, gene_lengths)
        assert result.shape == counts.shape

    def test_zero_gene_length_matches_slow_version(self) -> None:
        """長さ0を含む入力でもslow版と同じ非有限値を返す."""
        counts = np.array([[10.0], [20.0]])
        gene_lengths = np.array([0.0, 1000.0])
        with np.errstate(divide="ignore", invalid="ignore"):
            slow = normalize_tpm_slow(counts, gene_lengths)
            fast = normalize_tpm_fast(counts, gene_lengths)
        np.testing.assert_allclose(fast, slow, equal_nan=True)


class TestProfilePipeline:
    """profile_pipeline のテスト."""

    def test_returns_stats(self) -> None:
        """pstats.Stats オブジェクトを返す."""
        import pstats

        counts = np.array([[100, 200]], dtype=np.float64)
        gene_lengths = np.array([1000], dtype=np.float64)
        stats = profile_pipeline(normalize_tpm_fast, counts, gene_lengths)
        assert isinstance(stats, pstats.Stats)
