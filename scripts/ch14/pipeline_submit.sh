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
echo ""
echo "進捗確認: squeue -u \$USER"
echo "全キャンセル: scancel ${JOB1} ${JOB2} ${JOB3}"
