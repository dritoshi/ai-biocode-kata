# E5解消計画

- 作成日: 2026-07-25
- 基準コミット: `8153267`
- 基準対応表: [`code_correspondence.json`](./code_correspondence.json)
- 対象: 対応表でE5と判定された39ブロック
- 状態: 計画レビュー完了（第5巡で新規finding 0件）
- 非目的: 本計画作成時点での本文、`scripts/`、`tests/` の修正、コミット、プッシュ

## 1. 目的

本文に掲載する実装コード、テストコード、設定・ワークフロー定義について、
規約上必要な実体を `scripts/ch*` または `tests/ch*` に配置し、実体を直接読むテストで
検証したうえで本文と同期する。E5を機械的に「39ファイル新設」と解釈せず、既存実体との
対応漏れと配置不要例を先に再判定する。

完了時には、再生成した対応表でE5が0件であり、E5をE3やENへ移した場合も根拠と
対応先を追跡できる状態にする。

## 2. 前提と制約

### 2.1 執筆規約

- 実装コード、テストコード、設定・ワークフロー定義は実体配置が必要である
- 本文のコードを変える場合は、実体を先に修正し、テスト後に本文へ反映する
- 本文が意図的な抜粋なら、実体が動作し、抜粋部分に誤りがなければ完全一致は要求しない
- Pythonコードには型ヒントを付け、FASTA処理には `Bio.SeqIO` を使う
- `print()` をログ用途に使わず、ハードコードされた環境固有パスを置かない
- 新規実装にはテストを追加する

### 2.2 Git運用

現行ワークツリーは `revise/code-sync-inventory` 上にあり、対応表3成果物が未コミットである。
E5実装を同じ差分へ混ぜない。実装開始前に対応表を独立したPRとして確定し、ユーザーによる
マージ後の `main` から、実施単位ごとに `revise/e5-*` ブランチを作る。エージェントは
PRをマージしない。

本計画の作成では、新しいコミットとプッシュを行わない。

### 2.3 判定の扱い

E5の解消方法は次の3種類とする。

| 解消型 | 条件 | 完了後の判定 |
|---|---|---|
| A. 実体新設・既存実体拡張 | 規約上配置が必要で、対応実体がない | E0、E1、E2 |
| B. 既存対応の回収 | 対応実体が存在するが、名前や章をまたぐため検出されなかった | E1、E2、E3 |
| C. 配置不要への訂正 | 悪例、演習、ライブラリ利用紹介など、規約上実体が不要 | EN |

E3へ移すだけでは差異は解消しない。E5作業では「対応先不明」を解消したものとして記録し、
内容差は後続のE3解消作業へ引き渡す。

## 3. 完了条件

1. 基準E5 39件すべてに、解消型、対応先、テスト、本文反映方針がある
2. 新規・拡張するすべての実体を、テストが実ファイルから直接読み込む
3. Python実装は正常系、境界値、エラー系をテストする
4. 設定資産は構文だけでなく、必須キー、参照ファイル、相互整合をテストする
5. 外部ランタイムを通常テストへ導入できない資産も、合成文字列ではなく実資産を静的検証する
6. 実体とテストを通した後にだけ、本文へ必要な同期修正を行う
7. `pytest tests/ -q -p no:cacheprovider` が成功する
8. `ruff check scripts tests` が成功する
9. 対応表を全件再生成し、E5が0件になる
10. E5からE3・ENへ移した項目の根拠が対応表と作業記録に残る
11. `git diff --check` が成功し、対象外の章・実体に変更がない
12. 対応表の生成・監査処理がリポジトリ内のテスト済みツールとして再実行できる

## 4. 39件の解消マトリクス

### 4.1 シェル、基本設定、開発環境

