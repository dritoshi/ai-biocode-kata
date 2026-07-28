"""E1解消計画で固定した本文例の方針テスト."""

from __future__ import annotations

import ast
from pathlib import Path

from scripts.review.code_correspondence import extract_source_blocks

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CHAPTER_PATH = PROJECT_ROOT / "chapters/17_performance.md"


def test_generator_pipeline_uses_caller_path() -> None:
    """B-17-032の呼出例が固定パスではなくpath変数を使う."""
    blocks, _ = extract_source_blocks(CHAPTER_PATH, root=PROJECT_ROOT)
    block = next(item for item in blocks if item.id == "B-17-032")
    tree = ast.parse(block.code)

    read_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "read_fastq_records"
    ]
    assert len(read_calls) == 1
    assert len(read_calls[0].args) == 1
    assert isinstance(read_calls[0].args[0], ast.Name)
    assert read_calls[0].args[0].id == "path"

    fixed_paths = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Path"
        and node.args
        and isinstance(node.args[0], ast.Constant)
    ]
    assert fixed_paths == []
