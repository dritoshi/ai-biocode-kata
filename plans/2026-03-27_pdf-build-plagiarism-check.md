# フェーズ1: 最低限PDF化（剽窃チェック用）

## Context

iThenticateで剽窃チェックを行うために、章ごとのPDFと全章統合PDFを生成する。デザインは不要で、テキストが正しく抽出できるPDFであればよい。

## 環境

- pandoc: **未インストール** → `brew install pandoc` で導入
- LuaLaTeX: **インストール済み**（日本語対応）
- build/: 空ディレクトリ

## ビルドスクリプトの設計

`build/build_pdf.sh` を作成。

### 機能1: 章ごとPDF生成

```bash
# 各章を個別PDFに変換
for f in chapters/hajimeni.md chapters/0*.md chapters/1*.md chapters/2*.md \
         chapters/appendix_*.md chapters/glossary.md chapters/author.md; do
  pandoc "$f" -o "build/$(basename "${f%.md}.pdf")" \
    --pdf-engine=lualatex \
    -V documentclass=ltjsarticle \
    -V geometry:margin=2.5cm
done
```

### 機能2: 全章統合PDF生成

章の順序を定義し、1つのPDFに結合:

```
hajimeni.md → 00〜21 → appendix_a〜d → glossary → author
```

```bash
pandoc chapters/hajimeni.md \
       chapters/00_ai_agent.md \
       ... \
       chapters/author.md \
  -o build/ai-biocode-kata-full.pdf \
  --pdf-engine=lualatex \
  -V documentclass=ltjsarticle \
  -V geometry:margin=2.5cm \
  --toc --toc-depth=2 \
  -V title="AIエージェントと学ぶ バイオインフォマティクスプログラミングの作法" \
  -V author="二階堂 愛"
```

### pandocの日本語PDF設定

- `--pdf-engine=lualatex` — LuaLaTeX使用（日本語対応）
- `-V documentclass=ltjsarticle` — 日本語文書クラス
- `-V geometry:margin=2.5cm` — 最低限の余白設定
- `--toc` — 目次自動生成（統合版のみ）

### 出力ファイル

```
build/
├── hajimeni.pdf
├── 00_ai_agent.pdf
├── 01_design.pdf
├── ... (各章)
├── glossary.pdf
├── author.pdf
└── ai-biocode-kata-full.pdf  （統合版）
```

## 実行手順

1. `brew install pandoc`
2. `build/build_pdf.sh` を作成
3. `bash build/build_pdf.sh` を実行
4. build/ 配下にPDFが生成されることを確認
5. .gitignore に `build/*.pdf` を追加（PDFはgit管理しない）

## 検証

- 生成されたPDFで日本語テキストが正しく表示されること
- コードブロックが折り返されること
- 数式（$O(n)$等）がレンダリングされること
- 各章PDFがiThenticateにアップロードできること

## フェーズ2（後日）: KDP向けデザイン

剽窃チェック・リライト完了後に着手:
- トリムサイズ、マージン、フォント設定
- 表紙デザイン
- EPUB生成
- KDP仕様への準拠
