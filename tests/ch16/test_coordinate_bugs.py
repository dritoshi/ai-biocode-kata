"""coordinate_bugs.py のテスト."""

import pytest

from scripts.ch16.coordinate_bugs import (
    bed_to_gff_buggy,
    bed_to_gff_correct,
    extract_subsequence,
    gff_to_bed_correct,
    validate_coordinates,
)


class TestBedToGffBuggy:
    """バグ版がOff-by-oneエラーを起こすことを実証するテスト."""

    def test_demonstrates_bug(self):
        """BED (0, 10) → GFF は (1, 10) であるべきだが (0, 10) を返す."""
        chrom, start, end = bed_to_gff_buggy("chr1", 0, 10)
        # バグ版は start が 0 のまま（正しくは 1）
        assert start == 0  # バグの実証
        assert end == 10


class TestBedToGffCorrect:
    """修正版 bed_to_gff_correct のテスト."""

    def test_basic_conversion(self):
        """BED (0, 10) → GFF (1, 10) の基本変換."""
        chrom, start, end = bed_to_gff_correct("chr1", 0, 10)
        assert chrom == "chr1"
        assert start == 1
        assert end == 10

    def test_single_base(self):
        """1塩基: BED (5, 6) → GFF (6, 6)."""
        _, start, end = bed_to_gff_correct("chr1", 5, 6)
        assert start == 6
        assert end == 6

    def test_roundtrip(self):
        """BED → GFF → BED の往復変換で元に戻る."""
        original = ("chr1", 100, 200)
        gff = bed_to_gff_correct(*original)
        restored = gff_to_bed_correct(*gff)
        assert restored == original


class TestGffToBedCorrect:
    """gff_to_bed_correct のテスト."""

    def test_basic_conversion(self):
        """GFF (1, 10) → BED (0, 10) の基本変換."""
        chrom, start, end = gff_to_bed_correct("chr1", 1, 10)
        assert chrom == "chr1"
        assert start == 0
        assert end == 10


class TestExtractSubsequence:
    """extract_subsequence のテスト."""

    def test_bed_extraction(self):
        """BED座標での部分配列抽出."""
        seq = "ATCGATCG"
        result = extract_subsequence(seq, 0, 4, "bed")
        assert result == "ATCG"

    def test_gff_extraction(self):
        """GFF座標での部分配列抽出."""
        seq = "ATCGATCG"
        result = extract_subsequence(seq, 1, 4, "gff")
        assert result == "ATCG"

    def test_bed_gff_same_region(self):
        """同じ領域を BED と GFF で指定して同じ結果を得る."""
        seq = "ATCGATCG"
        bed_result = extract_subsequence(seq, 2, 5, "bed")
        gff_result = extract_subsequence(seq, 3, 5, "gff")
        assert bed_result == gff_result

    def test_unknown_system(self):
        """不明な座標系で ValueError が発生."""
        with pytest.raises(ValueError, match="不明な座標系"):
            extract_subsequence("ATCG", 0, 2, "sam")


class TestValidateCoordinates:
    """validate_coordinates のテスト."""

    def test_valid_bed(self):
        """正常なBED座標は True を返す."""
        assert validate_coordinates(0, 10, 100, "bed") is True

    def test_valid_gff(self):
        """正常なGFF座標は True を返す."""
        assert validate_coordinates(1, 10, 100, "gff") is True

    def test_negative_bed_start(self):
        """BEDの負の開始位置で ValueError."""
        with pytest.raises(ValueError, match="0 以上"):
            validate_coordinates(-1, 10, 100, "bed")

    def test_gff_start_zero(self):
        """GFFの開始が0で ValueError."""
        with pytest.raises(ValueError, match="1 以上"):
            validate_coordinates(0, 10, 100, "gff")

    def test_end_exceeds_length(self):
        """終了位置が配列長を超過で ValueError."""
        with pytest.raises(ValueError, match="超過"):
            validate_coordinates(0, 200, 100, "bed")

    def test_start_greater_than_end(self):
        """start > end で ValueError."""
        with pytest.raises(ValueError, match=">"):
            validate_coordinates(10, 5, 100, "bed")
