# 本文コード ↔ `scripts/` 対応表

- **作成日**: 2026-07-25
- **手法**: [`2026-07-25_code_correspondence_plan.md`](./2026-07-25_code_correspondence_plan.md)（第6版）
- **全件の機械可読版**: [`code_correspondence.json`](./code_correspondence.json)
- **本文と `scripts/` の実体は変更していない**。本書は対応表と修正案のみ

## 1. サマリ

### 対象範囲

| 項目 | 件数 |
|---|---|
| 章ファイル由来のコードブロック | 379 |
| 本文の名前付き定義 | 145 |
| 実体の名前付き定義 | 1298（`scripts/chNN` 291 + `tests/chNN` 1007） |

> 付録・はじめに・用語集（`appendix_*.md` `hajimeni.md` 等）は対象外。
> 対応する `scripts/appendix_*` が存在せず、全件が「対応なし」になるため。

### 構造軸の分布（本文の定義145件）

| 段階 | 意味 | 件数 |
|---|---|---|
| **S0** | 完全同一 | 5 |
| **S1** | docstring のみ差 | 35 |
| **S3** | 定義名のみ差 | 6 |
| **S3b** | 型注釈のみ差 | 5 |
| **S4** | 本文が実体の抜粋 | 5 |
| **S4e** | 本文が … で明示的に省略した抜粋 | 11 |
| **S6** | 同名・内容差 | 31 |
| **S8** | 対応なし | 47 |
| | **合計** | **145** |

**本質的に同じもの（S0〜S3b）が 51 件（35%）**、
**抜粋の関係（S4〜S5）が 16 件**、**内容が食い違うもの（S6）が 31 件**、
**実体に対応が無いもの（S8）が 47 件**である。

整形・コメント・docstring・型注釈・局所名の差を除いて比較した結果であり、
見かけの不一致は取り除いてある。

## 2. 要対応の一覧

### 2-1. 片側だけが更新された疑い（時系列軸）

S6（同名・内容差）31 件について、本文と実体それぞれの行範囲の最終更新日を
`git log -L` で調べた。本文のほうが新しいものは全体で 12 件あるが、うち 3 件は差が1日未満で、同じ作業セッション内の前後にすぎない（最小7分差）。

**実質的に取り残されているのは 9 件**である。

| 本文 | 定義 | 本文の更新 | 実体の更新 | 差 | 対応先 |
|---|---|---|---|---|---|
| `11_cli.md:289` | `gc_filter` | 2026-07-24 | 2026-03-19 | 127日 | `scripts/ch11/cli_click.py` |
| `11_cli.md:748` | `setup_logging` | 2026-07-23 | 2026-03-19 | 126日 | `scripts/ch11/logging_setup.py` |
| `00_ai_agent.md:172` | `viterbi` | 2026-07-23 | 2026-03-20 | 125日 | `scripts/ch00/hmm_gene_predict.py` |
| `20_security_ethics.md:111` | `scan_content` | 2026-07-24 | 2026-03-22 | 124日 | `scripts/ch20/secret_scanner.py` |
| `21_collaboration.md:315` | `check_type_hints` | 2026-07-23 | 2026-03-22 | 123日 | `scripts/ch21/review_helper.py` |
| `21_collaboration.md:550` | `parse_git_log` | 2026-07-23 | 2026-03-22 | 123日 | `scripts/ch21/progress_report.py` |
| `21_collaboration.md:667` | `validate_metadata` | 2026-07-23 | 2026-03-22 | 123日 | `scripts/ch21/analysis_intake.py` |
| `11_cli.md:51` | `parse_args` | 2026-07-23 | 2026-03-26 | 119日 | `scripts/ch11/cli_argparse.py` |
| `17_performance.md:647` | `filter_by_quality` | 2026-03-21 | 2026-03-19 | 1日 | `scripts/ch12/numpy_vectorize.py` ⚠️章またぎ |

**約4ヶ月の差がある8件は、2026年7月の改訂で本文を直した際に `scripts/` を
更新しなかったものである。** ⚠️ 印は章をまたぐ対応で、対応付け自体の確認が要る。

### 2-2. 本文にしかないコード（S8）

**47 件**。読者がリポジトリで確認できない。

