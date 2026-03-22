"""ファイルのチェックサム検証ユーティリティ.

ダウンロードしたファイルの整合性を MD5 または SHA256 で検証する。
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# サポートするハッシュアルゴリズム
SUPPORTED_ALGORITHMS = ("md5", "sha256")

# ファイル読み込みのバッファサイズ
BUFFER_SIZE = 65536  # 64 KB


@dataclass
class ChecksumResult:
    """チェックサム検証の結果.

    Attributes
    ----------
    path : Path
        検証対象ファイルのパス。
    algorithm : str
        使用したハッシュアルゴリズム。
    expected : str
        期待されるハッシュ値。
    actual : str
        実際に計算されたハッシュ値。
    ok : bool
        ハッシュ値が一致したかどうか。
    """

    path: Path
    algorithm: str
    expected: str
    actual: str
    ok: bool


def compute_hash(filepath: Path, algorithm: str = "md5") -> str:
    """ファイルのハッシュ値を計算する.

    Parameters
    ----------
    filepath : Path
        対象ファイルのパス。
    algorithm : str
        ハッシュアルゴリズム（``"md5"`` または ``"sha256"``）。

    Returns
    -------
    str
        16進数文字列のハッシュ値。

    Raises
    ------
    FileNotFoundError
        ファイルが存在しない場合。
    ValueError
        サポートされていないアルゴリズムの場合。
    """
    if algorithm not in SUPPORTED_ALGORITHMS:
        msg = (
            f"サポートされていないアルゴリズム: {algorithm}。"
            f"使用可能: {', '.join(SUPPORTED_ALGORITHMS)}"
        )
        raise ValueError(msg)

    if not filepath.exists():
        msg = f"ファイルが見つかりません: {filepath}"
        raise FileNotFoundError(msg)

    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            h.update(data)

    return h.hexdigest()


def verify_checksum(
    filepath: Path,
    expected: str,
    algorithm: str = "md5",
) -> ChecksumResult:
    """ファイルのチェックサムを検証する.

    Parameters
    ----------
    filepath : Path
        対象ファイルのパス。
    expected : str
        期待されるハッシュ値（16進数文字列）。
    algorithm : str
        ハッシュアルゴリズム。

    Returns
    -------
    ChecksumResult
        検証結果。
    """
    actual = compute_hash(filepath, algorithm)
    ok = actual == expected.lower().strip()

    if ok:
        logger.info("チェックサム一致: %s (%s)", filepath.name, algorithm)
    else:
        logger.warning(
            "チェックサム不一致: %s (%s) 期待=%s 実際=%s",
            filepath.name,
            algorithm,
            expected,
            actual,
        )

    return ChecksumResult(
        path=filepath,
        algorithm=algorithm,
        expected=expected.lower().strip(),
        actual=actual,
        ok=ok,
    )


def verify_checksum_list(
    pairs: list[tuple[Path, str]],
    algorithm: str = "md5",
) -> list[ChecksumResult]:
    """複数ファイルのチェックサムを一括検証する.

    Parameters
    ----------
    pairs : list[tuple[Path, str]]
        ``(ファイルパス, 期待ハッシュ値)`` のリスト。
    algorithm : str
        ハッシュアルゴリズム。

    Returns
    -------
    list[ChecksumResult]
        各ファイルの検証結果リスト。
    """
    results: list[ChecksumResult] = []
    for filepath, expected in pairs:
        result = verify_checksum(filepath, expected, algorithm)
        results.append(result)

    passed = sum(1 for r in results if r.ok)
    logger.info(
        "チェックサム検証完了: %d/%d 件一致", passed, len(results)
    )
    return results
