"""配列統計とFASTAフィルタリングのテスト."""

from pathlib import Path

import pytest

from scripts.ch07.seq_stats import filter_fasta_by_gc, gc_content


class TestGcContent:
    """gc_content() のテスト."""

    def test_typical_sequence(self) -> None:
        """標準的なDNA配列."""
        assert gc_content("ATGC") == pytest.approx(0.5)

    def test_all_gc(self) -> None:
        """GC含量100%."""
        assert gc_content("GCGCGC") == pytest.approx(1.0)

    def test_no_gc(self) -> None:
        """GC含量0%."""
        assert gc_content("AATTAA") == pytest.approx(0.0)

    def test_empty_string(self) -> None:
        """空文字列には0.0を返す."""
        assert gc_content("") == 0.0

    def test_case_insensitive(self) -> None:
        """小文字の入力."""
        assert gc_content("atgc") == pytest.approx(0.5)

    def test_single_base(self) -> None:
        """1塩基の配列."""
        assert gc_content("G") == pytest.approx(1.0)
        assert gc_content("A") == pytest.approx(0.0)

    def test_with_n(self) -> None:
        """N（不明塩基）を含む配列."""
        # NはGC/ATどちらにもカウントされないが、分母には含まれる
        result = gc_content("ATNGC")
        assert 0.0 <= result <= 1.0
        assert result == pytest.approx(2 / 5)


class TestFilterFastaByGc:
    """filter_fasta_by_gc() のテスト."""

    @pytest.fixture()
    def input_fasta(self, tmp_path: Path) -> Path:
        """テスト用FASTAファイルを作成する."""
        fasta_path = tmp_path / "input.fasta"
        fasta_path.write_text(
            ">seq1\nGCGCGCGC\n"
            ">seq2\nAAAATTTT\n"
            ">seq3\nATGCATGC\n"
        )
        return fasta_path

    def test_filter_high_gc(self, input_fasta: Path, tmp_path: Path) -> None:
        """GC含量が高い配列のみ抽出する."""
        output = tmp_path / "output.fasta"
        count = filter_fasta_by_gc(input_fasta, output, min_gc=0.4)
        assert count == 2
        text = output.read_text()
        assert "seq1" in text
        assert "seq3" in text
        assert "seq2" not in text

    def test_filter_low_gc(self, input_fasta: Path, tmp_path: Path) -> None:
        """GC含量が低い配列のみ抽出する."""
        output = tmp_path / "output.fasta"
        count = filter_fasta_by_gc(input_fasta, output, max_gc=0.1)
        assert count == 1
        text = output.read_text()
        assert "seq2" in text

    def test_no_filter(self, input_fasta: Path, tmp_path: Path) -> None:
        """フィルタなしでは全配列が含まれる."""
        output = tmp_path / "output.fasta"
        count = filter_fasta_by_gc(input_fasta, output)
        assert count == 3

    def test_file_not_found(self, tmp_path: Path) -> None:
        """存在しない入力ファイルでFileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            filter_fasta_by_gc(
                tmp_path / "nonexistent.fasta",
                tmp_path / "output.fasta",
            )
