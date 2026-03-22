"""secret_scanner モジュールのテスト.

既知のシークレットパターン検出と偽陽性排除を検証する。
"""

from pathlib import Path

import pytest

from scripts.ch20.secret_scanner import (
    ScanResult,
    SecretFinding,
    scan_content,
    scan_directory,
    scan_file,
)

# --- テスト用データ ---

CODE_WITH_AWS_KEY = """\
import boto3

# ハードコーディングされたAWSキー（危険！）
aws_access_key_id = "AKIAIOSFODNN7EXAMPLE"
aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
"""

CODE_WITH_API_KEY = """\
import requests

API_KEY = "sk_live_abcdefghij1234567890"
response = requests.get(url, headers={"Authorization": f"Bearer {API_KEY}"})
"""

CODE_WITH_PASSWORD = """\
config = {
    "host": "localhost",
    "password": "super_secret_password_123",
    "port": 5432,
}
"""

CODE_WITH_PRIVATE_KEY = """\
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----
"""

SAFE_CODE = """\
import os

# 環境変数から取得（安全）
api_key = os.environ.get("API_KEY")
password = os.environ.get("DATABASE_PASSWORD")

# 定数（シークレットではない）
MAX_RETRIES = 3
TIMEOUT = 30
"""

CODE_WITH_TOKEN = """\
TOKEN = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcd12"
"""


# --- scan_content ---

class TestScanContent:
    """テキスト内容のスキャンテスト."""

    def test_detect_aws_access_key(self) -> None:
        """AWS アクセスキーを検出する."""
        findings = scan_content(CODE_WITH_AWS_KEY)
        pattern_names = [f.pattern_name for f in findings]
        assert "AWS Access Key" in pattern_names

    def test_detect_aws_secret_key(self) -> None:
        """AWS シークレットキーを検出する."""
        findings = scan_content(CODE_WITH_AWS_KEY)
        pattern_names = [f.pattern_name for f in findings]
        assert "AWS Secret Key" in pattern_names

    def test_detect_api_key(self) -> None:
        """汎用APIキーを検出する."""
        findings = scan_content(CODE_WITH_API_KEY)
        assert len(findings) >= 1
        assert any(f.pattern_name == "Generic API Key assignment" for f in findings)

    def test_detect_password(self) -> None:
        """パスワードを検出する."""
        findings = scan_content(CODE_WITH_PASSWORD)
        assert len(findings) >= 1
        assert any(f.pattern_name == "Generic Password assignment" for f in findings)

    def test_detect_private_key(self) -> None:
        """秘密鍵ヘッダを検出する."""
        findings = scan_content(CODE_WITH_PRIVATE_KEY)
        assert len(findings) >= 1
        assert any(f.pattern_name == "Private Key header" for f in findings)

    def test_detect_token(self) -> None:
        """トークンを検出する."""
        findings = scan_content(CODE_WITH_TOKEN)
        assert len(findings) >= 1
        assert any(f.pattern_name == "Generic Token assignment" for f in findings)

    def test_no_false_positive_on_env_var(self) -> None:
        """環境変数からの取得は検出しない."""
        findings = scan_content(SAFE_CODE)
        assert len(findings) == 0

    def test_line_number_is_correct(self) -> None:
        """検出行番号が正しい."""
        findings = scan_content(CODE_WITH_API_KEY)
        api_key_finding = next(
            f for f in findings if f.pattern_name == "Generic API Key assignment"
        )
        assert api_key_finding.line_number == 3

    def test_filepath_default(self) -> None:
        """ファイルパスのデフォルトは <stdin>."""
        findings = scan_content(CODE_WITH_API_KEY)
        assert findings[0].filepath == Path("<stdin>")

    def test_filepath_custom(self) -> None:
        """カスタムファイルパスが設定される."""
        findings = scan_content(
            CODE_WITH_API_KEY, filepath=Path("test.py")
        )
        assert findings[0].filepath == Path("test.py")


# --- scan_file ---

class TestScanFile:
    """ファイルスキャンのテスト."""

    def test_detect_secrets_in_file(self, tmp_path: Path) -> None:
        """ファイル内のシークレットを検出する."""
        filepath = tmp_path / "config.py"
        filepath.write_text(CODE_WITH_API_KEY, encoding="utf-8")

        findings = scan_file(filepath)
        assert len(findings) >= 1
        assert findings[0].filepath == filepath

    def test_safe_file_no_findings(self, tmp_path: Path) -> None:
        """安全なファイルでは検出なし."""
        filepath = tmp_path / "safe.py"
        filepath.write_text(SAFE_CODE, encoding="utf-8")

        findings = scan_file(filepath)
        assert len(findings) == 0

    def test_file_not_found(self, tmp_path: Path) -> None:
        """存在しないファイルで FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="見つかりません"):
            scan_file(tmp_path / "nonexistent.py")

    def test_skip_binary_file(self, tmp_path: Path) -> None:
        """バイナリファイルはスキップする."""
        filepath = tmp_path / "image.png"
        filepath.write_bytes(b"\x89PNG\r\n\x1a\n")

        findings = scan_file(filepath)
        assert len(findings) == 0


# --- scan_directory ---

class TestScanDirectory:
    """ディレクトリスキャンのテスト."""

    def test_scan_finds_secrets(self, tmp_path: Path) -> None:
        """ディレクトリ内のシークレットを検出する."""
        (tmp_path / "config.py").write_text(
            CODE_WITH_API_KEY, encoding="utf-8"
        )
        (tmp_path / "safe.py").write_text(SAFE_CODE, encoding="utf-8")

        result = scan_directory(tmp_path)

        assert isinstance(result, ScanResult)
        assert result.has_secrets is True
        assert result.scanned_files == 2
        assert len(result.findings) >= 1

    def test_scan_clean_directory(self, tmp_path: Path) -> None:
        """シークレットのないディレクトリ."""
        (tmp_path / "main.py").write_text(SAFE_CODE, encoding="utf-8")

        result = scan_directory(tmp_path)

        assert result.has_secrets is False
        assert result.scanned_files == 1

    def test_scan_recursive(self, tmp_path: Path) -> None:
        """サブディレクトリも再帰的にスキャンする."""
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "secret.py").write_text(
            CODE_WITH_PASSWORD, encoding="utf-8"
        )

        result = scan_directory(tmp_path, recursive=True)
        assert result.has_secrets is True

    def test_scan_non_recursive(self, tmp_path: Path) -> None:
        """非再帰モードではサブディレクトリをスキャンしない."""
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "secret.py").write_text(
            CODE_WITH_PASSWORD, encoding="utf-8"
        )

        result = scan_directory(tmp_path, recursive=False)
        assert result.has_secrets is False

    def test_not_a_directory(self, tmp_path: Path) -> None:
        """ファイルパスで NotADirectoryError."""
        filepath = tmp_path / "file.txt"
        filepath.write_text("test", encoding="utf-8")

        with pytest.raises(NotADirectoryError, match="ディレクトリではありません"):
            scan_directory(filepath)

    def test_empty_directory(self, tmp_path: Path) -> None:
        """空ディレクトリのスキャン."""
        result = scan_directory(tmp_path)
        assert result.has_secrets is False
        assert result.scanned_files == 0

    def test_skip_binary_extensions(self, tmp_path: Path) -> None:
        """バイナリ拡張子のファイルはスキップする."""
        (tmp_path / "data.pyc").write_bytes(b"\x00\x01\x02")
        (tmp_path / "image.jpg").write_bytes(b"\xff\xd8\xff\xe0")

        result = scan_directory(tmp_path)
        assert result.scanned_files == 0
