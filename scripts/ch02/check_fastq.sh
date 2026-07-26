#!/bin/bash
set -euo pipefail

FASTQ_DIR="${1:?FASTQディレクトリを指定してください}"
SAMPLE_ID="${2:?サンプルIDを指定してください}"
OUTPUT_DIR="${3:?出力ディレクトリを指定してください}"

# ファイルの存在確認
if [[ -f "${FASTQ_DIR}/${SAMPLE_ID}_R1.fastq.gz" ]]; then
    echo "FASTQファイルが見つかった"
else
    echo "エラー: FASTQファイルが見つからない" >&2
    exit 1
fi

# ディレクトリの存在確認
if [[ ! -d "${OUTPUT_DIR}" ]]; then
    mkdir -p "${OUTPUT_DIR}"
fi
