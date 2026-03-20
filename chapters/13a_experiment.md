# §13A 実験管理（ML/計算実験の追跡）

[§13 コンテナと再現性](./13_container.md)では、Dockerやapptainerで実行環境を固定し、第三者が同一の環境を復元できるようにする方法を学んだ。しかし、環境が同一でも「どのパラメータで実験したか」が記録されていなければ、結果を再現することはできない。

計算実験では——機械学習のハイパーパラメータ探索であれ、scRNA-seq解析のクラスタリングパラメータ調整であれ、パイプラインのフィルタリング閾値の比較であれ——条件を変えながら何度も試行する。AIエージェントはコードを生成できるが、「先週のあの結果が出た条件」を後から復元するための記録——実験の追跡——は、人間が設計し管理する必要がある。

本章では、実験管理の必要性、主要な追跡ツール（wandb、MLflow等）、そしてツール導入前に始められる最小限の実験管理パターンを学ぶ。

---

## 13A-1. なぜ実験管理が必要か

### 「先週のあの結果」問題

以下の場面を想像してみよう:

**場面1: scRNA-seq解析のクラスタリング。** UMAPで細胞の次元削減を行い、`n_neighbors`と`min_dist`のパラメータを変えて10パターン以上試した。最も生物学的に意味のあるクラスタが得られた条件を発表に使いたいが、どのパラメータの組み合わせだったか思い出せない。Jupyter Notebookのセルを上書きしてしまい、履歴も残っていない。

**場面2: ディープラーニングのハイパーパラメータ探索。** タンパク質の機能予測モデルを学習している。learning rate、batch size、隠れ層のサイズ、ドロップアウト率を変えて数十回の学習を回した。最良の検証精度が出た組み合わせを論文に記載したいが、ターミナルの出力はスクロールして消えてしまった。

**場面3: 配列解析パイプラインのパラメータ比較。** RNA-seqのフィルタリング閾値（最小リード数、最小遺伝子数）を変えて差次的発現解析の結果を比較したい。3つの閾値セットで実行したが、どの`config.yaml`でどの結果が出たのか対応がわからなくなった。

### 管理すべき3つの要素

実験管理とは、以下の3要素を体系的に記録・検索可能にすることである:

| 要素 | 内容 | 例 |
|------|------|-----|
| **ハイパーパラメータ**（入力条件） | 実験ごとに変化させる設定値 | learning rate, n_neighbors, フィルタリング閾値 |
| **メトリクス**（評価値） | 実験結果を定量的に評価する指標 | accuracy, loss, silhouette score, DEG数 |
| **アーティファクト**（成果物） | 実験から生成されるファイル | モデルファイル(.pkl)、UMAPプロット、結果テーブル |

### Gitとの違い

[§6 バージョン管理（Git / GitHub）](./06_git.md)で学んだGitは**コード**のバージョン管理ツールである。一方、実験管理は**パラメータ × 結果**のバージョン管理である。

| | Git | 実験管理 |
|--|-----|---------|
| 管理対象 | ソースコード | パラメータ、メトリクス、アーティファクト |
| 追跡単位 | コミット | 実験（ラン） |
| 比較方法 | `git diff` | メトリクスの比較表・グラフ |
| 戻し方 | `git checkout` | 同じパラメータで再実行 |

両者は排他的ではなく、併用するものである。実験管理ツールの多くは、実験時のgitコミットハッシュを自動記録し、「あの精度が出たときのコードはどのバージョンだったか」を追跡できるようにしている。

#### エージェントへの指示例

実験管理の設計についてエージェントに相談する場合:

> 「このモデル学習スクリプトに実験追跡を追加したい。記録すべきハイパーパラメータとメトリクスを提案してください」

> 「scRNA-seqのクラスタリング解析で、n_neighbors、min_dist、resolutionの組み合わせを系統的に試したい。パラメータと結果を管理する方法を提案してください」

> 「Jupyter Notebookで実験を繰り返しているが、条件と結果の対応がわからなくなる。Notebookから実験ログを記録する仕組みを追加してください」

---

## 13A-2. 実験追跡ツール

### ツールの比較

[§12 ワークフロー管理](./12_workflow.md)の🤖コラムでSnakemake/Nextflowとの使い分けを紹介した。ここでは、実験追跡に特化したツールの特徴を整理する:

