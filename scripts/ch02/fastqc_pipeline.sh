#!/bin/bash
set -euo pipefail

# === 設定 ===
SAMPLE_ID="$1"                          # 第1引数をサンプルIDとして受け取る
FASTQ_DIR="data/fastq"
OUTPUT_DIR="results/${SAMPLE_ID}"

# === 前処理 ===
mkdir -p "${OUTPUT_DIR}"

# === 品質チェック ===
echo "品質チェック: ${SAMPLE_ID}"
fastqc "${FASTQ_DIR}/${SAMPLE_ID}_R1.fastq.gz" \
       -o "${OUTPUT_DIR}"

# === 完了 ===
echo "完了: ${SAMPLE_ID}"
