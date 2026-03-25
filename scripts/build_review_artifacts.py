#!/usr/bin/env python3
"""Generate reproducible review artifacts for the manuscript."""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = REPO_ROOT / "chapters"
REFERENCE_DIR = REPO_ROOT / "references"
REVIEW_DIR = REPO_ROOT / "docs" / "review"
MANUAL_CHAPTER_FIELDS = (
    "manual_status",
    "reviewer_life_science",
    "reviewer_info_science",
    "reviewer_cs",
    "reviewer_bioinformatics",
    "reviewer_programming",
    "notes",
)
AUTO_ISSUE_SOURCES = {"auto_scan", "pytest_log"}

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)]+)\)")
RAW_URL_RE = re.compile(r"https?://[^\s<>)]+")
BACKTICK_PATH_RE = re.compile(r"(?:scripts|tests|figures)/[A-Za-z0-9_./-]+/?")
BIB_URL_RE = re.compile(r"(?:url|howpublished)\s*=\s*\{?(https?://[^\s\},]+)\}?", re.IGNORECASE)
BIB_DOI_RE = re.compile(r"doi\s*=\s*\{([^\}]+)\}", re.IGNORECASE)
PYTEST_ERROR_RE = re.compile(r"^ERROR\s+(tests/\S+)", re.MULTILINE)
PYTEST_MISSING_MODULE_RE = re.compile(r"No module named '([^']+)'")


def iter_markdown_files() -> list[Path]:
    return sorted(CHAPTER_DIR.glob("*.md"))


def iter_reference_files() -> list[Path]:
    return sorted(REFERENCE_DIR.glob("*.bib"))


def strip_markdown(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_~]", "", text)
    return text.strip()


def slugify_heading(text: str) -> str:
    text = strip_markdown(text)
    text = unicodedata.normalize("NFKC", text).lower()
    pieces: list[str] = []

    for char in text:
        category = unicodedata.category(char)
        if char.isspace() or char == "-":
            pieces.append("-")
            continue
        if category.startswith(("P", "S")):
            continue
        pieces.append(char)

    return "".join(pieces).strip("-")


