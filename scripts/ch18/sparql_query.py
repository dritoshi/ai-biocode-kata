"""UniProt SPARQL エンドポイントへのクエリ実行.

requests を使って UniProt の SPARQL エンドポイントに
クエリを送信し、JSON 結果を辞書リストとして返す。
"""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

# UniProt SPARQL エンドポイント
UNIPROT_SPARQL_ENDPOINT = "https://sparql.uniprot.org/sparql"

# デフォルトのタイムアウト（秒）
DEFAULT_TIMEOUT = 30


def run_sparql_query(
    query: str,
    endpoint: str = UNIPROT_SPARQL_ENDPOINT,
    timeout: int = DEFAULT_TIMEOUT,
) -> list[dict[str, Any]]:
    """SPARQL クエリを実行し、結果を辞書リストで返す.

    Parameters
    ----------
    query : str
        SPARQL クエリ文字列。
    endpoint : str
        SPARQL エンドポイント URL。
    timeout : int
        HTTP リクエストのタイムアウト（秒）。

    Returns
    -------
    list[dict[str, Any]]
        各行を辞書にしたリスト。キーは SPARQL の変数名、
        値は ``{"type": ..., "value": ...}`` の辞書。

    Raises
    ------
    requests.HTTPError
        HTTP エラーが返された場合。
    ValueError
        レスポンスの JSON パースに失敗した場合。
    """
    logger.info("SPARQL クエリ送信: endpoint=%s", endpoint)
    logger.debug("クエリ本文:\n%s", query)

    headers = {"Accept": "application/sparql-results+json"}
    params = {"query": query, "format": "json"}

    response = requests.get(
        endpoint,
        headers=headers,
        params=params,
        timeout=timeout,
    )
    response.raise_for_status()

    try:
        data = response.json()
    except ValueError as exc:
        msg = "SPARQL レスポンスの JSON パースに失敗しました"
        raise ValueError(msg) from exc

    bindings: list[dict[str, Any]] = data["results"]["bindings"]
    logger.info("取得件数: %d 件", len(bindings))
    return bindings


def extract_values(
    bindings: list[dict[str, Any]],
    variables: list[str],
) -> list[dict[str, str]]:
    """SPARQL 結果のバインディングから値のみを抽出する.

    Parameters
    ----------
    bindings : list[dict[str, Any]]
        ``run_sparql_query`` の戻り値。
    variables : list[str]
        抽出する変数名のリスト。

    Returns
    -------
    list[dict[str, str]]
        各行の変数名→値（文字列）の辞書リスト。
    """
    rows: list[dict[str, str]] = []
    for binding in bindings:
        row: dict[str, str] = {}
        for var in variables:
            if var in binding:
                row[var] = binding[var]["value"]
            else:
                row[var] = ""
        rows.append(row)
    return rows


# ヒトのキナーゼファミリーを取得するサンプルクエリ
EXAMPLE_KINASE_QUERY = """\
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?protein ?gene ?name
WHERE {
  ?protein a up:Protein ;
           up:organism taxon:9606 ;
           up:encodedBy ?geneResource ;
           up:classifiedWith ?keyword ;
           rdfs:label ?name .
  ?geneResource up:name ?gene .
  ?keyword rdfs:label "Kinase" .
}
LIMIT 10
"""
