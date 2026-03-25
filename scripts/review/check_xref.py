#!/usr/bin/env python3
"""相互参照チェックスクリプト

chapters/ ディレクトリ内の全Markdownファイルを対象に:
- 章間リンク (](./NN_name.md) 形式) のリンク先ファイル存在確認
- #anchor 付きリンクのアンカー照合 (GitHub形式)
- ../figures/ 参照の画像ファイル存在確認

結果を review_results/xref_check.json に保存する。
"""

import json
import re
import unicodedata
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CHAPTERS_DIR = PROJECT_ROOT / "chapters"
FIGURES_DIR = PROJECT_ROOT / "figures"
OUTPUT_DIR = PROJECT_ROOT / "review_results"


def github_anchor(heading_text: str) -> str:
    """Markdownの見出しテキストからGitHub形式のアンカーを生成する。

    GitHubのルール:
    - 小文字化
    - スペースを '-' に置換
    - 英数字、'-'、'_'、日本語文字以外を除去
    - 連続する '-' は1つにまとめない（GitHubの実際の挙動に準拠）
    """
    # Markdown記法を除去
    text = heading_text.strip()
    # 太字 **...** を除去
    text = re.sub(r'\*\*([^*]*)\*\*', r'\1', text)
    # イタリック *...* を除去
    text = re.sub(r'\*([^*]*)\*', r'\1', text)
    # インラインコード `...` を除去
    text = re.sub(r'`([^`]*)`', r'\1', text)
    # リンク [text](url) → text
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    # 画像 ![alt](url) → alt
    text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', text)
    # 絵文字ショートコード :emoji: を除去
    text = re.sub(r':[a-zA-Z0-9_+-]+:', '', text)

    # 小文字化
    text = text.lower()

    # GitHub anchor生成: 許可文字以外を除去
    # 許可: 英数字、ハイフン、アンダースコア、CJK文字、ひらがな、カタカナ、その他日本語記号
    result = []
    for ch in text:
        if ch == ' ' or ch == '\t':
            result.append('-')
        elif ch in ('-', '_'):
            result.append(ch)
        elif ch.isascii() and ch.isalnum():
            result.append(ch)
        elif not ch.isascii():
            # CJK、ひらがな、カタカナ、その他非ASCII文字を保持
            cat = unicodedata.category(ch)
            if cat.startswith(('L', 'N', 'M')):
                result.append(ch)
            elif ch in ('（', '）', '「', '」', '・', '、', '。', '：', '＝', '—', '──'):
                # GitHubは全角記号も除去する
                pass
            else:
                # その他の非ASCII文字は保持を試みる
                result.append(ch)
        # ASCII特殊文字（:, (, ), ., /, etc.）は除去

    anchor = ''.join(result)
    # 先頭・末尾のハイフンを除去
    anchor = anchor.strip('-')

    return anchor


def extract_headings(filepath: Path) -> dict[str, int]:
    """Markdownファイルから見出しを抽出し、GitHub形式のアンカーを生成する。

    コードブロック内の見出しは無視する。
    重複する見出しにはGitHub形式で -1, -2, ... のサフィックスを付与する。

    Returns:
        dict: アンカー → 行番号のマッピング
    """
    anchors: dict[str, int] = {}
    anchor_counts: dict[str, int] = {}
    in_code_block = False

    try:
        lines = filepath.read_text(encoding="utf-8").splitlines()
    except Exception:
        return anchors

    for line_no, line in enumerate(lines, 1):
        # コードブロックの開始/終了を追跡
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # 見出しの検出
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            heading_text = match.group(2)
            anchor = github_anchor(heading_text)

            if anchor in anchor_counts:
                anchor_counts[anchor] += 1
                unique_anchor = f"{anchor}-{anchor_counts[anchor]}"
            else:
                anchor_counts[anchor] = 0
                unique_anchor = anchor

            anchors[unique_anchor] = line_no
            # 初出のアンカーも登録（サフィックスなし）
            if unique_anchor != anchor:
                pass  # 重複の場合はサフィックス付きのみ
            else:
                anchors[anchor] = line_no

    return anchors


def extract_links(filepath: Path) -> list[dict]:
    """Markdownファイルからリンクを抽出する。

    Returns:
        list of dict: 各リンクの情報（line, column, raw_link, link_file, anchor）
    """
    links = []
    in_code_block = False

    try:
        lines = filepath.read_text(encoding="utf-8").splitlines()
    except Exception:
        return links

    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Markdown リンクパターン: [text](url)
        # 画像も含む: ![alt](url)
        for match in re.finditer(r'!?\[([^\]]*)\]\(([^)]+)\)', line):
            url = match.group(2)
            col = match.start() + 1

            # 章間リンク: ./NN_name.md or ./NN_name.md#anchor
            if url.startswith('./'):
                parts = url.split('#', 1)
                link_file = parts[0]
                anchor = parts[1] if len(parts) > 1 else None
                links.append({
                    "line": line_no,
                    "column": col,
                    "raw_link": url,
                    "type": "chapter_link",
                    "link_file": link_file,
                    "anchor": anchor,
                })

            # 画像リンク: ../figures/...
            elif url.startswith('../figures/'):
                links.append({
                    "line": line_no,
                    "column": col,
                    "raw_link": url,
                    "type": "figure_link",
                    "link_file": url,
                    "anchor": None,
                })

    return links