| ID | 解消型 | 対応先案 | 必須検証 |
|---|---|---|---|
| `B-02-025` | A、4ブロックを1実体へ統合 | `scripts/ch02/safe_fastq_qc.sh` | `bash -n`、`set -euo pipefail` |
| `B-02-026` | A、同上 | `scripts/ch02/safe_fastq_qc.sh` | 一時ディレクトリと偽 `fastqc` で正常系 |
| `B-02-028` | A、同上 | `scripts/ch02/safe_fastq_qc.sh` | 入力欠落で非0終了、出力先作成 |
| `B-02-029` | A、同上 | `scripts/ch02/safe_fastq_qc.sh` | 複数サンプル処理、空入力 |
| `B-04-004` | A | `scripts/ch04/config_example.yaml` | `yaml.safe_load()`、samples・reference・threads |
| `B-04-005` | A、本文のPEP 621構造も修正 | `scripts/ch04/pyproject_example.toml` | `tomllib`、`project.dependencies` が配列 |
| `B-06-006` | A | `scripts/ch06/examples/requirements.txt` | 依存指定の構文、上限・下限 |
| `B-06-007` | A | `scripts/ch06/examples/pyproject.toml` | `tomllib`、必須メタデータ、依存配列 |
| `B-06-008` | A | `scripts/ch06/examples/environment.yml` | YAML構文、チャネル順、pip節 |
| `B-06-012` | A | `scripts/ch06/examples/condarc.example` | YAML構文、`channel_priority: strict` |

`B-04-005` の本文は `[project.dependencies]` をTOMLテーブルとしているが、PEP 621の
`dependencies` は `[project]` 内の文字列配列である。本文をそのまま実体へコピーせず、
有効な実体とテストを先に作成してから本文を修正する。

### 4.2 テスト、品質設定、CI

| ID | 解消型 | 対応先案 | 必須検証 |
|---|---|---|---|
| `B-08-008` | A | `tests/ch08/conftest.py`、`tests/ch08/data/sample.fasta` | fixtureを実際のテストから利用し、`Bio.SeqIO` で読める |
| `B-08-014` | A、3ブロックを1実体へ統合 | `scripts/ch08/examples/pyproject.toml` | Ruff基本設定 |
| `B-08-015` | A、同上 | `scripts/ch08/examples/pyproject.toml` | `per-file-ignores` |
| `B-08-020` | A、同上 | `scripts/ch08/examples/pyproject.toml` | mypy設定 |
| `B-08-022` | A | `scripts/ch08/examples/pre-commit-config.yaml` | 必須repo、rev、hook、追加依存 |
| `B-08-025` | A | `scripts/ch08/examples/claude-settings.json` | JSON構文、イベント・matcher・command、Codex側の同等機能の有無 |
| `B-08-026` | A、2ブロックを1実体へ統合 | `scripts/ch08/examples/github-actions-ci.yml` | checkout、Python、ruff、mypy、pytest |
| `B-08-027` | A、同上の抜粋 | `scripts/ch08/examples/github-actions-ci.yml` | 3.11〜3.14のmatrix、式の保持 |

CI、pre-commit、エージェントフックのバージョンとスキーマは変化するため、実装時に
公式一次情報を確認する。エージェントフックはClaude Code CLIとCodex CLIを別々に確認し、
同等機能が確認できない場合は架空の設定例を作らず、対照表で差を明示する。通常のpytestでは
ネットワーク処理を行わず、実ファイルの構文と構造を検証する。利用可能なら `actionlint` と
`pre-commit validate-config` も実行する。

### 4.3 Python実装と近接設定

| ID | 解消型 | 対応先案 | 必須検証 |
|---|---|---|---|
| `B-10-004` | A | `scripts/ch10/package_example/pyproject.toml` | PEP 621構造、build backend、CLI entry point |
| `B-10-023` | A、既存読込実装と接続 | `scripts/ch10/config.yaml` | `load_config()` が実ファイルを読み、値をマージ |
| `B-10-033` | A、本文はE2抜粋化 | `scripts/ch10/pipeline_fail_fast.py` | 入力・reference欠落、出力作成、処理開始順 |
| `B-11-024` | B、重複実装しない | `scripts/ch11/seqtool.py:filter_cmd` | 既存CLIテスト、stdout・stderr、TTY分岐を追加確認 |
| `B-12-002` | C、`str.count()` の利用紹介 | 実体新設なし | 前後文脈と規約表の根拠を対応表に記録 |
| `B-13-008` | A | `scripts/ch13/plot_config.py` | rcParams反映、他テストへの状態漏れを復元 |
| `B-13-010` | A | `scripts/ch13/tracks.ini` | INI構文、coverage・peaks・genesの必須値 |
| `B-17-022` | A | `scripts/ch17/memory_target.py` | 小さいshapeで平均値・再現性、既定値の型 |
| `B-17-036` | A | `scripts/ch17/streaming_fasta.py` | 一時FASTA、閾値境界、空ファイル、不正パス |

