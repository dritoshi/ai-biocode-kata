# PDF ビルドレポート

## 変更履歴

### フェーズ2: Eisvogelテンプレート導入（2026-04-01）

フェーズ1（iThenticate用）のltjsarticle + 素のpandocテンプレートから、Eisvogel 3.4.0テンプレートに移行。デザイン品質をL2（人間レビュー可）〜L3（出版可）に引き上げた。

#### 解決した問題

| # | 問題 | 原因 | 対処 |
|---|------|------|------|
| F2-1 | コードブロックに背景色がない | Eisvogelデフォルトでは`--highlight-style`未指定 | `--highlight-style=tango` を追加 |
| F2-2 | 章間に改ページがない | `--top-level-division`未指定で`#`がsectionになっていた | `--top-level-division=chapter` + `-V book=true` を追加 |
| F2-3 | フッターに著者名が表示される | Eisvogelのデフォルト`ifoot`が著者名 | `-V "footer-left= "` `-V "footer-right= "` で空に上書き |
| F2-4 | コラム（blockquote）のテキストが薄い | Eisvogelデフォルトのblockquote-textがRGB(119,119,119) | `eisvogel.latex`を直接パッチ: 背景RGB(245,245,245)、テキストRGB(51,51,51)、枠線なし |
| F2-5 | リスト（`-`）がレンダリングされない | `:`の直後に空行なしでリストが始まるとpandocが段落の一部と解釈 | `chapters/hajimeni.md`に空行を追加 |
| F2-6 | コードブロック・図の前後に大きな空白 | 図がフロート配置されページに収まらず次ページに送られる | 2段階ビルド: pandoc→.tex→`sed 's/\\begin{figure}/\\begin{figure}[H]/g'`→lualatex。`\raggedbottom`で下部余白を統一 |
| F2-7 | エピグラフが通常のblockquoteとして表示 | pandocにエピグラフの概念がない | `epigraph.lua` Luaフィルター新規作成。出典行`— `パターンを検出し`\epigraph{}{}`に変換 |
| F2-8 | エピグラフの出典行が改行される | `\epigraphwidth`が0.75\textwidthで長い出典が収まらない | `\epigraphwidth`を0.9\textwidthに拡大 |
| F2-9 | 章間リンクがPDF内で機能しない | pandocが`./filename.md`を`\href{./filename.md}`（外部リンク）に変換 | `fix-crossref.lua` Luaフィルター新規作成。`./filename.md#section`→`#section`に変換し`\hyperref`に |
| F2-10 | タイトルページがない | 以前のテンプレートにタイトルページ機能がなかった | Eisvogelの`-V titlepage=true`を利用 |

#### 不採用・削除した対処

| 対処 | 理由 |
|------|------|
| `\floatplacement{figure}{H}`（Eisvogel内蔵） | pandoc 3.9で`\begin{figure}`に配置子が付かず効かない |
| `figure-placement.lua`（Luaフィルターで図の属性を設定） | pandoc 3.9のFigure型でattributesが反映されない |
| `\renewenvironment{figure}`（LaTeXでfigure環境を再定義） | header-includesのロード順でEisvogel内蔵の`\usepackage{float}`と競合 |
| moshの記載 | サーバ側インストールが必要で共用HPCでは使えない。tmuxで十分 |

### フェーズ1: iThenticate用（2026-03-27）

初回のPDFビルド。ltjsarticle + pandocデフォルトテンプレートで、テキスト抽出のみを目的とした品質（L1）。

#### 解決した問題

| # | 問題 | 原因 | 対処 |
|---|------|------|------|
| E1 | ビルドスクリプトのSIGPIPE誤検出 | `pandoc \| head -5` でパイプが閉じpandocが非ゼロ終了 | `\| head -5` を削除 |
| E2 | ch04 テーブルセル内の `\n` | Markdownテーブルにリテラルな`\n`がありLaTeXが制御シーケンスと誤解釈 | 自然な日本語表現に置換 |
| E3 | ch20 ハイパーリンクのネスト不整合 | LuaLaTeXの一時的不整合 | 再ビルドで解消 |

---

## 品質レベルの定義と現状

| レベル | 定義 | 判定 |
|--------|------|------|
| **L1: 剽窃チェック可** | テキストが正しく抽出でき、iThenticateに投入可能 | **達成**（フェーズ1） |
| **L2: 人間レビュー可** | 本文・コード・表・エピグラフ・リンクが正しく読める | **達成**（フェーズ2） |
| **L3: 出版可** | 図・絵文字・レイアウトが完全で、読者に提供できる | **条件付き達成** |

### L3 残課題

| 項目 | 状態 | 備考 |
|------|------|------|
| 絵文字（🧬🤖📦） | Luaフィルターでテキスト置換済み | Noto Color Emojiフォールバックは未対応 |
| 図画像 | 統合PDF・章ごとPDFとも表示される | `--resource-path=chapters`で解決済み |
| 章間リンク | 統合PDFで機能する | `fix-crossref.lua`で解決済み |
| タイトルページ | 仮デザイン | サブタイトル・表紙デザインは未定（TODO参照） |
| drawio図のフォントサイズ | A4想定で小さい | B5向け再エクスポートが必要 |
