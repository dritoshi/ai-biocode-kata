# AIコーディングエージェントが機械学習・データ解析で使う用語集

> ML/データ解析のコーディング中にエージェントが説明なしに使ってくるカタカナ語・略語・混合表現をまとめたリスト。


## 略語（説明なしに出てくる）

### モデル・学習全般
| 略語 | 正式名称 | 意味 |
|---|---|---|
| ML | Machine Learning | 機械学習 |
| DL | Deep Learning | 深層学習 |
| NN | Neural Network | ニューラルネットワーク |
| LLM | Large Language Model | 大規模言語モデル |
| SLM | Small Language Model | 小規模言語モデル |
| FM | Foundation Model | 基盤モデル |
| SSL | Self-Supervised Learning | 自己教師あり学習 |
| SL | Supervised Learning | 教師あり学習 |
| RL | Reinforcement Learning | 強化学習 |
| RLHF | RL from Human Feedback | 人間のフィードバックによる強化学習 |
| DPO | Direct Preference Optimization | 直接選好最適化 |
| SFT | Supervised Fine-Tuning | 教師ありファインチューニング |
| PEFT | Parameter-Efficient Fine-Tuning | パラメータ効率的ファインチューニング |
| LoRA | Low-Rank Adaptation | 低ランク適応（軽量ファインチューニング手法） |
| QLoRA | Quantized LoRA | 量子化LoRA |
| FP16 / BF16 / FP32 | 浮動小数点精度 | 半精度/Brain浮動小数点/単精度 |
| INT8 / INT4 | 整数量子化ビット数 | 8ビット/4ビット量子化 |

### アーキテクチャ・レイヤー
| 略語 | 正式名称 | 意味 |
|---|---|---|
| MLP | Multi-Layer Perceptron | 多層パーセプトロン |
| CNN | Convolutional Neural Network | 畳み込みNN |
| RNN | Recurrent Neural Network | 再帰型NN |
| LSTM | Long Short-Term Memory | 長短期記憶 |
| GRU | Gated Recurrent Unit | ゲート付き再帰ユニット |
| GAN | Generative Adversarial Network | 敵対的生成ネットワーク |
| VAE | Variational Autoencoder | 変分オートエンコーダー |
| AE | Autoencoder | オートエンコーダー |
| GNN | Graph Neural Network | グラフNN |
| MoE | Mixture of Experts | 混合エキスパート |
| ViT | Vision Transformer | 画像用Transformer |
| MHA | Multi-Head Attention | マルチヘッドアテンション |
| FFN | Feed-Forward Network | 順伝播ネットワーク |
| BN | Batch Normalization | バッチ正規化 |
| LN | Layer Normalization | レイヤー正規化 |
| RMSNorm | Root Mean Square Normalization | RMS正規化 |

### 最適化・学習テクニック
| 略語 | 正式名称 | 意味 |
|---|---|---|
| SGD | Stochastic Gradient Descent | 確率的勾配降下法 |
| Adam / AdamW | Adaptive Moment Estimation | 適応的学習率最適化 |
| LR | Learning Rate | 学習率 |
| WD | Weight Decay | 重み減衰 |
| EMA | Exponential Moving Average | 指数移動平均 |
| KD | Knowledge Distillation | 知識蒸留 |
| CL | Curriculum Learning | カリキュラム学習 |
| CL | Contrastive Learning | 対照学習（文脈で判断） |
| DA | Data Augmentation | データ拡張 |
| GC | Gradient Clipping | 勾配クリッピング |
| GA | Gradient Accumulation | 勾配累積 |
| DDP | Distributed Data Parallel | 分散データ並列 |
| FSDP | Fully Sharded Data Parallel | 完全シャード化データ並列 |
| AMP | Automatic Mixed Precision | 自動混合精度 |

