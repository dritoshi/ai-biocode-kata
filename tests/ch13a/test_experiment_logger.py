"""experiment_loggerモジュールのテスト."""

import json
from pathlib import Path

import pytest

from scripts.ch13a.experiment_logger import (
    ExperimentRecord,
    find_best,
    load_experiments,
    log_experiment,
)


# --- log_experiment ---


class TestLogExperiment:
    """実験ログ書き込みのテスト."""

    def test_creates_log_file(self, tmp_path: Path) -> None:
        log_experiment(
            params={"lr": 0.01},
            metrics={"accuracy": 0.95},
            output_dir=tmp_path,
        )
        log_file = tmp_path / "experiment_log.jsonl"
        assert log_file.exists()

    def test_jsonl_format(self, tmp_path: Path) -> None:
        log_experiment(
            params={"n_neighbors": 15},
            metrics={"silhouette": 0.72},
            output_dir=tmp_path,
        )
        log_file = tmp_path / "experiment_log.jsonl"
        lines = log_file.read_text().strip().splitlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["params"]["n_neighbors"] == 15
        assert data["metrics"]["silhouette"] == 0.72

    def test_appends_multiple_records(self, tmp_path: Path) -> None:
        log_experiment(params={"lr": 0.01}, metrics={"loss": 0.5}, output_dir=tmp_path)
        log_experiment(params={"lr": 0.001}, metrics={"loss": 0.3}, output_dir=tmp_path)
        log_file = tmp_path / "experiment_log.jsonl"
        lines = log_file.read_text().strip().splitlines()
        assert len(lines) == 2

    def test_returns_record(self, tmp_path: Path) -> None:
        record = log_experiment(
            params={"epochs": 10},
            metrics={"f1": 0.88},
            output_dir=tmp_path,
        )
        assert isinstance(record, ExperimentRecord)
        assert record.params["epochs"] == 10
        assert record.metrics["f1"] == 0.88

    def test_has_timestamp(self, tmp_path: Path) -> None:
        record = log_experiment(
            params={}, metrics={}, output_dir=tmp_path,
        )
        assert len(record.timestamp) > 0

    def test_has_git_hash(self, tmp_path: Path) -> None:
        record = log_experiment(
            params={}, metrics={}, output_dir=tmp_path,
        )
        # gitリポジトリ内で実行されていればハッシュ文字列、そうでなければ"unknown"
        assert isinstance(record.git_hash, str)
        assert len(record.git_hash) > 0

    def test_custom_filename(self, tmp_path: Path) -> None:
        log_experiment(
            params={}, metrics={},
            output_dir=tmp_path,
            log_filename="custom.jsonl",
        )
        assert (tmp_path / "custom.jsonl").exists()


# --- load_experiments ---


class TestLoadExperiments:
    """実験ログ読み込みのテスト."""

    def test_load_written_records(self, tmp_path: Path) -> None:
        log_experiment(params={"a": 1}, metrics={"m": 0.5}, output_dir=tmp_path)
        log_experiment(params={"a": 2}, metrics={"m": 0.7}, output_dir=tmp_path)
        records = load_experiments(tmp_path / "experiment_log.jsonl")
        assert len(records) == 2
        assert records[0].params["a"] == 1
        assert records[1].metrics["m"] == 0.7

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        records = load_experiments(tmp_path / "nonexistent.jsonl")
        assert records == []

    def test_empty_file(self, tmp_path: Path) -> None:
        (tmp_path / "empty.jsonl").write_text("")
        records = load_experiments(tmp_path / "empty.jsonl")
        assert records == []

    def test_record_types(self, tmp_path: Path) -> None:
        log_experiment(params={"x": 1}, metrics={"y": 2.0}, output_dir=tmp_path)
        records = load_experiments(tmp_path / "experiment_log.jsonl")
        assert isinstance(records[0], ExperimentRecord)


# --- find_best ---


class TestFindBest:
    """最良実験検索のテスト."""

    def _make_records(self) -> list[ExperimentRecord]:
        return [
            ExperimentRecord(
                timestamp="2026-01-01T00:00:00",
                git_hash="aaa",
                params={"lr": 0.01},
                metrics={"accuracy": 0.90, "loss": 0.4},
            ),
            ExperimentRecord(
                timestamp="2026-01-02T00:00:00",
                git_hash="bbb",
                params={"lr": 0.001},
                metrics={"accuracy": 0.95, "loss": 0.2},
            ),
            ExperimentRecord(
                timestamp="2026-01-03T00:00:00",
                git_hash="ccc",
                params={"lr": 0.1},
                metrics={"accuracy": 0.85, "loss": 0.6},
            ),
        ]

    def test_maximize(self) -> None:
        best = find_best(self._make_records(), "accuracy", maximize=True)
        assert best is not None
        assert best.metrics["accuracy"] == 0.95

    def test_minimize(self) -> None:
        best = find_best(self._make_records(), "loss", maximize=False)
        assert best is not None
        assert best.metrics["loss"] == 0.2

    def test_missing_metric(self) -> None:
        best = find_best(self._make_records(), "nonexistent")
        assert best is None

    def test_empty_list(self) -> None:
        best = find_best([], "accuracy")
        assert best is None


# --- ExperimentRecord ---


class TestExperimentRecord:
    """ExperimentRecordのテスト."""

    def test_default_fields(self) -> None:
        r = ExperimentRecord(timestamp="now", git_hash="abc")
        assert r.params == {}
        assert r.metrics == {}

    def test_with_data(self) -> None:
        r = ExperimentRecord(
            timestamp="now",
            git_hash="abc",
            params={"lr": 0.01},
            metrics={"acc": 0.9},
        )
        assert r.params["lr"] == 0.01
        assert r.metrics["acc"] == 0.9
