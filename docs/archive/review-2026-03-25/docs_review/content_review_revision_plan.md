# 内容査読・修正計画

## 目的

本計画は、『AIエージェントと学ぶ バイオインフォマティクスプログラミングの作法』の**内容そのもの**を出版水準で査読し、必要な修正を台帳ベースで管理するための実行計画である。

ここでいう「内容査読」は、リンク切れや表記揺れのような機械監査ではなく、以下を対象とする。

- 事実の正確性
- 専門用語・概念説明の厳密性
- 生命科学・バイオインフォマティクス実務との整合
- 計算機科学・情報科学としての説明妥当性
- 初学者にとっての理解しやすさ
- 出版物としての断定表現の安全性

既存の自動監査で `S=0, A=0, B=0, C=0` になっていることを前提に、以後は本文の主張・比喩・推奨・用語定義・実例を人手で精査する。

## 既存台帳の使い方

内容査読では、既存の `docs/review/` 配下の台帳をそのまま使う。**CSVの列追加・スキーマ変更は行わない。**

### `chapter_review_sheet.csv`

章ごとの進捗管理に使う。

- `manual_status` は以下の4値で運用する
- `not_started`: 未着手
- `in_progress`: 査読中
- `reviewed`: 章の一次査読完了
- `rechecked`: 修正反映後の再確認完了

レビュー担当欄は役割別の観点を埋めるために使う。

- `reviewer_life_science`
- `reviewer_info_science`
- `reviewer_cs`
- `reviewer_bioinformatics`
- `reviewer_programming`

実際に人名を入れる必要はない。`done`、`pending`、`needs_recheck` のような状態管理でもよい。

### `master_issue_log.csv`

本文の問題点を記録する主台帳として使う。列は以下に固定する。

- `issue_id`
- `severity`
- `chapter_file`
- `line`
- `category`
- `subject`
- `evidence`
- `proposed_action`
- `source`

運用ルール:

- 1問題につき1行で記録する
- 感想ではなく `問題 / 根拠 / 修正案` の粒度で書く
- `line` は節先頭ではなく、問題のある断定文・表・コード例の行に合わせる
- `category` は `fact`, `concept`, `bio`, `cs`, `ux`, `pedagogy`, `terminology`, `reference` など、後で集計しやすい短い値に寄せる

### `manual_fact_checks.md`

時事性・制度・料金・サービス仕様・数値主張・ベンチマーク・法規制の裏取り専用に使う。

- 本文に残す数値は、原則として **日付** と **測定条件** を併記する
- 一次情報が取れないものは「推計」「報道」「二次情報」と明示する
- 出典の格を本文の断定強度に合わせる

### `reference_registry.csv`

URL、組織名、サービス名、DB名、公式資料の所在確認に使う。

- 内容査読では「その記述が現在も成立するか」を点検する際の入口として使う
- 参照先の実在性確認には使うが、本文の妥当性判定そのものは `master_issue_log.csv` に記録する

### `section_inventory.csv`

節ごとの位置特定と横断レビューに使う。

- 同一テーマが複数章にまたがる場合の追跡
- `roadmap.md` の重複記述との同期確認
- 節順や見出し粒度の見直し候補の特定

### `roadmap.md` の扱い

`roadmap.md` は元章の要約・重複記述を含むため、単独で先行査読しない。元章を修正した後に、対応する重複箇所を同期する対象とする。

## 査読観点

各章・各節を、少なくとも以下の5観点で読む。

### 生命科学

- 生物学的前提が正しいか
- 実験文脈を不当に単純化していないか
- ヒトデータ、臨床データ、オミクス解析の扱いに危険な誤解がないか
- 実験系研究者が読んだときに不自然な一般化がないか

### 情報科学

- データモデルや分類が整合しているか
- 抽象化の切り方が妥当か
- 「形式」「構造」「表現」の違いを混同していないか
- 評価軸や比較軸が適切に定義されているか