`B-10-033` は本文中に省略記号があるため、本文を完全実装として実体へコピーしない。
実体側で処理開始点を注入可能にするか、入力検証を独立関数へ分け、時間のかかる処理が
検証後にだけ呼ばれることをテストする。

`B-11-024` は既存の `filter_cmd` と同じCLI処理を説明している。関数名だけで新規実装を
作らず、対応をE3として回収する。命名、内包表記とループ、ステータスメッセージの差は
後続E3作業で解消方向を決める。

### 4.4 ワークフロー

| ID | 解消型 | 対応先案 | 必須検証 |
|---|---|---|---|
| `B-14-006` | A | `scripts/ch14/Snakefile.conda`、`scripts/ch14/envs/deseq2.yaml`、`scripts/ch14/run_deseq2.R` | rule・conda・script参照が実在 |
| `B-14-008` | A | `scripts/ch14/fastqc.nf` | DSL2宣言、入出力、チャネル接続 |
| `B-14-010` | A | `scripts/ch14/fastp_filter.cwl` | CWL v1.2、CommandLineTool、入出力 |
| `B-14-011` | A | `scripts/ch14/rnaseq_pipeline.cwl`、`scripts/ch14/hisat2_align.cwl` | `run` 参照、source型、step接続 |
| `B-14-012` | A | `scripts/ch14/inputs.yml` | 全Workflow入力、File・Directory構造 |

pytestでは実資産を読み、CWLの参照先、Snakemakeの補助ファイル、Nextflowの入出力を
静的検証する。さらに実装環境で以下を実行する。

- Snakemake: lintまたはdry-run
- Nextflow: `nextflow run scripts/ch14/fastqc.nf` のfixture smoke test
- CWL: `cwltool --validate`、外部ツールを差し替えたfixture smoke test
- R: 構文解析と、最小count fixtureによる出力確認

外部コマンドが無い場合は対象バッチを完了扱いにせず、導入の承認を求める。ユーザーが
静的検証だけでの完了を明示的に承認した場合は、未実行範囲をPRと対応表に残す。

### 4.5 コンテナと再現性

| ID | 解消型 | 対応先案 | 必須検証 |
|---|---|---|---|
| `B-15-012` | A | `scripts/ch15/samtools_sort.smk` | 完結したrule、入出力、container URI |
| `B-15-018` | A | `scripts/ch15/Dockerfile.gpu` | `FROM` 固定タグ、最小実行命令 |
| `B-15-019` | A | `scripts/ch15/Dockerfile.conda-lock`、対応lock fixture | COPY対象、導入順、lock利用 |
| `B-15-022` | A、3方式へ分離 | `scripts/ch15/version_pinning/` 配下のDockerfile群 | conda-lock、requirements、uvの各方式を混在させない |

`B-15-022` は現在、架空のdigestと3つの代替方式を1ブロックへ併記しており、そのままでは
単一のDockerfileとして実行できない。実装時は一次情報から実在digestを確認し、方式ごとの
Dockerfileと最小依存ファイルへ分割する。lockファイルは手書きせず、`uv lock` や
`conda-lock` の生成結果を使用する。本文の1つのコードブロックは、直前の説明と連続する
conda-lock方式の完全例へ修正する。requirements方式とuv方式は比較表と実体への相対リンクで
案内し、新しい本文コードブロックは増やさない。編集上3方式すべての掲載が必要になった場合は、
別々の抜粋として明示し、本文ブロック総数と対応IDの保存則を更新してから進める。

通常テストでは既存 `validate_dockerfile.py` を拡張し、合成文字列だけでなく新規Dockerfileを
直接検証する。Docker build smoke testも必須とし、daemonやネットワークを利用できない場合は
対象バッチを完了扱いにせず、ユーザーへ環境準備または検証範囲の判断を求める。

### 4.6 ドキュメント、セキュリティ、公開

