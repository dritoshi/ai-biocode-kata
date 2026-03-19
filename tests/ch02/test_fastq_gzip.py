"""gzip FASTQ処理関数のテスト."""

import gzip
from pathlib import Path

import pytest

from scripts.ch02.fastq_gzip import count_reads_in_gzip, extract_read_ids, head_gzip

# テスト用FASTQデータ（2リード分）
FASTQ_CONTENT = """\
@read1 length=50
ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGA
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
@read2 length=50
GCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
"""


@pytest.fixture()
def fastq_gz(tmp_path: Path) -> Path:
    """テスト用 .fastq.gz ファイルを作成する."""
    p = tmp_path / "reads.fastq.gz"
    with gzip.open(p, "wt") as f:
        f.write(FASTQ_CONTENT)
    return p


@pytest.fixture()
def empty_fastq_gz(tmp_path: Path) -> Path:
    """空の .fastq.gz ファイルを作成する."""
    p = tmp_path / "empty.fastq.gz"
    with gzip.open(p, "wt") as f:
        f.write("")
    return p


class TestCountReadsInGzip:
    """count_reads_in_gzip() のテスト."""

    def test_two_reads(self, fastq_gz: Path) -> None:
        assert count_reads_in_gzip(fastq_gz) == 2

    def test_empty_file(self, empty_fastq_gz: Path) -> None:
        assert count_reads_in_gzip(empty_fastq_gz) == 0

    def test_many_reads(self, tmp_path: Path) -> None:
        """10リードのFASTQを生成してカウントする."""
        p = tmp_path / "many.fastq.gz"
        with gzip.open(p, "wt") as f:
            for i in range(10):
                f.write(f"@read{i}\nATGC\n+\nIIII\n")
        assert count_reads_in_gzip(p) == 10


class TestExtractReadIds:
    """extract_read_ids() のテスト."""

    def test_all_ids(self, fastq_gz: Path) -> None:
        ids = extract_read_ids(fastq_gz)
        assert ids == ["read1", "read2"]

    def test_max_reads(self, fastq_gz: Path) -> None:
        ids = extract_read_ids(fastq_gz, max_reads=1)
        assert ids == ["read1"]

    def test_empty_file(self, empty_fastq_gz: Path) -> None:
        ids = extract_read_ids(empty_fastq_gz)
        assert ids == []

    def test_max_reads_exceeds_total(self, fastq_gz: Path) -> None:
        ids = extract_read_ids(fastq_gz, max_reads=100)
        assert len(ids) == 2


class TestHeadGzip:
    """head_gzip() のテスト."""

    def test_head_4(self, fastq_gz: Path) -> None:
        lines = head_gzip(fastq_gz, n_lines=4)
        assert len(lines) == 4
        assert lines[0] == "@read1 length=50"

    def test_head_exceeds_file(self, fastq_gz: Path) -> None:
        lines = head_gzip(fastq_gz, n_lines=100)
        assert len(lines) == 8  # 2リード × 4行

    def test_head_zero(self, fastq_gz: Path) -> None:
        lines = head_gzip(fastq_gz, n_lines=0)
        assert lines == []

    def test_empty_file(self, empty_fastq_gz: Path) -> None:
        lines = head_gzip(empty_fastq_gz)
        assert lines == []
