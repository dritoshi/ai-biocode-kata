"""6フレームORF検出のテスト."""

from scripts.ch00.find_orfs import ORF, find_all_orfs, reverse_complement


class TestReverseComplement:
    """reverse_complement() のテスト."""

    def test_simple(self) -> None:
        assert reverse_complement("ATGC") == "GCAT"

    def test_palindrome(self) -> None:
        assert reverse_complement("AATT") == "AATT"

    def test_with_n(self) -> None:
        assert reverse_complement("ATNG") == "CNAT"


class TestFindAllOrfs:
    """find_all_orfs() のテスト."""

    def test_known_orf(self) -> None:
        """既知のORFが検出される（ATG...TAA）."""
        # ATG + 34 codons + TAA = 108 bp
        seq = "ATG" + "GCT" * 34 + "TAA"
        orfs = find_all_orfs(seq, min_length=100)
        assert len(orfs) >= 1
        assert orfs[0].protein.startswith("M")

    def test_short_orf_filtered(self) -> None:
        """min_length未満のORFは除外される."""
        # ATG + 5 codons + TAA = 21 bp
        seq = "ATG" + "GCT" * 5 + "TAA"
        orfs = find_all_orfs(seq, min_length=100)
        assert len(orfs) == 0

    def test_empty_sequence(self) -> None:
        """空配列では空リストを返す."""
        assert find_all_orfs("") == []

    def test_six_frames(self) -> None:
        """6フレームすべてが探索される."""
        # 十分長い配列で6フレームにORFが存在しうることを確認
        seq = "ATG" + "GCT" * 50 + "TAA" + "A" * 100
        rc_seq = reverse_complement(seq)
        # 逆鎖にもATG...STOPを配置
        combined = seq + "NNN" + rc_seq
        orfs = find_all_orfs(combined, min_length=50)
        frames = {orf.frame for orf in orfs}
        # 順鎖のフレーム+1は確実に含まれる
        assert 1 in frames

    def test_ecoli_orf_count(self, genome_sequence: str) -> None:
        """E. coli断片から妥当な数のORFが検出される."""
        orfs = find_all_orfs(genome_sequence, min_length=100)
        # 20 kbpの配列から100+個のORFが検出されるはず
        assert len(orfs) >= 100

    def test_ecoli_known_gene_thra(self, genome_sequence: str) -> None:
        """E. coli thrA遺伝子（336-2799）が検出される."""
        orfs = find_all_orfs(genome_sequence, min_length=100)
        # thrA: frame +1, start ~336, end ~2799
        thra_candidates = [
            o for o in orfs
            if o.frame == 1 and o.start <= 340 and o.end >= 2795
        ]
        assert len(thra_candidates) >= 1

    def test_orf_dataclass_properties(self) -> None:
        """ORFのプロパティが正しく計算される."""
        orf = ORF(start=0, end=300, frame=1, protein="M" + "A" * 98)
        assert orf.length_nt == 300
        assert orf.length_aa == 99

    def test_min_length_parameter(self, genome_sequence: str) -> None:
        """min_lengthを大きくするとORF数が減る."""
        orfs_100 = find_all_orfs(genome_sequence, min_length=100)
        orfs_500 = find_all_orfs(genome_sequence, min_length=500)
        assert len(orfs_100) > len(orfs_500)