| ツール | 種別 | 特徴 | 向いている場面 |
|-------|------|------|--------------|
| **wandb**（Weights & Biases） | クラウドSaaS | 可視化が美しい、チーム共有が容易、無料枠あり | ML学習実験、ハイパーパラメータ探索 |
| **MLflow** | OSS | ローカル/サーバー両対応、モデルレジストリ | モデル管理、オンプレミス環境 |
| **hydra** | OSS | 設定ファイルの構成管理（追跡そのものではない） | パラメータの組み合わせ管理 |
| **DVC**（Data Version Control） | OSS | データとモデルのバージョン管理（Git連携） | 大規模データのバージョニング |

### wandb — クラウドベースの実験追跡

wandbは最も手軽に導入できる実験追跡ツールである。無料の個人アカウントで始められ、ブラウザ上でメトリクスの推移グラフやパラメータの比較表を確認できる。

以下は、scRNA-seqデータのクラスタリングにおいて、UMAPの次元削減パラメータ（`n_neighbors`: 近傍点の数、`min_dist`: 点間の最小距離）とクラスタリングの解像度（`resolution`）を変えて最適な細胞クラスタを探索する実験を記録する例である:

```python
import wandb

# プロジェクトと実験を初期化
wandb.init(project="rnaseq-clustering", name="umap-exp-01")

# ハイパーパラメータを記録
# n_neighbors: UMAPが参照する近傍点の数（大きいほど大域構造を重視）
# min_dist: UMAP上での点間の最小距離（小さいほどクラスタが密になる）
# resolution: Leidenクラスタリングの解像度（大きいほど細かいクラスタに分割）
wandb.config.update({
    "n_neighbors": 15,
    "min_dist": 0.1,
    "resolution": 0.5,
})

# ... scanpyによるUMAP + クラスタリング実行 ...

# メトリクスを記録
# silhouette_score: クラスタの分離度（-1〜1、高いほど良い）
# ari: Adjusted Rand Index（既知の細胞型ラベルとの一致度）
wandb.log({
    "silhouette_score": 0.72,
    "n_clusters": 5,
    "ari": 0.65,
})

# 可視化結果をアーティファクトとして保存
wandb.log({"umap_plot": wandb.Image("umap.png")})

wandb.finish()
```

### MLflow — オンプレミス対応の実験追跡

MLflowはオープンソースの実験管理プラットフォームである。クラウドに依存せず、ローカルマシンや研究室のサーバーで完結できる。モデルレジストリ機能により、学習済みモデルのバージョン管理も可能である。

以下は、タンパク質の機能予測モデル（ニューラルネットワーク）を学習する実験で、近傍点の数や点間距離を変えながら分類精度を比較する例である:

```python
import mlflow

# 実験を開始
with mlflow.start_run(run_name="protein-func-exp-01"):
    # ハイパーパラメータを記録
    mlflow.log_param("learning_rate", 0.001)
    mlflow.log_param("batch_size", 64)
    mlflow.log_param("hidden_dim", 256)
    mlflow.log_param("dropout", 0.3)

    # ... PyTorchによるモデル学習 ...

    # メトリクスを記録
    # accuracy: テストデータでの正解率
    # f1_score: クラス不均衡を考慮した総合指標
    mlflow.log_metric("accuracy", 0.95)
    mlflow.log_metric("f1_score", 0.88)

    # アーティファクトを保存（学習済みモデルと混同行列の図）
    mlflow.log_artifact("model.pkl")
    mlflow.log_artifact("confusion_matrix.png")
```

```bash
# MLflow UIを起動してブラウザで結果を確認
mlflow ui --port 5000
```

### ツール選択の判断基準

| 状況 | 推奨ツール |
|------|----------|
| 個人利用で手軽に始めたい | wandb（無料枠あり、セットアップが簡単） |
| オンプレミス/自前サーバーで管理したい | MLflow |
| パラメータの組み合わせが多い | hydra + wandb/MLflow |
| 大規模データ（数十GB以上のモデル等）のバージョン管理 | DVC |
| 配列解析パイプライン中心、ML要素が少ない | 次節の自前ログで十分 |

