"""seqtool filterの出力先とTTY分岐のテスト."""

import sys
from collections.abc import Iterable
from pathlib import Path
from types import ModuleType

import pytest
from click.testing import CliRunner, _NamedTextIOWrapper

from scripts.ch11.seqtool import cli

FASTA_DATA = """\
>high_gc
GCGCGCGCGC
>low_gc
ATATATATAT
"""


def _input_file(tmp_path: Path) -> Path:
    """テスト用FASTAファイルを作成する."""
    path = tmp_path / "input.fasta"
    path.write_text(FASTA_DATA, encoding="utf-8")
    return path


def test_filter_separates_stdout_and_stderr(tmp_path: Path) -> None:
    """FASTA結果はstdout、ステータスはstderrへ出力する."""
    result = CliRunner().invoke(
        cli,
        [
            "filter",
            str(_input_file(tmp_path)),
            "--min-gc",
            "0.6",
            "--no-progress",
        ],
    )

    assert result.exit_code == 0
    assert ">high_gc" in result.stdout
    assert "フィルタ結果" not in result.stdout
    assert "フィルタ結果: 2 配列中 1 配列を出力" in result.stderr
    assert ">high_gc" not in result.stderr


def test_filter_hides_progress_when_stderr_is_not_tty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """stderrがTTYでなければ既定有効のtqdmを呼び出さない."""

    def fail_tqdm(*args: object, **kwargs: object) -> None:
        raise AssertionError("非TTYでtqdmが呼び出された")

    fake_tqdm = ModuleType("tqdm")
    setattr(fake_tqdm, "tqdm", fail_tqdm)
    monkeypatch.setitem(sys.modules, "tqdm", fake_tqdm)

    result = CliRunner().invoke(
        cli,
        ["filter", str(_input_file(tmp_path)), "--min-gc", "0.6"],
    )

    assert result.exit_code == 0
    assert ">high_gc" in result.stdout


def test_filter_sends_progress_to_stderr_when_tty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """stderrがTTYならtqdmをstderrに接続する."""
    descriptions: list[str] = []

    def isatty(_: _NamedTextIOWrapper) -> bool:
        return True

    def fake_tqdm(
        records: Iterable[object],
        *,
        desc: str,
        file: object,
    ) -> Iterable[object]:
        assert file is sys.stderr
        descriptions.append(desc)
        return records

    fake_tqdm_module = ModuleType("tqdm")
    setattr(fake_tqdm_module, "tqdm", fake_tqdm)
    monkeypatch.setitem(sys.modules, "tqdm", fake_tqdm_module)
    monkeypatch.setattr(_NamedTextIOWrapper, "isatty", isatty)

    result = CliRunner().invoke(
        cli,
        ["filter", str(_input_file(tmp_path)), "--min-gc", "0.6"],
    )

    assert result.exit_code == 0
    assert descriptions == ["フィルタリング"]
