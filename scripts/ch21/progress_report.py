"""git logの出力をパースし、週次進捗レポートのMarkdownを生成するモジュール.

``git log --format="%H|%s|%ai"`` 形式の出力テキストを受け取り、
Conventional Commits の型で分類した進捗レポートを生成する。
subprocessは使用せず、テキスト入力のみで動作する。
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Conventional Commits のカテゴリ定義
_CATEGORY_LABELS: dict[str, str] = {
    "feat": "機能追加",
    "fix": "バグ修正",
    "docs": "ドキュメント",
    "refactor": "リファクタリング",
    "test": "テスト",
    "chore": "雑務",
    "other": "その他",
}

# Conventional Commits のプレフィックスパターン
_COMMIT_TYPE_PATTERN = re.compile(
    r"^(feat|fix|docs|refactor|test|chore)(?:\(.+?\))?:\s*"
)


@dataclass
class Commit:
    """パースされたコミット情報.

    Attributes
    ----------
    hash : str
        コミットハッシュ（フル）。
    subject : str
        コミットメッセージの件名。
    date : str
        コミット日時の文字列。
    """

    hash: str
    subject: str
    date: str


def parse_git_log(log_text: str) -> list[Commit]:
    """``git log --format="%H|%s|%ai"`` 形式の出力をパースする.

    Parameters
    ----------
    log_text : str
        git log の出力テキスト。各行は ``ハッシュ|件名|日時`` の形式。

    Returns
    -------
    list[Commit]
        パースされたコミットのリスト。
    """
    commits: list[Commit] = []

    for line in log_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        parts = line.split("|", maxsplit=2)
        if len(parts) != 3:
            logger.warning("不正な形式の行をスキップ: %s", line)
            continue

        commit_hash, subject, date = parts
        commits.append(
            Commit(hash=commit_hash.strip(), subject=subject.strip(), date=date.strip())
        )

    return commits


def categorize_commits(commits: list[Commit]) -> dict[str, list[Commit]]:
    """Conventional Commitsの型でコミットを分類する.

    Parameters
    ----------
    commits : list[Commit]
        コミットのリスト。

    Returns
    -------
    dict[str, list[Commit]]
        カテゴリ名をキー、該当コミットのリストを値とする辞書。
        カテゴリは ``feat``, ``fix``, ``docs``, ``refactor``,
        ``test``, ``chore``, ``other`` のいずれか。
    """
    categorized: dict[str, list[Commit]] = defaultdict(list)

    for commit in commits:
        match = _COMMIT_TYPE_PATTERN.match(commit.subject)
        if match:
            category = match.group(1)
        else:
            category = "other"
        categorized[category].append(commit)
        logger.debug("分類: %s -> %s", commit.subject[:50], category)

    return dict(categorized)


def generate_report(commits: list[Commit], period: str) -> str:
    """進捗報告のMarkdownを生成する.

    Parameters
    ----------
    commits : list[Commit]
        レポート対象のコミットリスト。
    period : str
        レポート期間の表示文字列（例: ``"2024-01-01 〜 2024-01-07"``）。

    Returns
    -------
    str
        Markdown形式の進捗レポート。
    """
    categorized = categorize_commits(commits)

    # カテゴリ別の変更一覧を生成
    sections: list[str] = []
    for category_key in _CATEGORY_LABELS:
        if category_key not in categorized:
            continue
        label = _CATEGORY_LABELS[category_key]
        items = categorized[category_key]
        lines = "\n".join(
            f"- {c.subject} (`{c.hash[:7]}`)" for c in items
        )
        sections.append(f"### {label}\n\n{lines}")

    sections_text = "\n\n".join(sections)

    # 統計情報
    total = len(commits)
    category_counts = ", ".join(
        f"{_CATEGORY_LABELS[k]}: {len(v)}件"
        for k, v in categorized.items()
        if k in _CATEGORY_LABELS
    )

    report = f"""\
# 進捗レポート

**期間**: {period}

**コミット数**: {total}件

## カテゴリ別変更一覧

{sections_text}

## 統計

{category_counts}
"""
    return report
