"""docstringカバレッジと品質をチェックするツール."""

from __future__ import annotations

import ast
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


@dataclass
class CoverageResult:
    """docstringカバレッジの計測結果.

    Attributes
    ----------
    total : int
        チェック対象の関数・クラス数
    documented : int
        docstringがある関数・クラス数
    missing : list[str]
        docstringがない関数・クラス名
    """

    total: int = 0
    documented: int = 0
    missing: list[str] = field(default_factory=list)

    @property
    def ratio(self) -> float:
        """カバレッジ率（0.0〜1.0）."""
        if self.total == 0:
            return 1.0
        return self.documented / self.total


def check_coverage(source: str) -> CoverageResult:
    """Pythonソースコードのdocstringカバレッジを計測する.

    公開関数・公開クラス（アンダースコアで始まらない名前）のdocstring有無を
    チェックする。ネストされた関数・クラスは対象外。

    Parameters
    ----------
    source : str
        Pythonソースコードの文字列

    Returns
    -------
    CoverageResult
        カバレッジ計測結果
    """
    tree = ast.parse(source)
    result = CoverageResult()

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = node.name
            # プライベート名はスキップ
            if name.startswith("_"):
                continue

            result.total += 1
            docstring = ast.get_docstring(node)
            if docstring:
                result.documented += 1
            else:
                result.missing.append(name)

    return result


# NumPy styleのセクションキーワード
_NUMPY_SECTIONS = {
    "Parameters",
    "Returns",
    "Raises",
    "Yields",
    "Attributes",
    "Notes",
    "References",
    "Examples",
    "See Also",
    "Warnings",
}


def check_numpy_style(docstring: str) -> tuple[bool, list[str]]:
    """docstringがNumPy style形式に準拠しているかチェックする.

    NumPy styleの特徴である「セクション名 + アンダーライン」の形式を
    検出し、基本的な構造を検証する。

    Parameters
    ----------
    docstring : str
        チェック対象のdocstring文字列

    Returns
    -------
    tuple[bool, list[str]]
        (NumPy style準拠か, 検出された問題のリスト)
    """
    issues: list[str] = []
    lines = docstring.splitlines()

    # セクションの検出: "SectionName\n----------" パターン
    found_sections: list[str] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped in _NUMPY_SECTIONS:
            # 次の行がアンダーラインか確認
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if re.match(r"^-{3,}$", next_line):
                    found_sections.append(stripped)
                else:
                    issues.append(
                        f"'{stripped}' セクションの下にアンダーラインがない"
                    )
            else:
                issues.append(
                    f"'{stripped}' セクションの下にアンダーラインがない"
                )

    # セクションが1つもなければNumPy styleではない
    if not found_sections and not issues:
        issues.append("NumPy styleのセクションが見つからない")

    return len(issues) == 0, issues
