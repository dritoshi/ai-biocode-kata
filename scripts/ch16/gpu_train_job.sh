#!/bin/bash
#SBATCH --job-name=protein_train     # ジョブ名
#SBATCH --output=logs/%j.out         # ログ出力先
#SBATCH --error=logs/%j.err
#SBATCH --time=48:00:00              # GPUジョブは長時間になりやすい
#SBATCH --mem=64G                    # GPU学習ではホストメモリも多めに確保
#SBATCH --cpus-per-task=8            # データローダの並列度（GPU 1基あたり4〜8が目安）
#SBATCH --gres=gpu:1                 # GPU 1基を申請
#SBATCH --partition=gpu              # GPUパーティションを指定

# ログディレクトリを作成
mkdir -p logs

# CUDAと深層学習フレームワークをロード
module load cuda/12.0
module load cudnn/8.9

# conda環境をアクティベート
source activate ml_env

# GPUが認識されているか確認（デバッグ用）
echo "=== GPU情報 ==="
nvidia-smi

# 学習スクリプトを実行（wandbで実験追跡）
python train_protein_classifier.py \
    --epochs 100 \
    --batch-size 32 \
    --learning-rate 1e-4 \
    --data-dir data/protein_sequences/ \
    --output-dir results/models/ \
    --wandb-project protein-classifier
