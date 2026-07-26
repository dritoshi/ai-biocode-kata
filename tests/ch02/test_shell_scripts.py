"""第2章のシェルスクリプト例を検証する."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = PROJECT_ROOT / "scripts" / "ch02"
SCRIPT_NAMES = (
    "fastqc_pipeline.sh",
    "check_fastq.sh",
    "batch_process.sh",
)


def _write_stub(bin_dir: Path, name: str) -> None:
    """外部ツール呼び出しを記録するスタブを作る."""
    path = bin_dir / name
    path.write_text(
        "#!/bin/bash\n"
        "set -euo pipefail\n"
        f'printf "{name}\\t%s\\n" "$*" >> "${{TOOL_LOG}}"\n',
        encoding="utf-8",
    )
    path.chmod(0o755)


def _tool_env(bin_dir: Path, log_path: Path) -> dict[str, str]:
    """スタブを優先する実行環境を返す."""
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    env["TOOL_LOG"] = str(log_path)
    return env


def _run(
    script_name: str,
    *args: Path | str,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """対象スクリプトを実行し、結果を返す."""
    return subprocess.run(
        [str(SCRIPT_DIR / script_name), *(str(arg) for arg in args)],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.mark.parametrize("script_name", SCRIPT_NAMES)
def test_bash_syntax(script_name: str) -> None:
    result = subprocess.run(
        ["bash", "-n", str(SCRIPT_DIR / script_name)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_fastqc_pipeline_creates_output_and_invokes_fastqc(
    tmp_path: Path,
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_stub(bin_dir, "fastqc")
    log_path = tmp_path / "tools.log"
    fastq_dir = tmp_path / "data" / "fastq"
    fastq_dir.mkdir(parents=True)
    (fastq_dir / "sample_A_R1.fastq.gz").touch()

    result = _run(
        "fastqc_pipeline.sh",
        "sample_A",
        cwd=tmp_path,
        env=_tool_env(bin_dir, log_path),
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "results" / "sample_A").is_dir()
    assert result.stdout.splitlines() == [
        "品質チェック: sample_A",
        "完了: sample_A",
    ]
    assert "data/fastq/sample_A_R1.fastq.gz -o results/sample_A" in (
        log_path.read_text(encoding="utf-8")
    )


def test_check_fastq_accepts_existing_input_and_creates_output(
    tmp_path: Path,
) -> None:
    fastq_dir = tmp_path / "fastq"
    fastq_dir.mkdir()
    (fastq_dir / "sample_A_R1.fastq.gz").touch()
    output_dir = tmp_path / "results" / "sample_A"

    result = _run(
        "check_fastq.sh",
        fastq_dir,
        "sample_A",
        output_dir,
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "FASTQファイルが見つかった"
    assert output_dir.is_dir()


def test_check_fastq_rejects_missing_input(tmp_path: Path) -> None:
    fastq_dir = tmp_path / "fastq"
    fastq_dir.mkdir()
    output_dir = tmp_path / "results"

    result = _run(
        "check_fastq.sh",
        fastq_dir,
        "missing",
        output_dir,
        cwd=tmp_path,
    )

    assert result.returncode == 1
    assert "FASTQファイルが見つからない" in result.stderr
    assert not output_dir.exists()


def test_batch_process_invokes_tools_for_samples_and_bam(
    tmp_path: Path,
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_stub(bin_dir, "fastqc")
    _write_stub(bin_dir, "samtools")
    log_path = tmp_path / "tools.log"
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    (results_dir / "sample_A.bam").touch()

    result = _run(
        "batch_process.sh",
        cwd=tmp_path,
        env=_tool_env(bin_dir, log_path),
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "処理中: sample_A",
        "処理中: sample_B",
        "処理中: sample_C",
    ]
    log_lines = log_path.read_text(encoding="utf-8").splitlines()
    assert sum(line.startswith("fastqc\t") for line in log_lines) == 3
    assert log_lines[-1] == "samtools\tindex results/sample_A.bam"
