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
│   ├── 00_hajimeni.md  # はじめに
│   ├── roadmap.md      # 全体構成マスタードキュメント
│   ├── 01_ai_agent.md  # §0: AIエージェントとの協働
│   ├── 02_design.md    # §1: 設計原則
│   ├── ...             # （以降、各章を追加）
│   └── appendix_c.md
├── figures/            # 図表
├── scripts/            # 書籍内コードサンプル
├── tests/              # サンプルコードのテスト
└── build/              # PDF/EPUB生成
```

## 執筆環境

- **Claude Code CLI** — 章の生成・リライト・構成の相談
- **Zed** — マークダウンプレビュー・手動の文体調整
- **tmux** — ターミナル分割（Claude Code + シェル）

## ビルド（予定）

```bash
# 今後追加予定
# pandoc による PDF/EPUB 生成
```
