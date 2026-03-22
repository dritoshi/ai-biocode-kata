"""実行環境を自動収集し、質問テンプレートをMarkdown生成するモジュール.

Biostars や GitHub Issue に質問・バグ報告を投稿する際、
再現に必要な環境情報を自動収集してテンプレートに埋め込む。
"""

from __future__ import annotations

import logging
import platform
import sys
from importlib.metadata import PackageNotFoundError, version

logger = logging.getLogger(__name__)

# 環境情報として収集する主要パッケージ
_TARGET_PACKAGES: list[str] = [
    "numpy",
    "pandas",
    "biopython",
    "matplotlib",
    "scipy",
    "scikit-learn",
]


def collect_environment() -> dict[str, str]:
    """Python版、OS、主要パッケージのバージョンを収集する.

    Returns
    -------
    dict[str, str]
        ``python_version``, ``os_info`` をキーとして含む辞書。
        各パッケージはパッケージ名をキー、バージョン文字列を値とする。
        インストールされていないパッケージは ``"not installed"``。
    """
    env: dict[str, str] = {
        "python_version": sys.version,
        "os_info": f"{platform.system()} {platform.release()}",
    }

    for pkg in _TARGET_PACKAGES:
        try:
            env[pkg] = version(pkg)
        except PackageNotFoundError:
            env[pkg] = "not installed"
            logger.debug("パッケージ未インストール: %s", pkg)

    return env


def format_biostars_question(
    title: str,
    body: str,
    error_trace: str,
    env: dict[str, str],
) -> str:
    """Biostars向けMarkdownテンプレートを生成する.

    Parameters
    ----------
    title : str
        質問タイトル。
    body : str
        質問本文。
    error_trace : str
        エラーのトレースバック。
    env : dict[str, str]
        :func:`collect_environment` の返り値。

    Returns
    -------
    str
        Markdown形式の質問テンプレート。
    """
    # 環境情報を整形
    env_lines = "\n".join(f"- **{key}**: {value}" for key, value in env.items())

    template = f"""\
# {title}

## 質問内容

{body}

## エラーメッセージ

```
{error_trace}
```

## 実行環境

{env_lines}

## 試したこと

<!-- ここに試した解決策を記載してください -->
"""
    return template


def format_github_issue(
    title: str,
    description: str,
    steps_to_reproduce: list[str],
    expected: str,
    actual: str,
    env: dict[str, str],
) -> str:
    """GitHub Issue向けバグレポートテンプレートを生成する.

    Parameters
    ----------
    title : str
        Issueタイトル。
    description : str
        バグの概要説明。
    steps_to_reproduce : list[str]
        再現手順のリスト。
    expected : str
        期待される動作。
    actual : str
        実際の動作。
    env : dict[str, str]
        :func:`collect_environment` の返り値。

    Returns
    -------
    str
        Markdown形式のバグレポートテンプレート。
    """
    # 再現手順を番号付きリストに整形
    steps_text = "\n".join(
        f"{i}. {step}" for i, step in enumerate(steps_to_reproduce, start=1)
    )

    # 環境情報を整形
    env_lines = "\n".join(f"- **{key}**: {value}" for key, value in env.items())

    template = f"""\
# {title}

## 概要

{description}

## 再現手順

{steps_text}

## 期待される動作

{expected}

## 実際の動作

{actual}

## 実行環境

{env_lines}
"""
    return template
