"""debug_print_demo.py のテスト."""

import logging

from scripts.ch09.debug_print_demo import (
    filter_sequences_logging_debug,
    filter_sequences_print_debug,
)


class TestFilterSequencesPrintDebug:
    """filter_sequences_print_debug のテスト."""

    def test_basic_filtering(self):
        """最小長でフィルタリングされることを確認."""
        seqs = ["ATCG", "AT", "ATCGATCG", "A"]
        result = filter_sequences_print_debug(seqs, min_length=3)
        assert result == ["ATCG", "ATCGATCG"]

    def test_empty_input(self):
        """空リスト入力で空リストが返る."""
        assert filter_sequences_print_debug([], min_length=5) == []

    def test_all_pass(self):
        """全配列が条件を満たす場合、すべて返される."""
        seqs = ["AAAA", "TTTT", "CCCC"]
        result = filter_sequences_print_debug(seqs, min_length=4)
        assert result == seqs

    def test_none_pass(self):
        """全配列が条件を満たさない場合、空リストが返る."""
        seqs = ["A", "T", "C"]
        result = filter_sequences_print_debug(seqs, min_length=5)
        assert result == []


class TestFilterSequencesLoggingDebug:
    """filter_sequences_logging_debug のテスト."""

    def test_basic_filtering(self):
        """最小長でフィルタリングされることを確認."""
        seqs = ["ATCG", "AT", "ATCGATCG", "A"]
        result = filter_sequences_logging_debug(seqs, min_length=3)
        assert result == ["ATCG", "ATCGATCG"]

    def test_empty_input(self):
        """空リスト入力で空リストが返る."""
        assert filter_sequences_logging_debug([], min_length=5) == []

    def test_logging_output(self, caplog):
        """DEBUGレベルのログが出力されることを確認."""
        seqs = ["ATCG", "AT"]
        with caplog.at_level(logging.DEBUG):
            filter_sequences_logging_debug(seqs, min_length=3)
        assert "フィルタ開始" in caplog.text
        assert "フィルタ完了" in caplog.text
        assert "採用" in caplog.text
        assert "除外" in caplog.text