| ID | 解消型 | 対応先案 | 必須検証 |
|---|---|---|---|
| `B-18-021` | A | `scripts/ch18/mkdocs_example/mkdocs.yml` と最小 `src/`・`docs/` | YAML、参照パス、可能なら `mkdocs build --strict` |
| `B-20-002` | A | `scripts/ch20/.env.example` | 必須キー、placeholder、実シークレット不在 |
| `B-21-009` | A、テンプレートとして配置 | `scripts/ch21/bioconda_recipe/meta.yaml.template` | 必須section、placeholder、test command |

Bioconda例は架空URLと架空SHA-256を実在値として扱わない。テンプレートであることを
ファイル名と本文で明示し、実ビルド成功とは主張しない。実在パッケージへ置き換える場合だけ、
公式のrecipe lint・buildを完了条件へ追加する。

## 5. 実施単位

依存関係とレビュー容易性から、次の順に分ける。

| 順序 | ブランチ案 | 対象 | 主な理由 |
|---:|---|---|---|
| 0 | `revise/e5-correspondence-tooling` | 対応表の生成・監査ツール | 各PRで同じ判定を再生成可能にする |
| 1 | `revise/e5-reclassification` | `B-11-024`、`B-12-002` | 重複実装を防ぎ、母数を37件へ確定 |
| 2 | `revise/e5-config-examples` | ch04、ch06、ch08品質設定、ch10設定、ch13 INI、ch20、ch21 | 外部実行を必要としない設定資産 |
| 3 | `revise/e5-python-samples` | ch08 fixture、ch10、ch13、ch17 | Python実装と振る舞いテスト |
| 4 | `revise/e5-shell-ci` | ch02、ch08 CI | fake executableと設定validatorを共有 |
| 5 | `revise/e5-workflows` | ch14 | Snakemake、Nextflow、CWL、Rの検証を集約 |
| 6 | `revise/e5-containers` | ch15 | Dockerとlock生成の検証を集約 |
| 7 | `revise/e5-documentation` | ch18 | MkDocs環境と最小サイトfixtureを分離 |

各実施単位は、実体・テスト・対応する本文・対応表更新を同じPRへ含める。途中PRで
未処理E5が残ることは許容するが、そのPRの対象IDはすべて完了させる。

### 5.1 対応表ツールの採用

精密対応表を生成した処理は現在 `/private/tmp` にあり、リポジトリから再実行できない。
最初の実施単位で次を採用する。

| 成果物案 | 役割 |
|---|---|
| `scripts/review/build_code_correspondence.py` | 全ブロック、実体、テスト、関係、集計の生成 |
| `scripts/review/code_correspondence_overrides.json` | 人手確定した分類・多対多・章横断関係と根拠 |
| `scripts/review/audit_code_correspondence.py` | 保存則、ハッシュ、参照ID、Markdown集計の独立再計算 |
| `tests/review/test_code_correspondence.py` | 抽出、分類、負例、保存則、override schemaのテスト |

生成ツールは既存の `scripts/review/check_code_sync.py` の行集合判定を正解として流用しない。
全529ブロックを保持し、E0〜EN、`target_file_id`、定義行、実テスト結果を生成する。
同一ソースから2回生成した場合、日時などの明示的な非決定項目を除いて同一になることを
テストする。

既存 `check_code_sync.py` は状態レポートや利用手順から参照されているため、競合する
「もう一つの正解」を残さない。新しい抽出・分類ライブラリを共通実装とし、既存CLIは
`--list`、`--max-unsynced` などの互換入口として共通実装を呼ぶ。旧行集合判定を残す場合は
参考指標と明記し、精密対応表のE判定には使わない。

### 5.2 E5件数の予定推移

| 実施後 | 解消するID数 | 期待E5 |
|---|---:|---:|
| 基準 | 0 | 39 |
| 再分類 | 2 | 37 |
| 設定例 | 16 | 21 |
| Python例 | 5 | 16 |
| shell・CI | 6 | 10 |
| ワークフロー | 5 | 5 |
| コンテナ | 4 | 1 |
| ドキュメント | 1 | 0 |

本文ブロック総数529は変えない。既知の判定移動は `B-11-024` によるE3の1件増加と、
`B-12-002` によるENの1件増加である。残り37件はE0〜E2へ移す。本文ブロックを追加・削除
する必要が生じた場合は、この保存則を更新してから実装を続ける。

