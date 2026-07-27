# E3解消計画

- 作成日: 2026-07-27
- 基準コミット: `2a51e75855e5372407690d247f1272466c9dab7f`
- 基準対応表: [`code_correspondence.json`](./code_correspondence.json)
- 対象: 対応表でE3と判定された37ブロック
- 状態: 計画レビュー完了（第5巡で新規finding 0件）
- 非目的: 本計画PRでの本文、`scripts/`、`tests/`、対応表の修正

## 1. 目的

本文と対応実体の間にある入出力、分岐、例外、定数、API、設定値の差を解消する。
実体を正解として本文を機械的に上書きするのではなく、本文の教育上の役割を確認し、
完全例はE0またはE1、意図的な抜粋はE2へ収束させる。

完了時には、再生成した対応表でE3とE5がともに0件であり、基準E3 37件すべての
解消根拠、対応実体、テスト結果を追跡できる状態にする。

## 2. 基準状態

現行の追跡済み対応表には生成時のソースコミットとして `e585e1d` が記録されている。
そこで計画作成時に、マージ後の基準コミット `2a51e75` から一時領域へ対応表を再生成し、
独立監査を実行した。対応関係とソースハッシュは再計算したが、テスト結果は追跡済み
対応表から再利用した。906 passed、7 skippedは基準値であり、この計画レビューで
テストを再実行した結果ではない。各実装PRでは対象テストと全体テストを再実行する。

| 項目 | 実測値 |
|---|---:|
| 本文コードブロック | 529 |
| 配置必須 | 134 |
| E0 | 40 |
| E1 | 38 |
| E2 | 19 |
| E3 | 37 |
| E5 | 0 |
| EN | 395 |
| `scripts/ch*` の実ファイル | 174 |
| テスト結果 | 906 passed、7 skipped、0 failed |
| 構造検査 | 27 findings |
| 相互参照検査 | 0 findings |

再生成したE3集合は追跡済み対応表の37件と一致し、独立監査の全チェックが成功した。
E3の内訳は実装コード29件、設定・ワークフロー6件、テストコード2件である。
構造検査27件は既存の著者・注意ページの必須セクション判定8件と、
太字内カッコ・カギ括弧19件であり、E3作業とは別スコープである。

差し替え試験は関係単位で12成功、8失敗、8未実行である。ただし `B-11-031` は
1ブロックから2実体への関係を持つため、ブロック単位では11件が成功している。
差し替え成功は現行テスト範囲での観測であり、本質的一致の証明には使わない。

## 3. 解消原則

### 3.1 収束先

| 解消型 | 条件 | 目標判定 |
|---|---|---|
| A. 判定訂正 | 観測可能な入出力・例外・副作用が同じで、差が局所名、docstring、冗長な分岐だけ | E1 |
| B. 完全同期 | 本文が単体で完結する完全例 | E0 |
| C. 抜粋同期 | 本文が対応実体の順序と制御構造を保つ、境界の明確な抜粋 | E2 |
| D. 実体拡張 | 本文の教育目的に必要な処理が既存実体にない | 実体とテストを先に変更後、E0またはE2 |
| E. 対応訂正 | 章横断の弱い候補や不要な多対多関係が原因 | 正しい実体へ対応し、E0〜E2 |

E1への訂正には、正常系だけでなく境界値、例外、副作用の手動比較とテストが必要である。
差し替え試験の成功だけではE1にしない。E2は行集合の包含だけでは認めず、順序、
制御構造、変数依存、抜粋の前後説明が実体と矛盾しないことを確認する。

### 3.2 修正順

本文のコードへ手を入れる前に、対応する `scripts/` または `tests/` を確認する。
実体の変更が必要なら、実体を先に変更して対象テストを通し、その後に本文へ反映する。
本文が意図的な抜粋なら、完全実体を動作させたうえで、抜粋の開始・終了と省略内容を
本文で明示する。

本文だけを先に変更するのは、型Aの判定訂正、または既存のテスト済み実体から
そのまま同期できる場合に限る。

