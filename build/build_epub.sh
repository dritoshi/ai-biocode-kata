#!/usr/bin/env bash
# build/build_epub.sh — pandoc で統合 EPUB3 を生成し epubcheck で検証
# 使い方: bash build/build_epub.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$SCRIPT_DIR"
CHAPTERS_DIR="$PROJECT_DIR/chapters"
FIGURES_DIR="$PROJECT_DIR/figures"

# 章の順序（build_pdf.sh と一致させる）
CHAPTER_ORDER=(
  hajimeni.md
  notice.md
  00_ai_agent.md
  01_design.md
  02_terminal.md
  03_cs_basics.md
  04_data_formats.md
  05_software_components.md
  06_dev_environment.md
  07_git.md
  08_testing.md
  09_debug.md
  10_deliverables.md
  11_cli.md
  12_data_processing.md
  13_visualization.md
  14_workflow.md
  15_container.md
  16_hpc.md
  17_performance.md
  18_documentation.md
  19_database_api.md
  20_security_ethics.md
  21_collaboration.md
  appendix_a_learning_patterns.md
  appendix_b_cli_reference.md
  appendix_c_checklist.md
  appendix_d_agent_vocabulary.md
  glossary.md
  author.md
)

# 入力ファイルパスを構築
INPUT_FILES=()
for chapter in "${CHAPTER_ORDER[@]}"; do
  src="$CHAPTERS_DIR/$chapter"
  if [[ -f "$src" ]]; then
    INPUT_FILES+=("$src")
  else
    echo "✗ ファイルが見つかりません: $src"
    exit 1
  fi
done

OUTPUT_EPUB="$BUILD_DIR/ai-biocode-kata.epub"
COVER_IMAGE="$FIGURES_DIR/cover.jpeg"
EPUB_CSS="$BUILD_DIR/epub.css"

if [[ ! -f "$COVER_IMAGE" ]]; then
  echo "✗ カバー画像が見つかりません: $COVER_IMAGE"
  exit 1
fi

if [[ ! -f "$EPUB_CSS" ]]; then
  echo "✗ EPUB CSS が見つかりません: $EPUB_CSS"
  exit 1
fi

echo "=== EPUB 生成 ==="
echo "  入力章数: ${#INPUT_FILES[@]}"
echo "  カバー画像: $COVER_IMAGE"
echo "  CSS: $EPUB_CSS"
echo "  出力: $OUTPUT_EPUB"
echo ""

# pandoc で EPUB3 生成
pandoc "${INPUT_FILES[@]}" \
  -f markdown+gfm_auto_identifiers \
  -t epub3 \
  -o "$OUTPUT_EPUB" \
  --lua-filter="$BUILD_DIR/epigraph.lua" \
  --lua-filter="$BUILD_DIR/fix-crossref.lua" \
  --epub-cover-image="$COVER_IMAGE" \
  --css="$EPUB_CSS" \
  --mathml \
  --toc --toc-depth=2 \
  --top-level-division=chapter \
  --resource-path="$CHAPTERS_DIR:$FIGURES_DIR" \
  -M title="AIエージェントを使いこなす はじめてのバイオインフォマティクス開発作法" \
  -M subtitle="情報技術の基礎から環境構築・設計・テスト・公開まで" \
  -M author="二階堂 愛" \
  -M lang="ja" \
  -M date="$(date +%Y-%m-%d)" \
  -M publisher="二階堂 愛" \
  -M rights="© 2026 Itoshi Nikaido. CC BY-NC-ND 4.0"

if [[ ! -f "$OUTPUT_EPUB" ]]; then
  echo "✗ EPUB の生成に失敗しました"
  exit 1
fi

echo "✓ EPUB 生成完了"
ls -lh "$OUTPUT_EPUB"
echo ""

# epubcheck で検証
echo "=== epubcheck ==="
if command -v epubcheck >/dev/null 2>&1; then
  if epubcheck "$OUTPUT_EPUB"; then
    echo ""
    echo "✓ epubcheck: 問題なし"
  else
    echo ""
    echo "✗ epubcheck: 問題が検出されました（上記参照）"
    exit 1
  fi
else
  echo "⚠ epubcheck がインストールされていません"
  echo "  インストール: brew install epubcheck"
fi
