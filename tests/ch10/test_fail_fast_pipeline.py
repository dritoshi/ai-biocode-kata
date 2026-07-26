"""fail-fastパイプラインのテスト."""

from pathlib import Path

import pytest

from scripts.ch10.fail_fast_pipeline import run_pipeline


def _config(tmp_path: Path) -> dict[str, str]:
    return {
        "input": str(tmp_path / "input.fastq"),
        "reference": str(tmp_path / "reference.fasta"),
        "output_dir": str(tmp_path / "results"),
    }


def test_rejects_missing_input_before_creating_output(tmp_path: Path) -> None:
    config = _config(tmp_path)

    with pytest.raises(FileNotFoundError, match="入力ファイル"):
        run_pipeline(config)

    assert not Path(config["output_dir"]).exists()


def test_rejects_missing_reference_before_creating_output(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    Path(config["input"]).write_text("@read\nACGT\n+\n!!!!\n", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="リファレンス"):
        run_pipeline(config)

    assert not Path(config["output_dir"]).exists()


def test_creates_output_after_inputs_are_valid(tmp_path: Path) -> None:
    config = _config(tmp_path)
    Path(config["input"]).write_text("@read\nACGT\n+\n!!!!\n", encoding="utf-8")
    Path(config["reference"]).write_text(">ref\nACGT\n", encoding="utf-8")

    run_pipeline(config)

    assert Path(config["output_dir"]).is_dir()
