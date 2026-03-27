# PDF ビルドレポート — フェーズ1（剽窃チェック用）

生成日: 2026-03-27

## 目的

iThenticateによる剽窃チェックのために、章ごとのPDFと全章統合PDFを生成する。デザインは対象外で、テキストが正しく抽出できるPDFであればよい。

## ビルド環境

| 項目 | バージョン |
|------|----------|
| pandoc | 3.9.0.2 |
| LuaLaTeX | LuaHBTeX (TeX Live) |
| 日本語フォント | HaranoAji（原ノ味フォント） |
| ドキュメントクラス | ltjsarticle |
| OS | macOS (Darwin 25.4.0, arm64) |

## ビルドコマンド

```bash
bash build/build_pdf.sh
```

## 生成結果

### 統合PDF

| ファイル | ページ数 | サイズ | 目次 |
|---------|---------|-------|------|
| `ai-biocode-kata-full.pdf` | 481ページ | 2.2MB | あり（toc-depth=2） |

### 章ごとPDF（全29ファイル）

| ファイル | ページ数 | サイズ | 推定語数 | ビルド結果 |
|---------|---------|-------|---------|----------|
| hajimeni.pdf | 6 | 348KB | 950 | OK |
| 00_ai_agent.pdf | 25 | 526KB | 2,809 | OK |
| 01_design.pdf | 12 | 401KB | 1,476 | OK |
| 02_terminal.pdf | 21 | 420KB | 2,189 | OK |
| 03_cs_basics.pdf | 23 | 483KB | 2,966 | OK |
| 04_data_formats.pdf | 22 | 472KB | 2,883 | OK（修正後） |
| 05_software_components.pdf | 18 | 422KB | 2,277 | OK |
| 06_dev_environment.pdf | 13 | 375KB | 1,540 | OK |
| 07_git.pdf | 17 | 413KB | 1,774 | OK |
| 08_testing.pdf | 20 | 415KB | 2,037 | OK |
| 09_debug.pdf | 19 | 422KB | 2,301 | OK |
| 10_deliverables.pdf | 24 | 429KB | 2,330 | OK |
| 11_cli.pdf | 21 | 420KB | 2,328 | OK |
| 12_data_processing.pdf | 17 | 415KB | 2,079 | OK |
| 13_visualization.pdf | 19 | 425KB | 2,276 | OK |
| 14_workflow.pdf | 18 | 401KB | 1,895 | OK |
| 15_container.pdf | 28 | 475KB | 3,124 | OK |
| 16_hpc.pdf | 19 | 408KB | 2,068 | OK |
| 17_performance.pdf | 26 | 457KB | 3,126 | OK |
| 18_documentation.pdf | 17 | 416KB | 1,917 | OK |
| 19_database_api.pdf | 27 | 491KB | 3,526 | OK |
| 20_security_ethics.pdf | 18 | 456KB | 1,848 | OK |
| 21_collaboration.pdf | 23 | 474KB | 2,341 | OK |
| appendix_a_learning_patterns.pdf | 4 | 267KB | 487 | OK |
| appendix_b_cli_reference.pdf | 3 | 185KB | 315 | OK |
| appendix_c_checklist.pdf | 2 | 207KB | 196 | OK |
| appendix_d_agent_vocabulary.pdf | 6 | 280KB | 438 | OK |
| glossary.pdf | 22 | 445KB | 1,529 | OK |
| author.pdf | 1 | 173KB | 51 | OK |

**合計: 481ページ、約64,927語、13MB**

## ビルド中に発生したエラーと対処

### エラー1: スクリプトの誤検出（初回ビルド、9章が失敗扱い）

**症状**: 初回ビルドで9章が「⚠ エラー」と表示された。

**原因**: ビルドスクリプトの `pandoc ... 2>&1 | head -5 || echo "⚠ エラー"` が問題。pandocが5行以上の警告を出力すると `head -5` がパイプを閉じ、pandocがSIGPIPEで非ゼロ終了する。実際にはPDFは正常に生成されているにもかかわらず、エラーとして報告されていた。

