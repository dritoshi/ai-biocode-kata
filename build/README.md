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

## ファイル構成

```
build/
├── build_pdf.sh              # メインビルドスクリプト
├── templates/
│   └── eisvogel.latex         # Eisvogel 3.4.0（blockquoteスタイルをパッチ済み）
├── eisvogel-custom.tex        # epigraphパッケージ設定、raggedbottom、tightlist
├── emoji-filter.lua           # 絵文字→テキスト変換フィルター
├── epigraph.lua               # エピグラフ（章頭引用句）変換フィルター
├── fix-crossref.lua           # 章間リンクを内部リンクに変換（統合PDF用）
├── custom.css                 # Vivliostyle用CSSカスタマイズ
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
