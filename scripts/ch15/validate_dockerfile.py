"""Dockerfileのベストプラクティス準拠をチェックするバリデータ."""

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


def _parse_from_instructions(text: str) -> list[dict[str, str]]:
    """DockerfileテキストからFROM命令を抽出する.

    Parameters
    ----------
    text : str
        Dockerfileのテキスト内容

    Returns
    -------
    list[dict[str, str]]
        各FROM命令の情報（image, tag, digest, as_name）
    """
    results: list[dict[str, str]] = []
    for match in re.finditer(
        r"^FROM\s+(\S+?)(?::(\S+?))?(?:@(sha256:\w+))?\s*(?:AS\s+(\S+))?$",
        text,
        re.MULTILINE | re.IGNORECASE,
    ):
        results.append(
            {
                "image": match.group(1),
                "tag": match.group(2) or "",
                "digest": match.group(3) or "",
                "as_name": match.group(4) or "",
            }
        )
    return results


def check_base_image_tag(text: str) -> tuple[bool, list[str], bool]:
    """ベースイメージのタグ固定を検証する.

    Parameters
    ----------
    text : str
        Dockerfileのテキスト内容

    Returns
    -------
    tuple[bool, list[str], bool]
        (全イメージがタグ固定か, 問題のあるイメージ名リスト, ダイジェスト指定があるか)
    """
    from_instructions = _parse_from_instructions(text)
    problematic: list[str] = []
    has_digest = False

    for instr in from_instructions:
        image = instr["image"]
        tag = instr["tag"]
        digest = instr["digest"]

        if digest:
            has_digest = True
            continue

        # latestタグまたはタグなしは警告
        if not tag or tag == "latest":
            problematic.append(image if not tag else f"{image}:latest")

    return len(problematic) == 0, problematic, has_digest


def check_layer_cache_order(text: str) -> tuple[bool, list[str]]:
    """レイヤーキャッシュの順序を検証する.

    依存インストール（pip install, conda install等）より前に
    COPY . . が来ていないかチェックする。

    Parameters
    ----------
    text : str
        Dockerfileのテキスト内容

    Returns
    -------
    tuple[bool, list[str]]
        (順序が適切か, 問題の説明リスト)
    """
    lines = text.strip().splitlines()
    issues: list[str] = []

    # 各ステージごとに解析する
    copy_all_line: int | None = None
    install_after_copy_all: list[int] = []

    install_patterns = re.compile(
        r"(pip\s+install|conda\s+install|mamba\s+install|apt-get\s+install)"
    )

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # FROMでステージリセット
        if re.match(r"^FROM\s+", stripped, re.IGNORECASE):
            copy_all_line = None
            install_after_copy_all = []
            continue

        # COPY . . / COPY ./ ./ / COPY . /workspace 等、カレントディレクトリ全体のコピー
        if re.match(r"^COPY\s+\./?(\s+\S+)$", stripped):
            copy_all_line = i

        # インストール命令
        if copy_all_line is not None and install_after_copy_all is not None:
            if install_patterns.search(stripped):
                install_after_copy_all.append(i)

    if copy_all_line is not None and install_after_copy_all:
        issues.append(
            f"COPY . .（{copy_all_line}行目）が依存インストール"
            f"（{install_after_copy_all[0]}行目）より前にある — "
            "依存定義ファイルだけを先にCOPYしてキャッシュを活用する"
        )

    return len(issues) == 0, issues


def check_run_consolidation(text: str) -> tuple[bool, list[str]]:
    """RUN命令の統合を検証する.

    apt-get updateとapt-get installが別のRUN命令に分離されていないかチェックする。

    Parameters
    ----------
    text : str
        Dockerfileのテキスト内容

    Returns
    -------
    tuple[bool, list[str]]
        (統合されているか, 問題の説明リスト)
    """
    lines = text.strip().splitlines()
    issues: list[str] = []

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # apt-get updateが単独のRUN命令にある場合
        if re.match(r"^RUN\s+apt-get\s+update\s*$", stripped):
            issues.append(
                f"RUN apt-get update（{i}行目）が単独のRUN命令になっている — "
                "apt-get installと && で統合する"
            )

    return len(issues) == 0, issues


def check_apt_cache_cleanup(text: str) -> tuple[bool, list[str]]:
    """apt-getキャッシュ削除の有無を検証する.

    apt-get installを使用している場合、同じRUN命令内で
    rm -rf /var/lib/apt/lists/* が実行されているかチェックする。

    Parameters
    ----------
    text : str
        Dockerfileのテキスト内容

    Returns
    -------
    tuple[bool, list[str]]
        (キャッシュ削除があるか, 問題の説明リスト)
    """
    issues: list[str] = []
    has_apt_install = False

    # RUN命令を抽出（行継続を考慮）
    # Dockerfileの行継続は \ で行われる
    merged_lines: list[tuple[int, str]] = []
    current_line = ""
    start_line = 0
    for i, line in enumerate(text.strip().splitlines(), 1):
        stripped = line.rstrip()
        if not current_line:
            start_line = i
        if stripped.endswith("\\"):
            current_line += stripped[:-1] + " "
        else:
            current_line += stripped
            merged_lines.append((start_line, current_line))
            current_line = ""

    if current_line:
        merged_lines.append((start_line, current_line))

    for line_no, merged in merged_lines:
        if not re.match(r"^RUN\s+", merged, re.IGNORECASE):
            continue
        if "apt-get install" not in merged:
            continue
        has_apt_install = True
        if "rm -rf /var/lib/apt/lists" not in merged:
            issues.append(
                f"RUN apt-get install（{line_no}行目）で"
                "キャッシュ削除（rm -rf /var/lib/apt/lists/*）がない — "
                "イメージサイズが不必要に大きくなる"
            )

    if not has_apt_install:
        # apt-getを使っていなければチェック対象外
        return True, []

    return len(issues) == 0, issues


def validate(text: str) -> ValidationResult:
    """Dockerfileテキストに対してベストプラクティスを一括検証する.

    Parameters
    ----------
    text : str
        Dockerfileのテキスト内容

    Returns
    -------
    ValidationResult
        検証結果
    """
    result = ValidationResult()

    # 1. ベースイメージのタグ固定チェック
    tag_ok, problematic, has_digest = check_base_image_tag(text)
    if tag_ok:
        result.passed.append("すべてのベースイメージにタグが固定されている")
    else:
        result.warnings.append(
            f"タグが未固定のベースイメージ: {', '.join(problematic)} — "
            "バージョンタグを明示する（例: python:3.11-slim）"
        )
    if has_digest:
        result.info.append(
            "ダイジェスト指定（@sha256:...）のイメージあり — 再現性が最も高い"
        )

    # 2. レイヤーキャッシュ順序チェック
    cache_ok, cache_issues = check_layer_cache_order(text)
    if cache_ok:
        result.passed.append("レイヤーキャッシュの順序が適切である")
    else:
        for issue in cache_issues:
            result.warnings.append(issue)

    # 3. RUN命令の統合チェック
    run_ok, run_issues = check_run_consolidation(text)
    if run_ok:
        result.passed.append("RUN命令が適切に統合されている")
    else:
        for issue in run_issues:
            result.warnings.append(issue)

    # 4. apt-getキャッシュ削除チェック
    apt_ok, apt_issues = check_apt_cache_cleanup(text)
    if apt_ok:
        result.passed.append("apt-getキャッシュが適切に削除されている")
    else:
        for issue in apt_issues:
            result.warnings.append(issue)

    return result
