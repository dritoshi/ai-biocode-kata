# 本文コード ↔ `scripts/ch*` 対応関係の再監査

- 生成日: 2026-07-26
- 対象コミット: `96d5dd89e862c24937bec22f5a2c6f6aa966ebe6`
- 調査計画: [`2026-07-25_code_correspondence_reaudit_plan.md`](./2026-07-25_code_correspondence_reaudit_plan.md)
- E5解消計画: [`2026-07-25_e5_remediation_plan.md`](./2026-07-25_e5_remediation_plan.md)
- 全件表: [`code_correspondence.json`](./code_correspondence.json)

本書の配置規約を先に適用し、その後に対応と本質的一致を判定した。
演習、悪例、ライブラリ紹介、コマンド、出力例など、規約上実体を
必要としないブロックは「欠落」に数えずENとして全件表に残した。

## 1. 結論

| 判定 | 件数 | 意味 |
|---|---:|---|
| E0 | 10 | コメント・空白を除いて同一 |
| E1 | 38 | docstringや説明上の差を除けば同じ処理 |
| E2 | 12 | 実体と矛盾しない抜粋 |
| E3 | 36 | 対応はあるが構造または振る舞いに差がある |
| E5 | 39 | 配置が必要だが対応実体がない |
| EN | 394 | 規約上、対応実体は不要 |
| **合計** | **529** | 全本文ブロック |

配置が必要なブロックは135件である。E5は39件であり、具体的な解消順序はE5解消計画に記録した。

`scripts/ch*` 側は全116ファイルで、本文コードと直接対応64件、本文から参照のみ23件、本文コードとの対応なし29件である。

## 2. 章別集計

| 章 | 全ブロック | 配置必須 | E0 | E1 | E2 | E3 | E4 | E5 | EN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ch00 | 11 | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 9 |
| ch01 | 9 | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 6 |
| ch02 | 35 | 5 | 0 | 0 | 0 | 1 | 0 | 4 | 30 |
| ch03 | 28 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 27 |
| ch04 | 20 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 18 |
| ch05 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 23 |
| ch06 | 16 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 12 |
| ch07 | 22 | 3 | 1 | 0 | 2 | 0 | 0 | 0 | 19 |
| ch08 | 29 | 17 | 0 | 5 | 1 | 3 | 0 | 8 | 12 |
| ch09 | 33 | 8 | 0 | 3 | 0 | 5 | 0 | 0 | 25 |
| ch10 | 35 | 8 | 2 | 3 | 0 | 0 | 0 | 3 | 27 |
| ch11 | 34 | 10 | 0 | 0 | 0 | 9 | 0 | 1 | 24 |
| ch12 | 20 | 15 | 0 | 14 | 0 | 0 | 0 | 1 | 5 |
| ch13 | 11 | 6 | 0 | 3 | 0 | 1 | 0 | 2 | 5 |
| ch14 | 23 | 14 | 1 | 0 | 4 | 4 | 0 | 5 | 9 |
| ch15 | 32 | 9 | 3 | 0 | 2 | 0 | 0 | 4 | 23 |
| ch16 | 26 | 6 | 3 | 0 | 2 | 1 | 0 | 0 | 20 |
| ch17 | 42 | 11 | 0 | 6 | 0 | 3 | 0 | 2 | 31 |
| ch18 | 30 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 29 |
| ch19 | 24 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 23 |
| ch20 | 12 | 4 | 0 | 0 | 1 | 2 | 0 | 1 | 8 |
| ch21 | 14 | 5 | 0 | 0 | 0 | 4 | 0 | 1 | 9 |
| **合計** | **529** | **135** | **10** | **38** | **12** | **36** | **0** | **39** | **394** |

## 3. 対応実体がないブロック