### 3.3 配置判定

37件はすべて現行規約で配置必須と判定済みである。本計画ではENへの移動を予定しない。
実装時に悪例、ライブラリ利用紹介、概念断片であることが新たに判明した場合は、
当該PRを止め、配置判定を変更する根拠と件数保存則を計画へ追記してから再開する。

## 4. 完了条件

1. 基準E3 37件すべてに、解消型、一次対応先、目標判定、検証結果がある
2. 再生成した対応表でE3が0件、E5が0件である
3. 本文529ブロック、配置必須134件、EN 395件を維持する
4. 新しいE3、E4、E5を発生させない
5. 変更・新設した実体を対応テストが直接importまたは実ファイル読込で検証する
6. Python実装は正常系、境界値、例外、必要な副作用を検証する
7. 設定・ワークフローは構文、必須項目、参照先、本文で説明する値を検証する
8. 実体テスト後に本文を同期し、完全例か抜粋かを本文の説明と対応表に記録する
9. 対応表を決定的に再生成し、独立監査の全項目が成功する
10. 対象章テスト、全体テスト、Ruff、対象Pythonの型検査が成功する
11. 構造検査と相互参照検査で新規findingを発生させない
12. `git diff --check` が成功し、対象外の章と実体に変更がない

計画上の一次目標はE0へ11件、E1へ3件、E2へ23件を移すことである。したがって
予定する最終内訳はE0 51、E1 41、E2 42、E3 0、E5 0、EN 395、合計529である。
実装時にE2予定のブロックをより厳密なE0またはE1へ収束できる場合は許容するが、
E0〜E2の合計134、EN 395、全体529を保存する。

## 5. 37件の解消マトリクス

### 5.1 ch13・ch21: 可視化と協働支援

| ID | 現在の差 | 解消方針 | 一次対応先 | 目標 | 必須検証 |
|---|---|---|---|---|---|
| `B-13-005` | 本文に出力先引数と保存分岐がない | B、テスト済み関数へ完全同期 | `scripts/ch13/seaborn_biodist.py` | E0 | 既存可視化テスト、戻り値、保存あり・なし |
| `B-21-004` | 完全実体のうち環境収集だけを簡略化 | C、実体の連続する抜粋へ同期 | `scripts/ch21/format_question.py` | E2 | 未導入パッケージ、OS・Python情報 |
| `B-21-007` | ローカル名とログ処理を省略 | C、関数本体の矛盾しない抜粋へ同期 | `scripts/ch21/review_helper.py` | E2 | 型ヒントあり・なし、インデント |
| `B-21-012` | 空行と不正行の処理が実体と異なる | C、入力処理を実体の抜粋へ同期 | `scripts/ch21/progress_report.py` | E2 | 空行、不正行、区切り文字を含む件名 |
| `B-21-014` | 空入力と局所名・ログ処理が異なる | C、検証処理を実体の抜粋へ同期 | `scripts/ch21/analysis_intake.py` | E2 | 空入力、列欠落、空セル |

### 5.2 ch08・ch09: テストとデバッグ

