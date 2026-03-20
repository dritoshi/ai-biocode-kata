# §13A「実験管理（ML/計算実験の追跡）」執筆プラン

- 作成日: 2026-03-20
- 目的: roadmapの§13A構成（3節）に従い、🤖章として新規執筆する

---

## Context

§13「コンテナと再現性」が完成済み。§13末尾に§13Aへの橋渡し文がある。§12の🤖コラムでDVC/MLflowを紹介済み。§13Aは書籍唯一の「章全体が🤖対象」のチャプターであり、バイオインフォ×機械学習プロジェクト向けの内容。読み飛ばしても本編に支障がない構成にする。

## リンク先ファイル名の統一

現在、他章からの§13A参照が3種類に不統一:
- `13_container.md`: `./13a_experiment.md`
- `05_dev_environment.md`: `./13a_experiment_tracking.md`
- `10_data_processing.md`: `./appendix_13a_experiment.md`

→ `13a_experiment.md` に統一する（CLAUDE.mdの命名規則 `NN_name.md` に準拠）。他章のリンクも修正する。

## 作成ファイル一覧

| ファイル | 種別 | 概要 |
|---------|------|------|
| `chapters/13a_experiment.md` | 新規 | 本文（~350行） |
| `scripts/ch13a/experiment_logger.py` | 新規 | 最小限の実験ログ記録ツール |
| `scripts/ch13a/__init__.py` | 新規 | パッケージ初期化 |
| `tests/ch13a/test_experiment_logger.py` | 新規 | ロガーのテスト |
| `tests/ch13a/__init__.py` | 新規 | パッケージ初期化 |
| `references/ch13a.bib` | 新規 | 参考文献（5-7件） |

## 章構成

### 導入部（~25行）
- 🤖マーク: 「本章はバイオインフォマティクス×機械学習プロジェクト向けの内容であり、読み飛ばしても後続の章に支障はない」
- 前章接続: §13でコンテナによる環境の再現性を学んだ → 環境が同一でも、どのパラメータで実験したかが記録されていなければ結果を再現できない
- エージェント協働: エージェントはモデル学習コードを生成できるが、実験の追跡（どのパラメータでどのメトリクスが出たか）は人間が設計・管理する必要がある
- 章の概要

### 13A-1. なぜ実験管理が必要か（~80行）
- 「先週のあの結果、どのパラメータで出したんだっけ？」問題
  - 具体例: scRNA-seq解析でUMAPのパラメータ（n_neighbors, min_dist）を変えて試行 → 最良の結果がどの条件だったか不明
  - 具体例: ディープラーニングのハイパーパラメータ探索（learning rate, batch size, epochs）
- 管理すべき3要素:
  - ハイパーパラメータ（入力条件）
  - メトリクス（結果の評価値）
  - アーティファクト（モデルファイル、可視化結果等）
- 配列解析でも有用: パイプラインのパラメータ違い（フィルタリング閾値、リファレンスゲノム版）の比較
- Git（§6）との違い: Gitはコードのバージョン管理、実験管理はパラメータ×結果のバージョン管理
- エージェントへの指示例

### 13A-2. 実験追跡ツール（~120行）
- ツール比較表（roadmapの表を拡張）:

| ツール | 種別 | 特徴 | 向いている場面 |
|-------|------|------|--------------|
| wandb | クラウドSaaS | 可視化が美しい、チーム共有が容易 | ML学習実験、ハイパラ探索 |
| MLflow | OSS | ローカル/サーバー両対応、モデルレジストリ | モデル管理、デプロイ連携 |
| hydra | OSS | 設定ファイルの構成管理 | パラメータの組み合わせ管理 |
| DVC | OSS | データとモデルのバージョン管理（Git連携） | 大規模データのバージョニング |

- **wandb** の使い方（最小限のコード例）:
  ```python
  import wandb
  wandb.init(project="rnaseq-clustering")
  wandb.config.update({"n_neighbors": 15, "min_dist": 0.1})
  # ... 学習・解析 ...
  wandb.log({"silhouette_score": 0.72, "n_clusters": 5})
  ```
- **MLflow** の使い方（最小限のコード例）:
  ```python
  import mlflow
  with mlflow.start_run():
      mlflow.log_param("n_neighbors", 15)
      # ... 学習 ...
      mlflow.log_metric("accuracy", 0.95)
      mlflow.log_artifact("model.pkl")
  ```
- §12の🤖コラムとの接続: Snakemake/Nextflowとの使い分け（配列解析=WF言語、ML実験=追跡ツール）
- 選択の判断基準:
  - 個人利用で手軽に始めたい → wandb（無料枠あり）
  - オンプレミス/自前サーバーで管理したい → MLflow
  - パラメータの組み合わせが多い → hydra + wandb/MLflow
  - 大規模データ（数十GB以上のモデル等）のバージョン管理 → DVC
