"""validate_slurmモジュールのテスト."""

import pytest

from scripts.ch14.validate_slurm import (
    ValidationResult,
    check_gpu_cpu_balance,
    check_job_name,
    check_memory_request,
    check_output_log,
    check_time_limit,
    validate,
)

# --- テスト用SLURMスクリプトテキスト ---

GOOD_SCRIPT = """\
#!/bin/bash
#SBATCH --job-name=rnaseq_align
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err
#SBATCH --time=04:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=8

module load hisat2/2.2.1
hisat2 -p 8 -x genome_index -1 reads_R1.fq.gz -2 reads_R2.fq.gz -S output.sam
"""

MINIMAL_SCRIPT = """\
#!/bin/bash
#SBATCH --job-name=test
#SBATCH --output=logs/%j.out
#SBATCH --time=00:10:00
#SBATCH --mem=1G

echo "Hello from SLURM"
"""

NO_JOB_NAME = """\
#!/bin/bash
#SBATCH --output=logs/%j.out
#SBATCH --time=01:00:00
#SBATCH --mem=4G

python analysis.py
"""

NO_OUTPUT = """\
#!/bin/bash
#SBATCH --job-name=analysis
#SBATCH --time=01:00:00
#SBATCH --mem=4G

python analysis.py
"""

NO_TIME = """\
#!/bin/bash
#SBATCH --job-name=analysis
#SBATCH --output=logs/%j.out
#SBATCH --mem=4G

python analysis.py
"""

NO_MEMORY = """\
#!/bin/bash
#SBATCH --job-name=analysis
#SBATCH --output=logs/%j.out
#SBATCH --time=01:00:00

python analysis.py
"""

MEM_PER_CPU_SCRIPT = """\
#!/bin/bash
#SBATCH --job-name=analysis
#SBATCH --output=logs/%j.out
#SBATCH --time=01:00:00
#SBATCH --mem-per-cpu=2G
#SBATCH --cpus-per-task=4

python analysis.py
"""

GPU_GOOD_SCRIPT = """\
#!/bin/bash
#SBATCH --job-name=gpu_train
#SBATCH --output=logs/%j.out
#SBATCH --time=24:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu

module load cuda/12.0
python train.py
"""

GPU_LOW_CPU_SCRIPT = """\
#!/bin/bash
#SBATCH --job-name=gpu_train
#SBATCH --output=logs/%j.out
#SBATCH --time=24:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu

python train.py
"""

GPU_NO_CPU_SCRIPT = """\
#!/bin/bash
#SBATCH --job-name=gpu_train
#SBATCH --output=logs/%j.out
#SBATCH --time=24:00:00
#SBATCH --mem=32G
#SBATCH --gres=gpu:2

python train.py
"""

GPU_NO_PARTITION_SCRIPT = """\
#!/bin/bash
#SBATCH --job-name=gpu_train
#SBATCH --output=logs/%j.out
#SBATCH --time=24:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1

python train.py
"""

GPU_TYPED_SCRIPT = """\
#!/bin/bash
#SBATCH --job-name=gpu_train
#SBATCH --output=logs/%j.out
#SBATCH --time=24:00:00
#SBATCH --mem=64G
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:a100:2
#SBATCH --partition=gpu

python train.py
"""

SHORT_FORM_SCRIPT = """\
#!/bin/bash
#SBATCH -J align_job
#SBATCH -o logs/%j.out
#SBATCH -e logs/%j.err
#SBATCH -t 02:00:00
#SBATCH --mem=8G
#SBATCH -c 4

hisat2 -p 4 -x index -1 R1.fq.gz -2 R2.fq.gz -S out.sam
"""

EMPTY_SCRIPT = """\
#!/bin/bash
echo "no SBATCH directives"
"""


# --- check_job_name ---

class TestCheckJobName:
    """ジョブ名指定の検証テスト."""

    def test_job_name_present(self) -> None:
        ok, issues = check_job_name(GOOD_SCRIPT)
        assert ok is True
        assert issues == []

    def test_job_name_missing(self) -> None:
        ok, issues = check_job_name(NO_JOB_NAME)
        assert ok is False
        assert len(issues) == 1
        assert "--job-name" in issues[0]

    def test_short_form(self) -> None:
        """短形式 -J でもジョブ名として認識される."""
        ok, issues = check_job_name(SHORT_FORM_SCRIPT)
        assert ok is True
        assert issues == []


# --- check_output_log ---

class TestCheckOutputLog:
    """ログ出力先指定の検証テスト."""

    def test_output_present(self) -> None:
        ok, issues = check_output_log(GOOD_SCRIPT)
        assert ok is True
        assert issues == []

    def test_output_missing(self) -> None:
        ok, issues = check_output_log(NO_OUTPUT)
        assert ok is False
        assert len(issues) == 1
        assert "--output" in issues[0]

    def test_short_form(self) -> None:
        """短形式 -o でも出力先として認識される."""
        ok, issues = check_output_log(SHORT_FORM_SCRIPT)
        assert ok is True
        assert issues == []


