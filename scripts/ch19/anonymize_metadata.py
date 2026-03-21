"""メタデータCSVの準識別子を一般化し、k-匿名性を検証する.

臨床メタデータに含まれる年齢・地域などの準識別子（quasi-identifier）を
一般化（generalization）することで再識別リスクを低減する。
一般化後のデータが k-匿名性を満たすかどうかも検証する。
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class KAnonymityResult:
    """k-匿名性検証の結果.

    Attributes
    ----------
    k : int
        達成された最小 k 値。
    target_k : int
        目標とする k 値。
    satisfies : bool
        目標 k 値を満たしているかどうか。
    total_groups : int
        準識別子の組み合わせによるグループ数。
    smallest_group_size : int
        最小グループのレコード数。
    total_records : int
        総レコード数。
    """

    k: int
    target_k: int
    satisfies: bool
    total_groups: int
    smallest_group_size: int
    total_records: int


def generalize_age(age: int, bin_size: int = 10) -> str:
    """年齢を年代に一般化する.

    Parameters
    ----------
    age : int
        元の年齢値。
    bin_size : int
        ビンの幅（デフォルト: 10）。

    Returns
    -------
    str
        一般化された年代（例: ``"30-39"``）。

    Raises
    ------
    ValueError
        年齢が負の値の場合。
    """
    if age < 0:
        msg = f"年齢は0以上でなければなりません: {age}"
        raise ValueError(msg)
    if bin_size <= 0:
        msg = f"ビンサイズは正の整数でなければなりません: {bin_size}"
        raise ValueError(msg)

    lower = (age // bin_size) * bin_size
    upper = lower + bin_size - 1
    return f"{lower}-{upper}"


def generalize_region(region: str, mapping: dict[str, str]) -> str:
    """地域名を上位の地域区分に一般化する.

    Parameters
    ----------
    region : str
        元の地域名。
    mapping : dict[str, str]
        地域名から上位区分へのマッピング。

    Returns
    -------
    str
        一般化された地域区分。マッピングにない場合は ``"その他"``。
    """
    return mapping.get(region, "その他")


def anonymize_record(
    record: dict[str, str],
    age_column: str = "age",
    region_column: str = "region",
    drop_columns: list[str] | None = None,
    region_mapping: dict[str, str] | None = None,
    age_bin_size: int = 10,
) -> dict[str, str]:
    """1レコードの準識別子を一般化する.

    Parameters
    ----------
    record : dict[str, str]
        CSV行を辞書にしたもの。
    age_column : str
        年齢カラム名。
    region_column : str
        地域カラム名。
    drop_columns : list[str] | None
        削除するカラム名のリスト（氏名、住所等の直接識別子）。
    region_mapping : dict[str, str] | None
        地域の一般化マッピング。
    age_bin_size : int
        年齢の一般化ビン幅。

    Returns
    -------
    dict[str, str]
        一般化後のレコード。
    """
    result = dict(record)

    # 直接識別子の削除
    if drop_columns:
        for col in drop_columns:
            result.pop(col, None)

    # 年齢の一般化
    if age_column in result and result[age_column]:
        try:
            age = int(result[age_column])
            result[age_column] = generalize_age(age, age_bin_size)
        except ValueError:
            logger.warning(
                "年齢の変換に失敗: %s = %r", age_column, result[age_column]
            )

    # 地域の一般化
    if region_column in result and region_mapping:
        result[region_column] = generalize_region(
            result[region_column], region_mapping
        )

    return result


def anonymize_csv(
    input_text: str,
    age_column: str = "age",
    region_column: str = "region",
    drop_columns: list[str] | None = None,
    region_mapping: dict[str, str] | None = None,
    age_bin_size: int = 10,
) -> str:
    """CSV文字列全体の準識別子を一般化する.

    Parameters
    ----------
    input_text : str
        入力CSV文字列。
    age_column : str
        年齢カラム名。
    region_column : str
        地域カラム名。
    drop_columns : list[str] | None
        削除するカラム名のリスト。
    region_mapping : dict[str, str] | None
        地域の一般化マッピング。
    age_bin_size : int
        年齢の一般化ビン幅。

    Returns
    -------
    str
        一般化後のCSV文字列。
    """
    reader = csv.DictReader(StringIO(input_text))
    if reader.fieldnames is None:
        return ""

    # 出力カラムから削除対象を除外
    output_columns = [
        col for col in reader.fieldnames
        if drop_columns is None or col not in drop_columns
    ]

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=output_columns)
    writer.writeheader()

    for row in reader:
        anonymized = anonymize_record(
            row,
            age_column=age_column,
            region_column=region_column,
            drop_columns=drop_columns,
            region_mapping=region_mapping,
            age_bin_size=age_bin_size,
        )
        writer.writerow(anonymized)

    return output.getvalue()


def check_k_anonymity(
    csv_text: str,
    quasi_identifiers: list[str],
    target_k: int = 5,
) -> KAnonymityResult:
    """CSV データの k-匿名性を検証する.

    k-匿名性とは、準識別子の各組み合わせについて、
    同じ組み合わせを持つレコードが少なくとも k 件存在することを要求する
    プライバシー保護の基準である。

    Parameters
    ----------
    csv_text : str
        検証対象のCSV文字列。
    quasi_identifiers : list[str]
        準識別子のカラム名リスト。
    target_k : int
        目標とする k 値。

    Returns
    -------
    KAnonymityResult
        検証結果。

    Raises
    ------
    ValueError
        準識別子がCSVのカラムに存在しない場合。
    """
    reader = csv.DictReader(StringIO(csv_text))
    rows = list(reader)

    if not rows:
        return KAnonymityResult(
            k=0,
            target_k=target_k,
            satisfies=False,
            total_groups=0,
            smallest_group_size=0,
            total_records=0,
        )

    # 準識別子のカラム存在チェック
    if reader.fieldnames:
        missing = [qi for qi in quasi_identifiers if qi not in reader.fieldnames]
        if missing:
            msg = f"準識別子がCSVに存在しません: {missing}"
            raise ValueError(msg)

    # 準識別子の組み合わせでグループ化
    groups: dict[tuple[str, ...], int] = {}
    for row in rows:
        key = tuple(row[qi] for qi in quasi_identifiers)
        groups[key] = groups.get(key, 0) + 1

    smallest = min(groups.values())
    achieved_k = smallest

    result = KAnonymityResult(
        k=achieved_k,
        target_k=target_k,
        satisfies=achieved_k >= target_k,
        total_groups=len(groups),
        smallest_group_size=smallest,
        total_records=len(rows),
    )

    if result.satisfies:
        logger.info(
            "k-匿名性を満たしています: k=%d (目標: k=%d)",
            achieved_k,
            target_k,
        )
    else:
        logger.warning(
            "k-匿名性を満たしていません: k=%d (目標: k=%d)",
            achieved_k,
            target_k,
        )

    return result