| ID | 現在の差 | 解消方針 | 一次対応先 | 目標 | 必須検証 |
|---|---|---|---|---|---|
| `B-08-002` | 実体だけに空文字列の早期returnがある | A、戻り値・例外が全入力で同じことを確認 | `scripts/ch08/reverse_complement.py` | E1 | 空、小文字、無効塩基、通常配列 |
| `B-08-005` | 本文は単独関数、実体はクラス内メソッド | D、`tests/ch08` 側を先に整理して本文と同期 | `tests/ch08/test_seq_stats.py` | E0 | `pytest.approx()`、代表値、テスト収集 |
| `B-08-007` | 対応先が章をまたぎ、同章実体がない | D、同じfixture例を `tests/ch08` へ実体化 | `tests/ch08/test_gc_fixture.py` | E0 | fixture注入、閾値境界、3レコード |
| `B-09-001` | 本文は `read_text()` 以降を省略した非実行断片 | C、省略境界を明示した実体の抜粋へ同期 | `scripts/ch09/traceback_demo.py` | E2 | ファイル欠落、空FASTA、複数レコード |
| `B-09-005` | 例外メッセージの一時変数だけが異なる | A、例外型・引数・戻り値の同一性を確認 | `scripts/ch09/traceback_demo.py` | E1 | 存在キー、不在キー、例外メッセージ |
| `B-09-008` | 本文は `breakpoint()` を含むが実体は通常実行用 | D、デバッグ専用関数を追加し抜粋を同期 | `scripts/ch09/pdb_demo.py` | E2 | `breakpoint` をmonkeypatchし、空・通常入力 |
| `B-09-018` | 座標検証の分岐と例外条件が一部だけ | C、実体の分岐を保つ抜粋へ同期 | `scripts/ch09/coordinate_bugs.py` | E2 | BED/GFF境界、start > end、不明形式 |
| `B-09-020` | 例外メッセージの組み立てだけが異なる | A、パス解決と例外の同一性を確認 | `scripts/ch09/path_bugs.py` | E1 | `~`、相対パス、欠落パス |

### 5.3 ch02・ch14・ch16: 接続設定とワークフロー

| ID | 現在の差 | 解消方針 | 一次対応先 | 目標 | 必須検証 |
|---|---|---|---|---|---|
| `B-02-031` | ch16の多段SSH設定だけが弱い章横断候補 | D、ch02の基本SSH例を独立実体化 | `scripts/ch02/ssh_config.example` | E0 | `ssh -G -F`、Host・HostName・User |
| `B-14-002` | `threads: 4` と設定ファイル参照が異なる | C、実体の設定参照を保つ抜粋へ同期 | `scripts/ch14/Snakefile` | E2 | dry-run、config値、入出力 |
| `B-14-014` | URL省略、変数、clean処理が異なる | B、実行可能なMakefileへ完全同期 | `scripts/ch14/Makefile` | E0 | `make -n`、依存関係、clean対象 |
| `B-14-017` | `protected` と `temp`、BAMパスが異なる | C、実体のライフサイクル指定へ同期 | `scripts/ch14/Snakefile` | E2 | dry-run、最終出力保護、中間出力 |
| `B-14-019` | shell文字列が説明用省略形 | C、log指定を含む実体の抜粋へ同期 | `scripts/ch14/Snakefile` | E2 | dry-run、logパス、shell参照 |
| `B-16-016` | Host別名とHostNameが本文と実体で異なる | B、実体を本文の多段SSH例へ完全同期 | `scripts/ch16/ssh_config.example` | E0 | `ssh -G -F`、ProxyJump展開、別名解決 |

### 5.4 ch17・ch19・ch20: 性能、DB、セキュリティ

| ID | 現在の差 | 解消方針 | 一次対応先 | 目標 | 必須検証 |
|---|---|---|---|---|---|
| `B-17-019` | 本文はkernprof注入前提、実体にはデコレータ自体がない | D、任意依存の `profile`、no-op fallback、最小main入口を実体へ追加後、抜粋を同期 | `scripts/ch17/profiling_demo.py` | E2 | 通常import、fallback、kernprof実行、計算結果 |
| `B-17-031` | 実体はrecords入力のgeneratorだけで、本文のpath入力APIがない | D、本文名のlist版・generator版wrapperを両方追加 | `scripts/ch17/generator_fastq.py` | E0 | 両版の同一結果、遅延評価、閾値境界 |
| `B-17-037` | 本文に2サンプル未満の検証がない | B、検証を含む実体へ完全同期 | `scripts/ch17/chunk_processing.py` | E0 | 0件・1件・複数件、複数チャンク |
| `B-19-022` | 本文はSQL直書き、実体は関数分割と追加列 | C、実体の公開関数を使う抜粋へ同期 | `scripts/ch19/local_db.py` | E2 | schema、挿入、検索、再実行 |
| `B-20-004` | 戻り値、パターン、引数、除外処理が異なる | C、`scan_content()` の正確な中核抜粋へ同期 | `scripts/ch20/secret_scanner.py` | E2 | 複数パターン、行番号、偽陽性、戻り値型 |
| `B-20-009` | 負の年齢と非正bin幅の検証がない | B、入力検証を含む実体へ完全同期 | `scripts/ch20/anonymize_metadata.py` | E0 | 境界年齢、負値、0以下のbin幅 |

