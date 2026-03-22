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
