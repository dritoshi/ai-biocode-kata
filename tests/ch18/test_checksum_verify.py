"""checksum_verify モジュールのテスト.

一時ファイルを作成して実際にハッシュ計算を行い、
一致/不一致を検証する。
"""

import hashlib
from pathlib import Path

import pytest

from scripts.ch18.checksum_verify import (
    ChecksumResult,
    compute_hash,
    verify_checksum,
    verify_checksum_list,
)

# --- テスト用ファイル作成ヘルパー ---

SAMPLE_CONTENT = b"ATGCATGCATGCATGC\nGCTAGCTAGCTAGCTA\n"


@pytest.fixture()
def sample_file(tmp_path: Path) -> Path:
    """テスト用の一時ファイルを作成する."""
    filepath = tmp_path / "test_sequence.fasta"
    filepath.write_bytes(SAMPLE_CONTENT)
    return filepath


@pytest.fixture()
def known_md5() -> str:
    """テスト用データの MD5 ハッシュ値."""
    return hashlib.md5(SAMPLE_CONTENT).hexdigest()


@pytest.fixture()
def known_sha256() -> str:
    """テスト用データの SHA256 ハッシュ値."""
    return hashlib.sha256(SAMPLE_CONTENT).hexdigest()


# --- compute_hash ---

class TestComputeHash:
    """ハッシュ値計算のテスト."""

    def test_md5(self, sample_file: Path, known_md5: str) -> None:
        """MD5 ハッシュが正しい."""
        result = compute_hash(sample_file, "md5")
        assert result == known_md5

    def test_sha256(self, sample_file: Path, known_sha256: str) -> None:
        """SHA256 ハッシュが正しい."""
        result = compute_hash(sample_file, "sha256")
        assert result == known_sha256

    def test_file_not_found(self, tmp_path: Path) -> None:
        """存在しないファイルで FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="見つかりません"):
            compute_hash(tmp_path / "nonexistent.txt")

    def test_unsupported_algorithm(self, sample_file: Path) -> None:
        """サポート外アルゴリズムで ValueError."""
        with pytest.raises(ValueError, match="サポートされていない"):
            compute_hash(sample_file, "sha512")


# --- verify_checksum ---

class TestVerifyChecksum:
    """チェックサム検証のテスト."""

    def test_match(self, sample_file: Path, known_md5: str) -> None:
        """一致する場合 ok=True."""
        result = verify_checksum(sample_file, known_md5)
        assert isinstance(result, ChecksumResult)
        assert result.ok is True
        assert result.actual == known_md5

    def test_mismatch(self, sample_file: Path) -> None:
        """不一致の場合 ok=False."""
        result = verify_checksum(sample_file, "0" * 32)
        assert result.ok is False

    def test_sha256_match(self, sample_file: Path, known_sha256: str) -> None:
        """SHA256 で一致する場合 ok=True."""
        result = verify_checksum(sample_file, known_sha256, algorithm="sha256")
        assert result.ok is True

    def test_case_insensitive(self, sample_file: Path, known_md5: str) -> None:
        """大文字のハッシュ値でも一致する."""
        result = verify_checksum(sample_file, known_md5.upper())
        assert result.ok is True

    def test_whitespace_stripped(self, sample_file: Path, known_md5: str) -> None:
        """前後のスペースは無視する."""
        result = verify_checksum(sample_file, f"  {known_md5}  ")
        assert result.ok is True

    def test_result_contains_path(self, sample_file: Path, known_md5: str) -> None:
        """結果にファイルパスが含まれる."""
        result = verify_checksum(sample_file, known_md5)
        assert result.path == sample_file
        assert result.algorithm == "md5"


# --- verify_checksum_list ---

class TestVerifyChecksumList:
    """一括検証のテスト."""

    def test_all_match(self, tmp_path: Path) -> None:
        """全ファイル一致."""
        pairs: list[tuple[Path, str]] = []
        for i in range(3):
            content = f"file_{i}".encode()
            filepath = tmp_path / f"file_{i}.txt"
            filepath.write_bytes(content)
            md5 = hashlib.md5(content).hexdigest()
            pairs.append((filepath, md5))

        results = verify_checksum_list(pairs)

        assert len(results) == 3
        assert all(r.ok for r in results)

    def test_partial_mismatch(self, tmp_path: Path) -> None:
        """一部不一致がある場合."""
        content = b"valid_content"
        filepath = tmp_path / "valid.txt"
        filepath.write_bytes(content)
        correct_md5 = hashlib.md5(content).hexdigest()

        content2 = b"another_content"
        filepath2 = tmp_path / "invalid.txt"
        filepath2.write_bytes(content2)

        pairs = [
            (filepath, correct_md5),
            (filepath2, "0" * 32),  # 不正なハッシュ
        ]

        results = verify_checksum_list(pairs)

        assert results[0].ok is True
        assert results[1].ok is False

    def test_empty_list(self) -> None:
        """空のリストでは空の結果."""
        results = verify_checksum_list([])
        assert results == []
