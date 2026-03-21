# §14 HPC

[§13A 実験管理](./13a_experiment.md)では、計算実験のパラメータと結果を体系的に記録・追跡する方法を学んだ。実験追跡の基盤が整ったことで、条件を変えながら多数の試行を繰り返す準備ができた。しかし、数十サンプルのRNA-seqアライメントや数百パターンのハイパーパラメータ探索を手元のノートPCで実行するのは現実的ではない。こうした大規模計算を効率的に実行するためのインフラが、HPC（High-Performance Computing）クラスタである。

HPCの知識は、エージェントとの協働で扱える解析の規模を一変させる。手元のPCだけでは1サンプルずつ逐次処理するしかないが、HPCクラスタの仕組みを理解していれば、エージェントにSLURMアレイジョブのスクリプトを生成させ、数十サンプルを並列に処理できる。ただし、リソース申請量（CPU・メモリ・GPU・実行時間）の適切さ、データの配置戦略（ホーム vs スクラッチ）、バックアップ計画——これらの判断は、自分のデータの特性とクラスタの運用ルールを理解している人間が行う必要がある。

本章では、HPCクラスタの基本構成、SLURMジョブスケジューラの使い方、リモート接続とファイル転送、そしてデータ管理・バックアップの実践を学ぶ。

---

## 14-1. HPCの基本

### HPCクラスタの構成

HPCクラスタは、ネットワークで接続された多数の計算機（ノード）の集合体である。大学や研究機関が共有リソースとして運用していることが多い。基本的な構成を以下に示す。

```
  ローカルPC                HPCクラスタ
 ┌─────────┐    SSH     ┌──────────────────────────────────────┐
 │          │──────────▶│  ログインノード                       │
 │  自分の  │           │  （ジョブ投入・ファイル編集用）        │
 │  PC      │           │     │                                │
 └─────────┘           │     │ sbatch                         │
                        │     ▼                                │
                        │  ┌──────────┐  ジョブ    ┌─────────┐ │
                        │  │ スケジュ │─────────▶│ 計算     │ │
                        │  │ ーラ     │  割当    │ ノード群 │ │
                        │  │ (SLURM)  │         │ (数百台) │ │
                        │  └──────────┘         └─────────┘ │
                        │                                      │
                        │  ┌──────────────────────────────┐   │
                        │  │  共有ファイルシステム          │   │
                        │  │  /home  /scratch  /work       │   │
                        │  └──────────────────────────────┘   │
                        └──────────────────────────────────────┘
```

**ログインノード**は、ユーザーがSSHで接続し、ジョブスクリプトの編集やジョブの投入を行うためのノードである。全ユーザーが共有しているため、ここで重い計算（アライメント、学習スクリプト等）を直接実行してはいけない。ログインノードに負荷をかけると、他のユーザーのジョブ投入やファイル操作にも影響する。

**計算ノード**は、実際の計算を実行するノードである。ユーザーは計算ノードに直接ログインせず、ジョブスケジューラ（SLURM等）を通じてリソースを申請し、ジョブを投入する。

**共有ファイルシステム**は、すべてのノードからアクセスできるストレージである。ログインノードで配置したデータは、計算ノードからも同じパスで参照できる。

### キューとパーティション

計算ノードは用途に応じて**パーティション**（partition）と呼ばれるグループに分けられている。施設ごとに名前や構成は異なるが、典型的な例を以下に示す。

| パーティション | 用途 | 制限時間の目安 | 特徴 |
|--------------|------|-------------|------|
| `short` / `debug` | テスト・デバッグ | 〜1時間 | 少数ノード、待ち時間短い |
| `normal` / `standard` | 通常の解析 | 〜72時間 | 汎用 |
| `long` | 長時間ジョブ | 〜14日 | 優先度低め |
| `gpu` | GPU計算 | 〜48時間 | GPUノード |
| `large-mem` / `highmem` | 大容量メモリ | 〜72時間 | 256GB〜1TB RAM |