## 6. 予定テストファイル

| 対象 | テストファイル案 |
|---|---|
| ch02 shell | `tests/ch02/test_safe_fastq_qc.py` |
| ch04 config | `tests/ch04/test_config_examples.py` |
| ch06 dependency config | `tests/ch06/test_dependency_examples.py` |
| ch08 fixture | `tests/ch08/test_shared_fixtures.py` |
| ch08 quality config・CI | `tests/ch08/test_config_examples.py` |
| ch10 package・config | `tests/ch10/test_package_example.py`、既存 `test_config_example.py` |
| ch10 fail-fast | `tests/ch10/test_pipeline_fail_fast.py` |
| ch13 style・INI | `tests/ch13/test_plot_config.py`、`tests/ch13/test_tracks_config.py` |
| ch14 workflow | `tests/ch14/test_workflow_assets.py` |
| ch15 container | `tests/ch15/test_container_examples.py`、既存 `test_validate_dockerfile.py` |
| ch17 performance | `tests/ch17/test_memory_target.py`、`tests/ch17/test_streaming_fasta.py` |
| ch18 MkDocs | `tests/ch18/test_mkdocs_example.py` |
| ch20 env template | `tests/ch20/test_env_example.py` |
| ch21 recipe | `tests/ch21/test_bioconda_recipe.py` |
| 対応表ツール | `tests/review/test_code_correspondence.py` |

## 7. 各実施単位の手順

1. 対象ID、本文行、既存候補、関連テストのハッシュを記録する
2. 本文の主張、入出力、外部依存、エラー条件をテスト仕様へ変換する
3. `scripts/` または `tests/` の実体を先に作成・修正する
4. 実資産を直接読むテストを追加し、対象章テストを実行する
5. 外部ランタイムがある場合は、静的検証に加えて可能なsmoke testを実行する
6. テスト済み実体から本文へ抜粋を反映し、完全例か抜粋かを本文で明示する
7. 本文と実体のコードを正規化比較し、E0〜E2のどこへ収束したか記録する
8. 全テスト、ruff、構造検査、相互参照検査を実行する
9. 対応表を再生成し、対象IDがE5でないことを確認する
10. PR本文に変更根拠、一次情報、テスト、未実行の外部検証を記載する

## 8. テスト戦略

### 8.1 必須テスト

- Python: importして実関数を呼び、正常系・境界・例外を確認
- shell: `bash -n`、一時ディレクトリ、PATH先頭の偽コマンドによる副作用確認
- TOML: `tomllib`
- YAML: `yaml.safe_load()` に加え、必須キーと型を検証
- JSON: `json.loads()` に加え、イベント・コマンド構造を検証
- INI: `configparser` でsection・値を検証
- Dockerfile、Snakefile、Nextflow、CWL、MkDocs、recipe:
  実ファイルを読む専用validatorと、参照先ファイルの存在確認

### 8.2 禁止する弱いテスト

- 実体とは別にテスト内へ同じ文字列を再掲し、その文字列だけを検証する
- ファイルが存在することだけを確認する
- YAML/TOMLがparseできることだけで意味的整合を確認しない
- 外部ツールがないため全検証をskipする
- 本文コードを直接テストし、`scripts/` の実体を読まない

### 8.3 コマンド

各PRで最低限、次を実行する。

```bash
.venv/bin/pytest tests/chNN/ -q -p no:cacheprovider
.venv/bin/pytest tests/ -q -p no:cacheprovider
.venv/bin/ruff check scripts tests
.venv/bin/mypy <対象の新規Pythonモジュール>
python3 scripts/review/check_structure.py
python3 scripts/review/check_xref.py
```

外部ランタイムの追加コマンドは対象PRの計画に具体化する。

### 8.4 現行ベースライン

計画作成時の結果を、後続PRの比較基準とする。

| 検証 | ベースライン |
|---|---|
| `pytest tests/` | 821 passed、1 skipped、0 failed |
| `ruff check scripts tests` | 成功 |
| `check_xref.py` | 0件 |
| `check_structure.py` | 27件 |

