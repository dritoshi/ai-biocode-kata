"""ジェネレータFASTQフィルタリングのテスト."""

from pathlib import Path

import pytest
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from scripts.ch15.generator_fastq import (
    filter_by_length,
    filter_by_quality,
    process_pipeline,
    read_fastq_records,
)


def _write_fastq(path: Path, records: list[tuple[str, str, list[int]]]) -> None:
    """テスト用のFASTQファイルを書き出すヘルパー.

    Parameters
    ----------
    path : Path
        出力先パス
    records : list[tuple[str, str, list[int]]]
        (id, sequence, quality_scores) のリスト
    """
    with open(path, "w") as f:
        for read_id, seq, quals in records:
            # Phredスコアを文字に変換（+33オフセット）
            qual_str = "".join(chr(q + 33) for q in quals)
            f.write(f"@{read_id}\n{seq}\n+\n{qual_str}\n")


@pytest.fixture()
def fastq_file(tmp_path: Path) -> Path:
    """テスト用FASTQファイルを生成するフィクスチャ."""
    path = tmp_path / "test.fastq"
    _write_fastq(
        path,
        [
            ("read1", "ATGCATGC", [30, 30, 30, 30, 30, 30, 30, 30]),  # 長さ8, 品質30
            ("read2", "ATG", [10, 10, 10]),  # 長さ3, 品質10
            ("read3", "ATGCATGCATGC", [25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25]),  # 長さ12, 品質25
            ("read4", "ATGCAT", [35, 35, 5, 5, 5, 5]),  # 長さ6, 平均品質15
        ],
    )
    return path


class TestReadFastqRecords:
    """read_fastq_records のテスト."""

    def test_reads_all_records(self, fastq_file: Path) -> None:
        """全レコードを読み込む."""
        records = list(read_fastq_records(fastq_file))
        assert len(records) == 4

    def test_record_ids(self, fastq_file: Path) -> None:
        """レコードIDが正しい."""
        records = list(read_fastq_records(fastq_file))
        ids = [r.id for r in records]
        assert ids == ["read1", "read2", "read3", "read4"]


class TestFilterByLength:
    """filter_by_length のテスト."""

    def test_filter_short_reads(self, fastq_file: Path) -> None:
        """最小長以上のレコードだけを返す."""
        records = read_fastq_records(fastq_file)
        filtered = list(filter_by_length(records, min_length=6))
        ids = [r.id for r in filtered]
        assert ids == ["read1", "read3", "read4"]

    def test_filter_all(self, fastq_file: Path) -> None:
        """閾値が非常に大きい場合、すべてフィルタされる."""
        records = read_fastq_records(fastq_file)
        filtered = list(filter_by_length(records, min_length=100))
        assert len(filtered) == 0


class TestFilterByQuality:
    """filter_by_quality のテスト."""

    def test_filter_low_quality(self, fastq_file: Path) -> None:
        """平均品質が閾値以上のレコードだけを返す."""
        records = read_fastq_records(fastq_file)
        filtered = list(filter_by_quality(records, min_avg_quality=20))
        ids = [r.id for r in filtered]
        # read1(品質30), read3(品質25) が通過。read2(品質10), read4(平均15)は除外
        assert ids == ["read1", "read3"]


class TestProcessPipeline:
    """process_pipeline のテスト."""

    def test_combined_filter(self, fastq_file: Path) -> None:
        """長さフィルタと品質フィルタを組み合わせる."""
        result = process_pipeline(fastq_file, min_length=6, min_avg_quality=20)
        ids = [r.id for r in result]
        # 長さ>=6 かつ 品質>=20: read1(長さ8,品質30), read3(長さ12,品質25)
        assert ids == ["read1", "read3"]

    def test_no_results(self, fastq_file: Path) -> None:
        """条件が厳しすぎると空リストを返す."""
        result = process_pipeline(fastq_file, min_length=100, min_avg_quality=40)
        assert result == []