### 5.5 ch11: CLI

| ID | 現在の差 | 解消方針 | 一次対応先 | 目標 | 必須検証 |
|---|---|---|---|---|---|
| `B-11-001` | 型注釈と引数処理の細部が異なる | B、テスト済み `parse_args()` へ完全同期 | `scripts/ch11/cli_argparse.py` | E0 | stdin/stdout既定、範囲、version |
| `B-11-002` | Click版本文は処理本体を省略 | C、デコレータとシグネチャを連続抜粋化 | `scripts/ch11/cli_click.py` | E2 | help、version、範囲、入出力 |
| `B-11-003` | Typer版の引数・出力・例外処理が異なり直接テストなし | D、実体を正としCLIテストを追加後に抜粋同期 | `scripts/ch11/cli_typer.py` | E2 | help、正常入力、範囲外、出力先 |
| `B-11-006` | help/versionだけの断片を関数全体として対応 | E、デコレータ範囲の抜粋関係へ訂正 | `scripts/ch11/cli_click.py` | E2 | help本文、version、CLI本体の既存テスト |
| `B-11-007` | 本文のgroupにversion処理がない | C、共通optionを含むgroup抜粋へ同期 | `scripts/ch11/seqtool.py` | E2 | help、version、各subcommand |
| `B-11-011` | 本文の終了処理が実体の入力検証と異なる | C、実体の例外変換部分へ同期 | `scripts/ch11/cli_click.py` | E2 | 終了コード0・1・2、stderr |
| `B-11-013` | ch10設定関数とch11 CLIの弱い多対多対応 | D・E、ch11専用の設定合成実体を追加 | `scripts/ch11/config_layering.py` | E2 | 既定値、YAML、CLI上書き、欠落・不正設定 |
| `B-11-024` | 関数名、ループ、進捗メッセージが異なる | C、`filter_cmd` のstdout/stderr処理へ同期 | `scripts/ch11/seqtool.py` | E2 | TTY有無、progress有無、stdout純度 |
| `B-11-030` | 本文groupにversion処理がない | C、log-levelを含むgroup抜粋へ同期 | `scripts/ch11/seqtool.py` | E2 | log-level優先順位、verbose、version |
| `B-11-031` | 本文、logging実体、progress demoが不適切な多対多 | B・E、logging実体へ完全同期しdemo関係を除く | `scripts/ch11/logging_setup.py` | E0 | 不正level、stderr、file、Rich有無、handler重複 |

### 5.6 ch00: ORFとHMM

| ID | 現在の差 | 解消方針 | 一次対応先 | 目標 | 必須検証 |
|---|---|---|---|---|---|
| `B-00-001` | 逆鎖処理と `_find_stop` の引数を省略 | C、6フレーム探索を保つ実体の抜粋へ同期 | `scripts/ch00/find_orfs.py` | E2 | 順鎖・逆鎖、座標、最小長、空入力 |
| `B-00-003` | 初期化・放出関数・バックトレースが未定義 | C、Viterbi再帰部の正確な抜粋へ同期 | `scripts/ch00/hmm_gene_predict.py` | E2 | 空・1コドン・複数コドン、経路復元 |

## 6. 実施単位と予定推移

計画PRがマージされた後、各実施単位をマージ済み `main` から別ブランチで開始する。
各PRは実体、テスト、対応本文、対応表更新を同じレビュー単位へ含める。

