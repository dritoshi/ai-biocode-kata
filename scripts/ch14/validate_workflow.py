"""Snakefileのベストプラクティス準拠をチェックするバリデータ."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ValidationResult:
    """バリデーション結果を格納する.

    Attributes
    ----------
    passed : list[str]
        合格したチェック項目
    warnings : list[str]
        警告事項
    """

    passed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """警告がなければTrue."""
        return len(self.warnings) == 0


def _extract_rules(text: str) -> list[str]:
    """Snakefileテキストからルール名を抽出する."""
    return re.findall(r"^rule\s+(\w+)\s*:", text, re.MULTILINE)


def _has_directive_in_rule(text: str, rule_name: str, directive: str) -> bool:
    """指定ルールに特定ディレクティブが存在するか判定する."""
    # ルールのブロックを抽出（次のruleまたはファイル末尾まで）
    pattern = rf"^rule\s+{re.escape(rule_name)}\s*:(.*?)(?=^rule\s|\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if match is None:
        return False
    block = match.group(1)
    return re.search(rf"^\s+{re.escape(directive)}\s*:", block, re.MULTILINE) is not None


def check_log_directives(text: str) -> tuple[bool, list[str]]:
    """各ルールにlog:ディレクティブがあるか検証する.

    Parameters
    ----------
    text : str
        Snakefileのテキスト内容

    Returns
    -------
    tuple[bool, list[str]]
        (全ルール合格か, log:のないルール名リスト)
    """
    rules = _extract_rules(text)
    missing: list[str] = []
    for rule_name in rules:
        if rule_name == "all":
            continue
        if not _has_directive_in_rule(text, rule_name, "log"):
            missing.append(rule_name)
    return len(missing) == 0, missing


def check_configfile(text: str) -> bool:
    """configfile:ディレクティブの使用を検証する.

    Parameters
    ----------
    text : str
        Snakefileのテキスト内容

    Returns
    -------
    bool
        configfile:が存在すればTrue
    """
    return re.search(r"^configfile\s*:", text, re.MULTILINE) is not None


def check_temp_usage(text: str) -> tuple[bool, list[str]]:
    """中間ファイルにtemp()が使われているか検証する.

    Parameters
    ----------
    text : str
        Snakefileのテキスト内容

    Returns
    -------
    tuple[bool, list[str]]
        (temp()使用ありか, temp()を含むルール名リスト)
    """
    rules = _extract_rules(text)
    temp_rules: list[str] = []
    for rule_name in rules:
        pattern = rf"^rule\s+{re.escape(rule_name)}\s*:(.*?)(?=^rule\s|\Z)"
        match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
        if match and "temp(" in match.group(1):
            temp_rules.append(rule_name)
    has_temp = len(temp_rules) > 0
    return has_temp, temp_rules


def check_io_separation(text: str) -> tuple[bool, list[str]]:
    """入力パスと出力パスの分離を検証する.

    入力にdata/やraw/を含むパスがあり、出力にresults/やoutput/を含むパスが
    あるかをチェックする。同じディレクトリに入出力が混在するルールを警告する。

    Parameters
    ----------
    text : str
        Snakefileのテキスト内容

    Returns
    -------
    tuple[bool, list[str]]
        (分離されているか, 混在ルール名リスト)
    """
    rules = _extract_rules(text)
    mixed: list[str] = []
    input_dirs = {"data/", "raw/"}
    output_dirs = {"results/", "output/"}

    for rule_name in rules:
        if rule_name == "all":
            continue
        pattern = rf"^rule\s+{re.escape(rule_name)}\s*:(.*?)(?=^rule\s|\Z)"
        match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
        if match is None:
            continue
        block = match.group(1)

        # input:とoutput:のブロックを抽出
        input_match = re.search(
            r"^\s+input\s*:(.*?)(?=^\s+(?:output|shell|script|log|conda|container|params|resources|threads)\s*:|\Z)",
            block,
            re.MULTILINE | re.DOTALL,
        )
        output_match = re.search(
            r"^\s+output\s*:(.*?)(?=^\s+(?:input|shell|script|log|conda|container|params|resources|threads)\s*:|\Z)",
            block,
            re.MULTILINE | re.DOTALL,
        )

        if input_match and output_match:
            input_text = input_match.group(1)
            output_text = output_match.group(1)
            # 出力に入力用ディレクトリが含まれている場合は混在
            for d in input_dirs:
                if d in output_text:
                    mixed.append(rule_name)
                    break
            # 入力に出力用ディレクトリが含まれている場合は混在としない
            # （中間ファイルの受け渡しはよくあるパターン）

    return len(mixed) == 0, mixed


def validate(text: str) -> ValidationResult:
    """Snakefileテキストに対してベストプラクティスを一括検証する.

    Parameters
    ----------
    text : str
        Snakefileのテキスト内容

    Returns
    -------
    ValidationResult
        検証結果
    """
    result = ValidationResult()

    # 1. configfile:チェック
    if check_configfile(text):
        result.passed.append("configfile:ディレクティブが使用されている")
    else:
        result.warnings.append("configfile:ディレクティブが見つからない — パラメータをハードコーディングしていないか確認")

    # 2. log:チェック
    log_ok, missing_log = check_log_directives(text)
    if log_ok:
        result.passed.append("すべてのルールにlog:ディレクティブがある")
    else:
        result.warnings.append(
            f"log:ディレクティブのないルール: {', '.join(missing_log)}"
        )

    # 3. temp()チェック
    has_temp, temp_rules = check_temp_usage(text)
    if has_temp:
        result.passed.append(f"temp()を使用しているルール: {', '.join(temp_rules)}")
    else:
        result.warnings.append("temp()が使われていない — 中間ファイルのディスク使用量に注意")

    # 4. 入出力分離チェック
    io_ok, mixed_rules = check_io_separation(text)
    if io_ok:
        result.passed.append("入力パスと出力パスが分離されている")
    else:
        result.warnings.append(
            f"入力/出力パスが混在しているルール: {', '.join(mixed_rules)}"
        )

    return result


def validate_file(path: Path) -> ValidationResult:
    """Snakefileを読み込んで検証する.

    Parameters
    ----------
    path : Path
        Snakefileのパス

    Returns
    -------
    ValidationResult
        検証結果
    """
    text = path.read_text(encoding="utf-8")
    return validate(text)
