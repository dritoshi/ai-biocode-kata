"""python_pitfalls.py のテスト."""

import numpy as np
import pandas as pd

from scripts.ch09.python_pitfalls import (
    add_gene_buggy,
    add_gene_fixed,
    deep_copy_demo,
    demonstrate_numpy_copy,
    demonstrate_numpy_view,
    filter_with_loc,
    remove_n_buggy,
    remove_n_fixed,
    shallow_copy_demo,
)


class TestMutableDefault:
    """ミュータブルデフォルト引数のテスト."""

    def test_buggy_shares_list(self) -> None:
        """バグ版: 2回呼ぶと状態が共有される."""
        # デフォルト引数をリセットするため直接テスト
        add_gene_buggy.__defaults__ = ([],)
        result1 = add_gene_buggy("BRCA1")
        result2 = add_gene_buggy("TP53")
        # 2回目の呼び出しで1回目の結果も含まれている
        assert result2 == ["BRCA1", "TP53"]
        assert result1 is result2  # 同じリストオブジェクト

    def test_fixed_independent(self) -> None:
        """修正版: 2回呼んでも独立."""
        result1 = add_gene_fixed("BRCA1")
        result2 = add_gene_fixed("TP53")
        assert result1 == ["BRCA1"]
        assert result2 == ["TP53"]
        assert result1 is not result2


class TestCopy:
    """浅いコピー vs 深いコピーのテスト."""

    def test_shallow_shares_nested(self) -> None:
        """浅いコピー: ネストされたリストへの変更が元に伝播する."""
        original, shallow = shallow_copy_demo()
        assert "EGFR" in original["genes"]
        assert "EGFR" in shallow["genes"]

    def test_deep_independent(self) -> None:
        """深いコピー: ネストされたリストへの変更が元に伝播しない."""
        original, deep = deep_copy_demo()
        assert "MYC" not in original["genes"]
        assert "MYC" in deep["genes"]


class TestStringImmutability:
    """文字列不変性のテスト."""

    def test_buggy_returns_original(self) -> None:
        """バグ版: 元の文字列（Nを含む）をそのまま返す."""
        result = remove_n_buggy("ATGCN")
        assert result == "ATGCN"

    def test_fixed_removes_n(self) -> None:
        """修正版: N を除去した文字列を返す."""
        result = remove_n_fixed("ATGCN")
        assert result == "ATGC"


class TestPandasLoc:
    """pandas .loc[] によるSettingWithCopyWarning回避のテスト."""

    def test_loc_modifies_correctly(self) -> None:
        """.loc[] で条件を満たす行の値が正しく更新される."""
        df = pd.DataFrame({"gene": ["BRCA1", "TP53"], "score": [0.9, 0.3]})
        result = filter_with_loc(df, threshold=0.5)
        assert result.loc[0, "gene"] == "HIGH"
        assert result.loc[1, "gene"] == "TP53"


class TestNumpyViewVsCopy:
    """NumPy ビュー vs コピーのテスト."""

    def test_view_shares_memory(self) -> None:
        """スライスはビューを返し、メモリを共有する."""
        _arr, _view, shares = demonstrate_numpy_view()
        assert shares is True

    def test_copy_does_not_share(self) -> None:
        """ファンシーインデックスはコピーを返し、メモリを共有しない."""
        _arr, _copy, shares = demonstrate_numpy_copy()
        assert shares is False

    def test_view_mutation_propagates(self) -> None:
        """ビューへの変更が元配列に反映される."""
        arr, view, _ = demonstrate_numpy_view()
        view[0] = 999
        assert arr[0] == 999

    def test_copy_mutation_independent(self) -> None:
        """コピーへの変更が元配列に反映されない."""
        arr, copy_arr, _ = demonstrate_numpy_copy()
        original_first = arr[0]
        copy_arr[0] = 888
        assert arr[0] == original_first
