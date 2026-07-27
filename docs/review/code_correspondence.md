# 本文コード ↔ `scripts/ch*` 対応関係の再監査

- 生成日: 2026-07-28
- 対象コミット: `d01340fceec35aa0c9c28fd405a60a245abb37ec`
- 調査計画: [`2026-07-25_code_correspondence_reaudit_plan.md`](./2026-07-25_code_correspondence_reaudit_plan.md)
- E5解消計画: [`2026-07-25_e5_remediation_plan.md`](./2026-07-25_e5_remediation_plan.md)
- 全件表: [`code_correspondence.json`](./code_correspondence.json)

本書の配置規約を先に適用し、その後に対応と本質的一致を判定した。
演習、悪例、ライブラリ紹介、コマンド、出力例など、規約上実体を
必要としないブロックは「欠落」に数えずENとして全件表に残した。

## 1. 結論

| 判定 | 件数 | 意味 |
|---|---:|---|
| E0 | 43 | コメント・空白を除いて同一 |
| E1 | 45 | docstringや説明上の差を除けば同じ処理 |
| E2 | 22 | 実体と矛盾しない抜粋 |
| E3 | 24 | 対応はあるが構造または振る舞いに差がある |
| E5 | 0 | 配置が必要だが対応実体がない |
| EN | 395 | 規約上、対応実体は不要 |
| **合計** | **529** | 全本文ブロック |

配置が必要なブロックは134件である。E5は0件であり、具体的な解消順序はE5解消計画に記録した。

`scripts/ch*` 側は全174ファイルで、本文コードと直接対応98件、本文から参照のみ43件、本文コードとの対応なし33件である。

## 2. 章別集計

| 章 | 全ブロック | 配置必須 | E0 | E1 | E2 | E3 | E4 | E5 | EN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ch00 | 11 | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 9 |
| ch01 | 9 | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 6 |
| ch02 | 35 | 5 | 1 | 0 | 3 | 1 | 0 | 0 | 30 |
| ch03 | 28 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 27 |
| ch04 | 20 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 18 |
| ch05 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 23 |
| ch06 | 16 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 12 |
| ch07 | 22 | 3 | 1 | 0 | 2 | 0 | 0 | 0 | 19 |
| ch08 | 29 | 17 | 6 | 6 | 5 | 0 | 0 | 0 | 12 |
| ch09 | 33 | 8 | 0 | 5 | 3 | 0 | 0 | 0 | 25 |
| ch10 | 35 | 8 | 5 | 3 | 0 | 0 | 0 | 0 | 27 |
| ch11 | 34 | 10 | 0 | 0 | 0 | 10 | 0 | 0 | 24 |
| ch12 | 20 | 14 | 0 | 14 | 0 | 0 | 0 | 0 | 6 |
| ch13 | 11 | 6 | 3 | 3 | 0 | 0 | 0 | 0 | 5 |
| ch14 | 23 | 14 | 6 | 0 | 4 | 4 | 0 | 0 | 9 |
| ch15 | 32 | 9 | 7 | 0 | 2 | 0 | 0 | 0 | 23 |
| ch16 | 26 | 6 | 3 | 0 | 2 | 1 | 0 | 0 | 20 |
| ch17 | 42 | 11 | 2 | 6 | 0 | 3 | 0 | 0 | 31 |
| ch18 | 30 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 29 |
| ch19 | 24 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 23 |
| ch20 | 12 | 4 | 1 | 0 | 1 | 2 | 0 | 0 | 8 |
| ch21 | 14 | 5 | 1 | 4 | 0 | 0 | 0 | 0 | 9 |
| **合計** | **529** | **134** | **43** | **45** | **22** | **24** | **0** | **0** | **395** |

## 3. 対応実体がないブロック

| ID | 章・開始行 | 種別 | 見出し |
|---|---|---|---|
| — | — | — | E5は0件 |

## 4. 対応はあるが差があるブロック

