# 本文コード ↔ `scripts/ch*` 対応関係の再監査

- 生成日: 2026-07-28
- 対象コミット: `d08de48cf6acd9d796630b0cb6cda47e679e6d10`
- 調査計画: [`2026-07-25_code_correspondence_reaudit_plan.md`](./2026-07-25_code_correspondence_reaudit_plan.md)
- E5解消計画: [`2026-07-25_e5_remediation_plan.md`](./2026-07-25_e5_remediation_plan.md)
- E1解消計画: [`2026-07-28_e1_remediation_plan.md`](./2026-07-28_e1_remediation_plan.md)
- 全件表: [`code_correspondence.json`](./code_correspondence.json)

本書の配置規約を先に適用し、その後に対応と本質的一致を判定した。
演習、悪例、ライブラリ紹介、コマンド、出力例など、規約上実体を
必要としないブロックは「欠落」に数えずENとして全件表に残した。

## 1. 結論

| 判定 | 件数 | 意味 |
|---|---:|---|
| E0 | 55 | コメント・空白を除いて同一 |
| E1 | 39 | docstringや説明上の差を除けば同じ処理 |
| E2 | 40 | 実体と矛盾しない抜粋 |
| E3 | 0 | 対応はあるが構造または振る舞いに差がある |
| E5 | 0 | 配置が必要だが対応実体がない |
| EN | 395 | 規約上、対応実体は不要 |
| **合計** | **529** | 全本文ブロック |

配置が必要なブロックは134件である。E5は0件であり、具体的な解消順序はE5解消計画に記録した。
E1解消バッチ4時点で、基準45件の定義単位関係は54件である。

`scripts/ch*` 側は全176ファイルで、本文コードと直接対応99件、本文から参照のみ43件、本文コードとの対応なし34件である。

## 2. 章別集計

| 章 | 全ブロック | 配置必須 | E0 | E1 | E2 | E3 | E4 | E5 | EN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ch00 | 11 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 9 |
| ch01 | 9 | 3 | 0 | 2 | 1 | 0 | 0 | 0 | 6 |
| ch02 | 35 | 5 | 2 | 0 | 3 | 0 | 0 | 0 | 30 |
| ch03 | 28 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 27 |
| ch04 | 20 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 18 |
| ch05 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 23 |
| ch06 | 16 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 12 |
| ch07 | 22 | 3 | 1 | 0 | 2 | 0 | 0 | 0 | 19 |
| ch08 | 29 | 17 | 6 | 5 | 6 | 0 | 0 | 0 | 12 |
| ch09 | 33 | 8 | 0 | 5 | 3 | 0 | 0 | 0 | 25 |
| ch10 | 35 | 8 | 5 | 3 | 0 | 0 | 0 | 0 | 27 |
| ch11 | 34 | 10 | 2 | 0 | 8 | 0 | 0 | 0 | 24 |
| ch12 | 20 | 14 | 2 | 12 | 0 | 0 | 0 | 0 | 6 |
| ch13 | 11 | 6 | 3 | 3 | 0 | 0 | 0 | 0 | 5 |
| ch14 | 23 | 14 | 7 | 0 | 7 | 0 | 0 | 0 | 9 |
| ch15 | 32 | 9 | 7 | 0 | 2 | 0 | 0 | 0 | 23 |
| ch16 | 26 | 6 | 4 | 0 | 2 | 0 | 0 | 0 | 20 |
| ch17 | 42 | 11 | 5 | 5 | 1 | 0 | 0 | 0 | 31 |
| ch18 | 30 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 29 |
| ch19 | 24 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 23 |
| ch20 | 12 | 4 | 2 | 0 | 2 | 0 | 0 | 0 | 8 |
| ch21 | 14 | 5 | 1 | 4 | 0 | 0 | 0 | 0 | 9 |
| **合計** | **529** | **134** | **55** | **39** | **40** | **0** | **0** | **0** | **395** |

## 3. 対応実体がないブロック

