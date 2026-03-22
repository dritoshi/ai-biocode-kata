"""parse_flatfile モジュールのテスト.

テスト用の GenBank データを文字列リテラルで定義し、
パース結果を検証する。
"""

from io import StringIO
from pathlib import Path

import pytest
from Bio import SeqIO

from scripts.ch19.parse_flatfile import CDSFeature, extract_cds_features, parse_genbank

# --- テスト用 GenBank データ ---

SAMPLE_GENBANK = """\
LOCUS       TEST_SEQ                 300 bp    DNA     linear   BCT 01-JAN-2024
DEFINITION  Test sequence for unit testing.
ACCESSION   TEST_SEQ
VERSION     TEST_SEQ.1
FEATURES             Location/Qualifiers
     source          1..300
                     /organism="Test organism"
                     /mol_type="genomic DNA"
     gene            10..150
                     /gene="testA"
     CDS             10..150
                     /gene="testA"
                     /product="test protein A"
                     /translation="MVLSPADKTNVKAAW"
     gene            complement(160..290)
                     /gene="testB"
     CDS             complement(160..290)
                     /gene="testB"
                     /product="test protein B"
                     /translation="MKTAYIAKQRQISFV"
ORIGIN
        1 atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc
       61 atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc
      121 atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc
      181 atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc
      241 atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc
//
"""

SAMPLE_GENBANK_NO_CDS = """\
LOCUS       EMPTY_SEQ                100 bp    DNA     linear   BCT 01-JAN-2024
DEFINITION  Sequence without CDS features.
ACCESSION   EMPTY_SEQ
VERSION     EMPTY_SEQ.1
FEATURES             Location/Qualifiers
     source          1..100
                     /organism="Test organism"
                     /mol_type="genomic DNA"
     gene            10..90
                     /gene="geneX"
ORIGIN
        1 atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc
       61 atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc
//
"""

SAMPLE_GENBANK_MISSING_QUALIFIERS = """\
LOCUS       PARTIAL_SEQ              200 bp    DNA     linear   BCT 01-JAN-2024
DEFINITION  Sequence with CDS missing some qualifiers.
ACCESSION   PARTIAL_SEQ
VERSION     PARTIAL_SEQ.1
FEATURES             Location/Qualifiers
     source          1..200
                     /organism="Test organism"
                     /mol_type="genomic DNA"
     CDS             20..180
                     /note="hypothetical protein"
ORIGIN
        1 atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc
       61 atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc
      121 atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc atgcatgcat gcatgcatgc
      181 atgcatgcat gcatgcatgc
//
"""


# --- フィクスチャ ---

@pytest.fixture()
def sample_record() -> SeqIO.SeqRecord:
    """テスト用の SeqRecord を返す."""
    return SeqIO.read(StringIO(SAMPLE_GENBANK), "genbank")


@pytest.fixture()
def genbank_file(tmp_path: Path) -> Path:
    """テスト用の GenBank ファイルを作成する."""
    filepath = tmp_path / "test.gb"
    filepath.write_text(SAMPLE_GENBANK)
    return filepath


# --- extract_cds_features ---

class TestExtractCdsFeatures:
    """CDS 抽出のテスト."""

    def test_extract_two_cds(self, sample_record: SeqIO.SeqRecord) -> None:
        """2つの CDS が正しく抽出される."""
        features = extract_cds_features(sample_record)
        assert len(features) == 2

    def test_gene_names(self, sample_record: SeqIO.SeqRecord) -> None:
        """遺伝子名が正しく取得される."""
        features = extract_cds_features(sample_record)
        genes = [f.gene for f in features]
        assert "testA" in genes
        assert "testB" in genes

    def test_product_names(self, sample_record: SeqIO.SeqRecord) -> None:
        """産物名が正しく取得される."""
        features = extract_cds_features(sample_record)
        products = [f.product for f in features]
        assert "test protein A" in products
        assert "test protein B" in products

    def test_record_id(self, sample_record: SeqIO.SeqRecord) -> None:
        """レコード ID がセットされる."""
        features = extract_cds_features(sample_record)
        assert all(f.record_id == "TEST_SEQ.1" for f in features)

    def test_location_is_string(self, sample_record: SeqIO.SeqRecord) -> None:
        """位置情報が文字列で格納される."""
        features = extract_cds_features(sample_record)
        assert all(isinstance(f.location, str) for f in features)

    def test_no_cds(self) -> None:
        """CDS が無いレコードでは空リストを返す."""
        record = SeqIO.read(StringIO(SAMPLE_GENBANK_NO_CDS), "genbank")
        features = extract_cds_features(record)
        assert features == []

    def test_missing_qualifiers(self) -> None:
        """gene/product が無い CDS では N/A が入る."""
        record = SeqIO.read(
            StringIO(SAMPLE_GENBANK_MISSING_QUALIFIERS), "genbank"
        )
        features = extract_cds_features(record)
        assert len(features) == 1
        assert features[0].gene == "N/A"
        assert features[0].product == "N/A"

    def test_returns_cds_feature_dataclass(
        self, sample_record: SeqIO.SeqRecord
    ) -> None:
        """返り値が CDSFeature インスタンスである."""
        features = extract_cds_features(sample_record)
        assert all(isinstance(f, CDSFeature) for f in features)


# --- parse_genbank ---

class TestParseGenbank:
    """GenBank ファイルパースのテスト."""

    def test_parse_file(self, genbank_file: Path) -> None:
        """ファイルから CDS を抽出できる."""
        features = parse_genbank(genbank_file)
        assert len(features) == 2
        assert features[0].gene == "testA"
        assert features[1].gene == "testB"

    def test_file_not_found(self, tmp_path: Path) -> None:
        """存在しないファイルで FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="見つかりません"):
            parse_genbank(tmp_path / "nonexistent.gb")

    def test_empty_cds_file(self, tmp_path: Path) -> None:
        """CDS の無いファイルでは空リストを返す."""
        filepath = tmp_path / "no_cds.gb"
        filepath.write_text(SAMPLE_GENBANK_NO_CDS)
        features = parse_genbank(filepath)
        assert features == []

    def test_multiple_records(self, tmp_path: Path) -> None:
        """複数レコードを含むファイルから全 CDS を抽出できる."""
        filepath = tmp_path / "multi.gb"
        filepath.write_text(SAMPLE_GENBANK + SAMPLE_GENBANK_NO_CDS)
        features = parse_genbank(filepath)
        # 最初のレコードに CDS 2件、2番目は 0件
        assert len(features) == 2