| 順序 | ブランチ案 | 対象 | 件数 | 期待E3 |
|---:|---|---|---:|---:|
| 0 | `revise/e3-baseline` | 対応表を現行コミットから再生成し基準を固定 | 0 | 37 |
| 1 | `revise/e3-ch13-ch21` | ch13、ch21 | 5 | 32 |
| 2 | `revise/e3-ch08-ch09` | ch08、ch09 | 8 | 24 |
| 3 | `revise/e3-config-workflows` | ch02、ch14、ch16 | 6 | 18 |
| 4 | `revise/e3-ch17-ch20` | ch17、ch19、ch20 | 6 | 12 |
| 5 | `revise/e3-ch11-cli` | ch11 | 10 | 2 |
| 6 | `revise/e3-ch00-algorithms` | ch00 | 2 | 0 |

順序0は追跡済み対応表の `source_commit` をマージ後のコミットへ更新し、以後の差分を
正確に比較するために必要である。内容分類を変えず、37件の集合一致を独立監査する。

## 7. 各実施単位の手順

1. 対象ID、本文ハッシュ、対応実体、関連テスト、基準判定を記録する
2. 本文の前後を読み、完全例、抜粋、教育上の段階例のいずれかを確定する
3. 入出力、例外、境界値、副作用、設定値を比較表へ起こす
4. 型Aは同値性をテストし、型B〜Eは実体またはテストを先に修正する
5. 対象章テストを実行する
6. テスト済み実体から本文を同期し、抜粋なら省略境界を明記する
7. 本文と実体の正規化比較と人手比較でE0〜E2を確定する
8. 変更した本文ハッシュ、目標判定、対応先、差の根拠を
   `scripts/review/code_correspondence_overrides.json` へ反映する
9. 実体、テスト、本文、overrideをソースコミットとして先にコミットする
10. そのソースコミットをHEADにして対応表を決定的に再生成し、独立監査を実行する
11. 生成したJSON・Markdownだけを後続コミットにし、同じPRへ含める
12. 対象ID集合、E判定件数、本文総数、配置件数の保存則を確認する
13. 全体検証を実行し、PR本文へ変更根拠、検証結果、未実行項目を記録する

この2段階コミットにより、対応表の `source_commit` は実体、テスト、本文、overrideを
含むソースコミットを指す。GitHub側でsquash mergeされた場合はコミットIDがmainへ
残らないため、実内容の同一性は `source_snapshot_sha256` を最終根拠とする。
overrideの `block_sha256` だけを先に書き換えて生成器の拒否を回避してはならない。
本文差分と新しい判定根拠をレビューした後に、hashと根拠を同じ差分で更新する。

## 8. 検証

### 8.1 共通コマンド

```bash
.venv/bin/pytest tests/chNN/ -q -p no:cacheprovider
.venv/bin/pytest tests/ -q -p no:cacheprovider
.venv/bin/ruff check scripts tests
.venv/bin/mypy <変更したPythonモジュール>
python3 scripts/review/check_structure.py
python3 scripts/review/check_xref.py
.venv/bin/python scripts/review/build_code_correspondence.py \
  --root . \
  --output docs/review/code_correspondence.json \
  --report docs/review/code_correspondence.md \
  --check-determinism
.venv/bin/python scripts/review/audit_code_correspondence.py \
  --root . \
  --input docs/review/code_correspondence.json \
  --report docs/review/code_correspondence.md
git diff --check
```

`check_structure.py` は各ブランチ開始時の既存finding数を基準にし、対象PRで新規findingを
増やさない。相互参照検査は0件を維持する。対応表生成では既存結果を無条件に再利用せず、
変更した対象テストと関係する差し替え試験を必ず再実行する。

### 8.2 追加検証

