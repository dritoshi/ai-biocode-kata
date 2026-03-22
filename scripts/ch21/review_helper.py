"""git diff（unified diff形式）をパースし、基本的なレビュー観点をチェックするモジュール.

コードレビューの観点から、型ヒントの欠落やdocstringの不足を
自動検出してMarkdownチェックリストを生成する。
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class DiffFile:
    """パースされたdiffの1ファイル分の情報.

    Attributes
    ----------
    path : str
        変更されたファイルのパス。
    added_lines : list[str]
        追加された行のリスト（``+`` プレフィックスを除去済み）。
    """

    path: str
    added_lines: list[str] = field(default_factory=list)


def parse_diff(diff_text: str) -> list[DiffFile]:
    """unified diff形式のテキストをパースして変更ファイル・追加行を抽出する.

    Parameters
    ----------
    diff_text : str
        ``git diff`` の出力テキスト（unified diff形式）。

    Returns
    -------
    list[DiffFile]
        ファイルごとの変更情報リスト。
    """
    files: list[DiffFile] = []
    current_file: DiffFile | None = None

    for line in diff_text.splitlines():
        # 新しいファイルの開始を検出（+++ b/path/to/file）
        if line.startswith("+++ b/"):
            path = line[6:]  # "+++ b/" の後がファイルパス
            current_file = DiffFile(path=path)
            files.append(current_file)
            logger.debug("ファイル検出: %s", path)
        elif line.startswith("+++ /dev/null"):
            # 削除されたファイルは対象外
            current_file = None
        elif (
            current_file is not None
            and line.startswith("+")
            and not line.startswith("+++")
        ):
            # 追加行を収集（"+" プレフィックスを除去）
            current_file.added_lines.append(line[1:])

    return files


def check_type_hints(added_lines: list[str]) -> list[str]:
    """追加された関数定義に型ヒントがあるか検査する.

    ``def`` で始まる行（先頭の空白は許容）に戻り値の型ヒント（``->``）が
    あるかを検査する。ない場合は指摘メッセージを返す。

    Parameters
    ----------
    added_lines : list[str]
        追加された行のリスト。

    Returns
    -------
    list[str]
        指摘メッセージのリスト。問題がなければ空リスト。
    """
    issues: list[str] = []
    # "def " を含む行を検出（インデントあり・なし両方）
    func_pattern = re.compile(r"^\s*def\s+(\w+)\s*\(")

    for line in added_lines:
        match = func_pattern.match(line)
        if match:
            func_name = match.group(1)
            if "->" not in line:
                issues.append(
                    f"関数 `{func_name}` に戻り値の型ヒントがありません"
                )
                logger.info("型ヒント欠落: %s", func_name)

    return issues


def check_docstrings(diff_text: str) -> list[str]:
    """追加された関数の次行にdocstringがあるか検査する.

    簡易チェックとして、``def`` 行の直後に ``\"\"\"`` が存在するかを確認する。

    Parameters
    ----------
    diff_text : str
        unified diff形式のテキスト。

    Returns
    -------
    list[str]
        指摘メッセージのリスト。
    """
    issues: list[str] = []
    lines = diff_text.splitlines()
    func_pattern = re.compile(r"^\+\s*def\s+(\w+)\s*\(")

    for i, line in enumerate(lines):
        match = func_pattern.match(line)
        if match:
            func_name = match.group(1)
            # 次の追加行を探す（空行やコメントを飛ばさず直後をチェック）
            next_idx = i + 1
            has_docstring = False
            while next_idx < len(lines):
                next_line = lines[next_idx]
                if next_line.startswith("+"):
                    # 追加行の内容を取得
                    content = next_line[1:].strip()
                    if '"""' in content or "'''" in content:
                        has_docstring = True
                    break
                elif next_line.startswith("-") or next_line.startswith("@@"):
                    break
                else:
                    # コンテキスト行（変更なしの行）
                    next_idx += 1
                    continue
                break  # pragma: no cover
            if not has_docstring:
                issues.append(
                    f"関数 `{func_name}` にdocstringがありません"
                )

    return issues


def generate_review_checklist(diff_text: str) -> str:
    """チェック結果をMarkdownチェックリストで出力する.

    Parameters
    ----------
    diff_text : str
        unified diff形式のテキスト。

    Returns
    -------
    str
        Markdown形式のチェックリスト。
    """
    diff_files = parse_diff(diff_text)
    all_added_lines: list[str] = []
    for df in diff_files:
        all_added_lines.extend(df.added_lines)

    # 各チェックを実行
    type_hint_issues = check_type_hints(all_added_lines)
    docstring_issues = check_docstrings(diff_text)

    # 変更ファイル一覧
    file_list = "\n".join(f"- `{df.path}`" for df in diff_files)

    # チェックリスト生成
    checklist_items: list[str] = []

    if type_hint_issues:
        for issue in type_hint_issues:
            checklist_items.append(f"- [ ] {issue}")
    else:
        checklist_items.append("- [x] すべての関数に型ヒントが付与されています")

    if docstring_issues:
        for issue in docstring_issues:
            checklist_items.append(f"- [ ] {issue}")
    else:
        checklist_items.append("- [x] すべての関数にdocstringがあります")

    checklist_text = "\n".join(checklist_items)

    report = f"""\
## コードレビューチェックリスト

### 変更ファイル

{file_list}

### チェック結果

{checklist_text}
"""
    return report
