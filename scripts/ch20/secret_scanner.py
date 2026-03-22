"""コードベース内のシークレット（APIキー・パスワード等）を検出するスキャナ.

正規表現パターンでハードコーディングされた秘密情報を検出し、
ファイルパスと該当行を報告する。git-secrets の簡易版として、
シークレット管理の原則を学ぶためのサンプル実装である。
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# 検出対象のシークレットパターン
# 各タプルは (パターン名, 正規表現) の組み合わせ
SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "AWS Access Key",
        re.compile(r"(?<![A-Z0-9])(AKIA[0-9A-Z]{16})(?![A-Z0-9])"),
    ),
    (
        "AWS Secret Key",
        re.compile(
            r"""(?i)aws[_\-]?secret[_\-]?(?:access[_\-]?)?key\s*[=:]\s*['"]?([A-Za-z0-9/+=]{40})['"]?"""
        ),
    ),
    (
        "Generic API Key assignment",
        re.compile(
            r"""(?i)(?:api[_\-]?key|apikey)\s*[=:]\s*['"]([A-Za-z0-9_\-]{20,})['"]"""
        ),
    ),
    (
        "Generic Password assignment",
        re.compile(
            r"""(?i)['"]?(?:password|passwd|pwd)['"]?\s*[=:]\s*['"]([^'"]{8,})['"]"""
        ),
    ),
    (
        "Generic Token assignment",
        re.compile(
            r"""(?i)(?:token|secret)\s*[=:]\s*['"]([A-Za-z0-9_\-]{20,})['"]"""
        ),
    ),
    (
        "Private Key header",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----"),
    ),
]

# スキャン対象外のファイル拡張子
SKIP_EXTENSIONS: frozenset[str] = frozenset({
    ".pyc", ".pyo", ".so", ".dll", ".exe", ".bin",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".zip", ".gz", ".tar", ".bz2", ".xz",
    ".pdf", ".doc", ".docx",
    ".whl", ".egg",
})


@dataclass
class SecretFinding:
    """検出されたシークレットの情報.

    Attributes
    ----------
    filepath : Path
        シークレットが検出されたファイルのパス。
    line_number : int
        該当行の行番号（1始まり）。
    pattern_name : str
        マッチしたパターンの名前。
    line : str
        該当行のテキスト（前後の空白を除去済み）。
    """

    filepath: Path
    line_number: int
    pattern_name: str
    line: str


@dataclass
class ScanResult:
    """スキャン結果の集約.

    Attributes
    ----------
    findings : list[SecretFinding]
        検出されたシークレットのリスト。
    scanned_files : int
        スキャンしたファイル数。
    """

    findings: list[SecretFinding] = field(default_factory=list)
    scanned_files: int = 0

    @property
    def has_secrets(self) -> bool:
        """シークレットが検出されたかどうか."""
        return len(self.findings) > 0


def _should_skip(filepath: Path) -> bool:
    """スキャン対象外のファイルかどうか判定する."""
    return filepath.suffix.lower() in SKIP_EXTENSIONS


def scan_content(
    content: str,
    filepath: Path | None = None,
    patterns: list[tuple[str, re.Pattern[str]]] | None = None,
) -> list[SecretFinding]:
    """テキスト内容をスキャンしてシークレットを検出する.

    Parameters
    ----------
    content : str
        スキャン対象のテキスト。
    filepath : Path | None
        ファイルパス（レポート用）。``None`` の場合は ``<stdin>``。
    patterns : list[tuple[str, re.Pattern[str]]] | None
        検出パターンのリスト。``None`` の場合はデフォルトパターンを使用。

    Returns
    -------
    list[SecretFinding]
        検出結果のリスト。
    """
    if patterns is None:
        patterns = SECRET_PATTERNS
    if filepath is None:
        filepath = Path("<stdin>")

    findings: list[SecretFinding] = []

    for line_number, line in enumerate(content.splitlines(), start=1):
        for pattern_name, pattern in patterns:
            if pattern.search(line):
                findings.append(
                    SecretFinding(
                        filepath=filepath,
                        line_number=line_number,
                        pattern_name=pattern_name,
                        line=line.strip(),
                    )
                )
                logger.warning(
                    "シークレット検出: %s:%d [%s]",
                    filepath,
                    line_number,
                    pattern_name,
                )

    return findings


def scan_file(
    filepath: Path,
    patterns: list[tuple[str, re.Pattern[str]]] | None = None,
) -> list[SecretFinding]:
    """1ファイルをスキャンしてシークレットを検出する.

    Parameters
    ----------
    filepath : Path
        スキャン対象ファイルのパス。
    patterns : list[tuple[str, re.Pattern[str]]] | None
        検出パターンのリスト。

    Returns
    -------
    list[SecretFinding]
        検出結果のリスト。

    Raises
    ------
    FileNotFoundError
        ファイルが存在しない場合。
    """
    if not filepath.exists():
        msg = f"ファイルが見つかりません: {filepath}"
        raise FileNotFoundError(msg)

    if _should_skip(filepath):
        logger.debug("スキップ（バイナリ）: %s", filepath)
        return []

    try:
        content = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        logger.debug("スキップ（デコード不可）: %s", filepath)
        return []

    return scan_content(content, filepath, patterns)


def scan_directory(
    directory: Path,
    patterns: list[tuple[str, re.Pattern[str]]] | None = None,
    recursive: bool = True,
) -> ScanResult:
    """ディレクトリ内のファイルを一括スキャンする.

    Parameters
    ----------
    directory : Path
        スキャン対象ディレクトリ。
    patterns : list[tuple[str, re.Pattern[str]]] | None
        検出パターンのリスト。
    recursive : bool
        サブディレクトリを再帰的にスキャンするかどうか。

    Returns
    -------
    ScanResult
        スキャン結果。

    Raises
    ------
    NotADirectoryError
        パスがディレクトリでない場合。
    """
    if not directory.is_dir():
        msg = f"ディレクトリではありません: {directory}"
        raise NotADirectoryError(msg)

    result = ScanResult()
    glob_pattern = "**/*" if recursive else "*"

    for filepath in sorted(directory.glob(glob_pattern)):
        if not filepath.is_file():
            continue
        if _should_skip(filepath):
            continue

        result.scanned_files += 1
        findings = scan_file(filepath, patterns)
        result.findings.extend(findings)

    logger.info(
        "スキャン完了: %d ファイル中 %d 件のシークレットを検出",
        result.scanned_files,
        len(result.findings),
    )
    return result
