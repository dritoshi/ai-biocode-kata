# AIエージェントと学ぶ バイオインフォマティクスプログラミングの作法

配列解析から機械学習まで、環境構築・テスト・設計・公開のベストプラクティス

## 概要

AIコーディングエージェント（Claude Code CLI / Codex CLI）との協働を前提として、
バイオインフォマティクスのプログラミングに必要な知識を体系的に解説する書籍。

## 章の一覧

### Phase I: AIと始めるプログラミングの基礎

| 章 | タイトル | 原稿 | ロードマップ |
|----|---------|------|-------------|
| はじめに | — | [hajimeni.md](chapters/hajimeni.md) | — |
| 0 | AIエージェントにコードを書かせる | [00_ai_agent.md](chapters/00_ai_agent.md) | [§0](chapters/roadmap.md#0-aiエージェントにコードを書かせる2026年のベストプラクティス) |
| 1 | 設計原則 — 良いコードとは何か | [01_design.md](chapters/01_design.md) | [§1](chapters/roadmap.md#1-設計原則--良いコードとは何か) |
| 2 | ターミナルとシェルの基本操作 | [02_terminal.md](chapters/02_terminal.md) | [§2](chapters/roadmap.md#2-ターミナルとシェルの基本操作) |
| 3 | コーディングに必要な計算機科学 | [03_cs_basics.md](chapters/03_cs_basics.md) | [§3](chapters/roadmap.md#3-コーディングに必要な計算機科学) |
| 4 | データフォーマットの選び方 | [04_data_formats.md](chapters/04_data_formats.md) | [§4](chapters/roadmap.md#4-データフォーマットの選び方) |
| 5 | ソフトウェアの構成要素 — importからpipまで | [05_software_components.md](chapters/05_software_components.md) | [§5](chapters/roadmap.md#5-ソフトウェアの構成要素--importからpipまで) |
| 6 | Python環境の構築 — pyenv・venv・conda・uv | [06_dev_environment.md](chapters/06_dev_environment.md) | [§6](chapters/roadmap.md#6-python環境の構築--pyenvvenvcondauv) |

### Phase II: 信頼できるコードを育てる技術

| 章 | タイトル | 原稿 | ロードマップ |
|----|---------|------|-------------|
| 7 | Git入門 — コードのバージョン管理 | [07_git.md](chapters/07_git.md) | [§7](chapters/roadmap.md#7-git入門--コードのバージョン管理) |
| 8 | コードの正しさを守るテスト技法 | [08_testing.md](chapters/08_testing.md) | [§8](chapters/roadmap.md#8-コードの正しさを守るテスト技法) |
| 9 | デバッグの技術 — tracebackから最小再現例まで | [09_debug.md](chapters/09_debug.md) | [§9](chapters/roadmap.md#9-デバッグの技術--tracebackから最小再現例まで) |
| 10 | ソフトウェア成果物の設計 — スクリプトからパッケージまで | [10_deliverables.md](chapters/10_deliverables.md) | [§10](chapters/roadmap.md#10-ソフトウェア成果物の設計--スクリプトからパッケージまで) |
| 11 | コマンドラインツールの設計と実装 | [11_cli.md](chapters/11_cli.md) | [§11](chapters/roadmap.md#11-コマンドラインツールの設計と実装) |

### Phase III: データを扱うコードを書く

| 章 | タイトル | 原稿 | ロードマップ |
|----|---------|------|-------------|
| 12 | データ処理の実践 — NumPy・pandas・polars | [12_data_processing.md](chapters/12_data_processing.md) | [§12](chapters/roadmap.md#12-データ処理の実践--numpypandaspolars) |
| 13 | 可視化の実践 — matplotlib・seaborn・plotly | [13_visualization.md](chapters/13_visualization.md) | [§13](chapters/roadmap.md#13-可視化の実践--matplotlibseabornplotly) |
| 14 | 解析パイプラインの自動化 — Snakemake・Nextflow | [14_workflow.md](chapters/14_workflow.md) | [§14](chapters/roadmap.md#14-解析パイプラインの自動化--snakemakenextflow) |

### Phase IV: ソフトウェア再現性と大規模計算

| 章 | タイトル | 原稿 | ロードマップ |
|----|---------|------|-------------|
| 15 | コンテナによるソフトウェア環境の再現 — Docker・Apptainer | [15_container.md](chapters/15_container.md) | [§15](chapters/roadmap.md#15-コンテナによるソフトウェア環境の再現--dockerapptainer) |
| 16 | スパコン・クラスタでの大規模計算 | [16_hpc.md](chapters/16_hpc.md) | [§16](chapters/roadmap.md#16-スパコンクラスタでの大規模計算) |
| 17 | コードのパフォーマンス改善 — プロファイリングと高速化 | [17_performance.md](chapters/17_performance.md) | [§17](chapters/roadmap.md#17-コードのパフォーマンス改善--プロファイリングと高速化) |

### Phase V: 共有のためのコード整備

| 章 | タイトル | 原稿 | ロードマップ |
|----|---------|------|-------------|
| 18 | コードのドキュメント化 | [18_documentation.md](chapters/18_documentation.md) | [§18](chapters/roadmap.md#18-コードのドキュメント化) |
| 19 | 公共データベースとAPI — データ取得の実践 | [19_database_api.md](chapters/19_database_api.md) | [§19](chapters/roadmap.md#19-公共データベースとapi--データ取得の実践) |
| 20 | コードとデータのセキュリティ・倫理 | [20_security_ethics.md](chapters/20_security_ethics.md) | [§20](chapters/roadmap.md#20-コードとデータのセキュリティ倫理) |
| 21 | 共同開発の実践 — レビュー・質問・OSS参加 | [21_collaboration.md](chapters/21_collaboration.md) | [§21](chapters/roadmap.md#21-共同開発の実践--レビュー質問oss参加) |

### 付録

| 章 | タイトル | 原稿 | ロードマップ |
|----|---------|------|-------------|
| 付録A | AIコーディングエージェントとの効果的な学習パターン | [appendix_a_learning_patterns.md](chapters/appendix_a_learning_patterns.md) | [§付録A](chapters/roadmap.md#付録a-aiコーディングエージェントとの効果的な学習パターン) |
| 付録B | クイックリファレンス対照表 | [appendix_b_cli_reference.md](chapters/appendix_b_cli_reference.md) | [§付録B](chapters/roadmap.md#付録b-claude-code-cli--codex-cli-クイックリファレンス対照表) |
| 付録C | 論文投稿前チェックリスト | [appendix_c_checklist.md](chapters/appendix_c_checklist.md) | [§付録C](chapters/roadmap.md#付録c-論文投稿前チェックリスト) |
| 付録D | AIコーディングエージェント頻出用語・フレーズ集 | [appendix_d_agent_vocabulary.md](chapters/appendix_d_agent_vocabulary.md) | [§付録D](chapters/roadmap.md#付録d-aiコーディングエージェント頻出用語フレーズ集) |

## ディレクトリ構成

```
ai-biocode-kata/
├── CLAUDE.md           # 執筆規約（Claude Code CLI用）
├── chapters/
│   ├── hajimeni.md     # はじめに（番号なし）
│   ├── roadmap.md      # 全体構成マスタードキュメント
│   ├── 00_ai_agent.md  # §0: AIエージェントとの協働
│   ├── 01_design.md    # §1: 設計原則
│   ├── ...             # （以降、各章を追加）
│   └── appendix_c.md
├── figures/            # 図表
├── scripts/            # 書籍内コードサンプル
├── tests/              # サンプルコードのテスト
└── build/              # PDF/EPUB生成
```

- 全体構成の詳細は [roadmap.md](chapters/roadmap.md) を参照。
- [用語集](chapters/glossary.md)
- [執筆 TODO](TODO.md)

## ライセンス

この書籍の内容は [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/deed.ja)（表示 - 非営利 - 改変禁止 4.0 国際）ライセンスの下で提供されている。
