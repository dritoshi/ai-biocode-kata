#!/usr/bin/env python3
"""全ゲート成功後だけE1対応表4生成物を反映・コミットする."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.review.check_e1_source_scope import (  # noqa: E402
    validate_source_scope,
)
from scripts.review.e1_remediation import (  # noqa: E402
    GENERATED_ARTIFACTS,
    load_fixture,
)


def _run(root: Path, command: list[str]) -> str:
    completed = subprocess.run(
        command,
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise ValueError(f"{' '.join(command)} に失敗:\n{detail}")
    return completed.stdout.strip()


def _python(root: Path) -> str:
    candidate = root / ".venv/bin/python"
    return str(candidate if candidate.is_file() else Path(sys.executable))


def finalize(
    root: Path,
    *,
    batch: int,
    baseline_ref: str,
    transition_baseline_ref: str,
    previous_ref: str,
    source_commit: str,
) -> dict[str, str]:
    """ゲート、生成、監査、反映、生成物コミットを順に実行する."""
    python = _python(root)
    head = _run(root, ["git", "rev-parse", "HEAD"])
    if head != source_commit:
        raise ValueError("HEADが指定source_commitと一致しない")
    fixture = load_fixture(root)
    validate_source_scope(
        root,
        fixture,
        batch,
        baseline_ref,
        source_commit,
        check_worktree=True,
        require_clean=True,
    )

    _run(
        root,
        [
            python,
            "scripts/review/run_e1_batch_gates.py",
            "--batch",
            str(batch),
            "--gate",
            "target-pytest",
        ],
    )
    _run(
        root,
        [
            str(root / ".venv/bin/pytest"),
            "-q",
            "-p",
            "no:cacheprovider",
        ],
    )
    _run(root, [str(root / ".venv/bin/ruff"), "check", "scripts", "tests"])
    _run(
        root,
        [
            python,
            "scripts/review/run_e1_batch_gates.py",
            "--batch",
            str(batch),
            "--gate",
            "mypy",
        ],
    )
    _run(
        root,
        [
            str(root / ".venv/bin/mypy"),
            "--no-incremental",
            "--follow-imports=skip",
            "--ignore-missing-imports",
            "scripts/review",
            "tests/review",
        ],
    )
    _run(root, ["git", "diff", "--check", baseline_ref, source_commit])

    with tempfile.TemporaryDirectory(
        prefix="ai-biocode-kata-e1-finalize-",
        dir="/private/tmp",
    ) as temporary:
        temp = Path(temporary)
        structure = temp / "structure_check.json"
        xref = temp / "xref_check.json"
        inventory = temp / "code_correspondence.json"
        report = temp / "code_correspondence.md"
        _run(
            root,
            [
                python,
                "scripts/review/check_structure.py",
                "--baseline",
                "docs/review/structure_check.json",
                "--output",
                str(structure),
            ],
        )
        _run(
            root,
            [
                python,
                "scripts/review/check_xref.py",
                "--output",
                str(xref),
            ],
        )
        _run(
            root,
            [
                python,
                "scripts/review/build_code_correspondence.py",
                "--output",
                str(inventory),
                "--report",
                str(report),
                "--check-determinism",
            ],
        )
        _run(
            root,
            [
                python,
                "scripts/review/audit_code_correspondence.py",
                "--input",
                str(inventory),
                "--report",
                str(report),
            ],
        )
        _run(
            root,
            [
                python,
                "scripts/review/check_e1_transition.py",
                "--batch",
                str(batch),
                "--transition-baseline-ref",
                transition_baseline_ref,
                "--previous-ref",
                previous_ref,
                "--current",
                str(inventory),
            ],
        )

        validate_source_scope(
            root,
            fixture,
            batch,
            baseline_ref,
            source_commit,
            check_worktree=True,
            require_clean=True,
        )
        generated = {
            "docs/review/code_correspondence.json": inventory,
            "docs/review/code_correspondence.md": report,
            "docs/review/structure_check.json": structure,
            "docs/review/xref_check.json": xref,
        }
        for relative, temporary_path in generated.items():
            shutil.copyfile(temporary_path, root / relative)

    changed = set(
        _run(root, ["git", "diff", "--name-only", "HEAD"]).splitlines()
    )
    required = {
        "docs/review/code_correspondence.json",
        "docs/review/code_correspondence.md",
    }
    if not required.issubset(changed) or not changed.issubset(
        GENERATED_ARTIFACTS
    ):
        raise ValueError("反映後の変更が許可した4生成物に限定されていない")
    _run(root, ["git", "diff", "--check"])
    _run(root, ["git", "add", *sorted(changed)])
    _run(
        root,
        ["git", "commit", "-m", "docs: refresh E1 correspondence artifacts"],
    )
    artifact_commit = _run(root, ["git", "rev-parse", "HEAD"])
    result = {
        "source_commit": source_commit,
        "artifact_commit": artifact_commit,
    }
    print(json.dumps(result))
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--batch", type=int, required=True)
    parser.add_argument("--baseline-ref", required=True)
    parser.add_argument("--transition-baseline-ref", required=True)
    parser.add_argument("--previous-ref", required=True)
    parser.add_argument("--source-commit", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    finalize(
        args.root.resolve(),
        batch=args.batch,
        baseline_ref=args.baseline_ref,
        transition_baseline_ref=args.transition_baseline_ref,
        previous_ref=args.previous_ref,
        source_commit=args.source_commit,
    )


if __name__ == "__main__":
    main()