### 計算機科学

- 計算量・アルゴリズム・型・メモリ・並列性の説明が正確か
- OS差分、実行環境差分、ランタイム差分を落としていないか
- 断定的な説明が、実際には実装依存・版依存になっていないか
- 比喩が概念理解を助けているか、誤解を生んでいないか

### バイオインフォマティクス

- FASTA / FASTQ / BAM / VCF / GFF / BED の説明が現場感覚と一致しているか
- 公共DB、API、ツールチェーン、ワークフロー、HPC の説明が実務に耐えるか
- 「研究現場では実際にどう使うか」が正しく表現されているか
- データ公開・再現性・法規制の扱いが実務的か

### 実装実務

- Python / Git / CLI / テスト / パッケージ管理 / コンテナ / CI の説明が現在の標準実務と整合するか
- コード例が読者に誤った習慣を教えていないか
- 「実務では避ける書き方」を教育的配慮なく推奨していないか
- 初学者にとって必要な前提説明が抜けていないか

## 優先順位とバッチ

査読順は**章順ではなくリスク順**とする。時事性、制度依存、専門性、誤解コストの高い章から優先して潰す。

### Batch 1: 高リスク章

- `hajimeni.md`
- `00_ai_agent.md`
- `04_data_formats.md`
- `19_database_api.md`
- `20_security_ethics.md`
- `21_collaboration.md`

重点:

- 時事性の高い数値・製品仕様・用語
- 倫理・法規制・利用規約
- 公共DBやAPIの制度・利用制限
- 読者がそのまま信じて運用しがちな断定表現

### Batch 2: 再現性・実行環境章

- `05_software_components.md`
- `06_dev_environment.md`
- `07_git.md`
- `14_workflow.md`
- `15_container.md`
- `16_hpc.md`
- `17_performance.md`

重点:

- OS差分
- ツール更新や版差分
- 環境構築、ワークフロー、HPC の実務妥当性
- 再現性に関する説明の具体性

### Batch 3: 基礎・教育章

- `01_design.md`
- `02_terminal.md`
- `03_cs_basics.md`
- `08_testing.md`
- `09_debug.md`
- `10_deliverables.md`
- `11_cli.md`
- `12_data_processing.md`
- `13_visualization.md`
- `18_documentation.md`

重点:

- 基礎概念の定義精度
- 比喩・導入・節順の妥当性
- 初学者が誤学習しない説明になっているか
- 参考文献と本文の主張強度の釣り合い

### Batch 4: 補助資料・重複資料

- `appendix_a_learning_patterns.md`
- `appendix_b_cli_reference.md`
- `appendix_c_checklist.md`
- `appendix_d_agent_vocabulary.md`
- `glossary.md`
- `roadmap.md`

重点:

- 本文との整合
- 用語統一
- 重複説明のズレ
- 索引性、検索性、要約の正確さ

## 章別重点論点

査読時に特に見落としやすい論点を、バッチごとに固定する。

### Batch 1

- `hajimeni.md`: 時事数値、AI性能比較、利用者数、業界動向の断定強度
- `00_ai_agent.md`: 製品仕様、権限制御、用語、CLI動作説明
- `04_data_formats.md`: データモデル、tidy data、long form、形式選択の判断基準
- `19_database_api.md`: DB分類、ID体系、利用制限、API速度制限、引用先の現行性
- `20_security_ethics.md`: GDPR / HIPAA / DUA / 匿名化 / 再識別リスク
- `21_collaboration.md`: OSS文化、レビュー慣行、質問の作法、共同研究文脈の現実性

### Batch 2

