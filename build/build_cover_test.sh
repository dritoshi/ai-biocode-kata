#!/usr/bin/env bash
# build/build_cover_test.sh — 表紙のみの高速テストビルド
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$SCRIPT_DIR"
OUTPUT="$BUILD_DIR/cover_test.pdf"

# 最小限の本文でフルtex生成（titlepageを含む完全なドキュメント）
cd "$PROJECT_DIR"
printf '\\phantom{x}\n' | pandoc -o "$BUILD_DIR/cover_test.tex" \
  --template="$BUILD_DIR/templates/eisvogel.latex" \
  --top-level-division=chapter \
  -H "$BUILD_DIR/eisvogel-custom.tex" \
  -V luatexjapresetoptions=haranoaji \
  -V monofont="JetBrains Mono NL" -V monofontoptions="Scale=0.85" \
  -V "geometry:margin=2.5cm" \
  -V colorlinks=true -V linkcolor=blue -V urlcolor=blue \
  -V book=true \
  --highlight-style=tango \
  -V code-block-font-size="\small" \
  -V titlepage=true \
  -V "titlepage-background=../figures/cover_v2.png" \
  -V titlepage-text-color=1E1E1E \
  -V "title-line1=AIエージェントを使いこなす" \
  -V "title-line2=はじめてのバイオインフォマティクス開発作法" \
  -V "subtitle=情報技術の基礎から環境構築・設計・テスト・公開まで" \
  -V "author=二階堂愛" \
  -V "title=AIエージェントを使いこなす はじめてのバイオインフォマティクス開発作法" \
  -V "header-left=バイオインフォマティクス開発作法" \
  -V "header-right=\\leftmark" \
  -V "footer-left= " -V "footer-center=\\thepage" -V "footer-right= " \
  --resource-path="chapters:figures" \
  2>/dev/null

# build/でlualatex実行
(cd "$BUILD_DIR" && \
  TEXINPUTS=".:$PROJECT_DIR/figures:$PROJECT_DIR/chapters:" \
  lualatex -interaction=nonstopmode cover_test.tex > /dev/null 2>&1)

# 中間ファイル削除
rm -f "$BUILD_DIR/cover_test.tex" "$BUILD_DIR/cover_test.aux" \
      "$BUILD_DIR/cover_test.log" "$BUILD_DIR/cover_test.out" \
      "$BUILD_DIR/cover_test.toc"

echo "Generated: $OUTPUT"
