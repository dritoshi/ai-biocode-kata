#!/usr/bin/env python3
"""E1バッチ番号から対象pytestまたはmypyを一意に実行する."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

TARGETS = {
    1: ("ch01", "ch03"),
    2: ("ch08", "ch09", "ch10"),
    3: ("ch12",),
    4: ("ch02", "ch13", "ch17"),
    5: ("ch21",),
}


def command_for(root: Path, batch: int, gate: str) -> list[str]:
    """指定バッチ・ゲートの単一コマンドを返す."""
    if batch not in TARGETS:
        raise ValueError("batchは1〜5でなければならない")
    chapters = TARGETS[batch]
    if gate == "target-pytest":
        return [
            str(root / ".venv/bin/pytest"),
            *(f"tests/{chapter}" for chapter in chapters),
            "-q",
            "-p",
            "no:cacheprovider",
        ]
    if gate == "mypy":
        paths = [
            path
            for chapter in chapters
            for path in (f"scripts/{chapter}", f"tests/{chapter}")
        ]
        return [
            str(root / ".venv/bin/mypy"),
            "--follow-imports=skip",
            "--ignore-missing-imports",
            *paths,
        ]
    raise ValueError(f"未知のgate: {gate}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--batch", type=int, required=True)
    parser.add_argument(
        "--gate",
        choices=("target-pytest", "mypy"),
        required=True,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    command = command_for(root, args.batch, args.gate)
    completed = subprocess.run(command, cwd=root, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
