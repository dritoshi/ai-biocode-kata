#!/usr/bin/env bash
# build/build_pdf.sh — 章ごとPDF + 全章統合PDF生成
# 使い方: bash build/build_pdf.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$SCRIPT_DIR"
CHAPTERS_DIR="$PROJECT_DIR/chapters"

# 章の順序（統合PDF用）
CHAPTER_ORDER=(
  hajimeni.md
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

# pandoc共通オプション
PANDOC_OPTS=(
  --pdf-engine=lualatex
  --template="$BUILD_DIR/templates/default.latex"
  -V documentclass=ltjsarticle
  -V "geometry:margin=2.5cm"
  --syntax-highlighting=tango
  --resource-path="$CHAPTERS_DIR"
)

FAILED=()

echo "=== 章ごとPDF生成 ==="
for chapter in "${CHAPTER_ORDER[@]}"; do
  src="$CHAPTERS_DIR/$chapter"
  dst="$BUILD_DIR/${chapter%.md}.pdf"
  if [[ -f "$src" ]]; then
    echo "  $chapter → $(basename "$dst")"
    if ! pandoc "$src" -o "$dst" "${PANDOC_OPTS[@]}" 2>/dev/null; then
      echo "  ⚠ エラー: $chapter"
      FAILED+=("$chapter")
    fi
  else
    echo "  ⚠ ファイルが見つかりません: $src"
  fi
done

echo ""
echo "=== 全章統合PDF生成 ==="
FULL_INPUTS=()
for chapter in "${CHAPTER_ORDER[@]}"; do
  src="$CHAPTERS_DIR/$chapter"
  if [[ -f "$src" ]]; then
    FULL_INPUTS+=("$src")
  fi
done

pandoc "${FULL_INPUTS[@]}" \
  -o "$BUILD_DIR/ai-biocode-kata-full.pdf" \
  "${PANDOC_OPTS[@]}" \
  --toc --toc-depth=2 \
  -V "title=AIエージェントと学ぶ バイオインフォマティクスプログラミングの作法" \
  -V "subtitle=配列解析から機械学習まで、環境構築・テスト・設計・公開のベストプラクティス" \
  -V "author=二階堂 愛" \
  2>/dev/null || echo "  ⚠ 統合PDF生成でエラー"

echo ""
echo "=== 生成されたPDF ==="
ls -lh "$BUILD_DIR"/*.pdf 2>/dev/null || echo "PDFが生成されませんでした"

if [[ ${#FAILED[@]} -gt 0 ]]; then
  echo ""
  echo "=== 失敗した章 (${#FAILED[@]}件) ==="
  for f in "${FAILED[@]}"; do echo "  - $f"; done
fi
