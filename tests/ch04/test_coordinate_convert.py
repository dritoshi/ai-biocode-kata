"""coordinate_convert モジュールのテスト."""

from scripts.ch04.coordinate_convert import (
    bed_to_gff,
    gff_to_bed,
    interval_length_bed,
    interval_length_gff,
)


class TestBedToGff:
    """BED→GFF変換のテスト."""

    def test_single_base(self) -> None:
        # BED chr1:9-10 → GFF chr1:10-10（10番目の塩基）
        assert bed_to_gff(9, 10) == (10, 10)

    def test_multi_base_region(self) -> None:
        # BED chr1:100-200 → GFF chr1:101-200
        assert bed_to_gff(100, 200) == (101, 200)

    def test_start_of_chromosome(self) -> None:
        # BED chr1:0-1 → GFF chr1:1-1
        assert bed_to_gff(0, 1) == (1, 1)


class TestGffToBed:
    """GFF→BED変換のテスト."""

    def test_single_base(self) -> None:
        assert gff_to_bed(10, 10) == (9, 10)

    def test_roundtrip(self) -> None:
        # BED → GFF → BED のラウンドトリップ
        original = (100, 200)
        gff = bed_to_gff(*original)
        assert gff_to_bed(*gff) == original


class TestIntervalLength:
    """区間長計算のテスト."""

    def test_bed_and_gff_same_length(self) -> None:
        # 同じ領域なら座標系によらず長さは同じ
        assert interval_length_bed(9, 10) == 1
        assert interval_length_gff(10, 10) == 1

    def test_hundred_bases(self) -> None:
        assert interval_length_bed(100, 200) == 100
        assert interval_length_gff(101, 200) == 100
