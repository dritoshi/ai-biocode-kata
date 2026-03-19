"""config_example モジュールのテスト."""

from pathlib import Path

from scripts.ch08.config_example import load_config


def test_load_config_defaults(tmp_path: Path) -> None:
    """設定ファイルが存在しない場合、デフォルト値を返す."""
    config = load_config(tmp_path / "nonexistent.yaml")
    assert config["filtering"]["min_qual"] == 20
    assert config["filtering"]["min_depth"] == 5
    assert config["output"]["directory"] == "results"


def test_load_config_override(tmp_path: Path) -> None:
    """ユーザー設定がデフォルトを上書きする."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "filtering:\n  min_qual: 30\n  min_depth: 10\n"
    )
    config = load_config(config_file)
    assert config["filtering"]["min_qual"] == 30
    assert config["filtering"]["min_depth"] == 10
    # 上書きされていないパラメータはデフォルト値のまま
    assert config["filtering"]["max_missing_rate"] == 0.2


def test_load_config_partial(tmp_path: Path) -> None:
    """一部のセクションだけ指定した場合、残りはデフォルト値."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("output:\n  format: tsv\n")
    config = load_config(config_file)
    assert config["output"]["format"] == "tsv"
    assert config["output"]["directory"] == "results"
    assert config["filtering"]["min_qual"] == 20


def test_load_config_empty_file(tmp_path: Path) -> None:
    """空の設定ファイルの場合、デフォルト値を返す."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("")
    config = load_config(config_file)
    assert config["filtering"]["min_qual"] == 20
    assert config["output"]["format"] == "vcf"


def test_load_config_new_section(tmp_path: Path) -> None:
    """デフォルトにないセクションが追加される."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("logging:\n  level: DEBUG\n")
    config = load_config(config_file)
    assert config["logging"]["level"] == "DEBUG"
    # デフォルトセクションも維持される
    assert config["filtering"]["min_qual"] == 20