| 章 | 件数 | 定義の例 |
|---|---|---|
| ch01 | 1 | `process_fastq` |
| ch03 | 7 | `trinucleotide_freq`, `parse_fasta`, `calculate_gc`, `filter_variants` |
| ch05 | 13 | `parse`, `SequenceAnalyzer`, `SequenceAnalyzer.parse`, `SequenceAnalyzer.align` |
| ch08 | 13 | `test_simple_sequence`, `test_empty_sequence`, `test_gc_content_typical`, `TestReverseComplement.test_empty` |
| ch10 | 2 | `filter_variants`, `run_pipeline` |
| ch11 | 2 | `filter`, `filter_sequences` |
| ch13 | 2 | `volcano_plot_interactive`, `apply_project_style` |
| ch17 | 6 | `load_large_data`, `filter_reads_list`, `filter_reads_generator`, `pairwise_distance` |
| ch19 | 1 | `fetch_sequences` |

### 2-3. テストの状況

テストファイル単位で個別に実行した（69 ファイル）。

- **passed 776 / failed 0 / skipped 1**
- 失敗したファイル: **0 件**
- skip を含むファイル: 1 件 — `tests/ch07/test_citation_cff.py`

> skip の1件は `cffconvert` が dev 依存に無いため。改訂プランの残タスクとして既知。

#### 振る舞い軸（本文版に差し替えて実体のテストを実行）

| 段階 | 意味 | 件数 |
|---|---|---|
| **B0** | 差し替えても全て通る | 16 |
| **B1** | 一部が失敗する | 14 |
| **B2** | 実行できない | 1 |
| **B3** | 対応するテストが無い | 5 |

**B1（本文版ではテストが落ちる）**: 本文のコードが実体と振る舞いレベルで違う。

- `00_ai_agent.md:105:find_all_orfs` — 10 failed, 18 passed in 5.66s
- `00_ai_agent.md:172:viterbi` — 8 failed, 1 passed in 0.10s
- `01_design.md:43:gc_content` — 9 failed in 0.03s
- `09_debug.md:208:calculate_gc_stats` — 4 failed, 5 passed in 0.06s
- `09_debug.md:407:validate_coordinates` — 3 failed, 12 passed in 0.03s
- `11_cli.md:182:gc_filter` — 6 failed, 3 passed in 0.15s
- `11_cli.md:201:cli` — 11 failed, 2 passed in 0.14s
- `11_cli.md:210:stats` — 5 failed, 8 passed in 0.12s
- `11_cli.md:289:gc_filter` — 6 failed, 3 passed in 0.16s
- `11_cli.md:311:load_config` — 5 failed in 0.29s
- `11_cli.md:327:gc_filter` — 6 failed, 3 passed in 0.12s
- `11_cli.md:724:cli` — 11 failed, 2 passed in 0.12s
- `17_performance.md:647:filter_by_quality` — 4 failed, 9 passed in 0.07s
- `17_performance.md:803:compute_stats_chunked` — 1 failed, 3 passed in 0.35s

> B0 の根拠の強さは対応するテストの厚さに依存する。テストが薄ければ通ってしまう。

## 3. 多対多の対応

対応を持つスクリプトは 47 件。うち **17 件が複数の本文ブロックに対応**する。

| スクリプト | 対応する本文ブロック数 |
|---|---|
| `scripts/ch01/gc_content.py` | 5 |
| `scripts/ch12/scipy_stats_bio.py` | 5 |
| `scripts/ch08/seq_stats.py` | 4 |
| `scripts/ch10/error_handling.py` | 4 |
| `scripts/ch11/cli_click.py` | 4 |
| `scripts/ch11/cli_typer.py` | 4 |
| `scripts/ch12/numpy_vectorize.py` | 4 |
| `scripts/ch12/pandas_bio_ops.py` | 4 |
| `scripts/ch09/traceback_demo.py` | 3 |
| `scripts/ch12/plot_vectorize_bench.py` | 3 |
| `scripts/ch17/profiling_demo.py` | 3 |
| `scripts/ch09/coordinate_bugs.py` | 2 |

## 4. 実体にしかないもの

**1202 件**。大半はテスト関数や図表生成で、本文に無くて当然のものである。

| 種別 | 件数 | 要対応か |
|---|---|---|
| テスト補助 | 997 | 否 |
| 図表生成 | 20 | 否 |
| 内部ヘルパー | 15 | 否 |
| デモ | 15 | 否 |
| 点検対象 | 155 | **本文で説明すべきものが埋もれていないか点検** |

## 5. ブロック単位の対応（定義を持たないコード）

定義を含まないブロック（設定ファイル・Snakefile・手続きのみ・断片）が **279 件**。

| 言語タグ | 件数 | 一致率50%以上 | 対応なし |
|---|---|---|---|
| `python` | 102 | 28 | 29 |
| `bash` | 65 | 4 | 60 |
| `none` | 52 | 2 | 49 |
| `markdown` | 18 | 0 | 17 |
| `yaml` | 16 | 4 | 12 |
| `dockerfile` | 8 | 6 | 1 |
| `toml` | 6 | 0 | 5 |
| `ini` | 2 | 0 | 2 |