[§12 ワークフロー管理](./12_workflow.md)の🤖コラムで述べたとおり、配列解析パイプライン（外部ツール呼び出しが中心）は[Snakemake/Nextflow](./12_workflow.md#12-2-ワークフロー言語)、機械学習実験（Pythonコードが中心）はwandb/MLflowと使い分けるのが現実的である。両方を含むプロジェクトでは、Snakemakeのワークフロー内でMLflowやwandbのトラッキングを呼び出す組み合わせも有効である。

#### エージェントへの指示例

実験追跡ツールの導入をエージェントに依頼する場合:

> 「この学習スクリプトにwandbの追跡を追加してください。ハイパーパラメータはconfig辞書から、メトリクスはエポックごとのlossとaccuracyを記録してください」

> 「MLflowでローカルに実験を追跡したい。セットアップ手順と、このスクリプトに組み込む最小限のコードを教えてください」

> 「hydraを使って、learning_rate=[0.001, 0.01, 0.1]、batch_size=[32, 64, 128]の組み合わせを自動的に実行する設定を作成してください」

---

## 13A-3. 最小限の実験管理パターン

### ツール導入前に始められる自前実装

wandbやMLflowを導入する前に、まず最小限のログ記録を自前で実装することを推奨する。これにより、「実験を記録する習慣」を身につけ、ツール導入後も何を記録すべきかの判断力が養われる。

本書のサンプルコード（`scripts/ch13a/experiment_logger.py`）に、JSONL形式の実験ログ記録ツールを用意している。

以下は、scRNA-seqデータのクラスタリングで、UMAPパラメータ（`n_neighbors`, `min_dist`）とクラスタリング解像度（`resolution`）の組み合わせを変えながらシルエットスコアで最良の条件を探す例である:

```python
from scripts.ch13a.experiment_logger import log_experiment, load_experiments, find_best

# 実験1: 近傍点15、最小距離0.1、解像度0.5 → 5クラスタ、シルエット0.72
log_experiment(
    params={"n_neighbors": 15, "min_dist": 0.1, "resolution": 0.5},
    metrics={"silhouette": 0.72, "n_clusters": 5},
    output_dir="results/experiments",
)

# 実験2: 近傍点を30に増やし、解像度を上げる → 3クラスタ、シルエット0.68
log_experiment(
    params={"n_neighbors": 30, "min_dist": 0.2, "resolution": 0.8},
    metrics={"silhouette": 0.68, "n_clusters": 3},
    output_dir="results/experiments",
)

# ログを読み込んで、シルエットスコアが最も高い実験を検索
experiments = load_experiments("results/experiments/experiment_log.jsonl")
best = find_best(experiments, "silhouette", maximize=True)
print(f"最良パラメータ: {best.params}")  # {"n_neighbors": 15, ...}
```

以下は生成されるJSONLファイルの内容例である。JSONL（JSON Lines）は1行に1つのJSONオブジェクトを記録する形式で、ファイルへの追記が容易であり、`pandas.read_json(path, lines=True)` で直接DataFrameに読み込める。

```json
{"timestamp": "2026-03-20T10:30:00+00:00", "git_hash": "a1b2c3d", "params": {"n_neighbors": 15, "min_dist": 0.1}, "metrics": {"silhouette": 0.72}}
{"timestamp": "2026-03-20T11:00:00+00:00", "git_hash": "a1b2c3d", "params": {"n_neighbors": 30, "min_dist": 0.2}, "metrics": {"silhouette": 0.68}}
```

JSONL（JSON Lines）は1行に1つのJSONオブジェクトを記録する形式である。ファイルの追記が容易で、`pandas.read_json(path, lines=True)`で直接DataFrameに読み込めるため、後からの分析にも便利である。

### 段階的な導入パス

実験管理ツールは、必要に応じて段階的に導入するのが現実的である:

| 段階 | 手法 | 導入タイミング |
|------|------|--------------|
| 1 | 自前JSONLログ（本節で実装） | 最初から。まず記録する習慣をつける |
| 2 | wandb導入 | 実験数が数十を超え、可視化・比較が手動では困難になったとき |
| 3 | hydraで設定管理 | パラメータの組み合わせが爆発し、手動でconfig.yamlを書くのが非効率になったとき |
| 4 | DVCでデータ版管理 | データセット自体のバージョンを管理する必要が出てきたとき |

段階1から始めて、プロジェクトの成長に合わせてツールを追加していく。すべてのツールを最初から導入する必要はない。

> 🧬 **コラム: 配列解析パイプラインの実験管理**
>
> 機械学習に限らず、配列解析パイプラインでもパラメータの比較は頻繁に発生する。RNA-seqの発現量フィルタリング閾値（最小リード数、最小検出細胞数）やアライメントオプション（ミスマッチ許容数、マルチマッピング方針）を変えて結果を比較するケースである。
>
> [§12 ワークフロー管理](./12_workflow.md#パラメータの設定ファイル化)で学んだSnakemakeの`config.yaml`を実験ごとに保存しておくと、簡易的な実験管理として機能する:
>
> ```bash
> # 実験ごとにconfigを保存
> cp config.yaml results/exp_01/config.yaml
> snakemake --configfile config.yaml --cores 8
>
> # パラメータを変更して再実験
> cp config_v2.yaml results/exp_02/config.yaml
> snakemake --configfile config_v2.yaml --cores 8
> ```
>
> 各実験ディレクトリに`config.yaml`のコピーを残すことで、「この結果はどのパラメータで出したか」を後から追跡できる。これは段階1（自前ログ）の一形態であり、wandb/MLflowが不要な規模のプロジェクトではこれで十分な場合も多い。

#### エージェントへの指示例

最小限の実験管理を導入する場合:

> 「この学習スクリプトに`experiment_logger.py`を組み込んで、各エポック終了時にパラメータとメトリクスを記録してください」

> 「`results/experiments/experiment_log.jsonl`に記録された実験結果を読み込んで、accuracyが最も高い実験のパラメータを表示するスクリプトを書いてください」

> 「現在は自前のJSONLログで実験管理しています。wandbに移行したいので、既存のログ記録部分をwandbの`init/config/log`に置き換えてください」

---

## まとめ

| 概念 | 内容 | 関連する章 |
|------|------|-----------|
| 実験管理の3要素 | パラメータ、メトリクス、アーティファクト | — |
| Gitとの違い | コード管理 vs パラメータ×結果の管理 | [§6 Git](./06_git.md) |
| wandb / MLflow | 専用追跡ツール | [§5 開発環境](./05_dev_environment.md) |
| Snakemake連携 | ワークフロー + 実験追跡の組み合わせ | [§12 ワークフロー](./12_workflow.md) |
| 段階的導入 | 自前ログ → wandb → hydra → DVC | — |

実験管理は、コードのバージョン管理（[§6 Git](./06_git.md)）、環境の再現性（[§13 コンテナ](./13_container.md)）と並んで、計算科学の再現性を支える3本目の柱である。まずは自前のJSONLログから始め、プロジェクトの規模に応じてwandbやMLflowに移行するのが現実的な導入戦略である。

次章の[§14 HPC](./14_hpc.md)では、HPCクラスタでの計算実行——SLURMジョブスケジューラ、GPUリソース管理、データ転送——を学ぶ。

---

## 参考文献

[1] Biewald, L. "Experiment Tracking with Weights and Biases." *Weights & Biases*, 2020. [https://www.wandb.com/](https://www.wandb.com/) (参照日: 2026-03-20)

[2] Zaharia, M. et al. "Accelerating the Machine Learning Lifecycle with MLflow." *IEEE Data Engineering Bulletin*, 41(4), 39–45, 2018. [https://doi.org/10.1109/DSAA.2018.00006](https://doi.org/10.1109/DSAA.2018.00006)

[3] Yadan, O. "Hydra — A framework for elegantly configuring complex applications." 2019. [https://hydra.cc/](https://hydra.cc/) (参照日: 2026-03-20)

[4] Iterative. "DVC: Data Version Control — Git for Data." [https://dvc.org/](https://dvc.org/) (参照日: 2026-03-20)

[5] Tatman, R., VanderPlas, J. & Dane, S. "A Practical Taxonomy of Reproducibility for Machine Learning Research." *Reproducibility in ML Workshop at ICML*, 2018.

[6] Weights & Biases. "W&B Documentation". [https://docs.wandb.ai/](https://docs.wandb.ai/) (参照日: 2026-03-20)

[7] MLflow Contributors. "MLflow Documentation". [https://mlflow.org/docs/latest/](https://mlflow.org/docs/latest/) (参照日: 2026-03-20)
