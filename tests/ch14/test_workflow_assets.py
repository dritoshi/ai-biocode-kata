"""第14章のワークフロー実資産を検証する."""

from __future__ import annotations

import csv
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

PROJECT_ROOT = Path(__file__).parents[2]
CH14_DIR = PROJECT_ROOT / "scripts" / "ch14"
RUN_EXTERNAL_RUNTIME_TESTS = (
    os.environ.get("RUN_EXTERNAL_RUNTIME_TESTS") == "1"
)


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _write_executable(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


def _fake_tool_environment(tmp_path: Path) -> dict[str, str]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    _write_executable(
        bin_dir / "fastqc",
        """#!/usr/bin/env bash
set -euo pipefail
input=""
outdir="."
while [[ $# -gt 0 ]]; do
    case "$1" in
        --outdir)
            outdir="$2"
            shift 2
            ;;
        *)
            input="$1"
            shift
            ;;
    esac
done
sample="$(basename "$input")"
sample="${sample%%.*}"
mkdir -p "$outdir"
: > "$outdir/${sample}_fastqc.html"
: > "$outdir/${sample}_fastqc.zip"
""",
    )
    _write_executable(
        bin_dir / "fastp",
        """#!/usr/bin/env bash
set -euo pipefail
out1=""
out2=""
html=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --out1)
            out1="$2"
            shift 2
            ;;
        --out2)
            out2="$2"
            shift 2
            ;;
        --html)
            html="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done
: > "$out1"
: > "$out2"
: > "$html"
""",
    )
    _write_executable(
        bin_dir / "hisat2",
        """#!/usr/bin/env bash
set -euo pipefail
printf '@HD\\tVN:1.6\\n'
printf 'read1\\t4\\t*\\t0\\t0\\t*\\t*\\t0\\t0\\tACGT\\tIIII\\n'
""",
    )
    _write_executable(
        bin_dir / "samtools",
        """#!/usr/bin/env bash
set -euo pipefail
output=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        -o)
            output="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done
cat > "$output"
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    return env


def _r_has_deseq2() -> bool:
    rscript = shutil.which("Rscript")
    if rscript is None:
        return False
    result = subprocess.run(
        [
            rscript,
            "-e",
            'quit(status=if(requireNamespace("DESeq2", quietly=TRUE)) 0 else 1)',
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def test_snakemake_assets_are_connected() -> None:
    snakefile = (CH14_DIR / "Snakefile.conda").read_text(encoding="utf-8")
    environment = _load_yaml(CH14_DIR / "envs" / "deseq2.yaml")

    assert 'counts="data/deseq2/counts.tsv"' in snakefile
    assert 'samples="data/deseq2/samples.tsv"' in snakefile
    assert '"envs/deseq2.yaml"' in snakefile
    assert '"run_deseq2.R"' in snakefile
    assert "r-base=4.5" in environment["dependencies"]
    assert "bioconductor-deseq2=1.50.2" in environment["dependencies"]

    for relative_path in (
        "data/deseq2/counts.tsv",
        "data/deseq2/samples.tsv",
        "envs/deseq2.yaml",
        "run_deseq2.R",
    ):
        assert (CH14_DIR / relative_path).is_file()


def test_deseq2_fixture_columns_match_sample_rows() -> None:
    with (CH14_DIR / "data" / "deseq2" / "counts.tsv").open(
        encoding="utf-8",
        newline="",
    ) as counts_file:
        count_header = next(csv.reader(counts_file, delimiter="\t"))[1:]
    with (CH14_DIR / "data" / "deseq2" / "samples.tsv").open(
        encoding="utf-8",
        newline="",
    ) as samples_file:
        sample_rows = list(csv.DictReader(samples_file, delimiter="\t"))

    assert count_header == [row["sample_id"] for row in sample_rows]
    assert {row["condition"] for row in sample_rows} == {"control", "treated"}


def test_nextflow_asset_declares_dsl2_dataflow() -> None:
    source = (CH14_DIR / "fastqc.nf").read_text(encoding="utf-8")

    assert "nextflow.enable.dsl = 2" in source
    assert "process FASTQC" in source
    assert "tuple val(sample_id), path(fastq)" in source
    assert "emit: reports" in source
    assert "Channel" in source
    assert ".fromPath(params.reads, checkIfExists: true)" in source
    assert "FASTQC(reads_ch)" in source


def test_cwl_tools_and_workflow_are_connected() -> None:
    fastp = _load_yaml(CH14_DIR / "fastp_filter.cwl")
    align = _load_yaml(CH14_DIR / "hisat2_align.cwl")
    workflow = _load_yaml(CH14_DIR / "rnaseq_pipeline.cwl")

    assert fastp["cwlVersion"] == "v1.2"
    assert fastp["class"] == "CommandLineTool"
    assert fastp["baseCommand"] == "fastp"
    assert fastp["requirements"] == {"InlineJavascriptRequirement": {}}
    assert fastp["hints"]["DockerRequirement"]["dockerPull"] == (
        "quay.io/biocontainers/fastp:0.23.4--h125f33a_5"
    )
    assert set(fastp["outputs"]) == {"filtered_r1", "filtered_r2", "report_html"}

    assert align["class"] == "CommandLineTool"
    assert align["baseCommand"] == "bash"
    assert set(align["inputs"]) == {
        "fastq_r1",
        "fastq_r2",
        "genome_index",
        "sample_name",
    }
    assert set(align["outputs"]) == {"bam_output"}

    assert workflow["class"] == "Workflow"
    assert set(workflow["inputs"]) == {
        "fastq_r1",
        "fastq_r2",
        "sample_name",
        "genome_index",
    }
    assert workflow["steps"]["filter"]["run"] == "fastp_filter.cwl"
    assert workflow["steps"]["align"]["run"] == "hisat2_align.cwl"
    assert workflow["steps"]["align"]["in"]["fastq_r1"] == "filter/filtered_r1"
    assert workflow["steps"]["align"]["in"]["fastq_r2"] == "filter/filtered_r2"


def test_cwl_job_has_all_inputs_and_existing_locations() -> None:
    job = _load_yaml(CH14_DIR / "inputs.yml")

    assert set(job) == {
        "fastq_r1",
        "fastq_r2",
        "sample_name",
        "genome_index",
    }
    for name in ("fastq_r1", "fastq_r2", "genome_index"):
        item = job[name]
        assert isinstance(item, dict)
        assert (CH14_DIR / item["location"]).exists()


@pytest.mark.runtime_smoke
@pytest.mark.skipif(
    not RUN_EXTERNAL_RUNTIME_TESTS or shutil.which("snakemake") is None,
    reason=(
        "SnakemakeテストはRUN_EXTERNAL_RUNTIME_TESTS=1かつ"
        "実行環境がある場合に実行する"
    ),
)
def test_snakemake_dry_run(tmp_path: Path) -> None:
    workflow_dir = tmp_path / "workflow"
    (workflow_dir / "data").mkdir(parents=True)
    shutil.copytree(
        CH14_DIR / "data" / "deseq2",
        workflow_dir / "data" / "deseq2",
    )
    shutil.copytree(CH14_DIR / "envs", workflow_dir / "envs")
    shutil.copy2(CH14_DIR / "Snakefile.conda", workflow_dir)
    shutil.copy2(CH14_DIR / "run_deseq2.R", workflow_dir)

    source_cache = tmp_path / "snakemake-source-cache"
    source_cache.mkdir()
    subprocess.run(
        [
            "snakemake",
            "--snakefile",
            str(workflow_dir / "Snakefile.conda"),
            "--directory",
            str(workflow_dir),
            "--cores",
            "1",
            "--dry-run",
            "--runtime-source-cache-path",
            str(source_cache),
        ],
        check=True,
    )


@pytest.mark.skipif(
    shutil.which("Rscript") is None,
    reason="Rscriptがインストールされていない",
)
def test_r_script_parses() -> None:
    subprocess.run(
        [
            "Rscript",
            "-e",
            f"parse(file={str(CH14_DIR / 'run_deseq2.R')!r})",
        ],
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.mark.runtime_smoke
@pytest.mark.skipif(
    not RUN_EXTERNAL_RUNTIME_TESTS or not _r_has_deseq2(),
    reason=(
        "DESeq2テストはRUN_EXTERNAL_RUNTIME_TESTS=1かつ"
        "実行環境がある場合に実行する"
    ),
)
def test_deseq2_smoke(tmp_path: Path) -> None:
    output_path = tmp_path / "deseq2_results.csv"
    log_path = tmp_path / "deseq2.log"

    subprocess.run(
        [
            "Rscript",
            str(CH14_DIR / "run_deseq2.R"),
            str(CH14_DIR / "data" / "deseq2" / "counts.tsv"),
            str(CH14_DIR / "data" / "deseq2" / "samples.tsv"),
            str(output_path),
            str(log_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    with output_path.open(encoding="utf-8", newline="") as result_file:
        rows = list(csv.DictReader(result_file))
    assert len(rows) == 20
    assert set(rows[0]) == {
        "gene_id",
        "baseMean",
        "log2FoldChange",
        "lfcSE",
        "stat",
        "pvalue",
        "padj",
    }
    assert "20遺伝子の結果を保存した" in log_path.read_text(encoding="utf-8")


@pytest.mark.runtime_smoke
@pytest.mark.skipif(
    not RUN_EXTERNAL_RUNTIME_TESTS or shutil.which("nextflow") is None,
    reason=(
        "NextflowテストはRUN_EXTERNAL_RUNTIME_TESTS=1かつ"
        "実行環境がある場合に実行する"
    ),
)
def test_nextflow_smoke(tmp_path: Path) -> None:
    fastq = tmp_path / "sample.fastq"
    fastq.write_text("@read1\nACGT\n+\nIIII\n", encoding="utf-8")
    outdir = tmp_path / "results"
    env = _fake_tool_environment(tmp_path)
    env.setdefault("NXF_HOME", str(tmp_path / ".nextflow"))
    env["NXF_ANSI_LOG"] = "false"
    env["NXF_OFFLINE"] = "true"

    subprocess.run(
        [
            "nextflow",
            "run",
            str(CH14_DIR / "fastqc.nf"),
            "--reads",
            str(fastq),
            "--outdir",
            str(outdir),
        ],
        cwd=tmp_path,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    assert (outdir / "qc" / "sample_fastqc.html").is_file()
    assert (outdir / "qc" / "sample_fastqc.zip").is_file()


@pytest.mark.runtime_smoke
@pytest.mark.skipif(
    not RUN_EXTERNAL_RUNTIME_TESTS or shutil.which("cwltool") is None,
    reason=(
        "CWLテストはRUN_EXTERNAL_RUNTIME_TESTS=1かつ"
        "実行環境がある場合に実行する"
    ),
)
def test_cwl_validate_and_smoke(tmp_path: Path) -> None:
    for filename in (
        "fastp_filter.cwl",
        "hisat2_align.cwl",
        "rnaseq_pipeline.cwl",
    ):
        subprocess.run(
            ["cwltool", "--validate", str(CH14_DIR / filename)],
            check=True,
            capture_output=True,
            text=True,
        )

    outdir = tmp_path / "results"
    outdir.mkdir()
    subprocess.run(
        [
            "cwltool",
            "--no-container",
            "--outdir",
            str(outdir),
            str(CH14_DIR / "rnaseq_pipeline.cwl"),
            str(CH14_DIR / "inputs.yml"),
        ],
        cwd=tmp_path,
        env=_fake_tool_environment(tmp_path),
        check=True,
        capture_output=True,
        text=True,
    )

    assert (outdir / "sample_A.bam").is_file()
    assert (outdir / "sample_A_fastp.html").is_file()