- `05_software_components.md`: import、shared library、パッケージ概念、OS差分
- `06_dev_environment.md`: pyenv / venv / conda / uv の役割分担と実務
- `07_git.md`: Git LFS、Zenodo、版管理運用の現行性
- `14_workflow.md`: Snakemake / Nextflow の版差分、ログ、再開性、HPC連携
- `15_container.md`: Docker / Apptainer、cgroups、ベースイメージ、再現性説明
- `16_hpc.md`: Slurm、リソース申請、転送、バックアップ、施設依存性
- `17_performance.md`: プロファイリング、並列化、Amdahl、I/O vs CPU 境界

### Batch 3

- `01_design.md`: 原則の出典、比喩、開発用語の過不足
- `02_terminal.md`: macOS / Linux 差分、可搬なコマンド例
- `03_cs_basics.md`: 計算量、アルゴリズム、数値計算、乱数、教育的誤差
- `08_testing.md`: TDD、pytest、mypy、品質管理実務
- `09_debug.md`: 最小再現例、traceback 読解、時制と前後章整合
- `10_deliverables.md`: 成果物分類、推奨パターンの境界
- `11_cli.md`: CLI設計、引数、ロギング、ユーザー向け挙動
- `12_data_processing.md`: pandas / polars / NumPy の使い分け
- `13_visualization.md`: グラフ選択、誤解を招く図の回避
- `18_documentation.md`: ドキュメント種別、ライセンス、質問の書き方

### Batch 4

- 付録・用語集は本文の縮約版として読まず、**本文と矛盾しないか**を主目的に確認する
- `roadmap.md` は元章の修正後に同期チェックする

## 記録ルール

### 問題の書き方

レビューコメントは感想ではなく、以下の構造で残す。

- 問題: 何が不正確か、何が危険か
- 根拠: どの一次情報・専門常識・コード実体に反するか
- 修正案: どう弱めるか、どう言い換えるか、どう削るか

### 重大度

`severity` は以下の4段階で固定する。

- `S`: 明確な誤情報。出版前に必ず除去
- `A`: 出版前必修正。誤解・誤運用・再現性低下を招く
- `B`: 品質改善。正確性は保てるが、説明や用語が弱い
- `C`: 任意改善。冗長さ、語感、流れ、補足不足など

### 数値・時事情報

- 数値主張は本文に残すなら **日付** と **測定条件** を併記する
- 比較表現は、比較対象・測定条件・時点が揃っていない限り弱める
- 一次情報がないものは削除するか、「推計」「報道」「二次情報」と明示する

### 行番号の付け方

- `line` は節見出しではなく、問題のある本文、表、コード例、箇条書きの行に合わせる
- 同一行に複数問題がある場合でも、1問題1行を原則とする

### 修正後の状態管理

- 査読開始時: `manual_status = in_progress`
- 一次査読完了: `manual_status = reviewed`
- 修正反映後の確認完了: `manual_status = rechecked`

## 完了条件

内容査読フェーズは、以下を満たした時点で完了とする。

- 29ファイルすべてが `reviewed` 以上になっている
- `master_issue_log.csv` に未解消の `S` と `A` がない
- 時事性の高い主張が `manual_fact_checks.md` で確認済みか、二次情報である旨が本文に明記されている
- 参考文献と本文の主張強度が釣り合っている
- `roadmap.md` と元章の重複記述が同期している
- 最終確認として以下を再実行し、自動監査0件を維持している

```bash
python3 scripts/build_review_artifacts.py --pytest-log /tmp/ai-biocode-kata-pytest.log
python3 scripts/review/check_structure.py
```

## 運用開始時の第一手

内容査読は以下の順で着手する。

1. `chapter_review_sheet.csv` の Batch 1 章を `in_progress` にする
2. `hajimeni.md` から `21_collaboration.md` まで、Batch 1 の主張を節単位で精読する
3. 問題は `master_issue_log.csv` に即時記録する
4. 時事性・数値・制度の裏取りは `manual_fact_checks.md` に追記する
5. Batch 1 の修正が終わったら `reviewed` → `rechecked` へ進める
6. 以後、Batch 2 → Batch 3 → Batch 4 の順で同じ運用を反復する
