# PDF / EPUB ビルド手順

## 前提環境

| ソフトウェア | バージョン | インストール |
|-----------|---------|---------|
| pandoc | 3.9+ | `brew install pandoc` |
| TeX Live | 2026 | https://tug.org/texlive/ |
| LuaLaTeX | TeX Live同梱 | — |
| HaranoAjiフォント | TeX Live同梱 | — |
| JetBrains Mono NL | 手動インストール | https://www.jetbrains.com/lp/mono/ |
| Node.js | 18+ | Vivliostyle用 |
| epigraph.sty | TeX Live同梱 | なければ `tlmgr install epigraph` |
| epubcheck | 5.3+ | `brew install epubcheck`（EPUB検証用、Java依存） |

## ファイル構成

```
build/
├── build_pdf.sh              # PDF メインビルドスクリプト
├── build_epub.sh             # EPUB メインビルドスクリプト（KDP向け）
├── templates/
│   └── eisvogel.latex         # Eisvogel 3.4.0（blockquoteスタイルをパッチ済み）
├── eisvogel-custom.tex        # epigraphパッケージ設定、raggedbottom、tightlist
├── emoji-filter.lua           # 絵文字→テキスト変換フィルター（PDF専用）
├── epigraph.lua               # エピグラフ（章頭引用句）変換フィルター（PDF/EPUB両対応）
├── fix-crossref.lua           # 章間リンクを内部リンクに変換（統合PDF/EPUB用、形式別マッピング）
├── custom.css                 # Vivliostyle用CSSカスタマイズ
├── epub.css                   # EPUB用CSSスタイル（KDP互換）
├── BUILD_REPORT.md            # ビルド履歴・問題解決ログ
└── README.md                  # 本ファイル
```

## pandoc + LuaLaTeX（Eisvogel）

### クイックスタート

```bash
bash build/build_pdf.sh
```

章ごとPDF（29ファイル）と統合PDF（`ai-biocode-kata-full.pdf`）が `build/` に生成される。

### ビルドパイプライン

```
Markdown → pandoc (Lua filters) → .tex → sed (figure[H]) → lualatex (2-pass) → PDF
```

1. **pandoc**: Markdownを`.tex`に変換。Eisvogelテンプレート + 3つのLuaフィルターを適用
2. **sed**: `\begin{figure}` → `\begin{figure}[H]` に置換（図のフロート配置を抑制し空白を防止）
3. **lualatex**: `.tex`をPDFにコンパイル。2回実行で目次・相互参照を解決

### Luaフィルター

| フィルター | 適用対象 | 機能 |
|---------|---------|------|
| `emoji-filter.lua` | 全PDF | 🧬→[BIO]、🤖→[ML]等の絵文字をテキストに置換 |
| `epigraph.lua` | 全PDF | 出典行（`— `）付きblockquoteをLaTeX `\epigraph{}{}`に変換。コラム（太字・絵文字で始まるblockquote）は除外 |
| `fix-crossref.lua` | 統合PDFのみ | `./filename.md#section` → `#section` に変換し、PDF内部リンクとして機能させる |

### Eisvogelテンプレートのカスタマイズ

`templates/eisvogel.latex` に直接パッチした箇所:
- **blockquoteスタイル**（L658-663）: 左ボーダーのみ → フラットなグレー背景（RGB 245,245,245）+ ダークテキスト（RGB 51,51,51）、枠線なし

`eisvogel-custom.tex`（`-H` header-includes）で追加した設定:
- `epigraph` パッケージ（幅0.9\textwidth、区切り線なし）
- `\raggedbottom`（ページ下部の余白を均等配分しない）
- `\tightlist` 定義（pandocのリスト表示用）

### 統合PDFの設定

| 設定 | 値 |
|------|------|
| 表紙 | `cover.pdf` を `\includepdf` で先頭に取り込み（`pdfpages`パッケージ）|
| 目次 | あり（depth=2） |
| ヘッダー左 | 書名（短縮版） |
| ヘッダー右 | 章タイトル（`\leftmark`） |
| フッター | ページ番号のみ（中央） |
| ドキュメントクラス | scrbook（Eisvogel book mode） |
| 日本語フォント | HaranoAji（luatexja-preset） |
| コードフォント | JetBrains Mono NL（Scale=0.85） |
| コードハイライト | tango |

## EPUB ビルド（KDP 向け）

### クイックスタート

```bash
bash build/build_epub.sh
```

統合 EPUB（`build/ai-biocode-kata.epub`）が生成され、続けて epubcheck で自動検証される。

### ビルドパイプライン

```
Markdown → pandoc -t epub3 (Lua filters) → EPUB3 → epubcheck
```