| ID | 章・開始行 | 種別 | 見出し |
|---|---|---|---|
| `B-02-025` | `ch02` L559 | config_workflow | set -euo pipefail — 安全なスクリプトの第一行 |
| `B-02-026` | `ch02` L576 | config_workflow | シェルスクリプトの基本構造 |
| `B-02-028` | `ch02` L615 | config_workflow | 条件分岐 |
| `B-02-029` | `ch02` L632 | config_workflow | ループ |
| `B-04-004` | `ch04` L204 | config_workflow | YAML / TOML — 設定ファイル |
| `B-04-005` | `ch04` L217 | config_workflow | YAML / TOML — 設定ファイル |
| `B-06-006` | `ch06` L152 | config_workflow | 依存関係定義ファイルの比較 |
| `B-06-007` | `ch06` L159 | config_workflow | 依存関係定義ファイルの比較 |
| `B-06-008` | `ch06` L171 | config_workflow | 依存関係定義ファイルの比較 |
| `B-06-012` | `ch06` L307 | config_workflow | チャネルとレジストリ |
| `B-08-008` | `ch08` L209 | test_code | conftest.py — フィクスチャの共有 |
| `B-08-014` | `ch08` L348 | config_workflow | pyproject.toml での設定 |
| `B-08-015` | `ch08` L378 | config_workflow | ルールをディレクトリ単位で調整する — per-file-ignores |
| `B-08-020` | `ch08` L447 | config_workflow | pyproject.toml でのmypy設定 |
| `B-08-022` | `ch08` L471 | config_workflow | pre-commit — コミット前の自動チェック |
| `B-08-025` | `ch08` L577 | config_workflow | 設定例 |
| `B-08-026` | `ch08` L626 | config_workflow | ワークフローYAMLの書き方 |
| `B-08-027` | `ch08` L679 | config_workflow | ワークフローの拡張 |
| `B-10-004` | `ch10` L77 | config_workflow | パターン2: pipインストール可能なPythonパッケージ |
| `B-10-023` | `ch10` L612 | config_workflow | 設定ファイルによる外部化 |
| `B-10-033` | `ch10` L929 | implementation | fail-fastの原則 |
| `B-11-024` | `ch11` L590 | implementation | stdoutとプログレスの棲み分け |
| `B-12-002` | `ch12` L40 | implementation | 高速化の前に — すでにC実装の道具がないか |
| `B-13-008` | `ch13` L415 | implementation | スクリプト化のポイント |
| `B-13-010` | `ch13` L530 | config_workflow | 論文用トラック図の作成 |
| `B-14-006` | `ch14` L193 | config_workflow | conda / container統合 |
| `B-14-008` | `ch14` L298 | config_workflow | DSL2の基本構文 |
| `B-14-010` | `ch14` L386 | config_workflow | CommandLineToolの基本構造 |
| `B-14-011` | `ch14` L437 | config_workflow | Workflowの定義 |
| `B-14-012` | `ch14` L481 | config_workflow | 入力ファイル（ジョブファイル） |
| `B-15-012` | `ch15` L389 | config_workflow | 承認ありモードでDockerfileを反復構築する |
| `B-15-018` | `ch15` L530 | config_workflow | GPUコンテナ |
| `B-15-019` | `ch15` L572 | config_workflow | 両方を併用する戦略 |
| `B-15-022` | `ch15` L645 | config_workflow | バージョン固定の実践 |
| `B-17-022` | `ch17` L358 | implementation | memrayによるメモリプロファイリング |
| `B-17-036` | `ch17` L772 | implementation | ストリーミング処理 — 全データをメモリに載せない |
| `B-18-021` | `ch18` L374 | config_workflow | docstringからのAPI自動生成 |
| `B-20-002` | `ch20` L58 | config_workflow | `.env` + `python-dotenv` のパターン |
| `B-21-009` | `ch21` L423 | config_workflow | Biocondaレシピ貢献 |

## 4. 対応はあるが差があるブロック

| ブロック | 対応先 | 差し替え結果 | 差の根拠 |
|---|---|---|---|
| `B-00-001` | `scripts/ch00/find_orfs.py` | 11 failed, 17 passed in 0.76s | ORFとfind_all_orfsは同題材だが入力検証・探索仕様に差がある |
| `B-00-003` | `scripts/ch00/hmm_gene_predict.py` | 8 failed, 1 passed in 0.11s | viterbiの初期化・バックトレースを本文が省略し、そのままでは同じ動作にならない |
| `B-02-031` | `scripts/ch16/ssh_config.example` | 対象外 | 同じSSH configだがホスト名・利用者・ProxyJump構成が異なる章横断候補 |
| `B-08-002` | `scripts/ch08/reverse_complement.py` | 7 passed in 0.01s | 基本処理は同じだが実体に空入力・不正塩基の検証があり例外仕様が異なる |
| `B-08-005` | `tests/ch08/test_seq_stats.py` | 対象外 | 同じgc_content正常系だが入力配列・関数名・クラス構造が異なる |
| `B-08-007` | `tests/ch01/test_gc_content.py` | 対象外 | fixtureとGCフィルタのテスト意図は同じだが、規約上の同章tests/ch08には存在しない |
| `B-09-001` | `scripts/ch09/traceback_demo.py` | 未実行: 本文定義が省略記号を含む: read_fasta_records | 同章・同名だがAST差 |
| `B-09-005` | `scripts/ch09/traceback_demo.py` | 12 passed in 0.02s | 同章・同名だがAST差 |
| `B-09-008` | `scripts/ch09/pdb_demo.py` | 未実行: 本文定義が省略記号を含む: calculate_gc_stats | 同章・同名だがAST差 |
| `B-09-018` | `scripts/ch09/coordinate_bugs.py` | 未実行: 本文定義が省略記号を含む: validate_coordinates | 同章・同名だがAST差 |
| `B-09-020` | `scripts/ch09/path_bugs.py` | 5 passed in 0.01s | 同章・同名だがAST差 |
| `B-11-001` | `scripts/ch11/cli_argparse.py` | 7 passed in 0.13s | 同章・同名だがAST差 |
| `B-11-002` | `scripts/ch11/cli_click.py` | 未実行: 本文定義が省略記号を含む: gc_filter | Click版に対応するが、実体は型ヒント・version・ログ・戻り値等を追加 |
| `B-11-003` | `scripts/ch11/cli_typer.py` | 未実行: 対応スクリプトに直接テストがない | Typer版に対応するが引数・出力・例外処理に差がある |
| `B-11-006` | `scripts/ch11/cli_click.py` | 6 failed, 3 passed in 0.15s | version/helpデコレータ例だが実体のgc_filterシグネチャと処理が異なる |
| `B-11-007` | `scripts/ch11/seqtool.py` | 1 failed, 12 passed in 0.17s | 同章・同名だがAST差 |
| `B-11-011` | `scripts/ch11/cli_click.py` | 未実行: 本文定義が省略記号を含む: gc_filter | 終了コードの例と実体のCLIで入力検証・終了処理が異なる |
| `B-11-013` | `scripts/ch10/config_example.py` | 対象外 | load_configは章横断候補だがdefaultsと戻り値仕様が異なる |
| `B-11-013` | `scripts/ch11/cli_click.py` | 未実行: 本文定義が省略記号を含む: gc_filter | 設定をCLIへ合成する処理は同題材だが実体のオプション・検証が異なる |
| `B-11-030` | `scripts/ch11/seqtool.py` | 1 failed, 12 passed in 0.16s | 同章・同名だがAST差 |
| `B-11-031` | `scripts/ch11/logging_setup.py` | 10 passed in 0.04s | 同名ロギング設定だが引数、ハンドラ再設定、Rich対応に差がある |
| `B-11-031` | `scripts/ch11/progress_demo.py` | 10 passed in 0.03s | 同じsetup_loggingの別実体にも対応する多対多関係 |
| `B-13-005` | `scripts/ch13/seaborn_biodist.py` | 5 passed in 1.68s | 同章・同名だがAST差 |
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
| `B-21-004` | `scripts/ch21/format_question.py` | 5 passed in 0.03s | 同章・同名だがAST差 |
| `B-21-007` | `scripts/ch21/review_helper.py` | 9 passed in 0.02s | 同章・同名だがAST差 |
| `B-21-012` | `scripts/ch21/progress_report.py` | 8 passed in 0.02s | 同章・同名だがAST差 |
| `B-21-014` | `scripts/ch21/analysis_intake.py` | 11 passed in 0.02s | 同章・同名だがAST差 |

