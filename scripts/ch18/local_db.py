"""SQLite によるサンプルメタデータのローカル管理.

CSV ファイルからメタデータを SQLite データベースに格納し、
条件に基づいたクエリを実行する。
"""

from __future__ import annotations

import csv
import logging
import sqlite3
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# サンプルメタデータテーブルのスキーマ
CREATE_TABLE_SQL = """\
CREATE TABLE IF NOT EXISTS samples (
    sample_id   TEXT PRIMARY KEY,
    accession   TEXT NOT NULL,
    organism    TEXT NOT NULL,
    condition   TEXT NOT NULL,
    replicate   INTEGER,
    platform    TEXT,
    read_length INTEGER
)
"""


def create_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """SQLite データベースへの接続を作成する.

    Parameters
    ----------
    db_path : str, optional
        データベースファイルのパス。
        ``None`` の場合はインメモリデータベースを使用する。

    Returns
    -------
    sqlite3.Connection
        データベース接続。
    """
    path = db_path or ":memory:"
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    logger.info("SQLite 接続: %s", path)
    return conn


def initialize_db(conn: sqlite3.Connection) -> None:
    """サンプルメタデータテーブルを作成する.

    Parameters
    ----------
    conn : sqlite3.Connection
        データベース接続。
    """
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()
    logger.info("samples テーブルを初期化しました")


def load_csv(conn: sqlite3.Connection, csv_path: Path) -> int:
    """CSV ファイルからメタデータを読み込んで挿入する.

    CSV のヘッダは ``sample_id, accession, organism, condition,
    replicate, platform, read_length`` を含む必要がある。

    Parameters
    ----------
    conn : sqlite3.Connection
        データベース接続。
    csv_path : Path
        CSV ファイルのパス。

    Returns
    -------
    int
        挿入した行数。

    Raises
    ------
    FileNotFoundError
        CSV ファイルが存在しない場合。
    """
    if not csv_path.exists():
        msg = f"CSV ファイルが見つかりません: {csv_path}"
        raise FileNotFoundError(msg)

    count = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conn.execute(
                """
                INSERT OR REPLACE INTO samples
                    (sample_id, accession, organism, condition,
                     replicate, platform, read_length)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["sample_id"],
                    row["accession"],
                    row["organism"],
                    row["condition"],
                    int(row["replicate"]) if row.get("replicate") else None,
                    row.get("platform"),
                    int(row["read_length"]) if row.get("read_length") else None,
                ),
            )
            count += 1

    conn.commit()
    logger.info("CSV から %d 行を挿入しました: %s", count, csv_path)
    return count


def insert_sample(
    conn: sqlite3.Connection,
    sample_id: str,
    accession: str,
    organism: str,
    condition: str,
    replicate: Optional[int] = None,
    platform: Optional[str] = None,
    read_length: Optional[int] = None,
) -> None:
    """サンプルメタデータを 1 件挿入する.

    Parameters
    ----------
    conn : sqlite3.Connection
        データベース接続。
    sample_id : str
        サンプルID。
    accession : str
        アクセッション番号。
    organism : str
        生物種。
    condition : str
        実験条件。
    replicate : int, optional
        レプリケート番号。
    platform : str, optional
        シーケンシングプラットフォーム。
    read_length : int, optional
        リード長。
    """
    conn.execute(
        """
        INSERT OR REPLACE INTO samples
            (sample_id, accession, organism, condition,
             replicate, platform, read_length)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (sample_id, accession, organism, condition,
         replicate, platform, read_length),
    )
    conn.commit()
    logger.debug("挿入: %s", sample_id)


def query_by_condition(
    conn: sqlite3.Connection,
    condition: str,
) -> list[dict[str, Any]]:
    """条件でサンプルをフィルタリングする.

    Parameters
    ----------
    conn : sqlite3.Connection
        データベース接続。
    condition : str
        実験条件（完全一致）。

    Returns
    -------
    list[dict[str, Any]]
        マッチしたサンプルの辞書リスト。
    """
    cursor = conn.execute(
        "SELECT * FROM samples WHERE condition = ?",
        (condition,),
    )
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def count_by_condition(conn: sqlite3.Connection) -> dict[str, int]:
    """条件ごとのサンプル数を集計する.

    Parameters
    ----------
    conn : sqlite3.Connection
        データベース接続。

    Returns
    -------
    dict[str, int]
        条件名 → サンプル数 の辞書。
    """
    cursor = conn.execute(
        "SELECT condition, COUNT(*) as cnt FROM samples GROUP BY condition"
    )
    return {row["condition"]: row["cnt"] for row in cursor.fetchall()}


def list_all_samples(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """全サンプルを取得する.

    Parameters
    ----------
    conn : sqlite3.Connection
        データベース接続。

    Returns
    -------
    list[dict[str, Any]]
        全サンプルの辞書リスト。
    """
    cursor = conn.execute("SELECT * FROM samples ORDER BY sample_id")
    return [dict(row) for row in cursor.fetchall()]
