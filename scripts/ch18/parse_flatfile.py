"""GenBank フラットファイルのパースユーティリティ.

Biopython の SeqIO を用いて GenBank 形式ファイルから
CDS（タンパク質コーディング領域）のアノテーション情報を抽出する。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

logger = logging.getLogger(__name__)


@dataclass
class CDSFeature:
    """CDS アノテーション情報.

    Attributes
    ----------
    record_id : str
        配列レコードの ID。
    gene : str
        遺伝子名。不明の場合は ``"N/A"``。
    product : str
        産物名（タンパク質名）。不明の場合は ``"N/A"``。
    location : str
        ゲノム上の位置情報（文字列表現）。
    """

    record_id: str
    gene: str
    product: str
    location: str


def extract_cds_features(record: SeqRecord) -> list[CDSFeature]:
    """SeqRecord から CDS feature 情報を抽出する.

    Parameters
    ----------
    record : SeqRecord
        Biopython の SeqRecord オブジェクト。

    Returns
    -------
    list[CDSFeature]
        抽出された CDS 情報のリスト。
    """
    features: list[CDSFeature] = []
    for feature in record.features:
        if feature.type != "CDS":
            continue
        gene = feature.qualifiers.get("gene", ["N/A"])[0]
        product = feature.qualifiers.get("product", ["N/A"])[0]
        location = str(feature.location)
        features.append(
            CDSFeature(
                record_id=record.id,
                gene=gene,
                product=product,
                location=location,
            )
        )
    logger.info(
        "レコード %s から %d 件の CDS を抽出", record.id, len(features)
    )
    return features


def parse_genbank(filepath: Path) -> list[CDSFeature]:
    """GenBank ファイルをパースして全 CDS 情報を返す.

    Parameters
    ----------
    filepath : Path
        GenBank 形式ファイルのパス。

    Returns
    -------
    list[CDSFeature]
        全レコードから抽出された CDS 情報。

    Raises
    ------
    FileNotFoundError
        ファイルが存在しない場合。
    """
    if not filepath.exists():
        msg = f"ファイルが見つかりません: {filepath}"
        raise FileNotFoundError(msg)

    all_features: list[CDSFeature] = []
    with open(filepath) as fh:
        for record in SeqIO.parse(fh, "genbank"):
            all_features.extend(extract_cds_features(record))

    logger.info(
        "%s から合計 %d 件の CDS を抽出", filepath.name, len(all_features)
    )
    return all_features