| ブロック | 対応先 | 差し替え結果 | 差の根拠 |
|---|---|---|---|
| `B-00-001` | `scripts/ch00/find_orfs.py` | 11 failed, 17 passed in 0.76s | ORFとfind_all_orfsは同題材だが入力検証・探索仕様に差がある |
| `B-00-003` | `scripts/ch00/hmm_gene_predict.py` | 8 failed, 1 passed in 0.11s | viterbiの初期化・バックトレースを本文が省略し、そのままでは同じ動作にならない |
| `B-02-031` | `scripts/ch16/ssh_config.example` | 対象外 | 同じSSH configだがホスト名・利用者・ProxyJump構成が異なる章横断候補 |
| `B-11-001` | `scripts/ch11/cli_argparse.py` | 7 passed in 0.13s | 同章・同名だがAST差 |
| `B-11-002` | `scripts/ch11/cli_click.py` | 未実行: 本文定義が省略記号を含む: gc_filter | Click版に対応するが、実体は型ヒント・version・ログ・戻り値等を追加 |
| `B-11-003` | `scripts/ch11/cli_typer.py` | 未実行: 対応スクリプトに直接テストがない | Typer版に対応するが引数・出力・例外処理に差がある |
| `B-11-006` | `scripts/ch11/cli_click.py` | 6 failed, 3 passed in 0.15s | version/helpデコレータ例だが実体のgc_filterシグネチャと処理が異なる |
| `B-11-007` | `scripts/ch11/seqtool.py` | 1 failed, 12 passed in 0.17s | 同章・同名だがAST差 |
| `B-11-011` | `scripts/ch11/cli_click.py` | 未実行: 本文定義が省略記号を含む: gc_filter | 終了コードの例と実体のCLIで入力検証・終了処理が異なる |
| `B-11-013` | `scripts/ch10/config_example.py` | 対象外 | load_configは章横断候補だがdefaultsと戻り値仕様が異なる |
| `B-11-013` | `scripts/ch11/cli_click.py` | 未実行: 本文定義が省略記号を含む: gc_filter | 設定をCLIへ合成する処理は同題材だが実体のオプション・検証が異なる |
| `B-11-024` | `scripts/ch11/seqtool.py` | 対象外 | 同じfilter CLI処理だが、関数名、内包表記とループ、ステータスメッセージに差がある |
| `B-11-030` | `scripts/ch11/seqtool.py` | 1 failed, 12 passed in 0.16s | 同章・同名だがAST差 |
| `B-11-031` | `scripts/ch11/logging_setup.py` | 10 passed in 0.04s | 同名ロギング設定だが引数、ハンドラ再設定、Rich対応に差がある |
| `B-11-031` | `scripts/ch11/progress_demo.py` | 10 passed in 0.03s | 同じsetup_loggingの別実体にも対応する多対多関係 |
| `B-14-002` | `scripts/ch14/Snakefile` | 対象外 | 処理は同じだがthreadsが定数4とconfig参照で異なる |
| `B-14-014` | `scripts/ch14/Makefile` | 対象外 | 依存関係は同じだが本文URLが省略記号で実行不能、変数・clean処理にも差がある |
| `B-14-017` | `scripts/ch14/Snakefile` | 対象外 | protectedとtemp、BAMパスが異なるため動作上の差がある |
| `B-14-019` | `scripts/ch14/Snakefile` | 対象外 | logの意図は同じだがshell文字列が説明用省略形 |
| `B-16-016` | `scripts/ch16/ssh_config.example` | 対象外 | ProxyJump構造は同じだがHost別名とHostNameが異なる |
| `B-17-019` | `scripts/ch17/profiling_demo.py` | 1 error in 0.11s | 同章・同名だがAST差 |
| `B-17-031` | `scripts/ch17/generator_fastq.py` | 対象外 | generator版はfilter_by_lengthと同じ目的だがAPIが異なり、list版の実体は無い |
| `B-17-037` | `scripts/ch17/chunk_processing.py` | 1 failed, 3 passed in 0.36s | 同章・同名だがAST差 |
| `B-19-022` | `scripts/ch19/local_db.py` | 未実行: 同名のトップレベル定義がない | 同じSQLite処理だが実体は関数分割・追加列・ロギングを持ち、本文は直書き |
| `B-20-004` | `scripts/ch20/secret_scanner.py` | 21 passed in 0.03s | 同名scan_contentだが戻り値・パターン・引数・除外処理に差がある |
| `B-20-009` | `scripts/ch20/anonymize_metadata.py` | 2 failed, 23 passed in 0.04s | 年代化の基本式は同じだが実体に入力検証とエラー仕様がある |

## 5. テスト状況

全対象テストファイルを個別実行し、その結果を対応表へ保存した。

| 項目 | 結果 |
|---|---:|
| テストファイル | 91 |
| 章別テストファイル | 89 |
| レビュー用テストファイル | 2 |
| passed | 908 |
| skipped | 11 |
| failed | 0 |
| errors | 0 |

## 6. 多対多対応

1ブロックから複数ファイルへの対応は7件ある。

| 本文ブロック | 対応先 |
|---|---|
| `B-05-004` | `scripts/ch05/mylib/core.py`、`scripts/ch05/mylib/utils.py` |
| `B-05-005` | `scripts/ch05/mylib/__init__.py`、`scripts/ch05/mylib/core.py` |
| `B-08-008` | `tests/ch08/conftest.py`、`tests/ch08/conftest.py` |
| `B-08-009` | `tests/ch08/test_reverse_complement.py`、`tests/ch08/test_seq_stats.py` |
| `B-08-025` | `scripts/ch08/examples/claude-settings.json`、`scripts/ch08/examples/codex-hooks.json` |
| `B-11-013` | `scripts/ch10/config_example.py`、`scripts/ch11/cli_click.py` |
| `B-11-031` | `scripts/ch11/logging_setup.py`、`scripts/ch11/progress_demo.py` |

## 7. 実体側だけにあるファイル

本文コードとの対応がない資産は33件である。
個別の役割とテスト結果は全件表の`scripts`に記録した。

| 役割 | ファイル数 |
|---|---:|
| data_support | 2 |
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

分類overrideは27件、関係overrideは112件である。override対象の本文ハッシュが変わった場合、生成処理は停止する。

## 9. 全件表の読み方

`blocks`は本文ブロック、`scripts`はスクリプト資産、`test_assets`は章別テスト資産、`test_files`は個別実行結果を保持する。
各関係の`target_file_id`は`scripts`または`test_assets`のIDへ解決され、定義単位の対応には`target_entity_locations`を記録する。

## 10. 限界

1. テスト成功は現行テスト範囲の観測であり、完全な意味論的等価の証明ではない
2. 非Python資産は統一構文木を持たないため、正規化行と人手確認を併用する
3. Git履歴は本文が行範囲、対応先がファイル単位であり偽陽性がありうる
4. 実体配置の要否は現行の執筆規約に基づく
