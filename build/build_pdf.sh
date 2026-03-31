#!/usr/bin/env bash
# build/build_pdf.sh — 章ごとPDF + 全章統合PDF生成（Eisvogelテンプレート）
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

# pandoc共通オプション（Eisvogelテンプレート）
PANDOC_OPTS=(
  --template="$BUILD_DIR/templates/eisvogel.latex"
  --lua-filter="$BUILD_DIR/emoji-filter.lua"
  --lua-filter="$BUILD_DIR/epigraph.lua"
  --top-level-division=chapter
  -H "$BUILD_DIR/eisvogel-custom.tex"
  -V luatexjapresetoptions=haranoaji
  -V monofont="JetBrains Mono NL"
  -V monofontoptions="Scale=0.85"
  -V "geometry:margin=2.5cm"
  -V colorlinks=true
  -V linkcolor=blue
  -V urlcolor=blue
  -V book=true
  --highlight-style=tango
  -V code-block-font-size="\small"
  --resource-path="$CHAPTERS_DIR"
)

# pandoc → .tex → sed(figure[H]修正) → lualatex の2段階ビルド
build_pdf_via_tex() {
  local input_files=("${@:1:$#-1}")
  local output_pdf="${!#}"
  local tex_file="${output_pdf%.pdf}.tex"

  # Step 1: pandoc で .tex を生成
  pandoc "${input_files[@]}" -o "$tex_file" "${PANDOC_OPTS[@]}" "${EXTRA_OPTS[@]}" 2>/dev/null

  # Step 2: \begin{figure} → \begin{figure}[H] に置換（フロート空白防止）
  sed -i '' 's/\\begin{figure}/\\begin{figure}[H]/g' "$tex_file"

  # Step 3: lualatex で PDF 生成（2回実行で相互参照を解決）
  local tex_dir
  tex_dir="$(dirname "$tex_file")"
  local tex_base
  tex_base="$(basename "$tex_file")"
  (cd "$tex_dir" && lualatex -interaction=nonstopmode "$tex_base" > /dev/null 2>&1 && \
   lualatex -interaction=nonstopmode "$tex_base" > /dev/null 2>&1) || return 1

  # Step 4: 中間ファイルを削除
  rm -f "${output_pdf%.pdf}.tex" "${output_pdf%.pdf}.aux" "${output_pdf%.pdf}.log" \
        "${output_pdf%.pdf}.out" "${output_pdf%.pdf}.toc" "${output_pdf%.pdf}.lof" \
        "${output_pdf%.pdf}.lot"
}

FAILED=()
EXTRA_OPTS=()

echo "=== 章ごとPDF生成 ==="
for chapter in "${CHAPTER_ORDER[@]}"; do
  src="$CHAPTERS_DIR/$chapter"
  dst="$BUILD_DIR/${chapter%.md}.pdf"
  if [[ -f "$src" ]]; then
    echo "  $chapter → $(basename "$dst")"
    if ! build_pdf_via_tex "$src" "$dst"; then
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

EXTRA_OPTS=(
  --toc --toc-depth=2
  -V titlepage=true
  -V titlepage-color=FFFFFF
  -V titlepage-text-color=333333
  -V "title=AIエージェントと学ぶ バイオインフォマティクスプログラミングの作法"
  -V "subtitle=配列解析から機械学習まで、環境構築・テスト・設計・公開のベストプラクティス"
  -V "author=二階堂 愛"
  -V "date=$(date +%Y-%m-%d)"
  -V "header-left=バイオインフォプログラミングの作法"
  -V "header-right=\\leftmark"
  -V "footer-left= "
  -V "footer-center=\\thepage"
  -V "footer-right= "
)

if ! build_pdf_via_tex "${FULL_INPUTS[@]}" "$BUILD_DIR/ai-biocode-kata-full.pdf"; then
  echo "  ⚠ 統合PDF生成でエラー"
fi

echo ""
echo "=== 生成されたPDF ==="
ls -lh "$BUILD_DIR"/*.pdf 2>/dev/null || echo "PDFが生成されませんでした"

if [[ ${#FAILED[@]} -gt 0 ]]; then
  echo ""
  echo "=== 失敗した章 (${#FAILED[@]}件) ==="
  for f in "${FAILED[@]}"; do echo "  - $f"; done
fi
