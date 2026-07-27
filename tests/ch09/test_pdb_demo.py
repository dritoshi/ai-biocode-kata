"""pdb_demo.py のテスト."""

import pytest

from scripts.ch09.pdb_demo import (
    calculate_gc_stats,
    calculate_gc_stats_debug,
    find_motif_positions,
)


class TestCalculateGcStats:
    """calculate_gc_stats のテスト."""

    def test_multiple_sequences(self):
        """複数配列のGC含量統計を正しく計算する."""
        seqs = ["GCGC", "ATAT", "GCAT"]
        stats = calculate_gc_stats(seqs)
        assert stats["mean_gc"] == pytest.approx(0.5)
        assert stats["min_gc"] == pytest.approx(0.0)
        assert stats["max_gc"] == pytest.approx(1.0)

    def test_empty_list(self):
        """空リストの場合は全て0.0を返す."""
        stats = calculate_gc_stats([])
        assert stats == {"mean_gc": 0.0, "min_gc": 0.0, "max_gc": 0.0}

    def test_all_gc(self):
        """全てGCの配列はGC含量1.0."""
        stats = calculate_gc_stats(["GCGCGC"])
        assert stats["mean_gc"] == pytest.approx(1.0)

    def test_case_insensitive(self):
        """大文字・小文字を区別しない."""
        stats = calculate_gc_stats(["gcgc", "GCGC"])
        assert stats["mean_gc"] == pytest.approx(1.0)


class TestCalculateGcStatsDebug:
    """calculate_gc_stats_debug のテスト."""

    def test_breakpoint_runs_for_each_sequence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """各配列の計算後にbreakpointを1回ずつ呼ぶ."""
        breakpoint_calls: list[bool] = []

        def fake_breakpoint() -> None:
            breakpoint_calls.append(True)

        monkeypatch.setattr("builtins.breakpoint", fake_breakpoint)

        stats = calculate_gc_stats_debug(["GCGC", "ATAT"])

        assert stats["mean_gc"] == pytest.approx(0.5)
        assert len(breakpoint_calls) == 2

    def test_empty_list_does_not_start_debugger(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """空リストではデバッガを起動せずゼロ値を返す."""

        def fail_if_called() -> None:
            pytest.fail("空リストでbreakpointが呼ばれた")

        monkeypatch.setattr("builtins.breakpoint", fail_if_called)

        stats = calculate_gc_stats_debug([])

        assert stats == {"mean_gc": 0.0, "min_gc": 0.0, "max_gc": 0.0}


class TestFindMotifPositions:
    """find_motif_positions のテスト."""

    def test_multiple_hits(self):
        """複数の出現位置を正しく返す."""
        positions = find_motif_positions("ATGATGATG", "ATG")
        assert positions == [0, 3, 6]

    def test_no_hit(self):
        """モチーフが見つからない場合は空リストを返す."""
        positions = find_motif_positions("AAAA", "GC")
        assert positions == []

    def test_overlapping(self):
        """重複するモチーフを検出する."""
        positions = find_motif_positions("AAAA", "AA")
        assert positions == [0, 1, 2]

    def test_case_insensitive(self):
        """大文字・小文字を区別しない."""
        positions = find_motif_positions("atgatg", "ATG")
        assert positions == [0, 3]

    def test_single_hit(self):
        """1箇所のみヒットする場合."""
        positions = find_motif_positions("TTTGATTT", "GA")
        assert positions == [3]
