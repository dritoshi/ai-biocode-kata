"""日本語環境のエンコーディング罠のテスト."""

import unicodedata
from pathlib import Path

from scripts.ch04.encoding_traps import (
    normalize_filename_nfc,
    read_csv_with_bom_handling,
    safe_path_match,
)


class TestReadCsvWithBomHandling:
    """read_csv_with_bom_handling() のテスト."""

    def test_bom_stripped(self, tmp_path: Path) -> None:
        """BOM付きUTF-8のCSVでも列名にU+FEFFが混入しない."""
        csv_file = tmp_path / "bom.csv"
        # BOM (EF BB BF) + 通常のCSV内容
        csv_file.write_bytes(
            b"\xef\xbb\xbfgene,value\n"
            b"TP53,10.5\n"
            b"BRCA1,5.2\n"
        )
        records = read_csv_with_bom_handling(csv_file)
        assert len(records) == 2
        # BOMが除去され、"gene" でアクセスできる（"\ufeffgene" にならない）
        assert "gene" in records[0]
        assert records[0]["gene"] == "TP53"
        assert records[1]["value"] == "5.2"

    def test_no_bom(self, tmp_path: Path) -> None:
        """BOMなしのUTF-8 CSVも正常に読み込める."""
        csv_file = tmp_path / "no_bom.csv"
        csv_file.write_text(
            "gene,value\nTP53,10.5\n",
            encoding="utf-8",
        )
        records = read_csv_with_bom_handling(csv_file)
        assert len(records) == 1
        assert records[0]["gene"] == "TP53"

    def test_japanese_content(self, tmp_path: Path) -> None:
        """日本語を含むBOM付きCSVが正しく読み込める."""
        csv_file = tmp_path / "japanese.csv"
        csv_file.write_bytes(
            "gene,組織\nTP53,肝臓\nBRCA1,乳腺\n".encode("utf-8-sig")
        )
        records = read_csv_with_bom_handling(csv_file)
        assert len(records) == 2
        assert records[0]["組織"] == "肝臓"
        assert records[1]["組織"] == "乳腺"


class TestNormalizeFilenameNfc:
    """normalize_filename_nfc() のテスト."""

    def test_nfd_to_nfc(self) -> None:
        """NFD（分解形）の日本語がNFC（合成形）に変換される."""
        # "が" のNFD表現: U+304B (か) + U+3099 (濁点)
        nfd_ga = "\u304b\u3099"
        assert unicodedata.is_normalized("NFD", nfd_ga)
        result = normalize_filename_nfc(nfd_ga)
        assert result == "が"
        assert unicodedata.is_normalized("NFC", result)

    def test_nfc_passthrough(self) -> None:
        """すでにNFCの文字列はそのまま返される."""
        nfc_str = "サンプル_001.fastq.gz"
        result = normalize_filename_nfc(nfc_str)
        assert result == nfc_str

    def test_ascii_passthrough(self) -> None:
        """ASCII文字列は変化しない."""
        ascii_str = "sample_001.fastq.gz"
        result = normalize_filename_nfc(ascii_str)
        assert result == ascii_str


class TestSafePathMatch:
    """safe_path_match() のテスト."""

    def test_nfd_vs_nfc_match(self) -> None:
        """NFDとNFCの同じ文字列がマッチする."""
        # "パフ" — NFD: ハ + 半濁点 + フ + 濁点... ではなく、より単純な例
        # "ガン" のNFD表現
        nfc_path = "data/ガン_sample.tsv"
        nfd_path = unicodedata.normalize("NFD", nfc_path)
        # 直接比較では不一致
        assert nfc_path != nfd_path
        # safe_path_match では一致
        assert safe_path_match(nfc_path, nfd_path) is True

    def test_different_paths_no_match(self) -> None:
        """異なるパスはマッチしない."""
        assert safe_path_match("data/sample_A.tsv", "data/sample_B.tsv") is False
