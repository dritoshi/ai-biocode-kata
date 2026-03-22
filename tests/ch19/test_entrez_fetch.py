"""entrez_fetch モジュールのテスト.

HTTP 通信を unittest.mock.patch でスタブ化し、
パース結果を検証する。
"""

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from Bio.SeqRecord import SeqRecord

from scripts.ch19.entrez_fetch import configure_entrez, fetch_fasta, search_and_fetch

# --- テスト用データ ---

FASTA_RESPONSE = """\
>NM_001301717.2 Homo sapiens breast cancer 1 (BRCA1), transcript variant 1, mRNA
ATGGATTTATCTGCTCTTCGCGTTGAAGAAGTACAAAATGTCATTAATGCTATGCAGAAAATCTTAGAGT
GTCCCATCTGTCTGGAGTTGATCAAGGAACCTGTCTCCACAAAGTGTGACCACATATTTTGCAAATTTTG
"""

SEARCH_RESPONSE = {
    "Count": "3",
    "RetMax": "2",
    "IdList": ["12345", "67890"],
}

MULTI_FASTA_RESPONSE = """\
>seq1 Gene A
ATGCATGCATGC
>seq2 Gene B
GCTAGCTAGCTA
"""


# --- configure_entrez ---

class TestConfigureEntrez:
    """Entrez 認証設定のテスト."""

    def test_with_explicit_args(self) -> None:
        """引数でメールと API キーを指定."""
        from Bio import Entrez

        configure_entrez(email="test@example.com", api_key="fake_key")
        assert Entrez.email == "test@example.com"
        assert Entrez.api_key == "fake_key"
        assert Entrez.tool == "biocode-kata"

    def test_from_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """環境変数からメールと API キーを読み込む."""
        from Bio import Entrez

        monkeypatch.setenv("NCBI_EMAIL", "env@example.com")
        monkeypatch.setenv("NCBI_API_KEY", "env_key")

        configure_entrez()
        assert Entrez.email == "env@example.com"
        assert Entrez.api_key == "env_key"

    def test_no_email_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """メールが未設定の場合は ValueError."""
        monkeypatch.delenv("NCBI_EMAIL", raising=False)
        with pytest.raises(ValueError, match="メールアドレス"):
            configure_entrez()

    def test_no_api_key_warns(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """API キーが未設定の場合はログ警告."""
        monkeypatch.delenv("NCBI_API_KEY", raising=False)
        import logging

        with caplog.at_level(logging.WARNING):
            configure_entrez(email="test@example.com")
        assert "API キーが未設定" in caplog.text


# --- fetch_fasta ---

class TestFetchFasta:
    """efetch による FASTA 取得のテスト."""

    @patch("scripts.ch19.entrez_fetch.Entrez.efetch")
    def test_returns_seq_record(self, mock_efetch: MagicMock) -> None:
        """正常系: SeqRecord を返す."""
        mock_handle = StringIO(FASTA_RESPONSE)
        mock_efetch.return_value = mock_handle

        record = fetch_fasta("NM_001301717.2")

        assert isinstance(record, SeqRecord)
        assert "NM_001301717.2" in record.id
        assert len(record.seq) > 0
        mock_efetch.assert_called_once_with(
            db="nucleotide",
            id="NM_001301717.2",
            rettype="fasta",
            retmode="text",
        )

    @patch("scripts.ch19.entrez_fetch.Entrez.efetch")
    def test_custom_db(self, mock_efetch: MagicMock) -> None:
        """db パラメータを変更できる."""
        mock_handle = StringIO(FASTA_RESPONSE)
        mock_efetch.return_value = mock_handle

        fetch_fasta("NM_001301717.2", db="protein")

        mock_efetch.assert_called_once_with(
            db="protein",
            id="NM_001301717.2",
            rettype="fasta",
            retmode="text",
        )

    @patch("scripts.ch19.entrez_fetch.Entrez.efetch")
    def test_network_error_raises(self, mock_efetch: MagicMock) -> None:
        """通信エラー時は RuntimeError."""
        mock_efetch.side_effect = IOError("Connection refused")

        with pytest.raises(RuntimeError, match="取得に失敗"):
            fetch_fasta("INVALID_ACC")


# --- search_and_fetch ---

class TestSearchAndFetch:
    """esearch → efetch の 2 ステップフローのテスト."""

    @patch("scripts.ch19.entrez_fetch.Entrez.efetch")
    @patch("scripts.ch19.entrez_fetch.Entrez.esearch")
    @patch("scripts.ch19.entrez_fetch.Entrez.read")
    def test_returns_records(
        self,
        mock_read: MagicMock,
        mock_esearch: MagicMock,
        mock_efetch: MagicMock,
    ) -> None:
        """正常系: 複数レコードを返す."""
        mock_esearch.return_value = MagicMock()
        mock_read.return_value = SEARCH_RESPONSE
        mock_efetch.return_value = StringIO(MULTI_FASTA_RESPONSE)

        records = search_and_fetch("BRCA1[Gene]", retmax=2)

        assert len(records) == 2
        assert all(isinstance(r, SeqRecord) for r in records)

    @patch("scripts.ch19.entrez_fetch.Entrez.esearch")
    @patch("scripts.ch19.entrez_fetch.Entrez.read")
    def test_empty_results(
        self,
        mock_read: MagicMock,
        mock_esearch: MagicMock,
    ) -> None:
        """検索結果が 0 件の場合は空リスト."""
        mock_esearch.return_value = MagicMock()
        mock_read.return_value = {"Count": "0", "IdList": []}

        records = search_and_fetch("nonexistent_gene_xyz")

        assert records == []
