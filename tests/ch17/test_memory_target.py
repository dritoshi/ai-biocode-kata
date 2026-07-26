"""メモリプロファイリング対象コードのテスト."""

import numpy as np

from scripts.ch17.memory_target import load_large_data


def test_load_large_data_returns_reproducible_column_means() -> None:
    result = load_large_data(n_rows=4, n_columns=3, seed=7)
    expected = np.random.default_rng(7).random((4, 3)).mean(axis=0)

    np.testing.assert_allclose(result, expected)
    assert result.shape == (3,)
