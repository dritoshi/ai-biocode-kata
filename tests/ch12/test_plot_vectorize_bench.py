"""GC含量ベンチマーク実装の直接テスト."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

from scripts.ch12 import plot_vectorize_bench as bench


def test_gc_contents_slow_values() -> None:
    """塩基ごとのループ版がGC含量を正しく返す."""
    result = bench.gc_contents_slow(["ATGC", "GGGG", "AAAA"])
    assert result == pytest.approx([0.5, 1.0, 0.0])


def test_gc_contents_slow_empty_input() -> None:
    """空リストには空リストを返す."""
    assert bench.gc_contents_slow([]) == []


def test_gc_content_per_seq_values_shape_and_dtype() -> None:
    """配列ごとのNumPy版が値・形状・dtypeを保つ."""
    result = bench.gc_content_per_seq(["ATGC", "GGGG", "AAAA"])
    np.testing.assert_allclose(result, [0.5, 1.0, 0.0])
    assert result.shape == (3,)
    assert result.dtype == np.float64


def test_gc_content_per_seq_empty_input() -> None:
    """空リストにはfloat64の空配列を返す."""
    result = bench.gc_content_per_seq([])
    assert result.shape == (0,)
    assert result.dtype == np.float64


def test_benchmark_calls_all_four_implementations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ベンチマークが比較対象4実装をすべて呼び出す."""
    calls: list[Callable[[list[str]], object]] = []

    def fake_best_ms(
        fn: Callable[[list[str]], object],
        sequences: list[str],
        reps: int = 5,
    ) -> float:
        assert len(sequences) == 2
        assert reps == 5
        calls.append(fn)
        return float(len(calls))

    monkeypatch.setattr(bench, "_best_ms", fake_best_ms)
    result = bench.benchmark_gc_calculation(n_sequences=2, seq_length=4)

    assert calls == [
        bench.gc_contents_slow,
        bench._gc_str_count,
        bench.gc_content_per_seq,
        bench.gc_content_vectorized,
    ]
    assert result == {
        "per-base\nloop": 1.0,
        "str.count": 2.0,
        "per-seq\nNumPy": 3.0,
        "batch\nNumPy": 4.0,
    }


def test_main_logs_saved_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """図の保存先をprintではなくINFOログへ記録する."""
    output_paths: list[Path | None] = []

    def fake_plot(output_path: Path | None = None) -> plt.Figure:
        output_paths.append(output_path)
        return plt.figure()

    monkeypatch.setattr(bench, "FIGURES_DIR", tmp_path)
    monkeypatch.setattr(bench, "plot_vectorize_bench", fake_plot)
    with caplog.at_level(logging.INFO, logger=bench.__name__):
        bench.main()

    expected = tmp_path / "ch12_vectorize_bench.png"
    assert output_paths == [expected]
    assert f"Saved: {expected}" in caplog.text
