"""最小限の実験ログ記録ツール.

ML専用ツール（wandb, MLflow等）を導入する前に使える、
JSONL形式の実験ログ記録・読み込み・検索ユーティリティ。
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class ExperimentRecord:
    """1回の実験を記録するデータクラス.

    Attributes
    ----------
    timestamp : str
        実験の実行日時（ISO 8601形式）
    git_hash : str
        実験時のgitコミットハッシュ
    params : dict
        ハイパーパラメータ（入力条件）
    metrics : dict
        メトリクス（結果の評価値）
    """

    timestamp: str
    git_hash: str
    params: dict[str, object] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)


def _get_git_hash() -> str:
    """現在のgitコミットハッシュを取得する."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return "unknown"


def log_experiment(
    params: dict[str, object],
    metrics: dict[str, float],
    output_dir: str | Path,
    log_filename: str = "experiment_log.jsonl",
) -> ExperimentRecord:
    """実験のパラメータとメトリクスをJSONL形式で記録する.

    Parameters
    ----------
    params : dict[str, object]
        ハイパーパラメータ
    metrics : dict[str, float]
        メトリクス
    output_dir : str | Path
        ログファイルの出力先ディレクトリ
    log_filename : str
        ログファイル名（デフォルト: experiment_log.jsonl）

    Returns
    -------
    ExperimentRecord
        記録された実験レコード
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    record = ExperimentRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        git_hash=_get_git_hash(),
        params=params,
        metrics=metrics,
    )

    log_path = output_path / log_filename
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")

    return record


def load_experiments(
    log_path: str | Path,
) -> list[ExperimentRecord]:
    """JSONL形式の実験ログを読み込む.

    Parameters
    ----------
    log_path : str | Path
        ログファイルのパス

    Returns
    -------
    list[ExperimentRecord]
        実験レコードのリスト
    """
    path = Path(log_path)
    if not path.exists():
        return []

    records: list[ExperimentRecord] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            records.append(
                ExperimentRecord(
                    timestamp=data["timestamp"],
                    git_hash=data["git_hash"],
                    params=data.get("params", {}),
                    metrics=data.get("metrics", {}),
                )
            )
    return records


def find_best(
    experiments: list[ExperimentRecord],
    metric_name: str,
    maximize: bool = True,
) -> ExperimentRecord | None:
    """指定メトリクスが最良の実験を返す.

    Parameters
    ----------
    experiments : list[ExperimentRecord]
        実験レコードのリスト
    metric_name : str
        比較するメトリクス名
    maximize : bool
        Trueなら最大値、Falseなら最小値を最良とする

    Returns
    -------
    ExperimentRecord | None
        最良の実験。対象メトリクスを持つ実験がなければNone
    """
    candidates = [e for e in experiments if metric_name in e.metrics]
    if not candidates:
        return None

    if maximize:
        return max(candidates, key=lambda e: e.metrics[metric_name])
    return min(candidates, key=lambda e: e.metrics[metric_name])
