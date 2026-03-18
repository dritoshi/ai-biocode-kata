"""逆相補鎖計算のテスト — TDDのデモ."""

from scripts.ch07.reverse_complement import reverse_complement


class TestReverseComplement:
    """reverse_complement() のテスト."""

    def test_simple_sequence(self) -> None:
        """ATGCの逆相補鎖はGCATである."""
        assert reverse_complement("ATGC") == "GCAT"

    def test_all_same_base(self) -> None:
        """同一塩基の配列."""
        assert reverse_complement("AAAA") == "TTTT"
        assert reverse_complement("CCCC") == "GGGG"

    def test_palindrome(self) -> None:
        """回文配列: 逆相補鎖が元の配列と同じ."""
        assert reverse_complement("ATAT") == "ATAT"
        assert reverse_complement("GCGC") == "GCGC"

    def test_empty_sequence(self) -> None:
        """空文字列には空文字列を返す."""
        assert reverse_complement("") == ""

    def test_case_insensitive(self) -> None:
        """小文字の入力も受け付ける."""
        assert reverse_complement("atgc") == "GCAT"

    def test_single_base(self) -> None:
        """1塩基の配列."""
        assert reverse_complement("A") == "T"
        assert reverse_complement("G") == "C"

    def test_long_sequence(self) -> None:
        """やや長い配列."""
        seq = "ATGCGATCGA"
        # 手計算: 逆順 AGCTAGCGTA → 相補 TCGATCGCAT
        assert reverse_complement(seq) == "TCGATCGCAT"