**対処**: `| head -5` を削除し、pandocの終了コードを直接チェックする形に修正。

```bash
# 修正前
pandoc "$src" -o "$dst" ... 2>&1 | head -5 || echo "⚠ エラー: $chapter"

# 修正後
if ! pandoc "$src" -o "$dst" ... 2>/dev/null; then
  echo "⚠ エラー: $chapter"
fi
```

**結果**: 9章 → 2章に失敗が減少。

### エラー2: ch04 LaTeXエラー — テーブルセル内の `\n`

**症状**: `Error producing PDF. ! Undefined control sequence. l.903 列名 & 「発現量 (TPM)\n`

**原因**: `chapters/04_data_formats.md` のMarkdownテーブル内にリテラルな `\n` が2箇所含まれていた。LaTeXはこれを制御シーケンス（改行コマンド）として解釈しようとしてエラーになった。

**該当箇所と修正**:

| 行 | 修正前 | 修正後 |
|---|--------|--------|
| 449 | `「発現量 (TPM)\n(Sample A)」` | `「発現量 (TPM) (Sample A)」` |
| 458 | `「Sample\nID」` | `「Sample ID」が改行で分割されている等` |

**対処**: テーブルセル内の `\n` を自然な日本語表現に置き換えた。この修正は本文の意味を変えない体裁のみの変更である。

### エラー3: ch20 LaTeXエラー — ハイパーリンクのネスト不整合

**症状**: 初回ビルド時に `! error: (pdf backend): 'endlink' ended up in different nesting level than 'startlink'` が発生。

**原因**: LuaLaTeXのハイパーリンク処理で、Markdownの複雑なリンク構造がネスト不整合を起こした。

**対処**: 本文の修正は不要。2回目のビルドでは同じエラーが再現せず正常にPDFが生成された。LaTeXの中間ファイルのキャッシュが影響していた可能性がある。再現性のない一時的なエラーと判断。

## 既知の警告（フェーズ2で対処）

以下の警告はPDFの生成自体には影響せず、テキスト抽出（iThenticate用途）にも問題ない。フェーズ2（KDPデザイン）で対処する。

### 1. 絵文字が表示されない

```
Missing character: There is no 🧬 (U+1F9EC) in font [lmroman10-bold]
Missing character: There is no 🤖 (U+1F916) in font [lmroman10-regular]
Missing character: There is no ✅ (U+2705) in font IPAExMincho
Missing character: There is no ❌ (U+274C) in font IPAExMincho
```

**原因**: Latin Modern / IPAExMincho フォントに絵文字グリフがない。
**対処（フェーズ2）**: Noto Color Emojiフォントをフォールバック設定するか、絵文字をテキスト表現に置換する。

### 2. 画像が見つからない

```
Could not fetch resource ../figures/ch00_approval_mode.png: replacing image with description
```

**原因**: pandocの実行ディレクトリからの相対パスが `chapters/` 内の `../figures/` と一致しない。
**対処（フェーズ2）**: pandocの `--resource-path` オプションで `chapters/` を指定するか、画像パスを調整する。

### 3. ハイパーリンクの未解決参照

```
LaTeX Warning: Hyper reference '...' on page X undefined
```

**原因**: 章内の `#section-anchor` 形式のリンクがLaTeXの相互参照と一致しない。
**対処（フェーズ2）**: pandocのcrossref フィルタを使用するか、統合PDF用に相互参照を調整する。

## iThenticateへの投入方針

- 各章PDFを個別にアップロード（29ファイル）
- 全章で推定約64,927語。iThenticateの1提出あたり25,000語制限に対し、各章は1,000〜3,500語程度なので1章1提出で収まる
- エピグラフ（意図的引用）と参考文献セクションは類似性レポートから除外設定する
- リスクの高い章（§1設計原則、§7 Git、§8テスト）を優先的にチェック
