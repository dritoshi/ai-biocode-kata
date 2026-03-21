"""traceback解読のデモ用関数群."""

from pathlib import Path


def read_fasta_records(path: Path) -> list[dict[str, str]]:
    """FASTAファイルを読み込み、ヘッダと配列のリストを返す.

    Parameters
    ----------
    path : Path
        FASTAファイルのパス。

    Returns
    -------
    list[dict[str, str]]
        各レコードを {"header": ..., "sequence": ...} で格納したリスト。

    Raises
    ------
    FileNotFoundError
        指定されたファイルが存在しない場合。
    ValueError
        ファイルが空の場合。
    """
    text = path.read_text()
    if not text.strip():
        msg = f"FASTAファイルが空です: {path}"
        raise ValueError(msg)

    records: list[dict[str, str]] = []
    current_header: str | None = None
    current_seq_parts: list[str] = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            # 前のレコードを保存
            if current_header is not None:
                records.append({
                    "header": current_header,
                    "sequence": "".join(current_seq_parts),
                })
            current_header = line[1:].strip()
            current_seq_parts = []
        else:
            current_seq_parts.append(line)

    # 最後のレコードを保存
    if current_header is not None:
        records.append({
            "header": current_header,
            "sequence": "".join(current_seq_parts),
        })

    return records


def parse_gene_expression(raw_data: list[str]) -> list[float]:
    """文字列リストを浮動小数点数のリストに変換する.

    発現量データが文字列として読み込まれた場合に、
    数値に変換する。変換できない値があると ValueError を送出する。

    Parameters
    ----------
    raw_data : list[str]
        数値を表す文字列のリスト（例: ["1.5", "2.3", "0.8"]）。

    Returns
    -------
    list[float]
        変換後の浮動小数点数リスト。

    Raises
    ------
    ValueError
        数値に変換できない文字列が含まれている場合。
    """
    results: list[float] = []
    for i, value in enumerate(raw_data):
        try:
            results.append(float(value))
        except ValueError:
            msg = (
                f"インデックス {i} の値 '{value}' を数値に変換できません"
            )
            raise ValueError(msg) from None
    return results


def lookup_gene_annotation(
    gene_id: str, db: dict[str, dict[str, str]]
) -> dict[str, str]:
    """遺伝子IDからアノテーション情報を検索する.

    Parameters
    ----------
    gene_id : str
        遺伝子ID（例: "BRCA1"）。
    db : dict[str, dict[str, str]]
        遺伝子IDをキー、アノテーション辞書を値とするデータベース。

    Returns
    -------
    dict[str, str]
        アノテーション情報の辞書。

    Raises
    ------
    KeyError
        指定された遺伝子IDがデータベースに存在しない場合。
    """
    if gene_id not in db:
        msg = f"遺伝子ID '{gene_id}' がデータベースに見つかりません"
        raise KeyError(msg)
    return db[gene_id]


def safe_parse_gene_expression(
    raw_data: list[str],
) -> tuple[list[float], list[tuple[int, str]]]:
    """文字列リストを浮動小数点数に変換し、変換できなかった値を記録する.

    parse_gene_expression とは異なり、変換エラーを例外として送出せず、
    正常な値と異常な値を分けて返す。

    Parameters
    ----------
    raw_data : list[str]
        数値を表す文字列のリスト。

    Returns
    -------
    tuple[list[float], list[tuple[int, str]]]
        (正常値リスト, [(インデックス, 元の文字列), ...] の異常値リスト)。
    """
    values: list[float] = []
    errors: list[tuple[int, str]] = []
    for i, item in enumerate(raw_data):
        try:
            values.append(float(item))
        except ValueError:
            errors.append((i, item))
    return values, errors
