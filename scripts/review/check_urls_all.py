#!/usr/bin/env python3
"""書籍プロジェクト全体のURL実在性チェックスクリプト.

chapters/*.md と references/*.bib から URL を抽出し、
HTTP HEAD/GET でアクセス可能かを確認する。
結果は JSON に保存される。既定の出力先は docs/review/url_check.json。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.client import RemoteDisconnected
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

# --- 定数 ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.reference_usage import extract_doi, extract_explicit_url, iter_used_bib_entries

CHAPTERS_DIR = PROJECT_ROOT / "chapters"
REFERENCES_DIR = PROJECT_ROOT / "references"
DEFAULT_OUTPUT_FILE = PROJECT_ROOT / "docs" / "review" / "url_check.json"

TIMEOUT = 15
MAX_WORKERS = 8

# ダミーURL除外パターン
DUMMY_PATTERNS = [
    "https://...",
    "http://...",
    "example.com",
    "example.org",
    "example.net",
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "your-username",
    "username",
    "your-org",
    "mypackage",
    "my-tool",
    "my-project",
    "github.com/author/tool/",
    "my-repo",
    "your-repo",
    "yourname",
]

# Anti-bot ステータスコード
ANTI_BOT_CODES = {403, 418}

# レート制限対象ドメイン (domain_substring -> min_interval_sec)
RATE_LIMITS: dict[str, float] = {
    "arxiv.org": 3.0,
    "ncbi.nlm.nih.gov": 0.34,  # 3リクエスト/秒 -> 0.34秒間隔
    "pubmed.ncbi.nlm.nih.gov": 0.34,
}

# --- URL抽出用正規表現 ---
# Markdown: [text](url)
MD_LINK_RE = re.compile(r"\[[^\]]*\]\((https?://[^\)\s]+)\)")
# Markdown reference: [ref]: url
MD_REF_RE = re.compile(r"^\[[^\]]+\]:\s*(https?://\S+)", re.MULTILINE)
# Angle-bracket URL: <url>
ANGLE_URL_RE = re.compile(r"<(https?://[^>]+)>")
# Bare URL: https://example.org/path
# Markdown 記法や日本語本文を巻き込まないよう、URL として妥当な ASCII のみ許容する。
BARE_URL_RE = re.compile(r"(https?://[A-Za-z0-9._~:/?#@!$&'*+,;=%-]+)")
def is_dummy_url(url: str) -> bool:
    """ダミー/プレースホルダ URL かどうか判定."""
    parsed = urlparse(url)
    if url.startswith(("http://", "https://")) and not parsed.netloc:
        return True

    lower = url.lower()
    for pat in DUMMY_PATTERNS:
        if pat in lower:
            return True
    return False


def clean_url(url: str) -> str:
    """末尾の句読点やMarkdown記法の残骸を除去."""
    # 末尾のカンマ、ピリオド、セミコロン、括弧を除去
    url = url.rstrip(".,;)")
    # 末尾のバックスラッシュ除去 (BibTeX)
    url = url.rstrip("\\")
    return url


def extract_urls_from_md(filepath: Path) -> list[tuple[str, int]]:
    """Markdownファイルから (url, line_number) のリストを抽出."""
    results = []
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    for line_no, line in enumerate(lines, start=1):
        seen_urls: set[str] = set()
        for regex in (MD_LINK_RE, MD_REF_RE, ANGLE_URL_RE, BARE_URL_RE):
            for match in regex.finditer(line):
                url = clean_url(match.group(1))
                if not is_dummy_url(url) and url not in seen_urls:
                    results.append((url, line_no))
                    seen_urls.add(url)
    return results


def extract_urls_from_bib(filepath: Path) -> list[tuple[str, int]]:
    """BibTeXファイルから (url, line_number) のリストを抽出."""
    results = []
    for entry in iter_used_bib_entries(filepath, PROJECT_ROOT):
        explicit_url = extract_explicit_url(entry)
        if explicit_url is not None:
            url, line_no = explicit_url
            url = clean_url(url)
            if not is_dummy_url(url):
                results.append((url, line_no))
            continue

        doi_info = extract_doi(entry)
        if doi_info is None:
            continue

        doi, line_no = doi_info
        if doi.startswith("http"):
            url = clean_url(doi)
        else:
            url = f"https://doi.org/{doi}"
        if not is_dummy_url(url):
            results.append((url, line_no))

    return results


def build_url_index(
    chapters_dir: Path, references_dir: Path
) -> dict[str, list[dict[str, Any]]]:
    """全ファイルからURLを抽出し、URL -> 出現箇所のマッピングを構築."""
    url_locations: dict[str, list[dict[str, Any]]] = defaultdict(list)

    # chapters/*.md
    for md_file in sorted(chapters_dir.glob("*.md")):
        rel_path = str(md_file.relative_to(PROJECT_ROOT))
        for url, line_no in extract_urls_from_md(md_file):
            url_locations[url].append({"file": rel_path, "line": line_no})

    # references/*.bib
    for bib_file in sorted(references_dir.glob("*.bib")):
        rel_path = str(bib_file.relative_to(PROJECT_ROOT))
        for url, line_no in extract_urls_from_bib(bib_file):
            url_locations[url].append({"file": rel_path, "line": line_no})

    return dict(url_locations)


def get_rate_limit_key(url: str) -> str | None:
    """URL がレート制限対象ドメインに該当するか判定."""
    parsed = urlparse(url)
    host = parsed.hostname or ""
    for domain, _ in RATE_LIMITS.items():
        if domain in host:
            return domain
    return None


def check_single_url(url: str) -> dict[str, Any]:
    """単一URLの到達性をチェック."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    result: dict[str, Any] = {
        "url": url,
        "status_code": None,
        "category": None,
        "error": None,
        "final_url": None,
    }

    is_doi = "doi.org/" in url

    # まず HEAD を試す (DOI以外)
    for method in (["GET"] if is_doi else ["HEAD", "GET"]):
        req = urllib.request.Request(url, headers=headers, method=method)

        try:
            response = urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx)
            status = response.getcode()
            final_url = response.geturl()

            result["status_code"] = status
            if final_url != url:
                result["final_url"] = final_url

            if 200 <= status < 300:
                result["category"] = "ok"
            elif 300 <= status < 400:
                result["category"] = "redirect"
            else:
                result["category"] = "error"
            return result

        except urllib.error.HTTPError as e:
            result["status_code"] = e.code
            if e.code in ANTI_BOT_CODES:
                result["category"] = "anti-bot"
                return result
            elif method == "HEAD":
                # HEAD が拒否されるサイトがあるので GET にフォールバック
                continue
            else:
                result["category"] = "error"
                result["error"] = f"HTTP {e.code}"
                return result

        except urllib.error.URLError as e:
            result["error"] = str(e.reason)
            result["category"] = "connection_error"
            return result

        except RemoteDisconnected:
            if method == "HEAD":
                continue
            result["error"] = "RemoteDisconnected"
            result["category"] = "connection_error"
            return result

        except TimeoutError:
            result["error"] = "Timeout"
            result["category"] = "timeout"
            return result

        except Exception as e:
            result["error"] = str(e)
            result["category"] = "connection_error"
            return result

    return result