構造検査27件はE5作業前から存在し、著者情報ページの必須セクション判定8件と
太字内カッコ・カギ括弧19件である。E5 PRでは対象章に新しい違反を追加せず、
全体件数を27件以下に保つ。既存27件の修正は別スコープとし、E5作業へ混ぜない。
先行PRで件数が変わる可能性があるため、各ブランチ作成直後にもベースラインを取り直す。

### 8.5 外部ランタイムの事前確認

計画作成時点の環境は次のとおりである。

| 対象 | 状態 |
|---|---|
| Bash | 5.3.15、利用可能 |
| Rscript | 4.5.2、利用可能。ただしDESeq2は未導入 |
| uv | 0.11.26、利用可能 |
| Docker | client 20.10.13、daemon利用不能 |
| Snakemake | 未導入 |
| Nextflow | 未導入 |
| cwltool | 未導入 |
| MkDocs | 未導入 |
| actionlint | 未導入 |
| pre-commit | 未導入 |
| shellcheck | 未導入 |
| hadolint | 未導入 |
| conda / conda-lock | 未導入 |

各対象バッチの開始時に再確認し、必要な導入は本番依存ではなく検証用依存または一時ツールとして
提案する。ネットワークアクセス、Docker daemon起動、ツール導入が必要なら、実行前に承認を得る。

## 9. 対応表の更新

各PRで、変更後ソースから対応表を再生成する。手作業でE5件数だけを書き換えない。

- 本文529ブロックの保存則
- `scripts/ch*` と `tests/ch*` のファイル保存則
- 関係先パス、ID、定義行
- 各実体の直接テストと結果
- 多対多関係
- E5からE3・ENへ訂正した根拠

最終PRではE5が0件であることに加え、新設した実体が `script_only` へ落ちていないこと、
新しいE3が意図せず増えていないことを独立監査する。

## 10. リスクと停止条件

| リスク | 対応 |
|---|---|
| 本文の例自体が無効 | 有効な実体を先に作り、テスト後に本文を修正 |
| 1ブロックが複数方式を混在 | 実体を方式別に分割し、本文は各実体の抜粋にする |
| 外部ツールが重い・利用不能 | 静的検証を先に行い、runtime導入または検証範囲についてユーザー判断を得るまで完了扱いにしない |
| タグ、action、schemaが更新済み | 実装時に公式一次情報を確認し、参照日をPRへ記録 |
| 既存実体と重複 | 第0段階で章横断・別名候補を再検索 |
| 新しい設定が実際のCIを起動 | `.github/workflows/` ではなく `scripts/ch*/examples/` に置く |
| 大容量fixtureや生成物を追加 | 最小fixtureだけを管理し、生成物はコミットしない |

次の場合は実装を止め、ユーザーへ判断を求める。

- 有効な完全例に直すと本文の説明意図が変わる
- 新しい外部依存を本番依存へ追加する必要がある
- 必須runtime検証のツールを導入・起動できない
- 実在digestや公開URLを固定する対象を選べない
- 1つの実施単位が複数章の大幅な文章改稿へ拡大する

## 11. 計画レビュー記録

### 第1巡

初版を規約、全件性、再現性、テスト可能性、Git運用の観点でレビューした。

| ID | finding | 対応 |
|---|---|---|
| P1 | 精密対応表の生成・独立監査処理が `/private/tmp` にしかなく、各E5 PRで再生成できない | 最初の実施単位として生成器、override台帳、独立監査、テストをリポジトリへ採用 |
| P2 | `check_structure.py` の全件成功を暗黙に要求すると、作業前からある27件により達成不能 | ベースラインを記録し、E5 PRでは新規違反なし・27件以下をゲート化 |
| P3 | 39件の実装先は列挙したが、追加するテストファイルの配置が一部曖昧 | 章別の予定テストファイル表を追加 |
| P4 | 全PRが未コミットの一時分析処理へ依存し、実施順の依存関係が欠けていた | 対応表ツールを順序0とし、そのマージ後に各実施単位を開始 |

4 findingsを反映した。次巡では、39件の保存則、内容の有効性、外部ランタイム、
本文同期順、完了条件を再点検する。

### 第2巡

第1巡反映後の計画を、本文例の有効性、runtime検証、型検査、再現性の観点でレビューした。

