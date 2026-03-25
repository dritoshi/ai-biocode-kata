#!/usr/bin/env python3
"""コードサンプルとテスト状況の要約レポートを生成する。"""

from __future__ import annotations

import argparse
import platform
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
TESTS_DIR = REPO_ROOT / "tests"
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "review" / "code_check.md"
DEFAULT_PYTEST_LOG = Path("/tmp/ai-biocode-kata-pytest.log")

SUMMARY_RE = re.compile(
    r"(?P<passed>\d+) passed"
    r"(?:, (?P<failed>\d+) failed)?"
    r"(?:, (?P<errors>\d+) errors?)?"
    r"(?:, (?P<skipped>\d+) skipped)?"
    r"(?:, (?P<warnings>\d+) warnings?)?"
    r" in (?P<seconds>[\d.]+)s"
)
WARNING_CLASS_RE = re.compile(r"([A-Za-z]+Warning):")


@dataclass(frozen=True)
class UntestedScript:
    chapter: str
    relpath: str
    note: str


def detect_command_version(command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
    except Exception:
        return "unknown"

    return completed.stdout.strip() or completed.stderr.strip() or "unknown"


def parse_pytest_summary(text: str) -> dict[str, str]:
    for line in reversed(text.splitlines()):
        match = SUMMARY_RE.search(line)
        if not match:
            continue
        data = {key: match.group(key) or "0" for key in ("passed", "failed", "errors", "skipped", "warnings")}
        data["seconds"] = match.group("seconds")
        return data

    raise ValueError("pytest サマリ行を log から検出できませんでした。")


def parse_warning_summary(text: str) -> list[tuple[str, str, int]]:
    if "warnings summary" not in text:
        return []

    section = text.split("warnings summary", maxsplit=1)[1]
    section = section.split("-- Docs:", maxsplit=1)[0]
    lines = section.splitlines()

    current_test = ""
    warnings: list[tuple[str, str]] = []

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("tests/"):
            current_test = line.strip()
            continue
        match = WARNING_CLASS_RE.search(line)
        if match:
            warnings.append((match.group(1), current_test))

    counter = Counter(warnings)
    summary = [(warning_class, test_name, count) for (warning_class, test_name), count in counter.items()]
    summary.sort(key=lambda item: (-item[2], item[0], item[1]))
    return summary


def iter_book_scripts() -> list[Path]:
    files: set[Path] = set()
    for pattern in ("ch*/*.py", "ch*/*/*.py"):
        for path in SCRIPTS_DIR.glob(pattern):
            if path.name == "__init__.py":
                continue
            files.add(path)
    return sorted(files)


def classify_untested_script(path: Path) -> str:
    rel = path.relative_to(SCRIPTS_DIR)
    rel_text = str(rel)
    stem = path.stem

    if stem.startswith(("plot_", "generate_")):
        return "図表生成スクリプト"
    if "/mylib/" in f"/{rel_text}/":
        return "ライブラリモジュール"
    if stem in {"cli_argparse", "cli_typer", "progress_demo"}:
        return "CLI デモ"
    if stem == "generate_traceback":
        return "デモ用トレースバック生成スクリプト"
    return "要確認"


def collect_untested_scripts() -> list[UntestedScript]:
    rows: list[UntestedScript] = []

    for script in iter_book_scripts():
        rel = script.relative_to(SCRIPTS_DIR)
        chapter = rel.parts[0]
        expected_test = TESTS_DIR / chapter / f"test_{script.stem}.py"
        if expected_test.exists():
            continue
        rows.append(
            UntestedScript(
                chapter=chapter,
                relpath=str(rel),
                note=classify_untested_script(script),
            )
        )

    return rows


def render_report(pytest_log: Path) -> str:
    text = pytest_log.read_text(encoding="utf-8")
    summary = parse_pytest_summary(text)
    warnings = parse_warning_summary(text)
    untested = collect_untested_scripts()
    warning_class_counts = Counter(item[0] for item in warnings)

    python_version = detect_command_version([str(REPO_ROOT / ".venv" / "bin" / "python"), "--version"])
    pytest_version = detect_command_version([str(REPO_ROOT / ".venv" / "bin" / "pytest"), "--version"])

    lines = [
        "# コードサンプル動作確認レポート",
        "",
        f"実行日: {date.today().isoformat()}",
        "",
        "## 1. pytest 実行結果",
        "",
        "### 実行環境",
        "",
        "| 項目 | 値 |",
        "|------|-----|",
        f"| Python | {python_version} |",
        f"| pytest | {pytest_version} |",
        f"| OS | {platform.system()} ({platform.machine()}) |",
        "",
        "### 実行コマンド",
        "",
        "```bash",
        ".venv/bin/pytest -q -ra",
        "```",
        "",
        "### 結果サマリー",
        "",
        "| 区分 | 件数 |",
        "|------|------|",
        f"| passed | {summary['passed']} |",
        f"| failed | {summary['failed']} |",
        f"| errors | {summary['errors']} |",
        f"| skipped | {summary['skipped']} |",
        f"| warnings | {summary['warnings']} |",
        f"| 実行時間 | {summary['seconds']}s |",
    ]

    if warnings:
        lines.extend(["", "### 警告", ""])
        for warning_class, test_name, count in warnings:
            suffix = f" ({count}件)" if count > 1 else ""
            lines.append(f"- `{warning_class}`: `{test_name}`{suffix}")
    else:
        lines.extend(["", "### 警告", "", "- なし"])

    lines.extend(
        [
            "",
            "## 2. 未カバースクリプト",
            "",
            "| 章 | スクリプト | 備考 |",
            "|----|-----------|------|",
        ]
    )
    for row in untested:
        lines.append(f"| {row.chapter} | `{row.relpath}` | {row.note} |")

    lines.extend(
        [
            "",
            f"合計: **{len(untested)} スクリプトが未カバー**",
            "",
            "## 3. 対応メモ",
            "",
        ]
    )

    if "BiopythonDeprecationWarning" in warning_class_counts:
        lines.append(
            "- `tests/ch10/test_error_handling.py` の `BiopythonDeprecationWarning` は将来 `ValueError` へ変わる可能性があるため、入力フィクスチャかパーサ指定の見直し候補である。"
        )
    if any(row.relpath in {"ch05/mylib/core.py", "ch05/mylib/utils.py", "ch11/cli_argparse.py"} for row in untested):
        lines.append(
            "- 未カバースクリプトのうち `ch05/mylib/core.py` `ch05/mylib/utils.py` `ch11/cli_argparse.py` は、図表生成や単発デモより優先度が高い品質改善候補である。"
        )
    if len(lines) > 0 and lines[-1] == "":
        lines.pop()

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pytest-log",
        type=Path,
        default=DEFAULT_PYTEST_LOG,
        help="pytest の出力ログ。既定は /tmp/ai-biocode-kata-pytest.log",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Markdown 出力先。既定は docs/review/code_check.md",
    )
    args = parser.parse_args()

    if not args.pytest_log.exists():
        raise SystemExit(f"pytest log が見つかりません: {args.pytest_log}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_report(args.pytest_log), encoding="utf-8")
    print(f"結果を {args.output.relative_to(REPO_ROOT)} に保存しました。")


if __name__ == "__main__":
    main()
