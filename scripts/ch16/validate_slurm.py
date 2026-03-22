"""SLURMジョブスクリプトのベストプラクティス準拠をチェックするバリデータ."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """バリデーション結果を格納する.

    Attributes
    ----------
    passed : list[str]
        合格したチェック項目
    warnings : list[str]
        警告事項
    info : list[str]
        推奨事項（警告より軽い情報提供）
    """

    passed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """警告がなければTrue."""
        return len(self.warnings) == 0


def _extract_sbatch_directives(text: str) -> dict[str, str]:
    """SLURMスクリプトから#SBATCHディレクティブを抽出する.

    Parameters
    ----------
    text : str
        SLURMジョブスクリプトのテキスト内容

    Returns
    -------
    dict[str, str]
        ディレクティブ名（長形式）をキー、値を値とする辞書
    """
    # 短形式オプションから長形式への変換マップ
    short_to_long: dict[str, str] = {
        "-J": "--job-name",
        "-o": "--output",
        "-e": "--error",
        "-t": "--time",
        "-p": "--partition",
        "-n": "--ntasks",
        "-c": "--cpus-per-task",
        "-N": "--nodes",
    }

    directives: dict[str, str] = {}
    for match in re.finditer(
        r"^#SBATCH\s+(--?\S+?)(?:=|\s+)(\S+)",
        text,
        re.MULTILINE,
    ):
        key = match.group(1)
        value = match.group(2)
        # 短形式を長形式に正規化
        key = short_to_long.get(key, key)
        directives[key] = value

    # 値なしのフラグ形式も拾う（例: #SBATCH --exclusive）
    for match in re.finditer(
        r"^#SBATCH\s+(--\S+)\s*$",
        text,
        re.MULTILINE,
    ):
        key = match.group(1)
        if key not in directives:
            directives[key] = ""

    return directives


def check_job_name(text: str) -> tuple[bool, list[str]]:
    """ジョブ名の指定を検証する.

    Parameters
    ----------
    text : str
        SLURMジョブスクリプトのテキスト内容

    Returns
    -------
    tuple[bool, list[str]]
        (ジョブ名が指定されているか, 問題の説明リスト)
    """
    directives = _extract_sbatch_directives(text)
    issues: list[str] = []

    if "--job-name" not in directives:
        issues.append(
            "--job-name が未指定 — "
            "squeueやsacctでジョブを識別しやすくするために名前を付ける"
        )

    return len(issues) == 0, issues


def check_output_log(text: str) -> tuple[bool, list[str]]:
    """ログ出力先の指定を検証する.

    Parameters
    ----------
    text : str
        SLURMジョブスクリプトのテキスト内容

    Returns
    -------
    tuple[bool, list[str]]
        (ログ出力先が指定されているか, 問題の説明リスト)
    """
    directives = _extract_sbatch_directives(text)
    issues: list[str] = []

    if "--output" not in directives:
        issues.append(
            "--output が未指定 — "
            "ログファイルの出力先を明示する（例: logs/%j.out）"
        )

    return len(issues) == 0, issues


def check_time_limit(text: str) -> tuple[bool, list[str]]:
    """制限時間の指定を検証する.

    Parameters
    ----------
    text : str
        SLURMジョブスクリプトのテキスト内容

    Returns
    -------
    tuple[bool, list[str]]
        (制限時間が指定されているか, 問題の説明リスト)
    """
    directives = _extract_sbatch_directives(text)
    issues: list[str] = []

    if "--time" not in directives:
        issues.append(
            "--time が未指定 — "
            "制限時間がないとデフォルト値が適用され、"
            "ジョブが途中で打ち切られる可能性がある"
        )

    return len(issues) == 0, issues


def check_memory_request(text: str) -> tuple[bool, list[str]]:
    """メモリ申請の指定を検証する.

    Parameters
    ----------
    text : str
        SLURMジョブスクリプトのテキスト内容

    Returns
    -------
    tuple[bool, list[str]]
        (メモリが指定されているか, 問題の説明リスト)
    """
    directives = _extract_sbatch_directives(text)
    issues: list[str] = []

    has_mem = "--mem" in directives or "--mem-per-cpu" in directives
    if not has_mem:
        issues.append(
            "--mem または --mem-per-cpu が未指定 — "
            "メモリ上限がないとOOMキラーにジョブが強制終了される可能性がある"
        )

    return len(issues) == 0, issues


def check_gpu_cpu_balance(text: str) -> tuple[bool, list[str], list[str]]:
    """GPU申請時のCPUバランスを検証する.

    GPUを申請している場合に、CPUが十分に確保されているか、
    またパーティション指定があるかをチェックする。

    Parameters
    ----------
    text : str
        SLURMジョブスクリプトのテキスト内容

    Returns
    -------
    tuple[bool, list[str], list[str]]
        (バランスが適切か, 警告リスト, 情報リスト)
    """
    directives = _extract_sbatch_directives(text)
    warnings: list[str] = []
    info: list[str] = []

    # --gres=gpu:N の検出
    gres = directives.get("--gres", "")
    gpu_match = re.match(r"gpu(?::[\w]+)?:(\d+)", gres)
    if not gpu_match:
        # GPUを使っていなければチェック対象外
        return True, [], []

    n_gpu = int(gpu_match.group(1))

    # CPUとのバランスチェック
    cpus_str = directives.get("--cpus-per-task", "")
    if cpus_str and cpus_str.isdigit():
        n_cpus = int(cpus_str)
        if n_cpus < 2 * n_gpu:
            warnings.append(
                f"GPU {n_gpu}基に対してCPU {n_cpus}コアは少ない — "
                "データローディングがボトルネックになりやすい"
                "（目安: GPU 1基あたり4〜8 CPU）"
            )
    else:
        info.append(
            "GPU使用時は --cpus-per-task を明示すると"
            "データローディングの並列度を制御できる"
        )

    # パーティション指定の確認
    if "--partition" not in directives:
        info.append(
            "GPU使用時は --partition でGPUパーティションを"
            "明示するとスケジューリングが確実になる"
        )

    return len(warnings) == 0, warnings, info


def validate(text: str) -> ValidationResult:
    """SLURMジョブスクリプトに対してベストプラクティスを一括検証する.

    Parameters
    ----------
    text : str
        SLURMジョブスクリプトのテキスト内容

    Returns
    -------
    ValidationResult
        検証結果
    """
    result = ValidationResult()

    # 1. ジョブ名チェック
    name_ok, name_issues = check_job_name(text)
    if name_ok:
        result.passed.append("ジョブ名が指定されている")
    else:
        result.warnings.extend(name_issues)

    # 2. ログ出力先チェック
    log_ok, log_issues = check_output_log(text)
    if log_ok:
        result.passed.append("ログ出力先が指定されている")
    else:
        result.warnings.extend(log_issues)

    # 3. 制限時間チェック
    time_ok, time_issues = check_time_limit(text)
    if time_ok:
        result.passed.append("制限時間が指定されている")
    else:
        result.warnings.extend(time_issues)

    # 4. メモリ申請チェック
    mem_ok, mem_issues = check_memory_request(text)
    if mem_ok:
        result.passed.append("メモリ申請が指定されている")
    else:
        result.warnings.extend(mem_issues)

    # 5. GPU/CPUバランスチェック
    gpu_ok, gpu_warnings, gpu_info = check_gpu_cpu_balance(text)
    if gpu_ok:
        # GPUを使っている場合のみ「合格」メッセージを追加
        gres = _extract_sbatch_directives(text).get("--gres", "")
        if "gpu" in gres:
            result.passed.append("GPU/CPUのバランスが適切である")
    else:
        result.warnings.extend(gpu_warnings)
    result.info.extend(gpu_info)

    return result
