"""validate_readmeモジュールのテスト."""

import pytest

from scripts.ch17.validate_readme import (
    ValidationResult,
    check_empty_sections,
    check_required_sections,
    check_research_readme,
    validate,
)

# --- テスト用READMEテキスト ---

GOOD_README = """\
# MyTool

## 概要

配列データを処理するPythonツール。

## インストール

```bash
pip install mytool
```

## 使い方

```bash
mytool run --input data.fasta
```

## ライセンス

MIT License
"""

BAD_README_MISSING = """\
# MyTool

## 概要

配列データを処理するPythonツール。

## インストール

```bash
pip install mytool
```
"""

EMPTY_SECTION_README = """\
# MyTool

## 概要

## インストール

```bash
pip install mytool
```

## 使い方

```bash
mytool run --input data.fasta
```

## ライセンス

MIT License
"""

RESEARCH_README = """\
# RNA-seq解析パイプライン

## 目的

論文「XXX」（DOI: 10.1234/example）の解析を再現するためのコード。

## 依存関係

- Python 3.11
- Snakemake 8.0

## 実行手順

```bash
snakemake --cores 4
```

## データの入手方法

GEO: GSE123456

## 引用方法

CITATION.cffを参照。

## ライセンス

MIT License
"""

BAD_RESEARCH_README = """\
# RNA-seq解析パイプライン

## 目的

論文の解析コード。

## ライセンス

MIT License
"""

NO_H1_README = """\
## 概要

ツールの説明。

## インストール

pip install mytool

## 使い方

mytool run

## ライセンス

MIT
"""


# --- check_required_sections ---

class TestCheckRequiredSections:
    """汎用READMEの必須セクション検証テスト."""

    def test_all_present(self) -> None:
        ok, missing = check_required_sections(GOOD_README)
        assert ok is True
        assert missing == []

    def test_missing_sections(self) -> None:
        ok, missing = check_required_sections(BAD_README_MISSING)
        assert ok is False
        assert "使い方" in missing
        assert "ライセンス" in missing

    def test_partial_missing(self) -> None:
        """概要とインストールはあるが使い方とライセンスがない."""
        ok, missing = check_required_sections(BAD_README_MISSING)
        assert "概要" not in missing
        assert "インストール" not in missing


# --- check_empty_sections ---

class TestCheckEmptySections:
    """空セクション検出テスト."""

    def test_no_empty(self) -> None:
        ok, empty = check_empty_sections(GOOD_README)
        assert ok is True
        assert empty == []

    def test_empty_section(self) -> None:
        ok, empty = check_empty_sections(EMPTY_SECTION_README)
        assert ok is False
        assert "概要" in empty

    def test_only_nonempty(self) -> None:
        """空でないセクションは報告しない."""
        ok, empty = check_empty_sections(EMPTY_SECTION_README)
        assert "インストール" not in empty
        assert "使い方" not in empty


# --- check_research_readme ---

class TestCheckResearchReadme:
    """研究リポジトリ向けREADME検証テスト."""

    def test_all_present(self) -> None:
        ok, missing = check_research_readme(RESEARCH_README)
        assert ok is True
        assert missing == []

    def test_missing_research_sections(self) -> None:
        ok, missing = check_research_readme(BAD_RESEARCH_README)
        assert ok is False
        assert "依存関係" in missing
        assert "実行手順" in missing
        assert "データ" in missing
        assert "引用" in missing


# --- validate ---

class TestValidate:
    """一括検証のテスト."""

    def test_good_readme(self) -> None:
        result = validate(GOOD_README)
        assert result.ok is True
        assert len(result.passed) >= 2
        assert result.warnings == []

    def test_missing_sections_warning(self) -> None:
        result = validate(BAD_README_MISSING)
        assert result.ok is False
        assert any("必須セクション" in w for w in result.warnings)

    def test_empty_section_warning(self) -> None:
        result = validate(EMPTY_SECTION_README)
        assert result.ok is False
        assert any("空のセクション" in w for w in result.warnings)

    def test_research_mode(self) -> None:
        result = validate(BAD_RESEARCH_README, research=True)
        assert result.ok is False
        assert any("研究リポジトリ" in w for w in result.warnings)

    def test_research_good(self) -> None:
        result = validate(RESEARCH_README, research=True)
        # 研究READMEには汎用セクション（概要等）がないため汎用チェックは失敗する
        # 研究リポジトリ向けチェックのみ確認
        assert any("研究リポジトリ" in p for p in result.passed)

    def test_h1_info(self) -> None:
        result = validate(GOOD_README)
        assert any("h1見出し" in i for i in result.info)

    def test_no_h1_info(self) -> None:
        result = validate(NO_H1_README)
        assert not any("h1見出し" in i for i in result.info)


# --- ValidationResult ---

class TestValidationResult:
    """ValidationResultのプロパティテスト."""

    def test_ok_when_no_warnings(self) -> None:
        r = ValidationResult(passed=["check1"], warnings=[], info=["info1"])
        assert r.ok is True

    def test_not_ok_when_warnings(self) -> None:
        r = ValidationResult(passed=[], warnings=["warn1"], info=[])
        assert r.ok is False

    def test_info_does_not_affect_ok(self) -> None:
        """infoフィールドはokに影響しない."""
        r = ValidationResult(passed=[], warnings=[], info=["info1", "info2"])
        assert r.ok is True