def check_chapter_link(
    source_file: Path,
    link_info: dict,
    heading_cache: dict[str, dict[str, int]],
) -> dict | None:
    """章間リンクの存在を確認する。

    Returns:
        問題があればissue dictを返す。問題なければNone。
    """
    link_file = link_info["link_file"]  # e.g., "./08_testing.md"
    anchor = link_info["anchor"]

    # ファイル名のみ取得
    target_filename = link_file.lstrip('./')
    target_path = CHAPTERS_DIR / target_filename

    if not target_path.exists():
        return {
            "file": str(source_file.relative_to(PROJECT_ROOT)),
            "line": link_info["line"],
            "severity": "CRITICAL",
            "type": "broken_file_link",
            "message": f"リンク先ファイルが存在しない: {link_file}",
            "raw_link": link_info["raw_link"],
        }

    if anchor is not None:
        # アンカーの存在を確認
        target_key = str(target_path)
        if target_key not in heading_cache:
            heading_cache[target_key] = extract_headings(target_path)

        available_anchors = heading_cache[target_key]
        if anchor not in available_anchors:
            return {
                "file": str(source_file.relative_to(PROJECT_ROOT)),
                "line": link_info["line"],
                "severity": "MAJOR",
                "type": "broken_anchor",
                "message": f"アンカーが見つからない: {link_info['raw_link']}",
                "raw_link": link_info["raw_link"],
                "expected_anchor": anchor,
                "available_anchors": list(available_anchors.keys())[:20],
            }

    return None


def check_figure_link(source_file: Path, link_info: dict) -> dict | None:
    """画像リンクの存在を確認する。

    Returns:
        問題があればissue dictを返す。問題なければNone。
    """
    raw_link = link_info["raw_link"]  # e.g., "../figures/ch01_xxx.png"
    # chapters/ から見た相対パスなので、chapters/../figures/ = figures/
    figure_filename = raw_link.replace('../figures/', '')
    figure_path = FIGURES_DIR / figure_filename

    if not figure_path.exists():
        return {
            "file": str(source_file.relative_to(PROJECT_ROOT)),
            "line": link_info["line"],
            "severity": "CRITICAL",
            "type": "broken_figure_link",
            "message": f"画像ファイルが存在しない: {raw_link}",
            "raw_link": raw_link,
        }

    return None


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    md_files = sorted(CHAPTERS_DIR.glob("*.md"))
    heading_cache: dict[str, dict[str, int]] = {}
    issues: list[dict] = []
    stats = {
        "total_files_checked": 0,
        "total_chapter_links": 0,
        "total_figure_links": 0,
        "broken_file_links": 0,
        "broken_anchors": 0,
        "broken_figure_links": 0,
    }

    for md_file in md_files:
        stats["total_files_checked"] += 1
        links = extract_links(md_file)

        for link_info in links:
            if link_info["type"] == "chapter_link":
                stats["total_chapter_links"] += 1
                issue = check_chapter_link(md_file, link_info, heading_cache)
                if issue:
                    issues.append(issue)
                    if issue["type"] == "broken_file_link":
                        stats["broken_file_links"] += 1
                    elif issue["type"] == "broken_anchor":
                        stats["broken_anchors"] += 1

            elif link_info["type"] == "figure_link":
                stats["total_figure_links"] += 1
                issue = check_figure_link(md_file, link_info)
                if issue:
                    issues.append(issue)
                    stats["broken_figure_links"] += 1

    # 重大度でソート
    severity_order = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2}
    issues.sort(key=lambda x: (severity_order.get(x["severity"], 99), x["file"], x["line"]))

    result = {
        "check": "cross_reference_check",
        "stats": stats,
        "total_issues": len(issues),
        "issues": issues,
    }

    output_path = OUTPUT_DIR / "xref_check.json"
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # コンソール出力
    print(f"=== 相互参照チェック結果 ===")
    print(f"チェック対象ファイル数: {stats['total_files_checked']}")
    print(f"章間リンク数: {stats['total_chapter_links']}")
    print(f"画像リンク数: {stats['total_figure_links']}")
    print(f"")
    print(f"問題件数: {len(issues)}")
    print(f"  CRITICAL (リンク先ファイル不在): {stats['broken_file_links']}")
    print(f"  CRITICAL (画像ファイル不在):     {stats['broken_figure_links']}")
    print(f"  MAJOR    (アンカー不一致):       {stats['broken_anchors']}")
    print()

    for issue in issues:
        severity = issue["severity"]
        print(f"[{severity}] {issue['file']}:{issue['line']} — {issue['message']}")

    print(f"\n結果を {output_path.relative_to(PROJECT_ROOT)} に保存しました。")


if __name__ == "__main__":
    main()
