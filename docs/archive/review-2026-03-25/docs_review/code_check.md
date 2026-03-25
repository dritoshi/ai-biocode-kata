# コードサンプル動作確認レポート

実行日: 2026-03-25

## 1. pytest 実行結果

### 実行環境

| 項目 | 値 |
|------|-----|
| Python | Python 3.14.3 |
| pytest | pytest 9.0.2 |
| OS | Darwin (arm64) |

### 実行コマンド

```bash
.venv/bin/pytest -q -ra
```

### 結果サマリー

| 区分 | 件数 |
|------|------|
| passed | 713 |
| failed | 0 |
| errors | 0 |
| skipped | 2 |
| warnings | 9 |
| 実行時間 | 16.35s |

### 警告

- `BiopythonDeprecationWarning`: `tests/ch10/test_error_handling.py::TestValidateFasta::test_no_sequences`
- `ClusterWarning`: `tests/ch13/test_bio_plots.py::TestExpressionHeatmap::test_small_matrix`

## 2. 未カバースクリプト

| 章 | スクリプト | 備考 |
|----|-----------|------|
| ch03 | `ch03/plot_bench.py` | 図表生成スクリプト |
| ch03 | `ch03/plot_complexity.py` | 図表生成スクリプト |
| ch05 | `ch05/mylib/core.py` | ライブラリモジュール |
| ch05 | `ch05/mylib/utils.py` | ライブラリモジュール |
| ch09 | `ch09/generate_traceback.py` | 図表生成スクリプト |
| ch11 | `ch11/cli_argparse.py` | CLI デモ |
| ch11 | `ch11/cli_typer.py` | CLI デモ |
| ch11 | `ch11/progress_demo.py` | CLI デモ |
| ch12 | `ch12/plot_vectorize_bench.py` | 図表生成スクリプト |
| ch13 | `ch13/generate_figures.py` | 図表生成スクリプト |
| ch13 | `ch13/plot_colormap_comparison.py` | 図表生成スクリプト |
| ch17 | `ch17/plot_amdahl.py` | 図表生成スクリプト |
| ch17 | `ch17/plot_profiling.py` | 図表生成スクリプト |

合計: **13 スクリプトが未カバー**

## 3. 対応メモ

- `tests/ch10/test_error_handling.py` の `BiopythonDeprecationWarning` は将来 `ValueError` へ変わる可能性があるため、入力フィクスチャかパーサ指定の見直し候補である。
- 未カバースクリプトのうち `ch05/mylib/core.py` `ch05/mylib/utils.py` `ch11/cli_argparse.py` は、図表生成や単発デモより優先度が高い品質改善候補である。