def check_urls_with_rate_limit(
    urls: list[str],
) -> dict[str, dict[str, Any]]:
    """レート制限を考慮しながら全URLをチェック."""
    # ドメイン別にグループ化
    rate_limited_groups: dict[str, list[str]] = defaultdict(list)
    normal_urls: list[str] = []

    for url in urls:
        key = get_rate_limit_key(url)
        if key:
            rate_limited_groups[key].append(url)
        else:
            normal_urls.append(url)

    results: dict[str, dict[str, Any]] = {}
    total = len(urls)
    checked = 0

    # レート制限対象を逐次処理
    for domain, domain_urls in rate_limited_groups.items():
        interval = RATE_LIMITS[domain]
        print(f"  Checking {len(domain_urls)} URLs for {domain} (interval={interval}s)...")
        for url in domain_urls:
            results[url] = check_single_url(url)
            checked += 1
            status = results[url]["status_code"]
            cat = results[url]["category"]
            print(f"  [{checked}/{total}] {cat} ({status}) {url[:80]}")
            time.sleep(interval)

    # 通常URLを並列処理
    print(f"  Checking {len(normal_urls)} general URLs (max_workers={MAX_WORKERS})...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {
            executor.submit(check_single_url, url): url for url in normal_urls
        }
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception as e:
                results[url] = {
                    "url": url,
                    "status_code": None,
                    "category": "connection_error",
                    "error": str(e),
                    "final_url": None,
                }
            checked += 1
            status = results[url]["status_code"]
            cat = results[url]["category"]
            print(f"  [{checked}/{total}] {cat} ({status}) {url[:80]}")

    return results


