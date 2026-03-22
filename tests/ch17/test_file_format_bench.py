"""CSV/Parquet往復保存の一致テスト."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts.ch17.file_format_bench import (
    benchmark_read,
    compare_formats,
    save_as_csv,
    save_as_parquet,
)

pyarrow = pytest.importorskip("pyarrow", reason="pyarrow が必要")


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    """テスト用の発現量DataFrameを生成するフィクスチャ."""
    rng = np.random.default_rng(42)
    data = rng.random((100, 10))
    gene_ids = [f"GENE_{i:04d}" for i in range(100)]
    sample_ids = [f"SAMPLE_{j:03d}" for j in range(10)]
    return pd.DataFrame(data, index=gene_ids, columns=sample_ids)


class TestSaveAsCsv:
    """save_as_csv のテスト."""

    def test_roundtrip(self, tmp_path: Path, sample_df: pd.DataFrame) -> None:
        """CSV保存→読み込みでデータが一致する."""
        csv_path = tmp_path / "test.csv"
        save_as_csv(sample_df, csv_path)
        loaded = pd.read_csv(csv_path, index_col=0)
        pd.testing.assert_frame_equal(loaded, sample_df, rtol=1e-10)


class TestSaveAsParquet:
    """save_as_parquet のテスト."""

    def test_roundtrip(self, tmp_path: Path, sample_df: pd.DataFrame) -> None:
        """Parquet保存→読み込みでデータが一致する."""
        parquet_path = tmp_path / "test.parquet"
        save_as_parquet(sample_df, parquet_path)
        loaded = pd.read_parquet(parquet_path)
        pd.testing.assert_frame_equal(loaded, sample_df)


class TestBenchmarkRead:
    """benchmark_read のテスト."""

    def test_csv_read(self, tmp_path: Path, sample_df: pd.DataFrame) -> None:
        """CSV読み込み時間が正の値を返す."""
        csv_path = tmp_path / "test.csv"
        save_as_csv(sample_df, csv_path)
        elapsed = benchmark_read(csv_path)
        assert elapsed > 0

    def test_parquet_read(self, tmp_path: Path, sample_df: pd.DataFrame) -> None:
        """Parquet読み込み時間が正の値を返す."""
        parquet_path = tmp_path / "test.parquet"
        save_as_parquet(sample_df, parquet_path)
        elapsed = benchmark_read(parquet_path)
        assert elapsed > 0

    def test_unsupported_format(self, tmp_path: Path) -> None:
        """未対応のファイル形式でエラーを返す."""
        fake_path = tmp_path / "test.xlsx"
        fake_path.touch()
        with pytest.raises(ValueError, match="未対応"):
            benchmark_read(fake_path)


class TestCompareFormats:
    """compare_formats のテスト."""

    def test_returns_both_formats(self, tmp_path: Path, sample_df: pd.DataFrame) -> None:
        """CSV/Parquet両方の結果を含む辞書を返す."""
        result = compare_formats(sample_df, tmp_path)
        assert "csv" in result
        assert "parquet" in result
        assert "size_bytes" in result["csv"]
        assert "read_time" in result["csv"]
        assert result["csv"]["size_bytes"] > 0
        assert result["parquet"]["size_bytes"] > 0