## 5. テスト状況

全対象テストファイルを個別実行し、その結果を対応表へ保存した。

| 項目 | 結果 |
|---|---:|
| テストファイル | 71 |
| 章別テストファイル | 69 |
| レビュー用テストファイル | 2 |
| passed | 836 |
| skipped | 1 |
| failed | 0 |
| errors | 0 |

## 6. 多対多対応

1ブロックから複数ファイルへの対応は5件ある。

| 本文ブロック | 対応先 |
|---|---|
| `B-05-004` | `scripts/ch05/mylib/core.py`、`scripts/ch05/mylib/utils.py` |
| `B-05-005` | `scripts/ch05/mylib/__init__.py`、`scripts/ch05/mylib/core.py` |
| `B-08-009` | `tests/ch08/test_reverse_complement.py`、`tests/ch08/test_seq_stats.py` |
| `B-11-013` | `scripts/ch10/config_example.py`、`scripts/ch11/cli_click.py` |
| `B-11-031` | `scripts/ch11/logging_setup.py`、`scripts/ch11/progress_demo.py` |

## 7. 実体側だけにあるファイル

本文コードとの対応がない資産は29件である。
個別の役割とテスト結果は全件表の`scripts`に記録した。

| 役割 | ファイル数 |
|---|---:|
| data_support | 1 |
| figure_generation | 8 |
| package_support | 19 |
| validator | 1 |

## 8. 手法と検証

1. 文字数や言語で除外せず、番号付き章の全コードブロックを抽出した
2. `scripts/ch*` と `tests/ch*` の全実ファイルを別母集団で抽出した
3. 機械分類後、ハッシュ付きoverride台帳の人手判断を適用した
4. Python AST、定義名、順序保存部分列、非Python正規化行を候補生成に使った
5. import、命名、直接パス参照から実体とテストを対応付けた
6. 独立監査でソースハッシュ、ID、参照先、集計、Markdownを再計算する

分類overrideは26件、関係overrideは83件である。override対象の本文ハッシュが変わった場合、生成処理は停止する。

## 9. 全件表の読み方

`blocks`は本文ブロック、`scripts`はスクリプト資産、`test_assets`は章別テスト資産、`test_files`は個別実行結果を保持する。
各関係の`target_file_id`は`scripts`または`test_assets`のIDへ解決され、定義単位の対応には`target_entity_locations`を記録する。

## 10. 限界

1. テスト成功は現行テスト範囲の観測であり、完全な意味論的等価の証明ではない
2. 非Python資産は統一構文木を持たないため、正規化行と人手確認を併用する
3. Git履歴は本文が行範囲、対応先がファイル単位であり偽陽性がありうる
4. 実体配置の要否は現行の執筆規約に基づく
