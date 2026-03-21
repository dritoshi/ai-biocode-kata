"""Mermaid記法の検証とパイプライン図生成ヘルパー."""

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


# サポートする図の種類の先頭キーワード
_DIAGRAM_TYPES = {
    "graph",
    "flowchart",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "gantt",
    "pie",
    "gitgraph",
}


def extract_mermaid_blocks(markdown: str) -> list[str]:
    """Markdownテキストからmermaidコードブロックを抽出する.

    Parameters
    ----------
    markdown : str
        Markdownテキスト

    Returns
    -------
    list[str]
        mermaidブロックの中身（フェンスを除く）のリスト
    """
    pattern = r"```mermaid\s*\n(.*?)```"
    return [m.group(1).strip() for m in re.finditer(pattern, markdown, re.DOTALL)]


def validate_mermaid_syntax(block: str) -> ValidationResult:
    """Mermaidブロックの基本的な構文を検証する.

    完全な構文解析ではなく、よくある間違いを検出する簡易チェッカー。

    Parameters
    ----------
    block : str
        Mermaidブロックのテキスト（フェンスなし）

    Returns
    -------
    ValidationResult
        検証結果
    """
    result = ValidationResult()
    lines = block.strip().splitlines()

    if not lines:
        result.warnings.append("Mermaidブロックが空である")
        return result

    # 1. 図の種類の宣言チェック
    first_line = lines[0].strip()
    # "graph TD", "flowchart LR" などの形式
    first_word = first_line.split()[0] if first_line.split() else ""
    if first_word not in _DIAGRAM_TYPES:
        result.warnings.append(
            f"図の種類が不明: '{first_word}' — "
            f"対応: {', '.join(sorted(_DIAGRAM_TYPES))}"
        )
    else:
        result.passed.append(f"図の種類: {first_word}")

    # 2. flowchart/graphの場合、方向指定チェック
    if first_word in {"graph", "flowchart"}:
        parts = first_line.split()
        valid_directions = {"TB", "TD", "BT", "RL", "LR"}
        if len(parts) >= 2 and parts[1] in valid_directions:
            result.passed.append(f"方向指定: {parts[1]}")
        elif len(parts) < 2:
            result.warnings.append(
                "方向が指定されていない — TB, TD, BT, RL, LR のいずれかを指定する"
            )

    # 3. ノード定義の存在チェック（flowchart/graph）
    if first_word in {"graph", "flowchart"}:
        # -->、---、==>  などのエッジ記法を含む行があるか
        has_edges = any(
            re.search(r"-->|---|==>|-.->|--\>", line)
            for line in lines[1:]
        )
        if has_edges:
            result.passed.append("エッジ定義が存在する")
        else:
            result.info.append("エッジ定義が見つからない — ノードのみの図の可能性")

    return result


@dataclass
class PipelineStep:
    """パイプラインの1ステップ.

    Attributes
    ----------
    name : str
        ステップ名（英数字）
    label : str
        表示ラベル
    """

    name: str
    label: str


def generate_pipeline_diagram(steps: list[PipelineStep]) -> str:
    """パイプラインのステップ一覧からMermaidフローチャートを生成する.

    Parameters
    ----------
    steps : list[PipelineStep]
        パイプラインのステップ一覧（順序通り）

    Returns
    -------
    str
        Mermaidフローチャートのテキスト

    Raises
    ------
    ValueError
        ステップが空の場合
    """
    if not steps:
        raise ValueError("ステップが空である")

    lines = ["flowchart TD"]
    # ノード定義
    for step in steps:
        lines.append(f"    {step.name}[{step.label}]")
    # エッジ定義
    for i in range(len(steps) - 1):
        lines.append(f"    {steps[i].name} --> {steps[i + 1].name}")

    return "\n".join(lines)