| 対象 | 追加検証 |
|---|---|
| SSH config | `ssh -G -F <config> <host>` で構文と展開値を確認 |
| Snakefile | Snakemake dry-run、設定値と参照ファイルの静的検証 |
| Makefile | `make -n`、ターゲット依存関係、clean対象の静的検証 |
| CLI | Click/Typer/argparseのrunnerまたはsubprocessでstdout、stderr、終了コード |
| 可視化 | 非対話backendでFigure、軸、保存ファイルを検証 |
| line_profiler | 通常importとkernprofが注入するデコレータ相当の両方を検証 |
| SQLite | 一時DBを使い、schema、挿入、検索、再実行を検証 |

ネットワーク接続、実SSH接続、大規模データ、コンテナbuildは不要である。Snakemakeは
既存資産のdry-runに限定し、データダウンロードや本解析は行わない。計画作成時点では
`snakemake` はPATH上にない。ch14バッチ開始時に利用可能性を再確認し、既に検証済みの
一時実行環境を使える場合は、次の形式で固定バージョンを記録して実行する。

```bash
E3_SNAKEMAKE_RUN_DIR="$(
  mktemp -d /private/tmp/ai-biocode-kata-e3-snakemake.XXXXXX
)"
cp scripts/ch14/config.yaml "$E3_SNAKEMAKE_RUN_DIR/config.yaml"
UV_CACHE_DIR=/private/tmp/ai-biocode-kata-e3-uv-cache \
uvx --python 3.13 --from 'snakemake==9.23.1' \
  snakemake --snakefile scripts/ch14/Snakefile \
  --directory "$E3_SNAKEMAKE_RUN_DIR" --cores 1 --dry-run \
  --config 'samples=[]'
```

`samples=[]` は実データなしで構文、設定読込、DAG構築を確認するための上書きである。
各ruleの入出力、値、参照先は `tests/ch14/test_workflow_assets.py` で実資産から別途確認する。
作業ディレクトリと `.snakemake/` は `mktemp` で作る一時領域へ隔離し、リポジトリへ
生成物を残さない。計画レビューではSnakemake 9.23.1でこのdry-runが成功した。
cacheに対象バージョンがなくダウンロードが必要な場合は、ネットワーク利用の承認を得る。
Snakemakeを実行できず、ユーザーから静的検証だけでよいとの明示的判断もない場合は、
ch14バッチを完了扱いにしない。

### 8.3 予定テストファイル

既存テストで不足する動作だけを追加し、同じ検証を別ファイルへ重複させない。

| 対象 | 予定テスト |
|---|---|
| ch00 ORF・HMM | 既存 `tests/ch00/test_find_orfs.py`、`tests/ch00/test_hmm_gene_predict.py` |
| ch02 SSH | `tests/ch02/test_ssh_config.py` |
| ch08 test block | 既存 `tests/ch08/test_seq_stats.py`、新規 `tests/ch08/test_gc_fixture.py` |
| ch09 debug | 既存章テストを拡張し、`tests/ch09/test_pdb_demo.py` にdebug hookを追加 |
| ch11 CLI | 既存CLIテスト、`tests/ch11/test_cli_typer.py`、`tests/ch11/test_config_layering.py` |
| ch13 visualization | 既存 `tests/ch13/test_seaborn_biodist.py` |
| ch14 workflow | 既存 `tests/ch14/test_workflow_assets.py` をmain `Snakefile` と `Makefile` の直接検証へ拡張 |
| ch16 SSH | 新規 `tests/ch16/test_ssh_config.py` |
| ch17 performance | 既存 `tests/ch17/test_profiling_demo.py`、`test_generator_fastq.py`、`test_chunk_processing.py` |
| ch19 SQLite | 既存 `tests/ch19/test_local_db.py` |
| ch20 security | 既存 `tests/ch20/test_secret_scanner.py`、`test_anonymize_metadata.py` |
| ch21 collaboration | 既存の対応する4テストファイル |

計画作成時点の `.venv` には `line_profiler` と `kernprof` がない。ch17の通常テストは
no-op fallbackを使って任意依存なしで実行可能にするが、PR完了前に一時環境へ
`line-profiler` 5.0.2を導入し、最小main入口に対して本文に示す
`kernprof -l -v` のsmoke testを実行する。

