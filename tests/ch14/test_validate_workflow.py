"""validate_workflowモジュールのテスト."""

import pytest

from scripts.ch14.validate_workflow import (
    ValidationResult,
    check_configfile,
    check_io_separation,
    check_log_directives,
    check_temp_usage,
    validate,
)

# --- テスト用Snakefileテキスト ---

GOOD_SNAKEFILE = """\
configfile: "config.yaml"

SAMPLES = config["samples"]

rule all:
    input:
        expand("results/counts/{sample}_counts.txt", sample=SAMPLES),

rule fastqc:
    input:
        "data/raw/{sample}.fastq.gz",
    output:
        html="results/qc/{sample}_fastqc.html",
    log:
        "logs/fastqc/{sample}.log",
    shell:
        "fastqc {input} --outdir results/qc 2> {log}"

rule trimmomatic:
    input:
        "data/raw/{sample}.fastq.gz",
    output:
        trimmed=temp("results/trimmed/{sample}_trimmed.fastq.gz"),
    log:
        "logs/trimmomatic/{sample}.log",
    shell:
        "trimmomatic SE {input} {output.trimmed} 2> {log}"

rule star_align:
    input:
        fastq="results/trimmed/{sample}_trimmed.fastq.gz",
    output:
        bam=temp("results/aligned/{sample}.bam"),
    log:
        "logs/star/{sample}.log",
    shell:
        "STAR --readFilesIn {input.fastq} 2> {log}"

rule featurecounts:
    input:
        bam="results/aligned/{sample}.bam",
        gtf=config["genome"]["gtf"],
    output:
        counts="results/counts/{sample}_counts.txt",
    log:
        "logs/featurecounts/{sample}.log",
    shell:
        "featureCounts -a {input.gtf} -o {output.counts} {input.bam} 2> {log}"
"""

NO_LOG_SNAKEFILE = """\
configfile: "config.yaml"

rule all:
    input:
        "results/output.txt",

rule step_one:
    input:
        "data/raw/input.txt",
    output:
        "results/output.txt",
    shell:
        "cat {input} > {output}"
"""

NO_CONFIG_SNAKEFILE = """\
SAMPLES = ["s1", "s2"]

rule all:
    input:
        expand("results/{sample}.txt", sample=SAMPLES),

rule process:
    input:
        "data/raw/{sample}.fastq.gz",
    output:
        "results/{sample}.txt",
    log:
        "logs/{sample}.log",
    shell:
        "echo {input} > {output} 2> {log}"
"""

MIXED_IO_SNAKEFILE = """\
configfile: "config.yaml"

rule all:
    input:
        "data/raw/result.txt",

rule bad_rule:
    input:
        "data/raw/input.txt",
    output:
        "data/raw/result.txt",
    log:
        "logs/bad.log",
    shell:
        "cat {input} > {output} 2> {log}"
"""


# --- check_log_directives ---

class TestCheckLogDirectives:
    """log:ディレクティブの検証テスト."""

    def test_all_rules_have_log(self) -> None:
        ok, missing = check_log_directives(GOOD_SNAKEFILE)
        assert ok is True
        assert missing == []

    def test_missing_log(self) -> None:
        ok, missing = check_log_directives(NO_LOG_SNAKEFILE)
        assert ok is False
        assert "step_one" in missing

    def test_all_rule_skipped(self) -> None:
        """allルールはlog:不要."""
        ok, missing = check_log_directives(NO_LOG_SNAKEFILE)
        assert "all" not in missing


# --- check_configfile ---

class TestCheckConfigfile:
    """configfile:ディレクティブの検証テスト."""

    def test_has_configfile(self) -> None:
        assert check_configfile(GOOD_SNAKEFILE) is True

    def test_no_configfile(self) -> None:
        assert check_configfile(NO_CONFIG_SNAKEFILE) is False


# --- check_temp_usage ---

class TestCheckTempUsage:
    """temp()の使用検証テスト."""

    def test_has_temp(self) -> None:
        has_temp, temp_rules = check_temp_usage(GOOD_SNAKEFILE)
        assert has_temp is True
        assert "trimmomatic" in temp_rules
        assert "star_align" in temp_rules

    def test_no_temp(self) -> None:
        has_temp, temp_rules = check_temp_usage(NO_LOG_SNAKEFILE)
        assert has_temp is False
        assert temp_rules == []


# --- check_io_separation ---

class TestCheckIOSeparation:
    """入出力パス分離の検証テスト."""

    def test_separated(self) -> None:
        ok, mixed = check_io_separation(GOOD_SNAKEFILE)
        assert ok is True
        assert mixed == []

    def test_mixed(self) -> None:
        ok, mixed = check_io_separation(MIXED_IO_SNAKEFILE)
        assert ok is False
        assert "bad_rule" in mixed


# --- validate ---

class TestValidate:
    """一括検証のテスト."""

    def test_good_snakefile(self) -> None:
        result = validate(GOOD_SNAKEFILE)
        assert result.ok is True
        assert len(result.passed) >= 3
        assert result.warnings == []

    def test_bad_snakefile_multiple_warnings(self) -> None:
        result = validate(NO_CONFIG_SNAKEFILE)
        assert result.ok is False
        # configfile:なし + temp()なし で最低2つの警告
        assert len(result.warnings) >= 2

    def test_mixed_io_warning(self) -> None:
        result = validate(MIXED_IO_SNAKEFILE)
        assert any("混在" in w for w in result.warnings)


# --- ValidationResult ---

class TestValidationResult:
    """ValidationResultのプロパティテスト."""

    def test_ok_when_no_warnings(self) -> None:
        r = ValidationResult(passed=["check1"], warnings=[])
        assert r.ok is True

    def test_not_ok_when_warnings(self) -> None:
        r = ValidationResult(passed=[], warnings=["warn1"])
        assert r.ok is False
