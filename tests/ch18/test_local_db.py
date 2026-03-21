"""local_db モジュールのテスト.

:memory: SQLite で挿入→クエリ→結果を検証する。
"""

from pathlib import Path

import pytest

from scripts.ch18.local_db import (
    count_by_condition,
    create_connection,
    initialize_db,
    insert_sample,
    list_all_samples,
    load_csv,
    query_by_condition,
)

# --- テスト用データ ---

SAMPLE_CSV_CONTENT = """\
sample_id,accession,organism,condition,replicate,platform,read_length
S001,SRR1234567,Homo sapiens,control,1,Illumina NovaSeq,150
S002,SRR1234568,Homo sapiens,control,2,Illumina NovaSeq,150
S003,SRR1234569,Homo sapiens,treatment,1,Illumina NovaSeq,150
S004,SRR1234570,Homo sapiens,treatment,2,Illumina NovaSeq,150
S005,SRR1234571,Homo sapiens,treatment,3,Illumina NovaSeq,150
"""


@pytest.fixture()
def db():
    """インメモリ SQLite データベースを初期化して返す."""
    conn = create_connection()
    initialize_db(conn)
    yield conn
    conn.close()


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    """テスト用 CSV ファイルを作成する."""
    filepath = tmp_path / "samples.csv"
    filepath.write_text(SAMPLE_CSV_CONTENT, encoding="utf-8")
    return filepath


# --- create_connection / initialize_db ---

class TestConnection:
    """データベース接続と初期化のテスト."""

    def test_memory_connection(self) -> None:
        """インメモリ接続が正常に動作する."""
        conn = create_connection()
        assert conn is not None
        conn.close()

    def test_initialize_creates_table(self, db) -> None:
        """initialize_db で samples テーブルが作成される."""
        cursor = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='samples'"
        )
        tables = cursor.fetchall()
        assert len(tables) == 1

    def test_initialize_is_idempotent(self, db) -> None:
        """initialize_db を2回呼んでもエラーにならない."""
        initialize_db(db)  # 2回目
        cursor = db.execute("SELECT COUNT(*) FROM samples")
        assert cursor.fetchone()[0] == 0


# --- insert_sample / query ---

class TestInsertAndQuery:
    """サンプル挿入とクエリのテスト."""

    def test_insert_and_list(self, db) -> None:
        """1件挿入して一覧取得."""
        insert_sample(
            db,
            sample_id="S001",
            accession="SRR1234567",
            organism="Homo sapiens",
            condition="control",
            replicate=1,
            platform="Illumina NovaSeq",
            read_length=150,
        )
        samples = list_all_samples(db)

        assert len(samples) == 1
        assert samples[0]["sample_id"] == "S001"
        assert samples[0]["accession"] == "SRR1234567"
        assert samples[0]["organism"] == "Homo sapiens"
        assert samples[0]["read_length"] == 150

    def test_query_by_condition(self, db) -> None:
        """条件でフィルタリング."""
        insert_sample(db, "S001", "SRR1", "Homo sapiens", "control", 1)
        insert_sample(db, "S002", "SRR2", "Homo sapiens", "treatment", 1)
        insert_sample(db, "S003", "SRR3", "Homo sapiens", "control", 2)

        controls = query_by_condition(db, "control")
        assert len(controls) == 2
        assert all(s["condition"] == "control" for s in controls)

    def test_query_no_match(self, db) -> None:
        """マッチしない条件では空リスト."""
        insert_sample(db, "S001", "SRR1", "Homo sapiens", "control", 1)
        result = query_by_condition(db, "nonexistent")
        assert result == []

    def test_count_by_condition(self, db) -> None:
        """条件ごとのサンプル数."""
        insert_sample(db, "S001", "SRR1", "Homo sapiens", "control", 1)
        insert_sample(db, "S002", "SRR2", "Homo sapiens", "control", 2)
        insert_sample(db, "S003", "SRR3", "Homo sapiens", "treatment", 1)

        counts = count_by_condition(db)
        assert counts["control"] == 2
        assert counts["treatment"] == 1

    def test_optional_fields_null(self, db) -> None:
        """省略可能フィールドを None で挿入."""
        insert_sample(
            db,
            sample_id="S001",
            accession="SRR1",
            organism="Homo sapiens",
            condition="control",
        )
        samples = list_all_samples(db)

        assert samples[0]["replicate"] is None
        assert samples[0]["platform"] is None
        assert samples[0]["read_length"] is None

    def test_upsert_replaces(self, db) -> None:
        """同じ sample_id で挿入すると上書きされる（INSERT OR REPLACE）."""
        insert_sample(db, "S001", "SRR1", "Homo sapiens", "control", 1)
        insert_sample(db, "S001", "SRR1_updated", "Homo sapiens", "treatment", 2)

        samples = list_all_samples(db)
        assert len(samples) == 1
        assert samples[0]["accession"] == "SRR1_updated"
        assert samples[0]["condition"] == "treatment"


# --- load_csv ---

class TestLoadCsv:
    """CSV 読み込みのテスト."""

    def test_load_csv(self, db, csv_file: Path) -> None:
        """CSV からの読み込みが正常に動作する."""
        count = load_csv(db, csv_file)

        assert count == 5
        samples = list_all_samples(db)
        assert len(samples) == 5

    def test_csv_data_integrity(self, db, csv_file: Path) -> None:
        """CSV の内容が正しくテーブルに格納される."""
        load_csv(db, csv_file)

        controls = query_by_condition(db, "control")
        assert len(controls) == 2

        treatments = query_by_condition(db, "treatment")
        assert len(treatments) == 3

    def test_csv_not_found(self, db, tmp_path: Path) -> None:
        """存在しない CSV で FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="見つかりません"):
            load_csv(db, tmp_path / "nonexistent.csv")

    def test_count_after_load(self, db, csv_file: Path) -> None:
        """読み込み後の条件別集計."""
        load_csv(db, csv_file)
        counts = count_by_condition(db)

        assert counts["control"] == 2
        assert counts["treatment"] == 3
