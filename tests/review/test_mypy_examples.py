"""本文に意図的に残したmypyエラー例を検証する."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.review.code_correspondence import extract_source_blocks

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CHAPTER_PATH = PROJECT_ROOT / "chapters/08_testing.md"


def test_ch08_assignment_error_is_detected_by_mypy(tmp_path: Path) -> None:
    """B-08-019が型不整合の教材として機能することを確認する."""

    blocks, _ = extract_source_blocks(CHAPTER_PATH, root=PROJECT_ROOT)
    block = next(item for item in blocks if item.id == "B-08-019")
    example_path = tmp_path / "mypy_assignment_error.py"
    example_path.write_text(f"{block.code}\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--no-incremental",
            "--show-error-codes",
            str(example_path),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    output = f"{completed.stdout}\n{completed.stderr}"
    assert completed.returncode == 1
    assert "Incompatible types in assignment" in output
    assert 'expression has type "float", variable has type "int"' in output
