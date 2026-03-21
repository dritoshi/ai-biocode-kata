"""sparql_query モジュールのテスト.

HTTP レスポンスを unittest.mock.patch でスタブ化し、
パース結果の型・キーを検証する。
"""

from unittest.mock import MagicMock, patch

import pytest

from scripts.ch18.sparql_query import (
    EXAMPLE_KINASE_QUERY,
    extract_values,
    run_sparql_query,
)

# --- テスト用データ ---

SPARQL_JSON_RESPONSE = {
    "results": {
        "bindings": [
            {
                "protein": {
                    "type": "uri",
                    "value": "http://purl.uniprot.org/uniprot/P00533",
                },
                "gene": {
                    "type": "literal",
                    "value": "EGFR",
                },
                "name": {
                    "type": "literal",
                    "value": "Epidermal growth factor receptor",
                },
            },
            {
                "protein": {
                    "type": "uri",
                    "value": "http://purl.uniprot.org/uniprot/P04626",
                },
                "gene": {
                    "type": "literal",
                    "value": "ERBB2",
                },
                "name": {
                    "type": "literal",
                    "value": "Receptor tyrosine-protein kinase erbB-2",
                },
            },
        ]
    }
}

EMPTY_SPARQL_RESPONSE = {"results": {"bindings": []}}


# --- run_sparql_query ---

class TestRunSparqlQuery:
    """SPARQL クエリ実行のテスト."""

    @patch("scripts.ch18.sparql_query.requests.get")
    def test_returns_bindings(self, mock_get: MagicMock) -> None:
        """正常系: バインディングリストを返す."""
        mock_response = MagicMock()
        mock_response.json.return_value = SPARQL_JSON_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = run_sparql_query("SELECT ?protein WHERE { }")

        assert isinstance(result, list)
        assert len(result) == 2
        assert "protein" in result[0]
        assert result[0]["protein"]["value"] == "http://purl.uniprot.org/uniprot/P00533"

    @patch("scripts.ch18.sparql_query.requests.get")
    def test_empty_result(self, mock_get: MagicMock) -> None:
        """結果が 0 件の場合は空リスト."""
        mock_response = MagicMock()
        mock_response.json.return_value = EMPTY_SPARQL_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = run_sparql_query("SELECT ?x WHERE { }")

        assert result == []

    @patch("scripts.ch18.sparql_query.requests.get")
    def test_http_error_raises(self, mock_get: MagicMock) -> None:
        """HTTP エラー時は例外."""
        import requests

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("429 Too Many Requests")
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            run_sparql_query("SELECT ?x WHERE { }")

    @patch("scripts.ch18.sparql_query.requests.get")
    def test_json_parse_error(self, mock_get: MagicMock) -> None:
        """JSON パースエラー時は ValueError."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="JSON パース"):
            run_sparql_query("SELECT ?x WHERE { }")

    @patch("scripts.ch18.sparql_query.requests.get")
    def test_custom_endpoint(self, mock_get: MagicMock) -> None:
        """カスタムエンドポイントを指定できる."""
        mock_response = MagicMock()
        mock_response.json.return_value = EMPTY_SPARQL_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        run_sparql_query("SELECT ?x WHERE { }", endpoint="https://example.com/sparql")

        call_args = mock_get.call_args
        assert call_args[0][0] == "https://example.com/sparql"


# --- extract_values ---

class TestExtractValues:
    """値抽出のテスト."""

    def test_extracts_specified_variables(self) -> None:
        """指定した変数の値を抽出する."""
        bindings = SPARQL_JSON_RESPONSE["results"]["bindings"]
        rows = extract_values(bindings, ["protein", "gene"])

        assert len(rows) == 2
        assert rows[0]["protein"] == "http://purl.uniprot.org/uniprot/P00533"
        assert rows[0]["gene"] == "EGFR"

    def test_missing_variable_returns_empty(self) -> None:
        """存在しない変数名は空文字になる."""
        bindings = SPARQL_JSON_RESPONSE["results"]["bindings"]
        rows = extract_values(bindings, ["protein", "nonexistent"])

        assert rows[0]["nonexistent"] == ""

    def test_empty_bindings(self) -> None:
        """空のバインディングからは空リスト."""
        rows = extract_values([], ["protein"])
        assert rows == []


# --- サンプルクエリの定義チェック ---

class TestExampleQuery:
    """サンプルクエリが定義されていることを確認."""

    def test_example_query_is_defined(self) -> None:
        assert "SELECT" in EXAMPLE_KINASE_QUERY
        assert "Kinase" in EXAMPLE_KINASE_QUERY
        assert "taxon:9606" in EXAMPLE_KINASE_QUERY