def find_inline_code_spans(line: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    stack: tuple[str, int] | None = None
    index = 0

    while index < len(line):
        if line[index] != "`":
            index += 1
            continue

        end = index
        while end < len(line) and line[end] == "`":
            end += 1

        fence = line[index:end]
        if stack is None:
            stack = (fence, index)
        elif stack[0] == fence:
            spans.append((stack[1], end))
            stack = None
        index = end

    return spans


def is_inside_spans(index: int, spans: list[tuple[int, int]]) -> bool:
    return any(start <= index < end for start, end in spans)


def normalize_url(url: str) -> str:
    return url.rstrip('`"\'.:,;')


def classify_url(url: str) -> str:
    if "..." in url:
        return "placeholder"
    if any(char in url for char in ('`', '"', "'")):
        return "malformed"
    if url != normalize_url(url):
        return "malformed"
    return "ok"


def path_looks_specific(path_text: str) -> bool:
    return (
        path_text.endswith((".py", ".md", ".png", ".drawio", ".yml", ".yaml", ".json", ".csv", ".tsv", ".txt", ".sh"))
        or "." in Path(path_text).name
    )


def resolve_repo_reference(source_path: Path, reference: str) -> Path:
    if reference.startswith(("./", "../")):
        return (source_path.parent / reference).resolve()
    return (REPO_ROOT / reference).resolve()


def line_suggests_repo_reference(line: str) -> bool:
    hints = (
        "本書のサンプルコード",
        "完全なコード",
        "全体は",
        "を参照",
        "にある",
        "用意している",
        "スクリプト ",
        "テストは ",
    )
    return any(hint in line for hint in hints)


def build_anchor_map(paths: list[Path]) -> tuple[dict[Path, set[str]], list[dict[str, Any]]]:
    anchors_by_path: dict[Path, set[str]] = {}
    section_rows: list[dict[str, Any]] = []

    for path in paths:
        anchors: set[str] = set()
        text = path.read_text(encoding="utf-8")
        in_code_fence = False

        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_code_fence = not in_code_fence
                continue
            if in_code_fence:
                continue

            match = HEADING_RE.match(line)
            if not match:
                continue

            level = len(match.group(1))
            title = strip_markdown(match.group(2))
            anchor = slugify_heading(title)
            anchors.add(anchor)
            section_rows.append(
                {
                    "chapter_file": path.name,
                    "line": line_number,
                    "heading_level": level,
                    "heading_text": title,
                    "anchor_slug": anchor,
                }
            )

        anchors_by_path[path.resolve()] = anchors

    return anchors_by_path, section_rows


def scan_manuscript(paths: list[Path], anchors_by_path: dict[Path, set[str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    reference_rows: list[dict[str, Any]] = []
    issue_rows: list[dict[str, Any]] = []
    chapter_rows: list[dict[str, Any]] = []
    issue_counter = 1

    for path in paths:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        stats = Counter()
        in_code_fence = False

        for line_number, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_code_fence = not in_code_fence
                if not in_code_fence:
                    stats["code_fences"] += 1
                continue

            if in_code_fence:
                continue

            inline_code_spans = find_inline_code_spans(line)
            link_spans: list[tuple[int, int]] = []

            if not in_code_fence:
                heading_match = HEADING_RE.match(line)
                if heading_match:
                    stats["headings"] += 1

            for match in LINK_RE.finditer(line):
                if is_inside_spans(match.start(), inline_code_spans):
                    continue

                link_spans.append((match.start(), match.end()))
                is_image = bool(match.group(1))
                label = match.group(2).strip()
                raw_target = match.group(3).strip()
                target_without_anchor, _, anchor = raw_target.partition("#")
                row_base = {
                    "chapter_file": path.name,
                    "line": line_number,
                    "source_kind": "image" if is_image else "markdown_link",
                    "label": label,
                    "raw_target": raw_target,
                    "context": line.strip(),
                }

                if "://" in raw_target:
                    stats["external_refs"] += 1
                    normalized = normalize_url(raw_target)
                    status = classify_url(raw_target)
                    reference_rows.append(
                        row_base
                        | {
                            "target_type": "external",
                            "normalized_target": normalized,
                            "domain": normalized.split("/")[2] if "://" in normalized else "",
                            "exists": "",
                            "anchor_target": "",
                            "anchor_status": "",
                            "syntax_status": status,
                        }
                    )
                    if status != "ok":
                        issue_rows.append(
                            {
                                "issue_id": f"AUTO-{issue_counter:04d}",
                                "severity": "A" if status == "malformed" else "B",
                                "chapter_file": path.name,
                                "line": line_number,
                                "category": f"{status}_external_reference",
                                "subject": raw_target,
                                "evidence": line.strip(),
                                "proposed_action": "URLの末尾記号や省略表記を取り除き、実際に到達可能なURLへ修正する。",
                                "source": "auto_scan",
                            }
                        )
                        issue_counter += 1
                    continue

                stats["local_links"] += 1
                target_text = target_without_anchor or "."
                if raw_target.startswith("#"):
                    resolved = path.resolve()
                    exists = True
                    anchor_target = anchor or raw_target[1:]
                else:
                    resolved = (path.parent / target_text).resolve()
                    exists = resolved.exists()
                    anchor_target = anchor

                anchor_status = ""
                if anchor_target:
                    valid_anchors = anchors_by_path.get(resolved, set())
                    anchor_status = "ok" if anchor_target in valid_anchors else "missing"
                    if anchor_status == "missing":
                        issue_rows.append(
                            {
                                "issue_id": f"AUTO-{issue_counter:04d}",
                                "severity": "A",
                                "chapter_file": path.name,
                                "line": line_number,
                                "category": "broken_anchor_link",
                                "subject": raw_target,
                                "evidence": line.strip(),
                                "proposed_action": "リンク先見出しのアンカーを現行見出しに合わせて修正する。",
                                "source": "auto_scan",
                            }
                        )
                        issue_counter += 1

                reference_rows.append(
                    row_base
                    | {
                        "target_type": "local",
                        "normalized_target": str(resolved.relative_to(REPO_ROOT)) if resolved.is_relative_to(REPO_ROOT) else str(resolved),
                        "domain": "",
                        "exists": "yes" if exists else "no",
                        "anchor_target": anchor_target,
                        "anchor_status": anchor_status,
                        "syntax_status": "ok",
                    }
                )

                if not exists:
                    issue_rows.append(
                        {
                            "issue_id": f"AUTO-{issue_counter:04d}",
                            "severity": "A",
                            "chapter_file": path.name,
                            "line": line_number,
                            "category": "broken_local_link",
                            "subject": raw_target,
                            "evidence": line.strip(),
                            "proposed_action": "リンク先のパスを現行ファイル名または相対パスに合わせて修正する。",
                            "source": "auto_scan",
                        }
                    )
                    issue_counter += 1

            for match in RAW_URL_RE.finditer(line):
                if is_inside_spans(match.start(), inline_code_spans):
                    continue
                if any(start <= match.start() < end for start, end in link_spans):
                    continue

                raw_url = match.group(0)
                normalized = normalize_url(raw_url)
                status = classify_url(raw_url)
                stats["external_refs"] += 1
                reference_rows.append(
                    {
                        "chapter_file": path.name,
                        "line": line_number,
                        "source_kind": "raw_url",
                        "label": "",
                        "raw_target": raw_url,
                        "normalized_target": normalized,
                        "target_type": "external",
                        "domain": normalized.split("/")[2] if "://" in normalized else "",
                        "exists": "",
                        "anchor_target": "",
                        "anchor_status": "",
                        "syntax_status": status,
                        "context": line.strip(),
                    }
                )
                if status != "ok":
                    issue_rows.append(
                        {
                            "issue_id": f"AUTO-{issue_counter:04d}",
                            "severity": "A" if status == "malformed" else "B",
                            "chapter_file": path.name,
                            "line": line_number,
                            "category": f"{status}_external_reference",
                            "subject": raw_url,
                            "evidence": line.strip(),
                            "proposed_action": "URLの表記を正規化し、必要なら脚注や本文で『例示URL』と明示する。",
                            "source": "auto_scan",
                        }
                    )
                    issue_counter += 1

            for start, end in inline_code_spans:
                inline_text = line[start:end].strip("`")
                if not line_suggests_repo_reference(line):
                    continue
                for match in BACKTICK_PATH_RE.finditer(inline_text):
                    relative_ref = match.group(0)
                    resolved = resolve_repo_reference(path, relative_ref)
                    if resolved.exists():
                        continue
                    if not path_looks_specific(relative_ref):
                        continue

                    stats["missing_repo_path_refs"] += 1
                    issue_rows.append(
                        {
                            "issue_id": f"AUTO-{issue_counter:04d}",
                            "severity": "A",
                            "chapter_file": path.name,
                            "line": line_number,
                            "category": "missing_repo_path_reference",
                            "subject": relative_ref,
                            "evidence": line.strip(),
                            "proposed_action": "本文中のファイル参照を現行リポジトリ構成に合わせて修正する。",
                            "source": "auto_scan",
                        }
                    )
                    issue_counter += 1

        issue_counts = Counter(
            row["category"] for row in issue_rows if row["chapter_file"] == path.name and row["source"] == "auto_scan"
        )
        chapter_rows.append(
            {
                "chapter_file": path.name,
                "chapter_title": next(
                    (strip_markdown(HEADING_RE.match(line).group(2)) for line in lines if HEADING_RE.match(line)),
                    "",
                ),
                "headings": stats["headings"],
                "code_fences": stats["code_fences"],
                "external_refs": stats["external_refs"],
                "local_links": stats["local_links"],
                "broken_local_links": issue_counts["broken_local_link"],
                "broken_anchor_links": issue_counts["broken_anchor_link"],
                "malformed_external_refs": issue_counts["malformed_external_reference"],
                "placeholder_external_refs": issue_counts["placeholder_external_reference"],
                "missing_repo_path_refs": issue_counts["missing_repo_path_reference"],
                "manual_status": "",
                "reviewer_life_science": "",
                "reviewer_info_science": "",
                "reviewer_cs": "",
                "reviewer_bioinformatics": "",
                "reviewer_programming": "",
                "notes": "",
            }
        )

    return reference_rows, issue_rows, chapter_rows


def scan_reference_files(paths: list[Path]) -> list[dict[str, Any]]:
    reference_rows: list[dict[str, Any]] = []

    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        rel_path = str(path.relative_to(REPO_ROOT))

        for line_number, line in enumerate(lines, start=1):
            for match in BIB_URL_RE.finditer(line):
                raw_url = match.group(1).strip()
                normalized = normalize_url(raw_url)
                reference_rows.append(
                    {
                        "chapter_file": rel_path,
                        "line": line_number,
                        "source_kind": "bib_url",
                        "label": "",
                        "target_type": "external",
                        "raw_target": raw_url,
                        "normalized_target": normalized,
                        "domain": normalized.split("/")[2] if "://" in normalized else "",
                        "exists": "",
                        "anchor_target": "",
                        "anchor_status": "",
                        "syntax_status": classify_url(raw_url),
                        "context": line.strip(),
                    }
                )

            for match in BIB_DOI_RE.finditer(line):
                doi = match.group(1).strip()
                raw_url = doi if doi.startswith("http") else f"https://doi.org/{doi}"
                normalized = normalize_url(raw_url)
                reference_rows.append(
                    {
                        "chapter_file": rel_path,
                        "line": line_number,
                        "source_kind": "bib_doi",
                        "label": "",
                        "target_type": "external",
                        "raw_target": raw_url,
                        "normalized_target": normalized,
                        "domain": normalized.split("/")[2] if "://" in normalized else "",
                        "exists": "",
                        "anchor_target": "",
                        "anchor_status": "",
                        "syntax_status": classify_url(raw_url),
                        "context": line.strip(),
                    }
                )

    return reference_rows


def parse_pytest_log(path: Path | None, existing_issue_count: int) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []

    text = path.read_text(encoding="utf-8")
    error_tests = PYTEST_ERROR_RE.findall(text)
    missing_modules = sorted(set(PYTEST_MISSING_MODULE_RE.findall(text)))
    if not error_tests and not missing_modules:
        return []

    rows: list[dict[str, Any]] = []
    issue_number = existing_issue_count + 1

    if missing_modules:
        rows.append(
            {
                "issue_id": f"AUTO-{issue_number:04d}",
                "severity": "A",
                "chapter_file": "(test-suite)",
                "line": "",
                "category": "test_environment_missing_dependency",
                "subject": ", ".join(missing_modules),
                "evidence": text.strip().splitlines()[-20:],
                "proposed_action": "レビュー実行環境の依存関係を明文化し、matplotlib/requests など不足モジュールを導入できる手順を追加する。",
                "source": "pytest_log",
            }
        )
        issue_number += 1

    if error_tests:
        rows.append(
            {
                "issue_id": f"AUTO-{issue_number:04d}",
                "severity": "A",
                "chapter_file": "(test-suite)",
                "line": "",
                "category": "test_collection_failure",
                "subject": ", ".join(error_tests),
                "evidence": text.strip().splitlines()[-20:],
                "proposed_action": "依存関係を整えた上で `pytest -q` が最後まで収集・実行できる状態に戻す。",
                "source": "pytest_log",
            }
        )

    for row in rows:
        if isinstance(row["evidence"], list):
            row["evidence"] = " | ".join(row["evidence"])

    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def merge_chapter_manual_fields(
    chapter_rows: list[dict[str, Any]],
    existing_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    existing_by_file = {
        row["chapter_file"]: row
        for row in existing_rows
        if row.get("chapter_file")
    }

    for row in chapter_rows:
        existing = existing_by_file.get(row["chapter_file"])
        if existing is None:
            continue
        for field in MANUAL_CHAPTER_FIELDS:
            row[field] = existing.get(field, "")

    return chapter_rows


def merge_manual_issue_rows(
    issue_rows: list[dict[str, Any]],
    existing_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    manual_rows = [
        row for row in existing_rows if row.get("source", "") not in AUTO_ISSUE_SOURCES
    ]
    return issue_rows + manual_rows


def build_summary(
    chapter_rows: list[dict[str, Any]],
    issue_rows: list[dict[str, Any]],
    reference_rows: list[dict[str, Any]],
) -> str:
    total_issues = len(issue_rows)
    severity_counts = Counter(row["severity"] for row in issue_rows)
    category_counts = Counter(row["category"] for row in issue_rows)
    top_issues = sorted(
        issue_rows,
        key=lambda row: (row["severity"], row["chapter_file"], str(row["line"])),
    )[:20]

    lines = [
        "# 原稿レビュー初回監査レポート",
        "",
        "## 概要",
        "",
        f"- 対象ファイル数: {len(chapter_rows)}",
        f"- 参照レジストリ件数: {len(reference_rows)}",
        f"- 現在の指摘件数: {total_issues}",
        f"- 重大度内訳: S={severity_counts.get('S', 0)}, A={severity_counts.get('A', 0)}, B={severity_counts.get('B', 0)}, C={severity_counts.get('C', 0)}",
        "",
        "## 指摘カテゴリ内訳",
        "",
        "| カテゴリ | 件数 |",
        "|---|---:|",
    ]
    for category, count in sorted(category_counts.items()):
        lines.append(f"| {category} | {count} |")

    lines.extend(
        [
            "",
            "## 章別サマリ",
            "",
            "| 章 | 外部参照 | ローカルリンク | 壊れたリンク | 壊れたアンカー | 破損URL | パス参照問題 |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in chapter_rows:
        lines.append(
            "| {chapter_file} | {external_refs} | {local_links} | {broken_local_links} | {broken_anchor_links} | {malformed_external_refs} | {missing_repo_path_refs} |".format(
                **row
            )
        )

    lines.extend(["", "## 優先対応候補（先頭20件）", ""])
    for row in top_issues:
        location = f"{row['chapter_file']}:{row['line']}" if row["line"] else row["chapter_file"]
        lines.append(f"- `{row['issue_id']}` [{row['severity']}] {location} `{row['category']}`: {row['subject']}")

    lines.extend(
        [
            "",
            "## 次のアクション",
            "",
            "- `master_issue_log.csv` の A 指摘から順に修正する。",
            "- `reference_registry.csv` を使い、外部URLと固有名詞の一次情報確認を進める。",
            "- 生命科学・情報科学・計算機科学・バイオインフォ・実装実務の各観点で `chapter_review_sheet.csv` を埋める。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pytest-log",
        type=Path,
        default=None,
        help="Optional pytest output log to merge into the issue log.",
    )
    args = parser.parse_args()

    existing_issue_rows = read_csv_rows(REVIEW_DIR / "master_issue_log.csv")
    existing_chapter_rows = read_csv_rows(REVIEW_DIR / "chapter_review_sheet.csv")

    markdown_files = iter_markdown_files()
    reference_files = iter_reference_files()
    anchors_by_path, section_rows = build_anchor_map(markdown_files)
    reference_rows, issue_rows, chapter_rows = scan_manuscript(markdown_files, anchors_by_path)
    reference_rows.extend(scan_reference_files(reference_files))
    issue_rows.extend(parse_pytest_log(args.pytest_log, len(issue_rows)))
    issue_rows = merge_manual_issue_rows(issue_rows, existing_issue_rows)
    chapter_rows = merge_chapter_manual_fields(chapter_rows, existing_chapter_rows)

    write_csv(
        REVIEW_DIR / "section_inventory.csv",
        section_rows,
        ["chapter_file", "line", "heading_level", "heading_text", "anchor_slug"],
    )
    write_csv(
        REVIEW_DIR / "reference_registry.csv",
        reference_rows,
        [
            "chapter_file",
            "line",
            "source_kind",
            "label",
            "target_type",
            "raw_target",
            "normalized_target",
            "domain",
            "exists",
            "anchor_target",
            "anchor_status",
            "syntax_status",
            "context",
        ],
    )
    write_csv(
        REVIEW_DIR / "master_issue_log.csv",
        issue_rows,
        [
            "issue_id",
            "severity",
            "chapter_file",
            "line",
            "category",
            "subject",
            "evidence",
            "proposed_action",
            "source",
        ],
    )
    write_csv(
        REVIEW_DIR / "chapter_review_sheet.csv",
        chapter_rows,
        [
            "chapter_file",
            "chapter_title",
            "headings",
            "code_fences",
            "external_refs",
            "local_links",
            "broken_local_links",
            "broken_anchor_links",
            "malformed_external_refs",
            "placeholder_external_refs",
            "missing_repo_path_refs",
            "manual_status",
            "reviewer_life_science",
            "reviewer_info_science",
            "reviewer_cs",
            "reviewer_bioinformatics",
            "reviewer_programming",
            "notes",
        ],
    )
    (REVIEW_DIR / "initial_review_report.md").write_text(
        build_summary(chapter_rows, issue_rows, reference_rows),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