# --- check_time_limit ---

class TestCheckTimeLimit:
    """制限時間指定の検証テスト."""

    def test_time_present(self) -> None:
        ok, issues = check_time_limit(GOOD_SCRIPT)
        assert ok is True
        assert issues == []

    def test_time_missing(self) -> None:
        ok, issues = check_time_limit(NO_TIME)
        assert ok is False
        assert len(issues) == 1
        assert "--time" in issues[0]

    def test_short_form(self) -> None:
        """短形式 -t でも制限時間として認識される."""
        ok, issues = check_time_limit(SHORT_FORM_SCRIPT)
        assert ok is True
        assert issues == []


# --- check_memory_request ---

class TestCheckMemoryRequest:
    """メモリ申請指定の検証テスト."""

    def test_mem_present(self) -> None:
        ok, issues = check_memory_request(GOOD_SCRIPT)
        assert ok is True
        assert issues == []

    def test_mem_missing(self) -> None:
        ok, issues = check_memory_request(NO_MEMORY)
        assert ok is False
        assert len(issues) == 1
        assert "--mem" in issues[0]

    def test_mem_per_cpu(self) -> None:
        """--mem-per-cpu でもメモリ指定として認識される."""
        ok, issues = check_memory_request(MEM_PER_CPU_SCRIPT)
        assert ok is True
        assert issues == []


# --- check_gpu_cpu_balance ---

class TestCheckGpuCpuBalance:
    """GPU/CPUバランスの検証テスト."""

    def test_good_gpu_balance(self) -> None:
        ok, warnings, info = check_gpu_cpu_balance(GPU_GOOD_SCRIPT)
        assert ok is True
        assert warnings == []

    def test_low_cpu_for_gpu(self) -> None:
        ok, warnings, info = check_gpu_cpu_balance(GPU_LOW_CPU_SCRIPT)
        assert ok is False
        assert len(warnings) == 1
        assert "CPU" in warnings[0]

    def test_no_cpu_specified_with_gpu(self) -> None:
        """GPU使用時にCPU未指定なら情報提供."""
        ok, warnings, info = check_gpu_cpu_balance(GPU_NO_CPU_SCRIPT)
        assert ok is True
        assert any("--cpus-per-task" in i for i in info)

    def test_no_partition_with_gpu(self) -> None:
        """GPU使用時にパーティション未指定なら情報提供."""
        ok, warnings, info = check_gpu_cpu_balance(GPU_NO_PARTITION_SCRIPT)
        assert ok is True
        assert any("--partition" in i for i in info)

    def test_no_gpu(self) -> None:
        """GPUを使っていなければチェック対象外."""
        ok, warnings, info = check_gpu_cpu_balance(GOOD_SCRIPT)
        assert ok is True
        assert warnings == []
        assert info == []

    def test_typed_gpu(self) -> None:
        """gpu:a100:2 のような型指定付きGPUもパースできる."""
        ok, warnings, info = check_gpu_cpu_balance(GPU_TYPED_SCRIPT)
        assert ok is True
        assert warnings == []


# --- validate ---

class TestValidate:
    """一括検証のテスト."""

    def test_good_script(self) -> None:
        result = validate(GOOD_SCRIPT)
        assert result.ok is True
        assert len(result.passed) >= 4
        assert result.warnings == []

    def test_missing_all(self) -> None:
        result = validate(EMPTY_SCRIPT)
        assert result.ok is False
        assert len(result.warnings) >= 4

    def test_no_job_name_warning(self) -> None:
        result = validate(NO_JOB_NAME)
        assert any("--job-name" in w for w in result.warnings)

    def test_no_output_warning(self) -> None:
        result = validate(NO_OUTPUT)
        assert any("--output" in w for w in result.warnings)

    def test_no_time_warning(self) -> None:
        result = validate(NO_TIME)
        assert any("--time" in w for w in result.warnings)

    def test_no_memory_warning(self) -> None:
        result = validate(NO_MEMORY)
        assert any("--mem" in w for w in result.warnings)

    def test_gpu_good(self) -> None:
        result = validate(GPU_GOOD_SCRIPT)
        assert result.ok is True
        assert any("GPU" in p for p in result.passed)

    def test_gpu_low_cpu_warning(self) -> None:
        result = validate(GPU_LOW_CPU_SCRIPT)
        assert result.ok is False
        assert any("CPU" in w for w in result.warnings)

    def test_gpu_info_messages(self) -> None:
        result = validate(GPU_NO_CPU_SCRIPT)
        assert len(result.info) >= 1

    def test_minimal_valid(self) -> None:
        result = validate(MINIMAL_SCRIPT)
        assert result.ok is True
        assert len(result.passed) >= 4


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