### 評価・メトリクス
| 略語 | 正式名称 | 意味 |
|---|---|---|
| AUC | Area Under the Curve | ROC曲線下面積 |
| ROC | Receiver Operating Characteristic | 受信者操作特性曲線 |
| mAP | mean Average Precision | 平均適合率 |
| IoU | Intersection over Union | 領域の重なり度合い |
| F1 | F1 Score | 適合率と再現率の調和平均 |
| BLEU | Bilingual Evaluation Understudy | 機械翻訳の評価指標 |
| ROUGE | Recall-Oriented Understudy for Gisting Evaluation | 要約の評価指標 |
| PPL | Perplexity | 言語モデルの困惑度 |
| FID | Fréchet Inception Distance | 生成画像の品質指標 |
| MSE | Mean Squared Error | 平均二乗誤差 |
| MAE | Mean Absolute Error | 平均絶対誤差 |
| RMSE | Root Mean Squared Error | 二乗平均平方根誤差 |
| CE | Cross Entropy | 交差エントロピー |
| KL | Kullback-Leibler (Divergence) | KLダイバージェンス |
| NLL | Negative Log-Likelihood | 負の対数尤度 |
| R² | R-squared / 決定係数 | 回帰モデルの当てはまり度 |

### データ解析・統計
| 略語 | 正式名称 | 意味 |
|---|---|---|
| EDA | Exploratory Data Analysis | 探索的データ分析 |
| PCA | Principal Component Analysis | 主成分分析 |
| t-SNE | t-distributed Stochastic Neighbor Embedding | 高次元データの2D/3D可視化 |
| UMAP | Uniform Manifold Approximation and Projection | 次元削減・可視化 |
| SVD | Singular Value Decomposition | 特異値分解 |
| NMF | Non-negative Matrix Factorization | 非負値行列因子分解 |
| GMM | Gaussian Mixture Model | 混合ガウスモデル |
| HMM | Hidden Markov Model | 隠れマルコフモデル |
| KDE | Kernel Density Estimation | カーネル密度推定 |
| IQR | Interquartile Range | 四分位範囲 |
| OLS | Ordinary Least Squares | 最小二乗法 |
| MLE | Maximum Likelihood Estimation | 最尤推定 |
| MAP | Maximum A Posteriori | 最大事後確率推定 |
| MCMC | Markov Chain Monte Carlo | マルコフ連鎖モンテカルロ法 |
| CI | Confidence Interval | 信頼区間 |
| FDR | False Discovery Rate | 偽発見率 |
| BH | Benjamini-Hochberg | FDR補正法 |
| CV | Cross-Validation | 交差検証 |
| k-NN | k-Nearest Neighbors | k近傍法 |
| SVM | Support Vector Machine | サポートベクターマシン |
| RF | Random Forest | ランダムフォレスト |
| XGB | XGBoost | 勾配ブースティング実装 |
| LGBM | LightGBM | 軽量勾配ブースティング |

### NLP
| 略語 | 正式名称 | 意味 |
|---|---|---|
| NLP | Natural Language Processing | 自然言語処理 |
| NER | Named Entity Recognition | 固有表現認識 |
| POS | Part of Speech (tagging) | 品詞タグ付け |
| TF-IDF | Term Frequency-Inverse Document Frequency | 文書中の単語重要度 |
| BPE | Byte Pair Encoding | トークナイザーの手法 |
| RAG | Retrieval-Augmented Generation | 検索拡張生成 |
| CoT | Chain of Thought | 思考の連鎖（推論手法） |
| ICL | In-Context Learning | 文脈内学習（Few-shot等） |

### バイオインフォマティクス関連
| 略語 | 正式名称 | 意味 |
|---|---|---|
| scRNA-seq | single-cell RNA sequencing | 単一細胞RNAシーケンシング |
| DEG | Differentially Expressed Gene | 発現変動遺伝子 |
| GO | Gene Ontology | 遺伝子オントロジー |
| GSEA | Gene Set Enrichment Analysis | 遺伝子セット濃縮解析 |
| QC | Quality Control | 品質管理 |
| HVG | Highly Variable Gene | 高変動遺伝子 |
| UMAP | （上記と同じ） | scRNA-seqでも頻出 |
| CPM / TPM / FPKM / RPKM | 各種発現量正規化法 | リードカウントの正規化指標 |
| WGS | Whole Genome Sequencing | 全ゲノムシーケンシング |
| WES | Whole Exome Sequencing | 全エクソームシーケンシング |
| MSA | Multiple Sequence Alignment | 多重配列アラインメント |


## カタカナ動詞

