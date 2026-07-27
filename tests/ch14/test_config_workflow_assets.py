"""第14章のSnakefileとMakefileを直接検証する."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CH14_DIR = PROJECT_ROOT / "scripts" / "ch14"


def _load_config() -> dict[str, Any]:
    """config.yamlを辞書として読み込む."""
    config = yaml.safe_load(
        (CH14_DIR / "config.yaml").read_text(encoding="utf-8")
    )
    assert isinstance(config, dict)
    return config


def test_snakefile_uses_config_and_tracks_intermediate_bam() -> None:
    """スレッド設定、BAMの寿命、ログ参照が実体に含まれる."""
    source = (CH14_DIR / "Snakefile").read_text(encoding="utf-8")
    config = _load_config()

    assert 'threads: config["params"]["fastqc"]["threads"]' in source
    assert config["params"]["fastqc"]["threads"] == 4
    assert (
        'bam=temp("results/aligned/{sample}_Aligned.sortedByCoord.out.bam")'
        in source
    )
    assert '"logs/star/{sample}.log"' in source
    assert "2> {log}" in source


def test_makefile_dry_run_preserves_dependency_order() -> None:
    """make -nでダウンロード、解凍、索引作成の順序を確認する."""
    result = subprocess.run(
        ["make", "-n", "-f", str(CH14_DIR / "Makefile"), "all"],
        cwd=CH14_DIR,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    commands = result.stdout.splitlines()
    curl_index = next(i for i, line in enumerate(commands) if "curl -L" in line)
    gunzip_index = next(i for i, line in enumerate(commands) if "gunzip -k" in line)
    samtools_index = next(
        i for i, line in enumerate(commands) if "samtools faidx" in line
    )
    assert curl_index < gunzip_index < samtools_index


def test_makefile_clean_lists_every_generated_file() -> None:
    """cleanが圧縮FASTA、展開後FASTA、索引を削除対象にする."""
    result = subprocess.run(
        ["make", "-n", "-f", str(CH14_DIR / "Makefile"), "clean"],
        cwd=CH14_DIR,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "GRCh38.fa.gz" in result.stdout
    assert "GRCh38.fa" in result.stdout
    assert "GRCh38.fa.fai" in result.stdout
