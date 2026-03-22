"""設定管理の例 — YAML設定ファイルの読み込みとデフォルト値のマージ."""

from pathlib import Path
from typing import Any

import yaml


def load_config(config_path: Path) -> dict[str, Any]:
    """YAML設定ファイルを読み込み、デフォルト値とマージする.

    Parameters
    ----------
    config_path : Path
        設定ファイルのパス

    Returns
    -------
    dict[str, Any]
        マージ済みの設定辞書
    """
    defaults: dict[str, Any] = {
        "filtering": {
            "min_qual": 20,
            "min_depth": 5,
            "max_missing_rate": 0.2,
        },
        "output": {
            "directory": "results",
            "format": "vcf",
        },
    }

    if config_path.exists():
        with open(config_path) as f:
            user_config = yaml.safe_load(f) or {}
        # ユーザー設定でデフォルトを上書き
        for section, values in user_config.items():
            if section in defaults and isinstance(values, dict):
                defaults[section].update(values)
            else:
                defaults[section] = values

    return defaults