| 用語 | 意味 | 使い方の例 |
|---|---|---|
| フィッティングする | モデルをデータに適合 | 「データにフィッティングします」 |
| チューニングする | ハイパーパラメータを調整 | 「学習率をチューニングしてください」 |
| ファインチューニングする | 事前学習モデルを追加学習 | 「下流タスクでファインチューニングします」 |
| クラスタリングする | データをグループに分類 | 「UMAP後にクラスタリングします」 |
| エンコードする | データを数値表現に変換 | 「カテゴリ変数をワンホットエンコードします」 |
| デコードする | 数値表現を元の形に復元 | 「トークンIDをテキストにデコードします」 |
| エンベッディングする | データを密ベクトルに変換 | 「テキストをエンベッディングします」 |
| サンプリングする | 確率的にデータを抽出 | 「温度パラメータでサンプリングします」 |
| パディングする | 長さを揃えるため値を埋める | 「系列長が違うのでパディングします」 |
| トランケートする | 長すぎるデータを切り詰める | 「最大長512でトランケートします」 |
| マスクする | 一部を隠して学習に使う | 「15%のトークンをマスクします」 |
| ノーマライズする | 値の範囲を揃える | 「特徴量をノーマライズします」 |
| スタンダライズする | 平均0・分散1に変換 | 「各カラムをスタンダライズします」 |
| ビニングする | 連続値を区間に分割 | 「年齢を10歳刻みでビニングします」 |
| インピュートする | 欠損値を補完 | 「中央値でインピュートします」 |
| アンサンブルする | 複数モデルを組み合わせる | 「3つのモデルをアンサンブルして精度を上げます」 |
| プルーニングする | 不要な枝やパラメータを削除 | 「モデルをプルーニングして軽量化します」 |
| クオンタイズする | 重みの精度を下げて軽量化 | 「INT8にクオンタイズします」 |
| トークナイズする | テキストをトークン列に分割 | 「BPEでトークナイズします」 |
| アノテーションする | ラベルを付ける | 「手動でアノテーションが必要です」 |
| オーバーフィットする | 学習データに過剰適合 | 「このモデルはオーバーフィットしています」 |
| アンダーフィットする | 学習が不十分 | 「モデルがアンダーフィットしています」 |
| コンバージする | 学習が収束する | 「ロスがコンバージしました」 |
| ダイバージする | 学習が発散する | 「学習率が高すぎてダイバージしました」 |
| インファレンスする | 学習済みモデルで推論 | 「バッチでインファレンスします」 |
| プリプロセスする | 前処理を行う | 「テキストをプリプロセスします」 |
| ポストプロセスする | 後処理を行う | 「出力をポストプロセスしてフォーマットします」 |
| アグリゲートする | 集約する | 「セルレベルの値をサンプルごとにアグリゲートします」 |
| フィルタリングする | 条件で絞り込む | 「低品質セルをフィルタリングします」 |


## カタカナ名詞

### データ・特徴量
| 用語 | 意味 |
|---|---|
| フィーチャー / 特徴量 | モデルに入力する各変数 |
| ラベル / ターゲット | 予測したい正解値 |
| アノテーション | 正解ラベルの付与 |
| グラウンドトゥルース | 真の正解データ |
| エンベッディング | データの密ベクトル表現 |
| レイテントスペース / 潜在空間 | 圧縮された内部表現の空間 |
| トークン | テキストの最小分割単位 |
| コーパス | 学習用の大量テキスト集合 |
| バッチ | まとめて処理するデータの塊 |
| ミニバッチ | バッチを小分けにしたもの |
| エポック | 全データを1回通す学習単位 |
| イテレーション / ステップ | 1回のパラメータ更新 |
| シーケンス | 順序のあるデータ列 |
| テンソル | 多次元配列（PyTorch/TF） |
| スパース | 大部分がゼロのデータ |
| デンス | 密な（ゼロが少ない）データ |