```bash
UV_CACHE_DIR=/private/tmp/ai-biocode-kata-e3-uv-cache \
uvx --python 3.13 --from 'line-profiler==5.0.2' \
  kernprof -l -v \
  -o /private/tmp/ai-biocode-kata-e3-profiling.lprof \
  scripts/ch17/profiling_demo.py
```

ダウンロードが必要なら承認を得る。導入できず、ユーザーから通常importの検証だけでよいとの
明示的判断もない場合は、`B-17-019` を完了扱いにしない。

## 9. リスクと停止条件

| リスク | 対応 |
|---|---|
| テスト成功だけでE1へ過小評価する | 正常系・境界・例外・副作用の手動比較を必須化 |
| 教育上の段階例を完成版で上書きする | TDDやデバッグの段階性を保持し、必要なら専用実体を追加 |
| 抜粋が実行可能な完全例に見える | 省略境界と完全実体への相対パスを本文で明示 |
| 1実体を複数の異なる説明へ無理に対応させる | 章固有実体または定義単位の関係へ分離 |
| 本文修正でブロックIDがずれる | 章内順序を維持し、ハッシュ変更後に全件再生成 |
| 外部CLIの導入が必要になる | 静的検証を先に行い、導入が不可欠ならユーザー判断まで停止 |
| 対応表overrideだけで差を隠す | ソース比較、テスト、根拠の3点が揃わなければE3を維持 |

次の場合は対象PRを完了扱いにせず、ユーザーへ判断を求める。

- 有効なコードへ直すと本文の教育上の主張が変わる
- 公開APIまたは既存サンプルの互換性を壊す必要がある
- 新しい本番依存を追加する必要がある
- ENへの配置判定変更、本文ブロック追加・削除、対象外章の大幅改稿が必要になる
- 必須の外部検証を現行環境で実行できない

## 10. 計画レビュー記録

### 第1巡

原台帳との集合一致、重複、目標判定の算術、実施単位の件数推移、コマンドと既存パスの
実在性をレビューした。

- 解消マトリクスは37件、重複0件で、原台帳のE3集合と完全一致した
- 目標はE0 11件、E1 3件、E2 23件で、合計37件であった
- 実施単位は5 + 8 + 6 + 6 + 10 + 2 = 37で、E3の予定推移と一致した
- 記載した既存の一次対応先はすべて実在した

| ID | finding | 対応 |
|---|---|---|
| P1 | 基準表の906 passed、7 skippedが計画作成時の再実行結果に読めた | 既存対応表から再利用した基準値であることと、各実装PRで再実行することを明記 |
| P2 | 実体拡張を予定する項目について、新設・拡張するテストファイルの配置が一部不明 | 章別の予定テストファイル表を追加 |
| P3 | Snakemake dry-runを要求しているが、現環境のPATHに `snakemake` がなく実行方法が不明 | `uvx` による一時実行形式と、ダウンロード承認・停止条件を追加 |

3 findingsを反映した。次巡では、本文の教育目的、完全例と抜粋の区別、E1判定の妥当性、
既存APIを壊さない修正順をレビューする。

### 第2巡

全37件について本文前後と一次対応先を読み、教育目的、完全例と抜粋、既存API、
検証可能性をレビューした。

| ID | finding | 対応 |
|---|---|---|
| P4 | `B-17-019` は実体にfallbackがある前提だったが、実際の `profiling_demo.py` には `@profile` もfallbackもない | 任意依存の `profile` とno-op fallbackを実体へ先に追加し、通常importと実kernprofを別々に検証する型Dへ訂正 |
| P5 | `B-17-031` はlist版だけを追加しても、本文の `filter_reads_generator(path, ...)` と既存 `filter_by_length(records, ...)` のAPI差が残る | 本文名のlist版・generator版wrapperを両方追加し、同一結果と遅延評価を検証 |
| P6 | `tests/ch16/test_ssh_config.py` を既存と記載したが実在しない | 新規テストであると訂正 |
| P7 | 既存 `tests/ch14/test_workflow_assets.py` はmain `Snakefile` と `Makefile` を直接検証していない | 両実資産を直接読むテストへ拡張すると明記 |
| P8 | Snakemakeコマンドの `--directory .` では `config.yaml` と相対入出力の基準が曖昧 | `--directory scripts/ch14 --snakefile Snakefile` へ訂正 |