| ID | 章・開始行 | 種別 | 見出し |
|---|---|---|---|
| — | — | — | E5は0件 |

## 4. 対応はあるが差があるブロック

| ブロック | 対応先 | 差し替え結果 | 差の根拠 |
|---|---|---|---|
| — | — | — | E3は0件 |

## 5. テスト状況

全対象テストファイルを個別実行し、その結果を対応表へ保存した。

| 項目 | 結果 |
|---|---:|
| テストファイル | 104 |
| 章別テストファイル | 95 |
| レビュー用テストファイル | 9 |
| passed | 1015 |
| skipped | 11 |
| failed | 0 |
| errors | 0 |

## 6. 多対多対応

1ブロックから複数ファイルへの対応は11件ある。

| 本文ブロック | 対応先 |
|---|---|
| `B-01-004` | `scripts/ch01/seq_filter.py`、`scripts/ch01/seq_filter.py`、`scripts/ch01/seq_filter.py`、`scripts/ch01/seq_filter.py` |
| `B-05-004` | `scripts/ch05/mylib/core.py`、`scripts/ch05/mylib/utils.py` |
| `B-05-005` | `scripts/ch05/mylib/__init__.py`、`scripts/ch05/mylib/core.py` |
| `B-08-003` | `tests/ch08/test_reverse_complement.py`、`tests/ch08/test_reverse_complement.py` |
| `B-08-008` | `tests/ch08/conftest.py`、`tests/ch08/conftest.py` |
| `B-08-009` | `tests/ch08/test_seq_stats.py`、`tests/ch08/test_seq_stats.py` |
| `B-08-025` | `scripts/ch08/examples/claude-settings.json`、`scripts/ch08/examples/codex-hooks.json` |
| `B-17-030` | `scripts/ch17/parallel_gc.py`、`scripts/ch17/parallel_gc.py` |
| `B-17-031` | `scripts/ch17/generator_fastq.py`、`scripts/ch17/generator_fastq.py` |
| `B-17-032` | `scripts/ch17/generator_fastq.py`、`scripts/ch17/generator_fastq.py`、`scripts/ch17/generator_fastq.py` |
| `B-17-038` | `scripts/ch17/file_format_bench.py`、`scripts/ch17/file_format_bench.py` |

## 7. 実体側だけにあるファイル

本文コードとの対応がない資産は34件である。
個別の役割とテスト結果は全件表の`scripts`に記録した。

| 役割 | ファイル数 |
|---|---:|
| data_support | 2 |
| demo | 1 |
| figure_generation | 8 |
| implementation | 2 |
| package_support | 20 |
| validator | 1 |

## 8. 手法と検証

1. 文字数や言語で除外せず、番号付き章の全コードブロックを抽出した
2. `scripts/ch*` と `tests/ch*` の全実ファイルを別母集団で抽出した
3. 機械分類後、ハッシュ付きoverride台帳の人手判断を適用した
4. Python AST、定義名、順序保存部分列、非Python正規化行を候補生成に使った
5. import、命名、直接パス参照から実体とテストを対応付けた
6. 独立監査でソースハッシュ、ID、参照先、集計、Markdownを再計算する

分類overrideは27件、関係overrideは117件である。override対象の本文ハッシュが変わった場合、生成処理は停止する。

## 9. 全件表の読み方

`blocks`は本文ブロック、`scripts`はスクリプト資産、`test_assets`は章別テスト資産、`test_files`は個別実行結果を保持する。
各関係の`target_file_id`は`scripts`または`test_assets`のIDへ解決され、定義単位の対応には`target_entity_locations`を記録する。

## 10. 限界

1. テスト成功は現行テスト範囲の観測であり、完全な意味論的等価の証明ではない
2. 非Python資産は統一構文木を持たないため、正規化行と人手確認を併用する
3. Git履歴は本文が行範囲、対応先がファイル単位であり偽陽性がありうる
4. 実体配置の要否は現行の執筆規約に基づく