### モデル・学習
| 用語 | 意味 |
|---|---|
| ハイパーパラメータ | 学習前に設定するパラメータ（学習率等） |
| ウェイト / 重み | モデルの学習可能パラメータ |
| バイアス | モデル内のオフセット項 / 偏り |
| グラディエント / 勾配 | パラメータの更新方向 |
| ロス / 損失 | モデルの予測誤差 |
| オプティマイザー | パラメータ更新の最適化手法 |
| スケジューラー | 学習率を動的に変更する仕組み |
| チェックポイント | 学習途中のモデル保存 |
| コールバック | 学習中の特定タイミングで呼ばれる処理 |
| レギュラライゼーション / 正則化 | 過学習を防ぐための制約 |
| ドロップアウト | ノードをランダムに無効化して正則化 |
| アーリーストッピング | 過学習の兆候で学習を打ち切る |
| ウォームアップ | 学習率を徐々に上げる初期フェーズ |
| バックボーン | モデルの主要な特徴抽出部分 |
| ヘッド | タスク固有の出力層 |
| フリーズする | パラメータを固定して更新しない |
| アテンション | 入力の重要部分に重み付けする仕組み |
| セルフアテンション | 入力同士の関係を計算する機構 |
| ソフトマックス | 出力を確率分布に変換する関数 |
| アクティベーション | 活性化関数（ReLU, GELU等） |
| プーリング | 情報を集約して次元を減らす |

### 推論・デプロイ
| 用語 | 意味 |
|---|---|
| レイテンシー | 推論にかかる時間 |
| スループット | 単位時間あたりの処理量 |
| バッチインファレンス | まとめて推論する |
| ストリーミング | 結果を逐次出力する |
| クオンタイゼーション / 量子化 | モデルの精度を下げて軽量化 |
| ディスティレーション / 蒸留 | 大モデルの知識を小モデルに移す |
| ONNX | モデルの相互運用フォーマット |
| TensorRT / TorchScript | 推論最適化エンジン |
| サービングする | モデルをAPI等で提供する |


## 日本語混合フレーズ（エージェントの定番表現）

| フレーズ | 意味 |
|---|---|
| 〜が過学習しています | 訓練データに適合しすぎて汎化できていない |
| 〜が収束しません | ロスが下がりきらない |
| 勾配爆発 / 勾配消失しています | 勾配が極端に大きく/小さくなる問題 |
| データリーケージの可能性があります | 学習データにテスト情報が漏れている |
| クラス不均衡を補正します | ラベルの偏りに対処する |
| 次元の呪いに注意してください | 高次元データで距離が無意味になる問題 |
| コールドスタート問題 | データ不足で推薦等ができない初期状態 |
| 分布シフト / ドメインシフト | 学習時と推論時のデータ分布の違い |
| 〜をフリーズして学習します | 特定レイヤーを固定して残りだけ更新 |
| 転移学習を活用します | 事前学習済みモデルの知識を別タスクに利用 |
| 特徴量エンジニアリングが必要です | 生データから有効な入力を設計する |
| アブレーションスタディ | 各要素の貢献を確かめる除去実験 |
| ベースラインと比較してください | 最低限のシンプルなモデルとの性能比較 |
| リークしている可能性があります | テスト情報が学習に混入 |
| 〜でアンサンブルすると精度が上がります | 複数モデルの統合で改善 |
| ハイパラサーチ / ハイパラチューニング | ハイパーパラメータの探索 |
| 学習曲線をプロットしてください | 学習の進み具合を可視化 |
| 混同行列を確認してください | 予測と正解の対応表で誤分類を分析 |
| 〜は表現力が足りません | モデルの容量が不足している |
| 正則化を強くします | 過学習抑制の制約を大きくする |
| ドロップアウト率を上げてください | ランダム無効化の割合を増やして正則化 |
| 〜をアップサンプリング/ダウンサンプリング | データ数を増減させる |
| ストラティファイドスプリット | クラス比率を保った分割 |
| 再現性のためにシードを固定 | 乱数を制御して結果を一定にする |
| OOM（Out of Memory）が出ます | GPUメモリ不足 |
| バッチサイズを下げてください | OOM対策の定番 |
| 勾配累積で実効バッチサイズを上げます | メモリ内でバッチを分割しつつ大バッチ効果 |
| 〜をデタッチしてください | 計算グラフから切り離す（PyTorch） |
| テンソルのシェイプが合いません | 次元・サイズの不一致エラー |
| ブロードキャストされます | 異なるシェイプの演算を自動拡張 |
