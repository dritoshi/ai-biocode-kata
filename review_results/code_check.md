# コードサンプル動作確認レポート

実行日: 2026-03-25

## 1. テスト実行結果

### 実行環境

| 項目 | 値 |
|------|-----|
| Python | 3.14.3 |
| pytest | 9.0.2 |
| OS | macOS (Darwin 25.3.0, arm64) |

### 実行コマンド

```
python3 -m pytest tests/ -v --tb=short
```

### 結果サマリー

| 区分 | 件数 |
|------|------|
| passed | 689 |
| failed | 0 |
| skipped | 2 |
| errors (収集時) | 3 |
| warnings | 9 |
| 実行時間 | 10.50s |

### 収集エラー (3件) -- 依存パッケージ不足

| テストファイル | 不足パッケージ |
|----------------|---------------|
| `tests/ch11/test_cli_click.py` | `click` |
| `tests/ch11/test_seqtool.py` | `click` |
| `tests/ch12/test_polars_bio_ops.py` | `polars` |

これらのテストは対応するパッケージがインストールされていないためインポート段階で失敗した。テストコード自体のバグではなく、環境に依存パッケージが未インストールであることが原因である。

### スキップされたテスト (2件)

| テスト | 理由 |
|--------|------|
| `tests/ch07/test_citation_cff.py::test_template_validates_with_cffconvert` | `cffconvert` コマンドが未インストール |
| (収集時スキップ 1件) | 収集段階での条件スキップ |

### 警告 (9件)

- `tests/ch10/test_error_handling.py::TestValidateFasta::test_no_sequences` -- Biopython の FASTA パーサが先頭コメント行の非推奨警告を出力 (`BiopythonDeprecationWarning`)。将来の Biopython リリースで `ValueError` に変更予定。
- `tests/ch13/test_bio_plots.py` の `TestExpressionHeatmap` 系 4テスト x 2 = 8件 -- scipy の `ClusterWarning`: 距離行列が凝縮されていない形式に見えるという警告。

### テスト失敗: なし

全689テストが正常に通過した。

---

## 2. スクリプト - テスト対応表

### テスト完全カバー済みの章

| 章 | スクリプト数 | テスト数 | 状態 |
|----|-------------|---------|------|
| ch00 | 3 | 3 | 全カバー |
| ch01 | 2 | 2 | 全カバー |
| ch02 | 4 | 4 | 全カバー |
| ch04 | 5 | 5 | 全カバー |
| ch06 | 1 | 1 | 全カバー |
| ch07 | 0 (テンプレート3件) | 1 | 全カバー |
| ch08 | 2 | 2 | 全カバー |
| ch10 | 2 | 2 | 全カバー |
| ch14 | 1 | 1 | 全カバー |
| ch15 | 2 | 2 | 全カバー |
| ch16 | 1 | 1 | 全カバー |
| ch18 | 3 | 3 | 全カバー |
| ch19 | 5 | 5 | 全カバー |
| ch20 | 2 | 2 | 全カバー |
| ch21 | 4 | 4 | 全カバー |

### テスト未カバーのスクリプト一覧

| 章 | スクリプト | テスト有無 | 備考 |
|----|-----------|-----------|------|
| ch03 | `plot_complexity.py` | なし | 図表生成スクリプト |
| ch03 | `plot_bench.py` | なし | 図表生成スクリプト |
| ch05 | `mylib/core.py` | なし | module_demo.py 経由で間接テストの可能性あり |
| ch05 | `mylib/utils.py` | なし | module_demo.py 経由で間接テストの可能性あり |
| ch09 | `generate_traceback.py` | なし | デモ用トレースバック生成スクリプト |
| ch11 | `cli_argparse.py` | なし | CLI デモ |
| ch11 | `cli_typer.py` | なし | CLI デモ (typer パッケージ依存) |
| ch11 | `progress_demo.py` | なし | プログレスバーデモ |
| ch12 | `plot_vectorize_bench.py` | なし | 図表生成スクリプト |
| ch13 | `generate_figures.py` | なし | 図表生成スクリプト |
| ch13 | `plot_colormap_comparison.py` | なし | 図表生成スクリプト |
| ch17 | `plot_profiling.py` | なし | 図表生成スクリプト |
| ch17 | `plot_amdahl.py` | なし | 図表生成スクリプト |
| (top) | `count_chars.py` | なし | ユーティリティスクリプト (書籍用ではない可能性) |

合計: **14 スクリプトがテスト未カバー**

### 未カバースクリプトの分類

| 類型 | 件数 | スクリプト |
|------|------|-----------|
| 図表生成 (plot/generate) | 7 | plot_complexity, plot_bench, plot_vectorize_bench, generate_figures, plot_colormap_comparison, plot_profiling, plot_amdahl |
| CLIデモ | 3 | cli_argparse, cli_typer, progress_demo |
| デモ/ヘルパー | 2 | generate_traceback, count_chars |
| ライブラリモジュール | 2 | mylib/core.py, mylib/utils.py |

---

## 3. 総合評価

### 良好な点

- 全689テストが **100% 通過** (失敗ゼロ)
- 22章中15章で全スクリプトがテストカバー済み
- テスト収集エラー3件は全て依存パッケージ不足が原因であり、コード自体の問題ではない
- 警告9件も全て外部ライブラリ由来であり、コードサンプルの品質には影響しない

### 対応推奨事項

1. **依存パッケージのインストール**: `click` と `polars` をインストールすれば収集エラー3件が解消される
2. **Biopython 警告への対応**: `tests/ch10/test_error_handling.py` で FASTA パーサの `format='fasta-pearson'` への移行を検討（将来の Biopython で `ValueError` になる可能性）
3. **テスト未カバースクリプト**: 図表生成スクリプト (7件) はテスト対象外として許容できるが、以下は検討の余地あり:
   - `scripts/ch05/mylib/core.py`, `scripts/ch05/mylib/utils.py` -- ライブラリモジュールとして個別テストがあると望ましい
   - `scripts/ch11/cli_argparse.py` -- ch11 の他の CLI スクリプト (cli_click, seqtool) にはテストがあるため、argparse 版にもテストがあると一貫性が保てる
