"""regex_basics.py のテスト."""

from scripts.ch02.regex_basics import (
    convert_chrom_ensembl_to_ucsc,
    convert_chrom_ucsc_to_ensembl,
    extract_accession,
    extract_all_accessions,
    extract_gene_id,
)


class TestExtractAccession:
    """extract_accession() のテスト."""

    def test_standard_header(self) -> None:
        """標準的なFASTAヘッダからアクセッション番号を抽出."""
        result = extract_accession(">NM_007294.4 Homo sapiens BRCA1")
        assert result == "NM_007294.4"

    def test_no_match(self) -> None:
        """アクセッション番号がないヘッダでは None を返す."""
        result = extract_accession(">invalid")
        assert result is None

    def test_multiple_dots(self) -> None:
        """ピリオドが複数ある場合は最初のマッチを返す."""
        result = extract_accession(">XM_123.45.6 some description")
        assert result == "XM_123.45"


class TestExtractGeneId:
    """extract_gene_id() のテスト."""

    def test_standard_gtf(self) -> None:
        """標準的なGTF attributeからgene_idを抽出."""
        attr = 'gene_id "ENSG00000012048"; transcript_id "ENST00000357654"'
        result = extract_gene_id(attr)
        assert result == "ENSG00000012048"

    def test_no_gene_id(self) -> None:
        """gene_idがないattributeでは None を返す."""
        result = extract_gene_id('transcript_id "ENST00000357654"')
        assert result is None

    def test_gene_id_with_version(self) -> None:
        """バージョン付きgene_idを正しく抽出."""
        result = extract_gene_id('gene_id "ENSG00000012048.15"')
        assert result == "ENSG00000012048.15"


class TestExtractAllAccessions:
    """extract_all_accessions() のテスト."""

    def test_multi_record_fasta(self) -> None:
        """複数レコードのFASTAから全アクセッション番号を抽出."""
        fasta_text = ">NM_007294.4 BRCA1\nATGC\n>NM_000059.4 BRCA2\nGCTA\n"
        result = extract_all_accessions(fasta_text)
        assert result == ["NM_007294.4", "NM_000059.4"]

    def test_empty_text(self) -> None:
        """空文字列では空リストを返す."""
        result = extract_all_accessions("")
        assert result == []


class TestConvertChrom:
    """染色体名変換のテスト."""

    def test_ucsc_to_ensembl(self) -> None:
        """UCSC → Ensembl 変換."""
        assert convert_chrom_ucsc_to_ensembl("chr1") == "1"
        assert convert_chrom_ucsc_to_ensembl("chrX") == "X"
        assert convert_chrom_ucsc_to_ensembl("chrMT") == "MT"

    def test_ensembl_to_ucsc(self) -> None:
        """Ensembl → UCSC 変換."""
        assert convert_chrom_ensembl_to_ucsc("1") == "chr1"
        assert convert_chrom_ensembl_to_ucsc("X") == "chrX"

    def test_already_correct(self) -> None:
        """変換不要な値はそのまま返す."""
        assert convert_chrom_ucsc_to_ensembl("1") == "1"
        assert convert_chrom_ensembl_to_ucsc("chr1") == "chr1"