## 6. 修正案

計画 10-3 の5型に沿って提示する。**実際の修正は行っていない**。

| 優先 | 型 | 対象 | 件数 | 内容 |
|---|---|---|---|---|
| 1 | C. 実体を本文へ寄せる | 時系列軸で本文が1日以上新しい | 9 | 2026-07 の改訂で本文だけ直した箇所。`scripts/` を追随させる |
| 2 | A. 実体を新設 | S8 のうち実装コード | 47 件から選別 | 読者がリポジトリで確認できないコードを `scripts/` に起こす |
| 3 | E. テストを補う | skip 1件 | 1 | `cffconvert` を dev 依存へ |
| 4 | B. 本文を抜粋へ | S6 のうち本文が古い | 6 | 実体が新しい箇所は本文を抜粋に置き換える |
| 5 | D. 対象外と記録 | 点検対象外の S8 | — | 悪例・ライブラリ紹介に `<!-- code-sync: skip -->` を付す |

### 6-1. 最優先: 実体が取り残された箇所

2-1 の表がそのまま対象（9件）。**本文が正で実体が古い**とみられるため、
`scripts/` を本文に合わせる。
ただし本文が抜粋の場合は実体のほうが詳しくてよいので、個別に中身を見る必要がある。

## 7. 手法の検証結果

| 検証 | 結果 |
|---|---|
| 保存則（取りこぼし） | ✅ 本文145件が漏れなく分類。段階の合計 = 母数 |
| 偽陽性検査（改変を同一と誤判定しないか） | ✅ 3/3 で誤判定なし（演算子反転・定数変更・文の順序入替） |
| 偽陰性検査（既知の対応が対応なしに落ちないか） | ✅ 4/4 で期待どおり（S0/S1/S3/S4） |
| ゴールドセット（12件・実装前に凍結） | ✅ 不一致 0 |

### 7-1. 実行中に見つかり修正した欠陥

ゴールドセット照合で2件の不一致が出て、いずれも**分類器の欠落**だった。

1. **型注釈のみの差を「内容が違う」と扱っていた** — 本文は簡略版で型ヒントを省くことがある。
   段階 **S3b** を追加し、5 件が該当した
2. **本文が `...` で本体を省略している形を扱えなかった** — 本文の定義145件のうち32件（22%）が
   この形を取る。段階 **S4e** を追加し、11 件が該当した。
   併せて、デコレータ付き関数でヘッダ行を1行しか取っていないバグも修正した

> ゴールドセットのラベル自体にも誤りがあった。`gc_filter` を「整形差のみ」と見立てたが、
> 実際は本体を `...` で省略した抜粋だった。凍結したラベルは動かさず、
> **手法の欠落として記録**している。

## 8. 既知の限界

1. **振る舞い等価はテストの範囲でしか言えない**。テストが薄い定義では B0 の根拠は弱い
2. **章をまたぐ対応は定義名が一致する場合のみ拾う**（7 件検出）。
   名前が違う章またぎ（§15 の Snakemake `rule` と `scripts/ch14/Snakefile` 等）は
   「対応なし」と出る
3. **どちらが正しいかは判定しない**。S6 は食い違いを示すだけで、正誤は人間が決める
4. **時系列軸は行範囲の履歴に依存する**。章の大規模な書き換えがあると精度が落ちる
5. **ブロック単位の比較は行集合**であり、定義単位ほど厳密ではない
6. `S3`（定義名のみ差）は改名だけでなく**コピペ由来の重複**も拾う

## 9. 再現性について

本表を生成した分析スクリプトは **リポジトリにコミットしていない**（計画の非目的）。
scratchpad 上の以下の構成で動作した。

| ファイル | 役割 |
|---|---|
| `extract.py` | 本文・実体から定義単位とブロック単位を抽出 |
| `normalize.py` | 正規化キー K0〜K4 と文の並びの生成 |
| `classify.py` | 構造軸 S0〜S8 の判定 |
| `tests_and_blocks.py` | テスト実行とブロック単位の対応付け |
| `axes_tb.py` | 時系列軸 T と振る舞い軸 B |
| `gates.py` | 偽陽性・偽陰性の検査 |
| `goldset.json` | 実装前に凍結したゴールドセット12件 |
| `report.py` | 本表の生成 |

**再点検が必要になった時点で `scripts/review/` への採用を提案する**。
その際はテストの付与が要る（禁止事項「テストのないコードサンプルの掲載」に準ずる）。

