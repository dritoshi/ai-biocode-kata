#!/bin/bash
set -euo pipefail

mkdir -p results

# 複数サンプルの一括処理
for SAMPLE in sample_A sample_B sample_C; do
    echo "処理中: ${SAMPLE}"
    fastqc "data/${SAMPLE}_R1.fastq.gz" -o results/
done

# ファイルを列挙してループ
for BAM_FILE in results/*.bam; do
    samtools index "${BAM_FILE}"
done
