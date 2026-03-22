"""mermaid_helperモジュールのテスト."""

import pytest

from scripts.ch18.mermaid_helper import (
    PipelineStep,
    ValidationResult,
    extract_mermaid_blocks,
    generate_pipeline_diagram,
    validate_mermaid_syntax,
)

# --- テスト用Markdownテキスト ---

MARKDOWN_WITH_MERMAID = """\
# 解析パイプライン

以下にフローを示す。

```mermaid
flowchart TD
    A[FASTQ] --> B[FastQC]
    B --> C[STAR]
    C --> D[featureCounts]
```

## 別のセクション

```mermaid
sequenceDiagram
    User->>Agent: コード生成依頼
    Agent->>User: コード提案
```

通常のコードブロック:

```python
print("hello")
```
"""

MARKDOWN_NO_MERMAID = """\
# README

```python
print("hello")
```

```bash
echo "test"
```
"""

GOOD_FLOWCHART = """\
flowchart TD
    A[入力] --> B[処理]
    B --> C[出力]
"""

GOOD_GRAPH = """\
graph LR
    A[Start] --> B[End]
"""

BAD_NO_TYPE = """\
    A[入力] --> B[処理]
"""

BAD_EMPTY = ""

BAD_UNKNOWN_TYPE = """\
unknown TD
    A --> B
"""

NO_DIRECTION = """\
flowchart
    A[入力] --> B[出力]
"""

NODES_ONLY = """\
flowchart TD
    A[入力]
    B[出力]
"""


# --- extract_mermaid_blocks ---

class TestExtractMermaidBlocks:
    """Mermaidブロック抽出テスト."""

    def test_extract_two_blocks(self) -> None:
        blocks = extract_mermaid_blocks(MARKDOWN_WITH_MERMAID)
        assert len(blocks) == 2

    def test_first_block_is_flowchart(self) -> None:
        blocks = extract_mermaid_blocks(MARKDOWN_WITH_MERMAID)
        assert blocks[0].startswith("flowchart")

    def test_second_block_is_sequence(self) -> None:
        blocks = extract_mermaid_blocks(MARKDOWN_WITH_MERMAID)
        assert blocks[1].startswith("sequenceDiagram")

    def test_no_mermaid(self) -> None:
        blocks = extract_mermaid_blocks(MARKDOWN_NO_MERMAID)
        assert blocks == []

    def test_python_block_not_extracted(self) -> None:
        """pythonコードブロックはmermaidとして抽出されない."""
        blocks = extract_mermaid_blocks(MARKDOWN_WITH_MERMAID)
        assert not any("print" in b for b in blocks)


# --- validate_mermaid_syntax ---

class TestValidateMermaidSyntax:
    """Mermaid構文検証テスト."""

    def test_good_flowchart(self) -> None:
        result = validate_mermaid_syntax(GOOD_FLOWCHART)
        assert result.ok is True
        assert any("flowchart" in p for p in result.passed)

    def test_good_graph(self) -> None:
        result = validate_mermaid_syntax(GOOD_GRAPH)
        assert result.ok is True
        assert any("graph" in p for p in result.passed)
        assert any("LR" in p for p in result.passed)

    def test_empty_block(self) -> None:
        result = validate_mermaid_syntax(BAD_EMPTY)
        assert result.ok is False
        assert any("空" in w for w in result.warnings)

    def test_unknown_type(self) -> None:
        result = validate_mermaid_syntax(BAD_UNKNOWN_TYPE)
        assert result.ok is False
        assert any("不明" in w for w in result.warnings)

    def test_no_direction(self) -> None:
        result = validate_mermaid_syntax(NO_DIRECTION)
        assert result.ok is False
        assert any("方向" in w for w in result.warnings)

    def test_edges_detected(self) -> None:
        result = validate_mermaid_syntax(GOOD_FLOWCHART)
        assert any("エッジ" in p for p in result.passed)

    def test_nodes_only_info(self) -> None:
        result = validate_mermaid_syntax(NODES_ONLY)
        assert any("エッジ" in i for i in result.info)


# --- generate_pipeline_diagram ---

class TestGeneratePipelineDiagram:
    """パイプライン図生成テスト."""

    def test_basic_pipeline(self) -> None:
        steps = [
            PipelineStep(name="A", label="FASTQ"),
            PipelineStep(name="B", label="FastQC"),
            PipelineStep(name="C", label="STAR"),
        ]
        diagram = generate_pipeline_diagram(steps)
        assert diagram.startswith("flowchart TD")
        assert "A[FASTQ]" in diagram
        assert "A --> B" in diagram
        assert "B --> C" in diagram

    def test_single_step(self) -> None:
        steps = [PipelineStep(name="A", label="唯一のステップ")]
        diagram = generate_pipeline_diagram(steps)
        assert "A[唯一のステップ]" in diagram
        assert "-->" not in diagram

    def test_empty_steps_raises(self) -> None:
        with pytest.raises(ValueError, match="空"):
            generate_pipeline_diagram([])

    def test_output_is_valid_mermaid(self) -> None:
        """生成された図がvalidate_mermaid_syntaxを通過する."""
        steps = [
            PipelineStep(name="A", label="Input"),
            PipelineStep(name="B", label="Process"),
            PipelineStep(name="C", label="Output"),
        ]
        diagram = generate_pipeline_diagram(steps)
        result = validate_mermaid_syntax(diagram)
        assert result.ok is True


# --- ValidationResult ---

class TestValidationResult:
    """ValidationResultのプロパティテスト."""

    def test_ok_when_no_warnings(self) -> None:
        r = ValidationResult(passed=["check1"], warnings=[], info=["info1"])
        assert r.ok is True

    def test_not_ok_when_warnings(self) -> None:
        r = ValidationResult(passed=[], warnings=["warn1"], info=[])
        assert r.ok is False

    def test_info_does_not_affect_ok(self) -> None:
        """infoフィールドはokに影響しない."""
        r = ValidationResult(passed=[], warnings=[], info=["info1", "info2"])
        assert r.ok is True