def main() -> None:
    """メイン処理."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help="JSON 出力先。既定は docs/review/url_check.json",
    )
    args = parser.parse_args()

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Scanning chapters in: {CHAPTERS_DIR}")
    print(f"Scanning references in: {REFERENCES_DIR}")
    print()

    # URL抽出
    url_index = build_url_index(CHAPTERS_DIR, REFERENCES_DIR)
    unique_urls = sorted(url_index.keys())
    total_occurrences = sum(len(locs) for locs in url_index.values())

    print(f"Found {len(unique_urls)} unique URLs ({total_occurrences} total occurrences)")
    print()

    # URLチェック
    print("Checking URLs...")
    check_results = check_urls_with_rate_limit(unique_urls)
    print()

    # 結果集約
    output: dict[str, Any] = {
        "metadata": {
            "total_unique_urls": len(unique_urls),
            "total_occurrences": total_occurrences,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        },
        "summary": {},
        "urls": [],
    }

    category_counts: dict[str, int] = defaultdict(int)

    for url in unique_urls:
        result = check_results.get(url, {})
        cat = result.get("category", "unknown")
        category_counts[cat] += 1

        entry = {
            "url": url,
            "status_code": result.get("status_code"),
            "category": cat,
            "error": result.get("error"),
            "final_url": result.get("final_url"),
            "locations": url_index[url],
        }
        output["urls"].append(entry)

    output["summary"] = dict(category_counts)

    # 出力
    output_file = args.output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Results saved to: {output_file}")
    print()

    # サマリー表示
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for cat, count in sorted(category_counts.items()):
        print(f"  {cat:20s}: {count}")
    print()

    # エラー詳細表示
    error_entries = [
        e for e in output["urls"]
        if e["category"] in ("error", "connection_error", "timeout")
    ]
    if error_entries:
        print("=" * 60)
        print("ERRORS (requires attention)")
        print("=" * 60)
        for entry in error_entries:
            severity = "HIGH" if entry["category"] == "error" else "MEDIUM"
            status = entry["status_code"] or "N/A"
            print(f"\n  [{severity}] {entry['url']}")
            print(f"    Status: {status}  Error: {entry['error']}")
            for loc in entry["locations"]:
                print(f"    -> {loc['file']}:{loc['line']}")

    # Anti-bot 表示
    anti_bot_entries = [
        e for e in output["urls"] if e["category"] == "anti-bot"
    ]
    if anti_bot_entries:
        print()
        print("=" * 60)
        print("ANTI-BOT (403/418 - likely valid but blocked)")
        print("=" * 60)
        for entry in anti_bot_entries:
            print(f"\n  {entry['url']} (HTTP {entry['status_code']})")
            for loc in entry["locations"]:
                print(f"    -> {loc['file']}:{loc['line']}")

    # リダイレクト (DOI等) 表示
    redirect_entries = [
        e for e in output["urls"]
        if e.get("final_url") and e["final_url"] != e["url"]
    ]
    if redirect_entries:
        print()
        print("=" * 60)
        print(f"REDIRECTS ({len(redirect_entries)} URLs)")
        print("=" * 60)
        for entry in redirect_entries:
            print(f"\n  {entry['url']}")
            print(f"    -> {entry['final_url']}")


if __name__ == "__main__":
    main()
