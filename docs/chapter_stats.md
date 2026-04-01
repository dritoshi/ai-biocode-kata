# 各章の文字数・読了時間

## 統計テーブル

| 章 | タイトル | 原稿 | 文字数(raw) | 本文文字数 | 全角換算 | 読了時間 |
|----|---------|------|-----------|----------|---------|:------:|
| はじめに | — | [hajimeni.md](../chapters/hajimeni.md) | 8,406 | 6,853 | 5,621 | 24m |
| §0 | AIエージェントにコードを書かせる | [00_ai_agent.md](../chapters/00_ai_agent.md) | 27,827 | 18,544 | 15,565 | 1h39m |
| §1 | 設計原則 — 良いコードとは何か | [01_design.md](../chapters/01_design.md) | 12,925 | 8,547 | 7,051 | 47m |
| §2 | ターミナルとシェルの基本操作 | [02_terminal.md](../chapters/02_terminal.md) | 20,074 | 10,921 | 8,750 | 1h11m |
| §3 | コーディングに必要な計算機科学 | [03_cs_basics.md](../chapters/03_cs_basics.md) | 22,795 | 15,286 | 11,941 | 1h24m |
| §4 | データフォーマットの選び方 | [04_data_formats.md](../chapters/04_data_formats.md) | 25,414 | 16,460 | 12,547 | 1h15m |
| §5 | ソフトウェアの構成要素 | [05_software_components.md](../chapters/05_software_components.md) | 19,585 | 11,933 | 9,710 | 1h15m |
| §6 | Python環境の構築 | [06_dev_environment.md](../chapters/06_dev_environment.md) | 13,947 | 8,798 | 6,746 | 44m |
| §7 | Git入門 | [07_git.md](../chapters/07_git.md) | 17,126 | 10,881 | 8,711 | 1h00m |
| §8 | コードの正しさを守るテスト技法 | [08_testing.md](../chapters/08_testing.md) | 19,942 | 9,801 | 8,105 | 1h21m |
| §9 | デバッグの技術 | [09_debug.md](../chapters/09_debug.md) | 22,213 | 11,453 | 9,100 | 1h27m |
| §10 | ソフトウェア成果物の設計 | [10_deliverables.md](../chapters/10_deliverables.md) | 23,428 | 12,382 | 10,497 | 1h35m |
| §11 | コマンドラインツールの設計と実装 | [11_cli.md](../chapters/11_cli.md) | 22,258 | 9,978 | 7,825 | 1h36m |
| §12 | データ処理の実践 | [12_data_processing.md](../chapters/12_data_processing.md) | 19,358 | 11,543 | 9,101 | 1h11m |
| §13 | 可視化の実践 | [13_visualization.md](../chapters/13_visualization.md) | 16,874 | 9,388 | 7,290 | 1h09m |
| §14 | 解析パイプラインの自動化 | [14_workflow.md](../chapters/14_workflow.md) | 20,265 | 11,806 | 9,489 | 1h14m |
| §15 | コンテナによるソフトウェア環境の再現 | [15_container.md](../chapters/15_container.md) | 34,742 | 19,821 | 15,888 | 1h54m |
| §16 | スパコン・クラスタでの大規模計算 | [16_hpc.md](../chapters/16_hpc.md) | 20,657 | 10,976 | 9,012 | 1h11m |
| §17 | コードのパフォーマンス改善 | [17_performance.md](../chapters/17_performance.md) | 29,143 | 14,933 | 12,104 | 1h56m |
| §18 | コードのドキュメント化 | [18_documentation.md](../chapters/18_documentation.md) | 19,229 | 12,192 | 9,607 | 1h06m |
| §19 | 公共データベースとAPI | [19_database_api.md](../chapters/19_database_api.md) | 30,435 | 20,237 | 16,218 | 1h52m |
| §20 | コードとデータのセキュリティ・倫理 | [20_security_ethics.md](../chapters/20_security_ethics.md) | 21,056 | 14,758 | 12,264 | 1h08m |
| §21 | 共同開発の実践 | [21_collaboration.md](../chapters/21_collaboration.md) | 24,863 | 15,273 | 13,140 | 1h33m |
| 付録A | 学習パターン集 | [appendix_a](../chapters/appendix_a_learning_patterns.md) | 5,598 | 4,776 | 3,615 | 11m |
| 付録B | CLIリファレンス対照表 | [appendix_b](../chapters/appendix_b_cli_reference.md) | 2,368 | 1,775 | 1,076 | 5m |
| 付録C | 論文投稿前チェックリスト | [appendix_c](../chapters/appendix_c_checklist.md) | 2,771 | 1,698 | 1,355 | 6m |
| 付録D | エージェント頻出用語集 | [appendix_d](../chapters/appendix_d_agent_vocabulary.md) | — | — | — | 14m |
| 用語集 | — | [glossary.md](../chapters/glossary.md) | 4,848 | 4,053 | 3,446 | 1h04m |
| 著者紹介 | — | [author.md](../chapters/author.md) | — | — | — | 2m |
| **合計** | | | **~508,000** | **~306,000** | **~243,000** | **~30h** |

読了時間は本文250文字/分・コード100文字/分（全角換算、参考文献セクションを除く）で推定。

## カウント方法

`python3 scripts/count_chars.py` で再計測可能。詳細は同スクリプトのソースを参照。

- **文字数(raw)**: Markdown記法・コードブロック・空白・改行を含む生の文字数
- **本文文字数**: mistune でMarkdownを解析し、本文テキストのみを抽出してカウント
- **全角換算**: Unicode文字幅プロパティ（UAX #11）に基づき半角文字を0.5換算
