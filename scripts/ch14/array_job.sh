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
