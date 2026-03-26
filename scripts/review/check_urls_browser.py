#!/usr/bin/env python3
"""anti-bot URL をヘッドレスブラウザで再確認する.

既存の docs/review/url_check.json を入力として読み込み、
指定カテゴリの URL に対して Playwright Chromium でアクセスを試みる。
結果は docs/review/url_check_browser.json に保存する。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_INPUT_FILE = PROJECT_ROOT / "docs" / "review" / "url_check.json"
DEFAULT_OUTPUT_FILE = PROJECT_ROOT / "docs" / "review" / "url_check_browser.json"
DEFAULT_CATEGORY = "anti-bot"
DEFAULT_TIMEOUT_SEC = 20.0
DEFAULT_DELAY_SEC = 1.0
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)
MAX_PREVIEW_CHARS = 280

BLOCK_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "challenge_page",
        re.compile(
            r"just a moment|verify you are human|security check|checking your browser|captcha",
            re.IGNORECASE,
        ),
    ),
    (
        "access_denied",
        re.compile(r"access denied|request blocked|forbidden|not allowed", re.IGNORECASE),
    ),
    (
        "login_or_paywall",
        re.compile(
            r"sign in|log in|institutional access|purchase access|subscribe|subscription required",
            re.IGNORECASE,
        ),
    ),
)


def load_url_check(path: Path) -> dict[str, Any]:
    """HTTP ベースの URL チェック結果 JSON を読み込む."""
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict) or "urls" not in data:
        raise ValueError(f"Invalid URL check document: {path}")
    return data


def select_target_entries(
    document: dict[str, Any],
    category: str,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """指定カテゴリの URL エントリを抽出する."""
    entries = [
        entry
        for entry in document.get("urls", [])
        if entry.get("category") == category
    ]
    if limit is not None:
        entries = entries[:limit]
    return entries


def normalize_text(text: str) -> str:
    """空白を正規化して比較しやすくする."""
    return re.sub(r"\s+", " ", text).strip().lower()


def summarize_body_text(text: str, limit: int = MAX_PREVIEW_CHARS) -> str:
    """本文の先頭断片を短く保持する."""
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return f"{compact[:limit].rstrip()}..."


def detect_block_reason(page_title: str, body_text: str) -> str | None:
    """タイトルと本文からブロック画面らしさを判定する."""
    combined = normalize_text(f"{page_title}\n{body_text}")
    if not combined:
        return None

    for label, pattern in BLOCK_PATTERNS:
        if pattern.search(combined):
            return label
    return None


def classify_browser_observation(
    page_title: str,
    body_text: str,
    response_status: int | None,
) -> tuple[str, str | None]:
    """取得結果を browser_ok / browser_blocked / browser_error に分類する."""
    block_reason = detect_block_reason(page_title, body_text)
    if block_reason is not None:
        return "browser_blocked", block_reason

    if page_title.strip() and (response_status is None or 200 <= response_status < 400):
        return "browser_ok", None

    return "browser_error", "missing_title_or_unexpected_status"


def build_output_document(
    source_path: Path,
    category: str,
    timeout_sec: float,
    delay_sec: float,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """ブラウザ再確認結果の JSON ドキュメントを構築する."""
    summary = Counter(row["browser_category"] for row in rows)
    return {
        "metadata": {
            "source_file": str(source_path),
            "category_filter": category,
            "timeout_sec": timeout_sec,
            "delay_sec": delay_sec,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "total_checked": len(rows),
        },
        "summary": dict(summary),
        "urls": rows,
    }


def ensure_playwright() -> tuple[Any, type[BaseException]]:
    """Playwright sync API を遅延 import する."""
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Playwright が未導入である。"
            " `.venv/bin/pip install -r scripts/review/requirements-browser.txt` と "
            " `.venv/bin/python -m playwright install chromium` を実行すること。"
        ) from exc

    return sync_playwright, PlaywrightTimeoutError


def check_single_url_with_browser(
    page: Any,
    entry: dict[str, Any],
    timeout_ms: int,
    timeout_error_type: type[BaseException],
) -> dict[str, Any]:
    """単一 URL をブラウザで再確認する."""
    url = entry["url"]
    response_status: int | None = None
    final_url: str | None = None
    page_title = ""
    body_text = ""

    try:
        response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        if response is not None:
            response_status = response.status

        try:
            page.wait_for_load_state("networkidle", timeout=min(timeout_ms, 5000))
        except timeout_error_type:
            pass

        final_url = page.url

        try:
            page_title = page.title()
        except timeout_error_type:
            page_title = ""

        try:
            body_text = page.locator("body").inner_text(timeout=min(timeout_ms, 5000))
        except timeout_error_type:
            body_text = ""

        browser_category, error = classify_browser_observation(
            page_title=page_title,
            body_text=body_text,
            response_status=response_status,
        )
    except timeout_error_type:
        browser_category = "browser_timeout"
        error = "Timeout"
        final_url = page.url or final_url
    except Exception as exc:  # pragma: no cover - Playwright 実行時の保険
        browser_category = "browser_error"
        error = str(exc)
        final_url = page.url or final_url

    return {
        "source_url": url,
        "original_category": entry.get("category"),
        "browser_category": browser_category,
        "response_status": response_status,
        "final_url": final_url,
        "page_title": page_title or None,
        "body_preview": summarize_body_text(body_text) if body_text else None,
        "error": error,
        "locations": entry.get("locations", []),
    }


def run_browser_checks(
    entries: list[dict[str, Any]],
    timeout_sec: float,
    delay_sec: float,
) -> list[dict[str, Any]]:
    """Playwright Chromium で URL 群を逐次確認する."""
    sync_playwright, timeout_error_type = ensure_playwright()
    timeout_ms = int(timeout_sec * 1000)
    rows: list[dict[str, Any]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=DEFAULT_USER_AGENT,
            locale="en-US",
        )
        page = context.new_page()

        for index, entry in enumerate(entries, start=1):
            row = check_single_url_with_browser(
                page=page,
                entry=entry,
                timeout_ms=timeout_ms,
                timeout_error_type=timeout_error_type,
            )
            rows.append(row)

            print(
                f"[{index}/{len(entries)}] {row['browser_category']}"
                f" {entry['url']}"
            )
            if delay_sec > 0 and index < len(entries):
                time.sleep(delay_sec)

        context.close()
        browser.close()

    return rows


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI 引数を解釈する."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_FILE,
        help="入力 JSON。既定は docs/review/url_check.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help="出力 JSON。既定は docs/review/url_check_browser.json",
    )
    parser.add_argument(
        "--category",
        default=DEFAULT_CATEGORY,
        help="再確認対象カテゴリ。既定は anti-bot",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="確認件数を先頭 N 件に制限する",
    )
    parser.add_argument(
        "--timeout-sec",
        type=float,
        default=DEFAULT_TIMEOUT_SEC,
        help="各 URL のブラウザ待機秒数。既定は 20 秒",
    )
    parser.add_argument(
        "--delay-sec",
        type=float,
        default=DEFAULT_DELAY_SEC,
        help="URL 間の待機秒数。既定は 1 秒",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI エントリポイント."""
    args = parse_args(argv)
    document = load_url_check(args.input)
    entries = select_target_entries(
        document=document,
        category=args.category,
        limit=args.limit,
    )

    print(f"Input: {args.input}")
    print(f"Target category: {args.category}")
    print(f"Selected URLs: {len(entries)}")

    if not entries:
        output = build_output_document(
            source_path=args.input,
            category=args.category,
            timeout_sec=args.timeout_sec,
            delay_sec=args.delay_sec,
            rows=[],
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as handle:
            json.dump(output, handle, ensure_ascii=False, indent=2)
        print(f"No matching URLs. Empty result saved to: {args.output}")
        return 0

    try:
        rows = run_browser_checks(
            entries=entries,
            timeout_sec=args.timeout_sec,
            delay_sec=args.delay_sec,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    output = build_output_document(
        source_path=args.input,
        category=args.category,
        timeout_sec=args.timeout_sec,
        delay_sec=args.delay_sec,
        rows=rows,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)

    print()
    print("SUMMARY")
    for name, count in sorted(output["summary"].items()):
        print(f"  {name}: {count}")
    print(f"Saved to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
