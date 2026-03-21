"""NCBI Entrez APIを使った配列データの取得.

Biopython の Entrez モジュールを使い、アクセッション番号から
FASTA 形式の配列データを取得する。
"""

from __future__ import annotations

import logging
import os
from io import StringIO
from typing import Optional

from Bio import Entrez, SeqIO
from Bio.SeqRecord import SeqRecord

logger = logging.getLogger(__name__)


def configure_entrez(
    email: Optional[str] = None,
    api_key: Optional[str] = None,
    tool: str = "biocode-kata",
) -> None:
    """Entrez モジュールの認証情報を設定する.

    Parameters
    ----------
    email : str, optional
        NCBI に通知するメールアドレス。
        省略時は環境変数 ``NCBI_EMAIL`` から読み込む。
    api_key : str, optional
        NCBI API キー。
        省略時は環境変数 ``NCBI_API_KEY`` から読み込む。
    tool : str
        ツール名（NCBI に通知）。

    Raises
    ------
    ValueError
        メールアドレスが環境変数にも引数にも設定されていない場合。
    """
    resolved_email = email or os.environ.get("NCBI_EMAIL")
    if not resolved_email:
        msg = (
            "NCBI Entrez にはメールアドレスが必須です。"
            "引数 email または環境変数 NCBI_EMAIL を設定してください。"
        )
        raise ValueError(msg)

    Entrez.email = resolved_email
    Entrez.tool = tool

    resolved_key = api_key or os.environ.get("NCBI_API_KEY")
    if resolved_key:
        Entrez.api_key = resolved_key
        logger.info("NCBI API キーを設定しました")
    else:
        logger.warning(
            "NCBI API キーが未設定です。レート制限が厳しくなります"
        )


def fetch_fasta(
    accession: str,
    db: str = "nucleotide",
) -> SeqRecord:
    """アクセッション番号から FASTA 配列を1件取得する.

    Parameters
    ----------
    accession : str
        NCBI アクセッション番号（例: ``"NM_001301717.2"``）。
    db : str
        検索対象データベース（デフォルト: ``"nucleotide"``）。

    Returns
    -------
    SeqRecord
        取得した配列レコード。

    Raises
    ------
    RuntimeError
        配列の取得またはパースに失敗した場合。
    """
    logger.info("Entrez efetch: db=%s, id=%s", db, accession)

    try:
        handle = Entrez.efetch(db=db, id=accession, rettype="fasta", retmode="text")
        text = handle.read()
        handle.close()
    except Exception as exc:
        msg = f"NCBI からの取得に失敗しました: {accession}"
        raise RuntimeError(msg) from exc

    record = SeqIO.read(StringIO(text), "fasta")
    logger.info(
        "取得完了: %s (%d bp)", record.id, len(record.seq)
    )
    return record


def search_and_fetch(
    query: str,
    db: str = "nucleotide",
    retmax: int = 5,
) -> list[SeqRecord]:
    """キーワード検索してヒットした配列を取得する.

    esearch で ID を検索し、efetch で FASTA を一括取得する
    2 ステップフローの実装。

    Parameters
    ----------
    query : str
        NCBI 検索クエリ（例: ``"BRCA1[Gene] AND Homo sapiens[Organism]"``）。
    db : str
        検索対象データベース。
    retmax : int
        最大取得件数。

    Returns
    -------
    list[SeqRecord]
        取得した配列レコードのリスト。
    """
    logger.info("Entrez esearch: db=%s, query=%s, retmax=%d", db, query, retmax)

    # Step 1: esearch で ID リストを取得
    search_handle = Entrez.esearch(db=db, term=query, retmax=retmax)
    search_results = Entrez.read(search_handle)
    search_handle.close()

    id_list: list[str] = search_results["IdList"]
    if not id_list:
        logger.warning("検索結果が 0 件です: %s", query)
        return []

    logger.info("検索ヒット: %d 件（取得: %d 件）", int(search_results["Count"]), len(id_list))

    # Step 2: efetch で FASTA を一括取得
    fetch_handle = Entrez.efetch(
        db=db,
        id=",".join(id_list),
        rettype="fasta",
        retmode="text",
    )
    text = fetch_handle.read()
    fetch_handle.close()

    records = list(SeqIO.parse(StringIO(text), "fasta"))
    logger.info("取得完了: %d 件", len(records))
    return records
