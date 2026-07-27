"""CLI引数・YAML設定・デフォルト値を優先順位どおりに合成する."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, cast

import yaml


class FilterConfig(TypedDict):
    """GCフィルタの設定値."""

    min_gc: float
    max_gc: float
    format: str


DEFAULT_CONFIG: FilterConfig = {
    "min_gc": 0.0,
    "max_gc": 1.0,
    "format": "fasta",
}


def _validate_config(config: dict[str, object]) -> FilterConfig:
    """設定値の型と範囲を検証する."""
    min_gc = config.get("min_gc")
    max_gc = config.get("max_gc")
    output_format = config.get("format")

    if (
        isinstance(min_gc, bool)
        or not isinstance(min_gc, (int, float))
        or isinstance(max_gc, bool)
        or not isinstance(max_gc, (int, float))
    ):
        raise ValueError("min_gcとmax_gcは数値で指定してください")

    min_gc_float = float(min_gc)
    max_gc_float = float(max_gc)
    if not 0.0 <= min_gc_float <= max_gc_float <= 1.0:
        raise ValueError("GC含量は0.0以上1.0以下で、min_gc <= max_gcにしてください")

    if output_format not in {"fasta", "tab"}:
        raise ValueError("formatはfastaまたはtabを指定してください")

    return {
        "min_gc": min_gc_float,
        "max_gc": max_gc_float,
        "format": cast(str, output_format),
    }


def load_config(config_path: Path | None = None) -> FilterConfig:
    """デフォルト値へYAML設定を重ねて返す."""
    config: dict[str, object] = dict(DEFAULT_CONFIG)
    if config_path is None:
        return _validate_config(config)
    if not config_path.is_file():
        raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")

    try:
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML設定を読み込めません: {config_path}") from exc

    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        raise ValueError("YAML設定の最上位はマッピングにしてください")

    unknown = set(loaded) - set(DEFAULT_CONFIG)
    if unknown:
        names = ", ".join(sorted(str(name) for name in unknown))
        raise ValueError(f"未知の設定項目です: {names}")

    config.update(loaded)
    return _validate_config(config)


def resolve_config(
    config_path: Path | None = None,
    *,
    min_gc: float | None = None,
    max_gc: float | None = None,
    output_format: str | None = None,
) -> FilterConfig:
    """YAML設定へ明示されたCLI値を上書きして返す."""
    config: dict[str, object] = dict(load_config(config_path))
    if min_gc is not None:
        config["min_gc"] = min_gc
    if max_gc is not None:
        config["max_gc"] = max_gc
    if output_format is not None:
        config["format"] = output_format
    return _validate_config(config)
