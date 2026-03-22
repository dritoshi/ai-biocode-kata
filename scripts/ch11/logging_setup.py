"""ロギング設定ユーティリティ — CLIツール向けのセットアップ関数."""

import logging
import sys
from pathlib import Path


def setup_logging(
    level: str = "INFO",
    log_file: str | Path | None = None,
    use_rich: bool = False,
) -> None:
    """アプリケーション全体のロギングを設定する.

    Parameters
    ----------
    level : str
        ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    log_file : str | Path | None
        ログファイルのパス。Noneの場合はstderrのみに出力
    use_rich : bool
        Trueの場合、RichHandlerを使用してカラー出力を行う
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        msg = f"不正なログレベル: {level}"
        raise ValueError(msg)

    # ルートロガーを設定
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # 既存のハンドラをクリア（重複防止）
    root_logger.handlers.clear()

    # フォーマッタ（ISO 8601タイムスタンプ）
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # stderrハンドラ
    if use_rich:
        try:
            from rich.logging import RichHandler

            stderr_handler: logging.Handler = RichHandler(
                console=__import__("rich.console", fromlist=["Console"]).Console(
                    stderr=True
                ),
                show_time=True,
                show_path=False,
            )
        except ImportError:
            # richが利用できない場合はStreamHandlerにフォールバック
            stderr_handler = logging.StreamHandler(sys.stderr)
            stderr_handler.setFormatter(formatter)
    else:
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(formatter)

    root_logger.addHandler(stderr_handler)

    # ファイルハンドラ（オプション）
    if log_file is not None:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