5 findingsを反映した。次巡では、検証コマンドの副作用、外部依存、各PRの独立性、
対応表生成時のハッシュ・override更新、停止条件をレビューする。

### 第3巡

検証コマンドの実行性、対応表生成とGit履歴の関係、override台帳、外部ツールの
再現性をレビューした。

| ID | finding | 対応 |
|---|---|---|
| P9 | ソース未コミットのまま対応表を生成すると、`source_commit` が実内容より古いHEADを記録する | ソースを先にコミットし、そのHEADから生成物を作る2段階コミットを各PRの手順へ追加。squash時はsnapshot hashを最終根拠にする |
| P10 | 本文ハッシュ変更後のoverride更新手順がなく、hashだけを機械更新して差を隠せる余地があった | 本文差分と判定根拠のレビュー後に、hash・判定・対応根拠を同時更新する順序を追加 |
| P11 | Snakemakeとline_profilerの一時実行が版未固定だった | 計画レビューで動作確認したSnakemake 9.23.1、line-profiler 5.0.2へ固定 |
| P12 | 修正後のSnakemakeコマンドも `--snakefile` の解決順と入力欠落により、そのままでは失敗した | リポジトリ相対のSnakefileパス、ch14作業ディレクトリ、`samples=[]` を組み合わせ、実際に成功したコマンドへ訂正 |

4 findingsを反映した。次巡では、37件の集合と算術を再計算し、全パス、全コマンド、
レビュー記録、変更範囲をfresh eyeで独立監査する。

### 第4巡

原台帳からID集合と算術を再計算し、計画内パス、コマンドの副作用、検査基準、
作業ツリーの変更範囲を独立にレビューした。

- E3マトリクスは37件、重複0件、欠落0件、余分0件であった
- 目標内訳はE0 11件、E1 3件、E2 23件であった
- `tests/review/` は63 passedであった
- 構造検査は既存27件、相互参照検査は0件であった

| ID | finding | 対応 |
|---|---|---|
| P13 | Snakemake dry-runが `scripts/ch14/.snakemake/` を生成し、作業ツリーを汚した | 設定を `mktemp` の一時作業領域へコピーし、`--directory` を一時領域へ変更。レビュー時の生成物は削除 |
| P14 | kernprofは既定でスクリプトの近くに `.lprof` を生成する | `-o /private/tmp/ai-biocode-kata-e3-profiling.lprof` を指定 |
| P15 | 新規findingなしを比較するための構造検査・相互参照検査の基準値が基準表にない | 構造27件の内訳と相互参照0件を基準状態へ追加 |

3 findingsを反映した。次巡では同じ独立監査を最初から再実行し、新規findingがなければ
計画レビューを収束とする。

### 第5巡

第4巡の修正後、原台帳から独立監査を最初から再実行した。

- 原台帳のE3集合と解消マトリクスは37件すべて一致した
- 重複、欠落、余分なIDは0件であった
- 目標内訳はE0 11件、E1 3件、E2 23件で、合計37件であった
- 実施単位は5 + 8 + 6 + 6 + 10 + 2 = 37であった
- 一次対応先は既存34件、新規予定3件で、想定外の欠落は0件であった
- 計画内の相対リンクはすべて解決した
- `tests/review/` は63 passedであった
- `git diff --check` は成功した
- 計画書と既存の未追跡 `sandbox/` 以外に作業ツリー差分はなかった

新規findingは0件であった。これを計画レビューの収束条件とし、実装は計画PRの
ユーザーマージ後に、順序0から別PRとして開始する。
