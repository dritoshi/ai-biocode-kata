#!/usr/bin/env python3
"""本文コード対応表とMarkdownレポートを再生成する."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.review.code_correspondence import (  # noqa: E402
    build_inventory,
    collect_test_results,
    load_overrides,
    normalized_for_determinism,
    render_report,
)

DEFAULT_OVERRIDES = (
    PROJECT_ROOT / "scripts/review/code_correspondence_overrides.json"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "docs/review/code_correspondence.json"
DEFAULT_REPORT = PROJECT_ROOT / "docs/review/code_correspondence.md"


def _load_test_results(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    results = data.get("test_files", data)
    if not isinstance(results, dict):
        raise ValueError("テスト結果はobjectでなければならない")
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--reuse-test-results",
        type=Path,
        help="既存の対応表または個別pytest結果JSONを再利用する",
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="E3関係のGit更新履歴を生成しない",
    )
    parser.add_argument(
        "--check-determinism",
        action="store_true",
        help="非決定項目を除く2回生成の一致も確認する",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    overrides = load_overrides(args.overrides)
    if args.reuse_test_results:
        test_results = _load_test_results(args.reuse_test_results)
    else:
        test_results = collect_test_results(root)
    data = build_inventory(
        root,
        overrides,
        test_results,
        include_history=not args.no_history,
    )
    if args.check_determinism:
        second = build_inventory(
            root,
            overrides,
            test_results,
            include_history=not args.no_history,
        )
        if normalized_for_determinism(data) != normalized_for_determinism(second):
            raise SystemExit("非決定項目を除いた2回生成の結果が一致しない")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.report.write_text(render_report(data), encoding="utf-8")
    summary = data["summary"]
    print(
        "対応表を生成: "
        f"本文{summary['book_blocks']}、"
        f"scripts {summary['script_files']}、"
        f"E5 {summary['correspondence_all'].get('E5', 0)}"
    )
    print(args.output)
    print(args.report)


if __name__ == "__main__":
    main()
