"""config_layering モジュールのテスト."""

from pathlib import Path

import pytest

from scripts.ch11.config_layering import load_config, resolve_config


def _write_config(path: Path, content: str) -> Path:
    """YAML設定を書き出す."""
    path.write_text(content, encoding="utf-8")
    return path


def test_defaults() -> None:
    """設定指定なしではデフォルト値を返す."""
    assert load_config() == {
        "min_gc": 0.0,
        "max_gc": 1.0,
        "format": "fasta",
    }


def test_yaml_overrides_defaults(tmp_path: Path) -> None:
    """YAML値がデフォルト値を上書きする."""
    path = _write_config(
        tmp_path / "config.yaml",
        "min_gc: 0.3\nformat: tab\n",
    )

    assert load_config(path) == {
        "min_gc": 0.3,
        "max_gc": 1.0,
        "format": "tab",
    }


def test_cli_overrides_yaml(tmp_path: Path) -> None:
    """明示されたCLI値がYAML値を上書きする."""
    path = _write_config(
        tmp_path / "config.yaml",
        "min_gc: 0.3\nmax_gc: 0.8\nformat: tab\n",
    )

    assert resolve_config(
        path,
        min_gc=0.5,
        output_format="fasta",
    ) == {
        "min_gc": 0.5,
        "max_gc": 0.8,
        "format": "fasta",
    }


def test_missing_file() -> None:
    """存在しない設定ファイルは拒否する."""
    with pytest.raises(FileNotFoundError, match="見つかりません"):
        load_config(Path("missing-config.yaml"))


def test_malformed_yaml(tmp_path: Path) -> None:
    """構文が壊れたYAMLは拒否する."""
    path = _write_config(tmp_path / "broken.yaml", "min_gc: [0.3\n")

    with pytest.raises(ValueError, match="YAML設定を読み込めません"):
        load_config(path)


def test_unknown_key(tmp_path: Path) -> None:
    """未知の設定項目は入力ミスとして拒否する."""
    path = _write_config(tmp_path / "unknown.yaml", "minimum_gc: 0.3\n")

    with pytest.raises(ValueError, match="未知の設定項目"):
        load_config(path)


def test_invalid_range(tmp_path: Path) -> None:
    """GC含量の逆転した範囲は拒否する."""
    path = _write_config(
        tmp_path / "invalid.yaml",
        "min_gc: 0.8\nmax_gc: 0.3\n",
    )

    with pytest.raises(ValueError, match="min_gc <= max_gc"):
        load_config(path)