1. **pandoc**: Markdown を EPUB3 に変換。`gfm_auto_identifiers` 拡張で GitHub 互換のヘッダー ID を生成
2. **Lua filters**: `epigraph.lua`（章頭引用句の HTML 変換）と `fix-crossref.lua`（章間リンク解決）を適用。`emoji-filter.lua` は EPUB では使用しない（Unicode 絵文字をリーダーがネイティブ表示）
3. **epubcheck**: 生成された EPUB を W3C EPUB3 仕様に対する準拠チェック

### EPUB 特有の設定

| 設定 | 値 |
|------|------|
| Reader | `markdown+gfm_auto_identifiers` |
| 出力 | EPUB3 |
| カバー画像 | `figures/cover.jpeg`（1684x2528、JPEG） |
| CSS | `build/epub.css`（Kindle 互換、相対サイズのみ） |
| 数式 | MathML |
| 目次 | あり（depth=2） |
| 言語 | ja |
| 出版社 | 二階堂 愛（自費出版想定） |
| ライセンス | CC BY-NC-ND 4.0 |

### KDP アップロード時の注意

- カバー画像（1.6:1 推奨、最低 1000px）は EPUB 内に既に埋め込まれているが、KDP で別途アップロードを求められた場合は `figures/cover.jpeg` を使う
- 絵文字（🧬🤖📦）は Unicode のまま埋め込まれている。古い Kindle 端末では tofu 表示になる可能性があるため、Kindle Previewer で要確認
- 数式は MathML で埋め込まれている。Kindle Previewer 推奨

### `fix-crossref.lua` の形式別マッピング

pandoc は LaTeX 出力と HTML/EPUB 出力で異なる identifier 生成規則を使う:

- **LaTeX (PDF)**: デフォルトの auto_identifiers — 先頭の非アルファベット文字を除去
- **HTML/EPUB**: gfm_auto_identifiers — 先頭の数字も保持

そのため `fix-crossref.lua` は `FILE_TO_CHAPTER_ID_LATEX` と `FILE_TO_CHAPTER_ID_HTML` の2系統マッピングを持ち、`FORMAT` グローバル変数で出力形式を判定して切り替える。

## Vivliostyle（CSS組版）

### クイックスタート

```bash
npx vivliostyle build
```

`build/ai-biocode-kata-vivliostyle.pdf`（B5, 182x257mm）が生成される。

### 設定ファイル

- `vivliostyle.config.js` — エントリーポイント・テーマ・出力先の設定
- `build/custom.css` — KDP対応マージン、画像サイズ、URL脚注抑制、表レイアウト

### 依存パッケージ

```bash
npm install
```

`@vivliostyle/cli` と `@vivliostyle/theme-techbook` がインストールされる。

## 表紙・裏表紙

### 表紙（独立生成）

表紙はEisvogelのtitlepage機能ではなく、独立したLaTeXファイルで生成する（背景画像の全面配置がscrbook内で正しく動作しないため）。

```bash
# 表紙のみテストビルド（高速）
bash build/build_cover_test.sh
# → build/cover_test.pdf

# 表紙の本番ビルド
cd build && lualatex cover.tex
# → build/cover.pdf
```

テキストの位置・サイズ調整は `build/cover.tex` を直接編集する。

### 裏表紙

裏表紙は `build/back-cover.tex` で定義し、本文PDFビルド時に `-A` オプションで最終ページに挿入される。

### 表紙+本文の統合

`build_pdf.sh` の統合PDFビルドで、表紙PDFは `pdfpages` パッケージの `\includepdf` により本文PDFの先頭に自動的に取り込まれる。

```bash
# 一括ビルド（表紙生成→本文ビルド→統合を自動実行）
bash build/build_pdf.sh
# → build/ai-biocode-kata-full.pdf（表紙+目次+本文+裏表紙、リンク完全動作）
```

**注意**: `pdfunite` による外部結合はPDF内部リンクが壊れるため使用しない。`\includepdf` によるLaTeX内部での結合がリンクを維持する唯一の方法である。

---

## 2つのPDFパイプラインの使い分け

| | pandoc + LuaLaTeX | Vivliostyle |
|---|---|---|
| 用途 | iThenticate剽窃チェック、レビュー配布 | KDP出版用の最終版 |
| サイズ | A4相当 | B5（182x257mm） |
| 特徴 | エピグラフ組版、章間リンク、目次 | CSSベースの精密なレイアウト制御 |
| 絵文字 | テキスト置換（[BIO]等） | Noto Color Emoji表示 |
| ファイル | `ai-biocode-kata-full.pdf` | `ai-biocode-kata-vivliostyle.pdf` |
