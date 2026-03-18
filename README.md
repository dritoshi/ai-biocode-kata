# AIエージェントと学ぶ バイオインフォマティクスプログラミングの作法

配列解析から機械学習まで、環境構築・テスト・設計・公開のベストプラクティス

## 概要

AIコーディングエージェント（Claude Code CLI / Codex CLI）との協働を前提として、
バイオインフォマティクスのプログラミングに必要な「開発の作法」を体系的に解説する書籍。

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

全体構成の詳細は [roadmap.md](chapters/roadmap.md) を参照。

- [用語集](chapters/glossary.md)
- [執筆 TODO](TODO.md)

## 章の一覧

| 章 | タイトル | 原稿 | ロードマップ |
|----|---------|------|-------------|
| はじめに | — | [hajimeni.md](chapters/hajimeni.md) | — |
| 0 | AIコーディングエージェントとの協働 | [00_ai_agent.md](chapters/00_ai_agent.md) | [§0](chapters/roadmap.md#0-aiコーディングエージェントとの協働2026年のベストプラクティス) |
| 1 | 設計原則 | [01_design.md](chapters/01_design.md) | [§1](chapters/roadmap.md#1-設計原則) |
| 2 | ターミナル環境 | — | [§2](chapters/roadmap.md#2-ターミナル環境) |
| 3 | 計算機科学の基礎知識 | [03_cs_basics.md](chapters/03_cs_basics.md) | [§3](chapters/roadmap.md#3-計算機科学の基礎知識) |
| 4 | データフォーマットの判断力 | [04_data_formats.md](chapters/04_data_formats.md) | [§4](chapters/roadmap.md#4-データフォーマットの判断力) |
| 5 | 開発環境の構築 | [05_dev_environment.md](chapters/05_dev_environment.md) | [§5](chapters/roadmap.md#5-開発環境の構築) |
| 6 | バージョン管理（Git / GitHub） | — | [§6](chapters/roadmap.md#6-バージョン管理git--github) |
| 7 | テスト・品質管理 | — | [§7](chapters/roadmap.md#7-テスト品質管理) |
| 8 | 成果物の形式とプロジェクト設計 | — | [§8](chapters/roadmap.md#8-成果物の形式とプロジェクト設計) |
| 9 | CLIツールの設計 | — | [§9](chapters/roadmap.md#9-cliツールの設計) |
| 10 | データ処理ライブラリ | — | [§10](chapters/roadmap.md#10-データ処理ライブラリ) |
| 11 | 可視化 | — | [§11](chapters/roadmap.md#11-可視化) |
| 12 | ワークフロー管理 | — | [§12](chapters/roadmap.md#12-ワークフロー管理) |
| 13 | コンテナと再現性 | — | [§13](chapters/roadmap.md#13-コンテナと再現性) |
| 13A | 実験管理（ML/計算実験の追跡） | — | [§13A](chapters/roadmap.md#13a-実験管理ml計算実験の追跡) |
| 14 | HPC | — | [§14](chapters/roadmap.md#14-hpc) |
| 15 | パフォーマンスと最適化 | — | [§15](chapters/roadmap.md#15-パフォーマンスと最適化) |
| 16 | デバッグの技術 | — | [§16](chapters/roadmap.md#16-デバッグの技術) |
| 17 | ドキュメント化 | — | [§17](chapters/roadmap.md#17-ドキュメント化) |
| 18 | データベースとAPI | — | [§18](chapters/roadmap.md#18-データベースとapi) |
| 19 | セキュリティと倫理 | — | [§19](chapters/roadmap.md#19-セキュリティと倫理) |
| 20 | コラボレーション | — | [§20](chapters/roadmap.md#20-コラボレーション) |
| 付録A | 学習順序の推奨 | — | [§付録A](chapters/roadmap.md#付録a-学習順序の推奨) |
| 付録B | AIコーディングエージェントとの効果的な学習パターン | — | [§付録B](chapters/roadmap.md#付録b-aiコーディングエージェントとの効果的な学習パターン) |
| 付録C | クイックリファレンス対照表 | — | [§付録C](chapters/roadmap.md#付録c-claude-code-cli--codex-cli-クイックリファレンス対照表) |

> 章ファイルが追加され次第、原稿カラムのリンクを更新する。

## ビルド（予定）

```bash
# 今後追加予定
# pandoc による PDF/EPUB 生成
```
