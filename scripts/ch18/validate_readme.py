"""README.mdの構造をチェックするバリデータ."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """バリデーション結果を格納する.

    Attributes
    ----------
    passed : list[str]
        合格したチェック項目
    warnings : list[str]
        警告事項
    info : list[str]
        推奨事項（警告より軽い情報提供）
    """

    passed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """警告がなければTrue."""
        return len(self.warnings) == 0


# 汎用READMEの必須セクション
REQUIRED_SECTIONS = [
    "概要",
    "インストール",
    "使い方",
    "ライセンス",
]

# 研究リポジトリREADMEの追加必須セクション
RESEARCH_SECTIONS = [
    "目的",
    "依存関係",
    "実行手順",
    "データ",
    "引用",
]


def _extract_headings(text: str) -> list[str]:
    """Markdownテキストから見出しテキストを抽出する.

    Parameters
    ----------
    text : str
        Markdownテキスト

    Returns
    -------
    list[str]
        見出しテキストのリスト（#を除去し、小文字化）
    """
    headings: list[str] = []
    for match in re.finditer(r"^#{1,6}\s+(.+)$", text, re.MULTILINE):
        headings.append(match.group(1).strip().lower())
    return headings


def check_required_sections(text: str) -> tuple[bool, list[str]]:
    """汎用READMEの必須セクションが存在するか検証する.

    Parameters
    ----------
    text : str
        READMEのテキスト内容

    Returns
    -------
    tuple[bool, list[str]]
        (全セクション存在するか, 欠損セクション名リスト)
    """
    headings = _extract_headings(text)
    heading_text = " ".join(headings)
    missing: list[str] = []

    for section in REQUIRED_SECTIONS:
        # 見出しテキストにセクション名が含まれているかチェック
        if not any(section.lower() in h for h in headings):
            missing.append(section)

    return len(missing) == 0, missing


def check_empty_sections(text: str) -> tuple[bool, list[str]]:
    """空の見出しセクションを検出する.

    見出しの直後に次の見出しが来る（内容が空の）セクションを検出する。

    Parameters
    ----------
    text : str
        Markdownテキスト

    Returns
    -------
    tuple[bool, list[str]]
        (空セクションがないか, 空セクションの見出し名リスト)
    """
    lines = text.strip().splitlines()
    empty_sections: list[str] = []

    for i, line in enumerate(lines):
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if not heading_match:
            continue

        heading_level = len(heading_match.group(1))
        heading_text = heading_match.group(2).strip()

        # 見出しの次の非空行を探す
        has_content = False
        for j in range(i + 1, len(lines)):
            stripped = lines[j].strip()
            if not stripped:
                continue
            next_heading = re.match(r"^(#{1,6})\s+", stripped)
            if next_heading:
                next_level = len(next_heading.group(1))
                # 子見出し（レベルが深い）ならコンテンツとみなす
                if next_level > heading_level:
                    has_content = True
                # 同レベルまたは親レベルの見出しなら空セクション
                break
            has_content = True
            break

        if not has_content:
            # ファイル末尾の見出しも空セクション
            empty_sections.append(heading_text)

    return len(empty_sections) == 0, empty_sections


def check_research_readme(text: str) -> tuple[bool, list[str]]:
    """研究リポジトリ向けREADMEの追加必須セクションを検証する.

    Parameters
    ----------
    text : str
        READMEのテキスト内容

    Returns
    -------
    tuple[bool, list[str]]
        (全セクション存在するか, 欠損セクション名リスト)
    """
    headings = _extract_headings(text)
    missing: list[str] = []

    for section in RESEARCH_SECTIONS:
        if not any(section.lower() in h for h in headings):
            missing.append(section)

    return len(missing) == 0, missing


def validate(text: str, *, research: bool = False) -> ValidationResult:
    """READMEテキストに対して構造を一括検証する.

    Parameters
    ----------
    text : str
        READMEのテキスト内容
    research : bool
        研究リポジトリ向けの追加チェックを行うか

    Returns
    -------
    ValidationResult
        検証結果
    """
    result = ValidationResult()

    # 1. 必須セクションチェック
    req_ok, req_missing = check_required_sections(text)
    if req_ok:
        result.passed.append("汎用READMEの必須セクションがすべて存在する")
    else:
        result.warnings.append(
            f"必須セクションが不足: {', '.join(req_missing)}"
        )

    # 2. 空セクションチェック
    empty_ok, empty_sections = check_empty_sections(text)
    if empty_ok:
        result.passed.append("すべてのセクションに内容がある")
    else:
        result.warnings.append(
            f"内容が空のセクション: {', '.join(empty_sections)}"
        )

    # 3. 研究リポジトリ向けチェック（オプション）
    if research:
        res_ok, res_missing = check_research_readme(text)
        if res_ok:
            result.passed.append("研究リポジトリ向けの必須セクションがすべて存在する")
        else:
            result.warnings.append(
                f"研究リポジトリ向けセクションが不足: {', '.join(res_missing)}"
            )

    # 4. 情報提供: h1見出し（プロジェクト名）の有無
    if re.search(r"^# .+", text, re.MULTILINE):
        result.info.append("プロジェクト名（h1見出し）が記載されている")

    return result