- エージェントへの指示例

### 13A-3. 最小限の実験管理パターン（~100行）
- ML専用ツールを導入する前の自前実装（`experiment_logger.py`）
  - JSONL形式で実験ログを記録
  - 記録項目: タイムスタンプ、gitハッシュ、パラメータ、メトリクス
  - `scripts/ch13a/experiment_logger.py` の紹介
- 段階的な導入パス:
  1. 自前JSONLログ（本節で実装）
  2. wandb導入（実験数が増えたら）
  3. hydraで設定管理（パラメータ組み合わせが爆発したら）
  4. DVCでデータ版管理（データセット自体のバージョンが必要なら）
- 🧬コラム: バイオインフォマティクスの実験管理（~25行）
  - 配列解析パイプラインでの実験管理: パラメータ違い（フィルタリング閾値、アライメントオプション等）を記録する実例
  - Snakemakeの`config.yaml`を実験ごとに保存する方法（§12との連携）
- エージェントへの指示例

### まとめ（~20行）
- 実験管理の3要素（パラメータ、メトリクス、アーティファクト）
- ツール選択の判断フロー
- 段階的導入パスの一覧
- 次章への接続（§14 HPC）

### 参考文献

## コードサンプル

`scripts/ch13a/experiment_logger.py`:
- `ExperimentRecord` dataclass（timestamp, git_hash, params, metrics）
- `log_experiment(params, metrics, output_dir)` — JSONL形式で記録
- `load_experiments(log_path)` — ログファイルを読み込んでリスト返却
- `find_best(experiments, metric_name, maximize)` — 最良実験を検索

§12の`validate_workflow.py`パターンを踏襲（dataclass + 個別関数 + 統合関数）。

## テスト

`tests/ch13a/test_experiment_logger.py`:
- `TestLogExperiment`: ログ書き込み、JSONL形式の検証、gitハッシュ取得
- `TestLoadExperiments`: 読み込み、空ファイル、複数レコード
- `TestFindBest`: 最大化、最小化、空リスト

## 参考文献候補（5-7件）

1. Biewald 2020 — "Experiment Tracking with Weights and Biases"（wandb公式）
2. Zaharia et al. 2018 — "Accelerating the Machine Learning Lifecycle with MLflow"（MLflow原著）
3. Yadan 2019 — "Hydra - A framework for elegantly configuring complex applications"（hydra）
4. Iterative 2020 — "DVC: Data Version Control"（DVC公式）
5. Tatman et al. 2018 — "A Practical Taxonomy of Reproducibility for ML Research"
6. wandb Documentation（Web）
7. MLflow Documentation（Web）

## 相互参照マップ

| §13Aの節 | 参照先 | 文脈 |
|----------|--------|------|
| 導入 | §13 コンテナ | 前章接続 |
| 13A-1 | §6 Git | コードのバージョン管理との違い |
| 13A-2 | §12 ワークフロー | Snakemake/NextflowとDVC/MLflowの使い分け |
| 13A-2 | §5 開発環境 | wandb/MLflowのインストール |
| 13A-3 | §12 ワークフロー | config.yamlとの連携 |
| まとめ | §14 HPC | 次章接続 |

## 他章のリンク修正

| ファイル | 現在のリンク | 修正後 |
|---------|-------------|--------|
| `chapters/05_dev_environment.md` | `./13a_experiment_tracking.md` | `./13a_experiment.md` |
| `chapters/10_data_processing.md` | `./appendix_13a_experiment.md` | `./13a_experiment.md` |

## 目次更新

- `chapters/roadmap.md`: §13Aの目次に原稿リンク追加 + 本文セクションに📖原稿リンク追加
- `README.md`: §13Aの原稿カラムにリンク追加

## 実施順序

1. コードサンプル（`scripts/ch13a/experiment_logger.py`）
2. テスト（`tests/ch13a/test_experiment_logger.py`）→ pytest通過確認
3. 本文（`chapters/13a_experiment.md`）
4. 参考文献（`references/ch13a.bib`）
5. 他章のリンク修正（`05_dev_environment.md`, `10_data_processing.md`）
6. 目次更新（`roadmap.md`, `README.md`）
7. 全テスト実行

## 検証方法

1. `pytest tests/ch13a/` — 全テスト通過
2. 導入部に🤖マーク・前章接続・エージェント協働・章の概要があること
3. 各節末に「エージェントへの指示例」があること
4. §13Aへの全リンクが`./13a_experiment.md`に統一されていること
5. roadmap§13Aの節構成と本文の見出しが対応していること