利用可能なパーティションは `sinfo` コマンドで確認できる（詳細は[14-2節](#14-2-slurm)で学ぶ）。

### リソース申請の考え方

SLURMでは、ジョブごとに必要なリソースを4つの軸で申請する。

| リソース | ディレクティブ | 過少の場合 | 過大の場合 |
|---------|--------------|-----------|-----------|
| CPU | `--cpus-per-task` | 処理が遅い | 他ユーザーの待ち時間増 |
| メモリ | `--mem` | OOMキラーで強制終了 | リソースの無駄遣い |
| GPU | `--gres=gpu:N` | — | 高価なGPUが遊ぶ |
| 時間 | `--time` | タイムアウトで打ち切り | キューの待ち時間増 |

初めて実行するジョブでは、適切な申請量がわからないことが多い。以下の手順で段階的に調整するとよい。

1. **小さく試す**: まずサンプル1件で実行し、実際の使用量を観測する
2. **sacctで確認する**: ジョブ完了後に `sacct` コマンド（[14-2節](#14-2-slurm)参照）で実際の使用メモリと実行時間を確認する
3. **余裕を持たせる**: 実測値の1.5〜2倍を目安に申請する。ギリギリの値はサンプルによる変動で失敗しやすい

以下のコマンドで、完了済みジョブの実際のリソース使用量を確認できる。`sacct`はSLURMの会計情報を表示するコマンドで、`--format`で表示する項目を指定する。

```bash
# ジョブID 12345 の実際のメモリ使用量と実行時間を確認する
# MaxRSS: 最大メモリ使用量、Elapsed: 実行時間
sacct -j 12345 --format=JobID,MaxRSS,Elapsed,State
```

#### エージェントへの指示例

リソース申請の妥当性をエージェントに相談する場合:

> 「RNA-seqのHISAT2アライメントをHPCで実行したい。ヒトゲノム（hg38）に対して、ペアエンドで各サンプル約5000万リードのFASTQファイルが6サンプルある。SLURM用のジョブスクリプトを作成してください。メモリとCPUの推奨値も教えてください」

> 「このSLURMジョブスクリプトをレビューして、リソース申請量が適切か確認してください。過去のジョブでMaxRSSが12GBで実行時間が2時間だった」

> 「HPCのパーティション一覧（sinfoの出力）を見て、このジョブに最適なパーティションを提案してください」

---

## 14-2. SLURM

SLURM（Simple Linux Utility for Resource Management）は、HPCクラスタで最も広く使われているジョブスケジューラである。ユーザーのジョブを受け取り、利用可能な計算ノードに割り当て、実行結果を返す。

### SLURMの基本コマンド

以下の5つのコマンドを覚えておけば、日常的なHPC利用に対応できる。

| コマンド | 用途 | 使用例 |
|---------|------|--------|
| `sbatch` | ジョブスクリプトを投入する | `sbatch job.sh` |
| `squeue` | 自分のジョブの状態を確認する | `squeue -u $USER` |
| `scancel` | ジョブをキャンセルする | `scancel 12345` |
| `sinfo` | パーティションとノードの状態を確認する | `sinfo -s` |
| `sacct` | 完了済みジョブのリソース使用量を確認する | `sacct -j 12345` |

`squeue`の出力に表示されるジョブの状態コードの主要なものを以下に示す。

| 状態コード | 意味 |
|-----------|------|
| `PD` (PENDING) | キューで待機中（リソースが空くのを待っている） |
| `R` (RUNNING) | 実行中 |
| `CG` (COMPLETING) | 完了処理中 |
| `CA` (CANCELLED) | キャンセルされた |
| `F` (FAILED) | エラーで失敗 |
| `TO` (TIMEOUT) | 制限時間超過で打ち切り |
| `OOM` (OUT_OF_MEMORY) | メモリ不足で強制終了 |

### ジョブスクリプトの書き方

SLURMジョブスクリプトは、`#SBATCH` で始まるディレクティブ行でリソースを指定し、その後にシェルコマンドを記述するBashスクリプトである。以下は最小構成の例で、FastQCによる品質確認を4スレッドで実行する。

```bash
#!/bin/bash
#SBATCH --job-name=fastqc_run        # squeueで表示されるジョブ名
#SBATCH --output=logs/%j.out         # 標準出力ログ（%jはジョブIDに展開）
#SBATCH --error=logs/%j.err          # 標準エラーログ
#SBATCH --time=01:00:00              # 制限時間（時:分:秒）
#SBATCH --mem=4G                     # メモリ上限
#SBATCH --cpus-per-task=4            # CPUコア数

# ログディレクトリを作成（存在しなければ）
mkdir -p logs

# 環境モジュールをロード
module load fastqc/0.12.1

# FastQCを4スレッドで実行
fastqc --threads 4 data/*.fastq.gz --outdir results/fastqc/
```

`#SBATCH` ディレクティブはスクリプトの先頭（`#!/bin/bash` の直後）にまとめて記述する必要がある。途中にコメントや空行以外の行を挟むと、それ以降の `#SBATCH` はSLURMに無視される。

投入は `sbatch` コマンドで行う。

```bash
# ジョブスクリプトをSLURMに投入する
# 投入後、ジョブIDが表示される（例: Submitted batch job 12345）
sbatch basic_job.sh
```

### アレイジョブ

複数のサンプルに対して同じ処理を並列実行する場合は、**アレイジョブ**（array job）が便利である。`--array` オプションでタスクの範囲を指定すると、SLURMは各タスクに `SLURM_ARRAY_TASK_ID` という環境変数で通し番号を割り当てる。

以下の例では、`samples.txt` に記載された6サンプルのFASTQファイルをそれぞれ別の計算ノードでアライメントする。`sed -n "${SLURM_ARRAY_TASK_ID}p"` で、サンプルリストのN行目を取得している。

```bash
#!/bin/bash
#SBATCH --job-name=hisat2_array      # ジョブ名
#SBATCH --output=logs/%A_%a.out      # %A=アレイ親ID, %a=タスクID
#SBATCH --error=logs/%A_%a.err
#SBATCH --time=04:00:00              # 1サンプルあたりの制限時間
#SBATCH --mem=16G                    # 1タスクあたりのメモリ
#SBATCH --cpus-per-task=8            # 1タスクあたりのCPU
#SBATCH --array=1-6                  # サンプル数に合わせて変更

# ログディレクトリを作成
mkdir -p logs

# サンプルリストからN行目を取得（SLURM_ARRAY_TASK_IDは1始まり）
SAMPLE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" samples.txt)

echo "Processing sample: ${SAMPLE} (task ${SLURM_ARRAY_TASK_ID})"

# 環境モジュールをロード
module load hisat2/2.2.1
module load samtools/1.19

# HISAT2でアライメント → SAMをBAMに変換・ソート
hisat2 -p 8 -x genome_index \
    -1 "data/${SAMPLE}_R1.fastq.gz" \
    -2 "data/${SAMPLE}_R2.fastq.gz" \
    | samtools sort -@ 4 -o "results/${SAMPLE}.sorted.bam"

# BAMインデックスを作成
samtools index "results/${SAMPLE}.sorted.bam"

echo "Done: ${SAMPLE}"
```

`samples.txt` はサンプル名を1行に1つ記載したテキストファイルである。

```
sample_A
sample_B
sample_C
sample_D
sample_E
sample_F
```

同時実行数を制限したい場合は `--array=1-100%10` のように `%N` を付ける。この例では100タスク中、同時に最大10タスクまで実行する。

### 依存ジョブ

パイプラインのように複数のステップを順序通りに実行する場合は、`--dependency` オプションで前のジョブの完了を待ってから次のジョブを開始できる。

以下のスクリプトは、FastQC → アライメント → カウント定量の3段階を依存ジョブチェーンとして投入する。`sbatch --parsable` はジョブIDのみを返すオプションで、変数に格納して次のジョブの `--dependency` に渡している。

```bash
#!/bin/bash
# RNA-seqパイプラインを依存ジョブチェーンとして投入するスクリプト
# 各ステップは前のステップが成功（afterok）した場合のみ開始する

set -euo pipefail  # エラー時に停止

echo "=== RNA-seq パイプライン投入 ==="

# ステップ1: FastQC（品質確認）
JOB1=$(sbatch --parsable \
    --job-name=step1_fastqc \
    --output=logs/step1_%j.out \
    --time=01:00:00 \
    --mem=4G \
    --cpus-per-task=4 \
    --wrap="module load fastqc/0.12.1 && fastqc data/*.fastq.gz -o results/fastqc/")
echo "Step 1 (FastQC): Job ${JOB1}"

# ステップ2: アライメント（ステップ1の成功後に開始）
JOB2=$(sbatch --parsable \
    --dependency=afterok:${JOB1} \
    --job-name=step2_align \
    --output=logs/step2_%j.out \
    --time=08:00:00 \
    --mem=32G \
    --cpus-per-task=16 \
    --wrap="module load hisat2/2.2.1 samtools/1.19 && bash scripts/run_alignment.sh")
echo "Step 2 (Alignment): Job ${JOB2} (depends on ${JOB1})"

# ステップ3: カウント定量（ステップ2の成功後に開始）
JOB3=$(sbatch --parsable \
    --dependency=afterok:${JOB2} \
    --job-name=step3_count \
    --output=logs/step3_%j.out \
    --time=02:00:00 \
    --mem=8G \
    --cpus-per-task=4 \
    --wrap="module load subread/2.0.6 && featureCounts -T 4 -a annotation.gtf -o counts.txt results/*.bam")
echo "Step 3 (FeatureCounts): Job ${JOB3} (depends on ${JOB2})"

echo ""
echo "=== 依存関係 ==="
echo "  ${JOB1} (FastQC) → ${JOB2} (Alignment) → ${JOB3} (FeatureCounts)"
```

`--dependency=afterok:JOB_ID` は「指定したジョブが正常終了した場合のみ開始する」という意味である。ステップ1が失敗した場合、ステップ2以降は自動的にキャンセルされる。

なお、より大規模なパイプラインでは依存ジョブの手動管理は煩雑になる。[§12 ワークフロー管理](./12_workflow.md)で学んだSnakemakeには `--slurm` オプションがあり、Snakemakeが各ルールのSLURMジョブ投入と依存関係を自動管理してくれる。

### インタラクティブジョブ

デバッグや小規模なテストでは、計算ノード上でシェルを直接操作したいことがある。`srun --pty bash` を使うと、計算ノード上でインタラクティブなBashセッションを開始できる。`--pty`は疑似端末を割り当てるオプションである。

```bash
# 計算ノード上でインタラクティブシェルを開始する
# 4コア・8GBメモリを1時間確保する
srun --cpus-per-task=4 --mem=8G --time=01:00:00 --pty bash
```

GPUを使ったインタラクティブセッションの場合:

```bash
# GPUノードでインタラクティブシェルを開始する
srun --partition=gpu --gres=gpu:1 --cpus-per-task=4 --mem=16G --time=01:00:00 --pty bash
```

セッション内では、ログインノードと同様にコマンドを実行できる。ただし、`--time` で指定した時間を超えるとセッションは自動的に終了する。

### GPU申請

GPU計算を行うには、`--gres=gpu:N` でGPUの数を申請する。`gres` は Generic Resource の略で、GPUに限らず特殊なリソースを申請するための仕組みである。

```bash
# GPU 1基を申請する
#SBATCH --gres=gpu:1

# 特定のGPU型番を指定する（施設が対応している場合）
#SBATCH --gres=gpu:a100:1
```

ジョブ内でGPUが正しく認識されているかは `nvidia-smi` コマンドで確認できる。

```bash
# GPU情報を表示する（割り当てられたGPUが見えることを確認）
nvidia-smi
```

GPU使用時は、以下の点に注意する:

- **CPUも十分に確保する**: データローディングはCPUで行うため、GPU 1基あたり4〜8 CPUを目安に申請する
- **CUDAバージョンを合わせる**: `module load cuda/12.0` でGPUドライバに対応するCUDAをロードする。[§13 コンテナと再現性](./13_container.md)で学んだApptainerを使えば、CUDA環境もコンテナ内に固定できる
- **メモリに余裕を持たせる**: GPU学習ではホストメモリも使用するため、通常の解析より多めに申請する

> **🤖 コラム: GPU学習ジョブのSLURMスクリプト**
>
> [§13A 実験管理](./13a_experiment.md)で学んだwandbと組み合わせた、深層学習の学習ジョブの実用的な構成例を示す。`--wandb-project` でwandbのプロジェクト名を指定し、学習のパラメータと結果を自動的に追跡する。
>
> ```bash
> #!/bin/bash
> #SBATCH --job-name=protein_train     # ジョブ名
> #SBATCH --output=logs/%j.out         # ログ出力先
> #SBATCH --error=logs/%j.err
> #SBATCH --time=48:00:00              # GPUジョブは長時間になりやすい
> #SBATCH --mem=64G                    # GPU学習ではホストメモリも多めに確保
> #SBATCH --cpus-per-task=8            # データローダの並列度（GPU 1基あたり4〜8が目安）
> #SBATCH --gres=gpu:1                 # GPU 1基を申請
> #SBATCH --partition=gpu              # GPUパーティションを指定
>
> # ログディレクトリを作成
> mkdir -p logs
>
> # CUDAと深層学習フレームワークをロード
> module load cuda/12.0
> module load cudnn/8.9
>
> # conda環境をアクティベート
> source activate ml_env
>
> # GPUが認識されているか確認（デバッグ用）
> echo "=== GPU情報 ==="
> nvidia-smi
>
> # 学習スクリプトを実行（wandbで実験追跡）
> python train_protein_classifier.py \
>     --epochs 100 \
>     --batch-size 32 \
>     --learning-rate 1e-4 \
>     --data-dir data/protein_sequences/ \
>     --output-dir results/models/ \
>     --wandb-project protein-classifier
> ```
>
> GPUジョブのデバッグ時には、まず `srun --pty bash` でインタラクティブにGPUノードに入り、`nvidia-smi` でGPUが見えることを確認してからスクリプトを実行するとよい。

> **🧬 コラム: バイオインフォの典型的なHPCジョブパターン**
>
> バイオインフォマティクスの主要な解析タイプごとに、HPCリソースのボトルネックが異なる。以下の表を目安としてリソースを申請するとよい。実際の値はデータサイズやツールのバージョンによって変動するため、まず小規模に試して `sacct` で実測値を確認する。
>
> | 解析タイプ | ボトルネック | CPU目安 | メモリ目安 | 時間目安 | 備考 |
> |-----------|------------|---------|----------|---------|------|
> | RNA-seq（アライメント） | CPU | 8〜16 | 16〜32 GB | 2〜8時間/サンプル | HISAT2/STARはマルチスレッド対応 |
> | WGS（バリアントコール） | CPU・メモリ | 8〜16 | 32〜64 GB | 12〜48時間/サンプル | GATKのHaplotypeCallerは高メモリ |
> | scRNA-seq | メモリ | 4〜8 | 64〜256 GB | 1〜4時間 | カウント行列が大きい |
> | メタゲノム（アセンブリ） | メモリ | 16〜32 | 128〜512 GB | 12〜72時間 | MEGAHIT/SPAdesは大量メモリ |
> | 深層学習 | GPU | 4〜8 | 32〜64 GB | 数時間〜数日 | GPU 1基以上必須 |

#### エージェントへの指示例

SLURMジョブスクリプトの作成や管理をエージェントに依頼する場合:

> 「以下の解析をHPCで実行するSLURMジョブスクリプトを書いてください。HISAT2でヒトゲノムにアライメントし、samtoolsでBAMに変換・ソートする。サンプルは6つで、アレイジョブとして投入したい」

> 「このSLURMジョブスクリプトにエラーハンドリングを追加してください。ジョブ失敗時にSlackに通知する仕組みも含めて」

> 「sacctの出力を解析して、過去1週間のジョブのメモリ使用率と実行時間効率をまとめるワンライナーを書いてください」

---

## 14-3. リモート接続とファイル転送

HPCを利用するには、ローカルPCからクラスタへのSSH接続と、解析データの転送が必要になる。SSH接続の基礎は[§2 ターミナルとシェルの基礎](./02_terminal.md)を参照してほしい。ここでは、HPC利用に特化した実践的なテクニックを扱う。

### rsyncによるファイル転送

ローカルPCとHPC間のデータ転送には `rsync` が最適である。`scp` も使えるが、rsyncには以下の利点がある。

| 特徴 | `scp` | `rsync` |
|------|-------|---------|
| 差分転送 | 不可（毎回全ファイルを転送） | 可（変更されたファイルのみ転送） |
| 中断からの再開 | 不可 | 可（`--partial`） |
| 転送前の確認 | 不可 | 可（`--dry-run`） |
| ファイル除外 | 不可 | 可（`--exclude`） |

以下に、rsyncの基本的な使い方を示す。`-a`はアーカイブモード（パーミッション等を保持）、`-v`は進捗表示、`-z`は転送時の圧縮を意味する。

```bash
# ローカル → HPC: dataディレクトリをHPCのプロジェクト領域に転送する
# 末尾のスラッシュ（data/）に注意: ディレクトリの中身を転送する
rsync -avz data/ hpc:~/project/data/

# HPC → ローカル: 結果をダウンロードする
rsync -avz hpc:~/project/results/ ./results/

# 転送前の確認（--dry-run）: 実際には転送せず、何が転送されるかを表示する
rsync -avz --dry-run data/ hpc:~/project/data/

# 特定のファイルを除外する: 中間ファイルや巨大なFASTQを除外する例
rsync -avz --exclude="*.bam" --exclude="*.fastq.gz" results/ hpc:~/project/results/
```

大容量のFASTQファイルを転送する場合は、`--progress` で進捗を確認しながら転送するとよい。途中で通信が切れた場合は、同じコマンドを再実行すれば差分転送で再開される。

```bash
# 大容量ファイルを進捗表示付きで転送し、中断時に再開可能にする
rsync -avz --progress --partial data/large_fastq/ hpc:~/project/data/
```

### ポートフォワーディング

HPC上でJupyter NotebookやTensorBoardを使いたい場合、計算ノードのポートはローカルPCから直接アクセスできない。SSHの**ポートフォワーディング**（`-L` オプション）を使うと、ローカルPCのポートをHPC上のポートに転送し、ブラウザからアクセスできるようになる。

手順は以下の通りである。

1. HPC上でJupyter Notebookを起動する（計算ノード上で実行すること）

```bash
# インタラクティブジョブとしてJupyterを起動する
srun --cpus-per-task=4 --mem=8G --time=04:00:00 --pty bash

# 計算ノード上で:
module load anaconda3
jupyter notebook --no-browser --port=8888
# 出力にURLが表示される（例: http://localhost:8888/?token=abc123...）
```

2. 別のターミナルからSSHポートフォワーディングを設定する。`-L 8888:計算ノード名:8888` で、ローカルの8888番ポートを計算ノードの8888番ポートに転送する。

```bash
# ローカルPCから: ローカル8888 → HPC上の計算ノード8888 を転送する
# 「compute-node-01」はsrunで割り当てられたノード名に置き換える
ssh -L 8888:compute-node-01:8888 hpc
```

3. ローカルPCのブラウザで `http://localhost:8888` にアクセスすると、HPC上のJupyterに接続できる

### 多段SSH（ProxyJump）

多くの研究機関では、HPCクラスタに直接接続できず、**踏み台サーバ**（bastion host）を経由する必要がある。`~/.ssh/config` に以下の設定を追加すると、`ssh hpc` だけで踏み台を自動的に経由できる。

```
# ~/.ssh/config の設定例

# 踏み台サーバ
Host bastion
    HostName gateway.example.ac.jp
    User your_username
    IdentityFile ~/.ssh/id_ed25519

# HPC（踏み台経由で自動接続）
Host hpc
    HostName login.hpc.internal
    User your_username
    IdentityFile ~/.ssh/id_ed25519
    ProxyJump bastion
    ServerAliveInterval 60
```

`ProxyJump bastion` が踏み台経由の設定である。この設定により、以下のコマンドが使えるようになる。

```bash
# 1コマンドでHPCに接続（踏み台を自動経由）
ssh hpc

# rsyncも同じホスト名で使える
rsync -avz data/ hpc:~/project/data/
```

`ServerAliveInterval 60` は60秒ごとにキープアライブ信号を送る設定で、無操作時のSSH切断を防ぐ。

#### エージェントへの指示例

リモート接続やファイル転送の設定をエージェントに依頼する場合:

> 「HPCクラスタへのSSH接続を~/.ssh/configに設定したい。以下の情報で設定ファイルを生成してください: ホスト名=login.hpc.univ.ac.jp、ユーザー名=tanaka、踏み台=gateway.univ.ac.jp」

> 「HPC上のJupyter Notebookにローカルからアクセスするためのポートフォワーディングの手順を教えてください。HPCにはProxyJump経由で接続しています」

> 「大容量のFASTQファイル（合計500GB）をローカルからHPCに転送するrsyncコマンドを書いてください。途中で切れても再開でき、中間ファイル（*.bam, *.sam）は除外したい」

---

## 14-4. データ管理・バックアップ・共有

HPCのストレージ構成は、個人のノートPCとは大きく異なる。用途に応じて複数の領域を使い分ける必要がある。

### ホーム vs スクラッチ

HPCの典型的なストレージ構成を以下に示す。

| 領域 | パス例 | 容量 | 永続性 | 速度 | 用途 |
|------|-------|------|--------|------|------|
| ホーム | `/home/username` | 〜50 GB | 永続・バックアップあり | 低速 | 設定ファイル、小さなスクリプト |
| スクラッチ | `/scratch/username` | 〜10 TB | **一時的・自動パージ** | 高速 | 解析中のデータ、中間ファイル |
| ワーク | `/work/group_name` | 〜1 TB | 永続・バックアップなし | 中速 | グループ共有データ |
| ローカルSSD | `$TMPDIR` | 〜500 GB | **ジョブ終了時に消去** | 最速 | ジョブ内の一時ファイル |

**重要**: スクラッチ領域は定期的にパージ（自動削除）される。一般的には30〜90日間アクセスのないファイルが対象となる。スクラッチに置いたデータは永続的な保管場所ではない。

ジョブ内で高速なI/Oが必要な場合（大量の小ファイルの読み書き等）は、`$TMPDIR`（ノードローカルのSSD）を活用する。ジョブスクリプト内でデータを `$TMPDIR` にコピーし、処理結果をスクラッチにコピーして戻す。

```bash
# ジョブスクリプト内: ローカルSSDを活用してI/Oを高速化する
# $TMPDIR はSLURMがジョブごとに割り当てる一時領域
cp -r /scratch/$USER/input_data "$TMPDIR/"

cd "$TMPDIR"
# ここで解析を実行（高速I/O）
python analysis.py --input input_data/ --output output/

# 結果をスクラッチにコピーして戻す
cp -r output/ /scratch/$USER/results/
```

> **🧬 コラム: スクラッチの事故事例**
>
> ある研究室の大学院生が、全ゲノムシーケンシングの生データ（FASTQ、合計2 TB）をスクラッチ領域にのみ保存していた。クラスタの90日パージポリシーを把握しておらず、論文執筆に集中している間にデータが自動削除された。シーケンシングの再実行にはサンプルの再調製からやり直す必要があり、半年の遅延が生じた。
>
> スクラッチ領域は**計算中の一時置き場**であり、保管場所ではない。生データは必ず別の永続的なストレージにバックアップを取ってから解析を始める。

### モジュールシステム

HPCでは、ソフトウェアの管理に**モジュールシステム**（Environment Modules / Lmod）が使われていることが多い。`module load` でツールをロードし、`module unload` でアンロードする。モジュールシステムは環境変数（`PATH`、`LD_LIBRARY_PATH`等）を切り替えることで、同じクラスタ上で複数バージョンのツールを共存させている。

```bash
# 利用可能なモジュールを検索する（部分一致）
module avail samtools

# モジュールをロードする
module load samtools/1.19

# 現在ロードされているモジュールを一覧表示する
module list

# モジュールをアンロードする
module unload samtools/1.19
```

モジュールシステムで提供されていないツールが必要な場合は、[§5 開発環境の構築](./05_dev_environment.md)で学んだconda環境を使う。ただし、HPCによってはホームディレクトリの容量制限でconda環境が圧迫されることがある。その場合は、ワーク領域やスクラッチにconda環境を配置する。

```bash
# conda環境をスクラッチに作成する（ホームの容量節約）
conda create --prefix /scratch/$USER/envs/rnaseq python=3.11 numpy pandas
conda activate /scratch/$USER/envs/rnaseq
```

### 共有ファイルシステムの注意

HPCの共有ファイルシステム（Lustre、GPFS等）は、大きなファイルの連続読み書きに最適化されている。逆に、大量の小ファイル（数十万個のファイル）の操作は性能が極端に低下し、他のユーザーにも影響する。[§3 計算機の基礎](./03_cs_basics.md)で学んだファイルシステムの仕組みを思い出してほしい。

対策として:

- **大量の小ファイルは `tar` でまとめる**: 前処理済みの個別ファイルをアーカイブにまとめてから転送・保管する

```bash
# 大量の小ファイルをtarでまとめる（圧縮なし、速度重視）
tar cf processed_data.tar processed/

# 圧縮ありでまとめる
tar czf processed_data.tar.gz processed/
```

- **ジョブ内ではローカルSSD (`$TMPDIR`) を使う**: 小ファイルの読み書きが多い処理はノードローカルで実行する

### 3-2-1バックアップルール

研究データの損失は取り返しがつかない。以下の**3-2-1ルール**に従ってバックアップを設計する。

- **3コピー**: データのコピーを3つ以上持つ（オリジナル + 2つのバックアップ）
- **2メディア**: 2種類以上の異なるメディアに保存する（HDD + クラウド等）
- **1オフサイト**: 少なくとも1つは物理的に離れた場所に保管する（クラウドストレージ等）

### ストレージの使い分け

研究プロジェクトで利用可能なストレージを、目的に応じて使い分ける。

| ストレージ | 用途 | バックアップ | アクセス速度 | コスト |
|-----------|------|------------|------------|-------|
| HPC スクラッチ | 計算実行中の一時利用 | なし（パージあり） | 高速 | 無料（利用時間課金内） |
| HPC ワーク領域 | グループ共有データ | 施設による | 中速 | 無料〜低 |
| ラボ内NAS | 中長期保管、グループ共有 | RAID等 | 中速 | 初期投資 |
| クラウド（S3, GCS等） | オフサイトバックアップ、外部共有 | 冗長化済み | 低速（転送依存） | 容量課金 |
| 大学データリポジトリ | 公開・永続保管 | 管理者運用 | 低速 | 通常無料 |

### 将来のグループメンバーがアクセスできる設計

HPCのプロジェクトデータは、自分だけでなく後任の学生やポスドクもアクセスする。以下の3つの原則を守る。

**1. 命名規則を統一する**

ディレクトリ名に日付・プロジェクト名を含め、見ただけで内容がわかるようにする。[§8 成果物のパッケージング](./08_deliverables.md)で学んだプロジェクト構成の考え方をHPC上でも適用する。

```
/work/lab_name/
├── 20240315_rnaseq_mouse_liver/
├── 20240501_wgs_patient_cohort/
└── 20241001_scrna_tumor_atlas/
```

**2. プロジェクトREADMEを設置する**

各プロジェクトディレクトリの直下にREADMEを置き、データの概要・取得元・処理状況を記録する。以下はテンプレートの抜粋である（完全版は `scripts/ch14/project_readme_template.md` を参照）。

```markdown
# プロジェクト名: RNA-seq マウス肝臓

## データ
- 生データ: data/raw/ — Illumina NovaSeq 6000, PE150, 6サンプル
- 外部データベース: GRCm39 (Ensembl release 111)

## 解析の実行手順
1. 品質確認: sbatch scripts/step1_fastqc.sh
2. アライメント: sbatch scripts/step2_align.sh
3. カウント定量: sbatch scripts/step3_count.sh
```

**3. 個人アカウントに依存しない**

- グループ共有のワーク領域（`/work/lab_name/`）を使い、データを個人のホームディレクトリに置かない
- [§6 Git](./06_git.md)でスクリプトを管理し、組織のGitHubリポジトリに格納する
- 退職・異動後もデータにアクセスできる体制を整える

→ 投稿前のバックアップ・共有の最終確認は[付録D 論文投稿前チェックリスト](./roadmap.md#付録d-論文投稿前チェックリスト)を参照。

#### エージェントへの指示例

データ管理やバックアップの設計をエージェントに相談する場合:

> 「HPCのスクラッチ領域にある解析結果をラボのNASにバックアップするrsyncコマンドを書いてください。cronで週次実行にしたい」

> 「このプロジェクトのディレクトリ構成をレビューして、データ管理の改善点を指摘してください。現在、生データと結果が同じディレクトリに混在しています」

> 「新しいプロジェクト用のディレクトリ構成とREADMEテンプレートを作成してください。RNA-seqの解析で、6サンプル、ペアエンドです」

---

## まとめ

本章で学んだHPC利用の主要概念を整理する。

| 概念 | 要点 |
|------|------|
| **クラスタ構成** | ログインノード（軽作業のみ）+ 計算ノード（ジョブ投入経由） |
| **リソース申請** | CPU・メモリ・GPU・時間の4軸、小さく試してsacctで調整 |
| **SLURM基本** | sbatch（投入）、squeue（確認）、scancel（取消）、sacct（実績） |
| **アレイジョブ** | `--array` + `SLURM_ARRAY_TASK_ID` で多サンプル並列実行 |
| **依存ジョブ** | `--dependency=afterok:JOB_ID` でパイプライン構築 |
| **rsync** | 差分転送・中断再開が可能なファイル転送 |
| **ポートフォワーディング** | `ssh -L` でJupyter/TensorBoardにアクセス |
| **ホーム vs スクラッチ** | スクラッチは一時領域、自動パージに注意 |
| **3-2-1バックアップ** | 3コピー、2メディア、1オフサイト |
| **データ共有設計** | 命名規則、README設置、個人アカウント非依存 |

次章の[§15 パフォーマンスと最適化](./15_performance.md)では、プログラムの実行時間とメモリ使用量を計測・改善する方法——プロファイリング、アルゴリズムの選択、並列化——を学ぶ。

---

## 参考文献

[1] SchedMD. "Slurm Workload Manager Documentation". https://slurm.schedmd.com/documentation.html (参照日: 2026-03-21)

[2] SchedMD. "sbatch - Submit a batch script to Slurm". https://slurm.schedmd.com/sbatch.html (参照日: 2026-03-21)

[3] SchedMD. "sacct - Display accounting data for all jobs". https://slurm.schedmd.com/sacct.html (参照日: 2026-03-21)

[4] NIH HPC. "Biowulf User Guide". https://hpc.nih.gov/docs/userguide.html (参照日: 2026-03-21)

[5] Andrew Tridgell and Paul Mackerras. "The rsync algorithm". https://rsync.samba.org/tech_report/ (参照日: 2026-03-21)

[6] Peter Bailis and Kyle Kingsbury. "The Network is Reliable". *Communications of the ACM*, 57(9), 48-55, 2014. https://doi.org/10.1145/2643130

[7] US-CERT. "Securing Network Infrastructure Devices". https://www.cisa.gov/news-events/alerts (参照日: 2026-03-21)

[8] Australian BioCommons. "Introduction to HPC for Bioinformatics". https://australianbiocommons.github.io/how-to-guides/hpc_guide (参照日: 2026-03-21)
