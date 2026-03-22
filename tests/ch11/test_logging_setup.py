"""logging_setup モジュールのテスト."""

import logging
from pathlib import Path

import pytest

from scripts.ch11.logging_setup import setup_logging


@pytest.fixture(autouse=True)
def _reset_logging() -> None:
    """各テスト後にルートロガーをリセットする."""
    yield
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.WARNING)


def test_default_level() -> None:
    """デフォルトのログレベルがINFOである."""
    setup_logging()
    root = logging.getLogger()
    assert root.level == logging.INFO


def test_debug_level() -> None:
    """DEBUGレベルを設定できる."""
    setup_logging(level="DEBUG")
    root = logging.getLogger()
    assert root.level == logging.DEBUG


def test_warning_level() -> None:
    """WARNINGレベルを設定できる."""
    setup_logging(level="WARNING")
    root = logging.getLogger()
    assert root.level == logging.WARNING


def test_case_insensitive() -> None:
    """ログレベルの指定は大文字小文字を問わない."""
    setup_logging(level="debug")
    root = logging.getLogger()
    assert root.level == logging.DEBUG


def test_invalid_level() -> None:
    """不正なログレベルでValueErrorが発生する."""
    with pytest.raises(ValueError, match="不正なログレベル"):
        setup_logging(level="INVALID")


def test_stderr_handler() -> None:
    """stderrハンドラが追加される."""
    setup_logging()
    root = logging.getLogger()
    assert len(root.handlers) == 1
    assert isinstance(root.handlers[0], logging.StreamHandler)


def test_file_handler(tmp_path: Path) -> None:
    """ファイルハンドラが追加される."""
    log_file = tmp_path / "test.log"
    setup_logging(log_file=log_file)

    root = logging.getLogger()
    # stderrハンドラ + ファイルハンドラの2つ
    assert len(root.handlers) == 2

    # ログを書き込んで確認
    test_logger = logging.getLogger("test")
    test_logger.info("テストメッセージ")
    # ファイルハンドラをフラッシュ
    for handler in root.handlers:
        handler.flush()

    content = log_file.read_text()
    assert "テストメッセージ" in content


def test_file_handler_format(tmp_path: Path) -> None:
    """ファイルハンドラがISO 8601フォーマットで出力する."""
    log_file = tmp_path / "test.log"
    setup_logging(log_file=log_file, level="INFO")

    test_logger = logging.getLogger("test_format")
    test_logger.info("フォーマットテスト")
    for handler in logging.getLogger().handlers:
        handler.flush()

    content = log_file.read_text()
    # ISO 8601形式のタイムスタンプ（YYYY-MM-DDTHH:MM:SS）
    assert "T" in content
    assert "[INFO]" in content


def test_no_duplicate_handlers() -> None:
    """setup_loggingを2回呼んでもハンドラが重複しない."""
    setup_logging()
    setup_logging()
    root = logging.getLogger()
    assert len(root.handlers) == 1


def test_rich_handler() -> None:
    """use_rich=Trueでエラーなく設定できる."""
    setup_logging(use_rich=True)
    root = logging.getLogger()
    assert len(root.handlers) == 1