| ID | finding | 対応 |
|---|---|---|
| P5 | Snakemake、Nextflow、CWL、Dockerのruntime検証を「利用不能なら記録」で省略できた | 未導入・daemon停止の現状を記録し、導入または明示的な検証範囲のユーザー判断まで完了扱いにしない |
| P6 | 新規Python実装に型ヒントを要求するが、型検査コマンドが無かった | 対象新規モジュールへのmypyを必須コマンドに追加 |
| P7 | バージョン固定例でlockファイルを手書きする余地があった | `uv lock`・`conda-lock` 等の生成物だけを使うと明記 |
| P8 | 構造検査の27件を全バッチで固定すると、先行PRによる正当な変化を扱えない | 各ブランチ開始時にベースラインを再取得し、新規違反の有無で比較 |
| P9 | 外部検証に必要なツールの現状が不明で、実装開始後に停止する可能性が高かった | Bash・R・uv・Dockerと未導入ツールを事前実測し、導入承認の停止条件を追加 |

5 findingsを反映した。次巡では、各IDの解消型、ファイル参照、テストの証拠強度、
PR分割と最終保存則を再点検する。

### 第3巡

全39 IDを実施単位へ割り当て直し、既存ツールとの競合、PRの凝集性、件数保存則を
レビューした。

| ID | finding | 対応 |
|---|---|---|
| P10 | ch08 CIが設定バッチとshell・CIバッチの両方へ含まれていた | 設定バッチを品質設定5件、shell・CIバッチをCI 2件へ明確に分離 |
| P11 | ch15コンテナとch18ドキュメントを1PRへまとめており、技術的関連が薄かった | コンテナとMkDocsを別ブランチ・別PRへ分割 |
| P12 | 既存 `check_code_sync.py` と新しい生成器が異なる正解を出す可能性があった | 共通実装へ統合し、既存CLIを互換入口として維持する方針を追加 |
| P13 | 各PR後のE5件数が定義されず、重複・漏れを最終時まで検出できなかった | 39→37→21→16→10→5→1→0の予定推移を追加 |
| P14 | 最終保存則が「E5=0」だけで、E3・ENへの既知移動を検証できなかった | E3 +1、EN +1、残り37件はE0〜E2、総数529を明記 |

5 findingsを反映した。次巡では、各表の算術、ID集合、コマンド実在性、停止条件、
変更範囲を独立に再計算する。

### 第4巡

39件の表と原台帳を照合したうえで、本文同期後の形、ツール間差異、外部依存の
事前確認精度をレビューした。

| ID | finding | 対応 |
|---|---|---|
| P15 | `B-08-025` はClaude Code CLIの設定だけを実体化する計画で、本文中のCodex CLIへの同等機能の主張を検証する手順が弱かった | 両ツールの公式一次情報を別々に確認し、同等機能がなければ架空の設定を作らず対照表で差を示す |
| P16 | `B-15-022` の「3実体からの抜粋」は、本文コードブロック総数529を維持する方針と両立するか不明だった | 本文はconda-lock方式の完全例1つにし、他方式は比較表と実体リンクで案内する。3ブロック化する場合の保存則更新も明記 |
| P17 | Rscriptの存在だけでRワークフローを実行可能と見なしていたが、必要なDESeq2の状態を確認していなかった | DESeq2未導入をベースラインへ記録し、導入または検証範囲の判断を停止条件として適用 |

3 findingsを反映した。次巡では、原台帳との集合一致、重複、件数推移、実在コマンド、
未着手の実装範囲を独立監査する。

### 第5巡

第4巡反映後の計画を、原台帳から独立に再計算して監査した。

- 原台帳のE5集合と解消マトリクスのID集合は39件すべて一致した
- 解消マトリクス内の重複IDは0件であった
- 実施単位の件数は2 + 16 + 5 + 6 + 5 + 4 + 1 = 39であった
- 予定推移は39→37→21→16→10→5→1→0で整合した
- `pytest`、`ruff`、`mypy`、構造検査、相互参照検査のコマンドまたはスクリプトが存在した
- `chapters/`、`scripts/`、`tests/` に本計画作成による差分はなかった
- 基準コミットは `8153267`、作業ブランチは `revise/code-sync-inventory` のままであった
- `git diff --check` は成功した

新規findingは0件であった。これを計画レビューの収束条件とし、実装は別作業として開始する。
