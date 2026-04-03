# PDF ビルドレポート

## 変更履歴

### フェーズ3: 表紙・裏表紙デザイン（2026-04-02〜03）

表紙に背景画像とタイトルテキストを配置し、裏表紙を最終ページに挿入する。

#### 解決した問題

| # | 問題 | 原因 | 対処 |
|---|------|------|------|
| F3-1 | 表紙の背景画像が上端数mmしか表示されない | Eisvogelの`titlepage-background`のtikz `\node` による全面配置が、`scrbook`クラスの内部ページ構造と干渉して正しく描画されなかった | 表紙を独立LaTeXファイル(`build/cover.tex`)で生成する方式に変更。背景画像は`eso-pic`パッケージの`\AddToShipoutPictureBG*`で配置し、テキストはtikz overlayで重ねる |
| F3-2 | タイトル2行目が改行される | `text width` + `fontsize` の組み合わせでCJK文字が収まらない | フォントサイズの縮小とtext widthの拡大を繰り返し調整。最終的にtext widthを0.90に統一し、フォントサイズで幅を制御 |
| F3-3 | 裏表紙の前に空白ページがある | `scrbook`のbook modeでは章が奇数ページから始まるため、本文最終ページが奇数なら偶数ページが自動挿入される | 書籍組版として正しい動作。修正不要 |
| F3-4 | 署名ブロックが左寄せのプレーンテキスト | Markdownに右寄せの標準構文がない | `<div align="right">` + `flushright.lua`（Div要素のalign=rightを`\begin{flushright}`に変換）|
| F3-5 | テストビルドで`\end{document}`の`\e`が消える | bashの`echo '\end{document}'`で`\e`がエスケープシーケンスとして解釈された | `printf`に変更。最終的にはtex切り取り方式をやめ、完全なドキュメントとしてビルドする方式に変更 |
| F3-6 | `microtype`の`\textls`でCJK文字が消える | `microtype`パッケージのトラッキング機能が`luatexja`のCJK描画と干渉し、テキストが一切レンダリングされなくなった | `microtype`を使用しない方針に変更。字間調整は将来必要に応じて`luatexja`の`kanjiskip`で対応 |
| F3-7 | フォントをBlackに変更しても太くならない | `\newfontfamily`は欧文フォントのみを制御し、CJK文字には適用されない。`Noto Serif CJK JP Black`を指定しても日本語部分はluatexja-presetのHaranoAji Regularのまま描画されていた | `\newjfontfamily`（和文用）と`\newfontfamily`（欧文用）を両方定義し、tikzノード内で両方のコマンドを呼ぶことで和文・欧文ともにBlackウェイトを適用 |
| F3-8 | `Noto Serif CJK JP Bold`指定でテキストが消える | `fc-list`上のフォント名が`Noto Serif CJK JP`（style=Bold）であり、`Noto Serif CJK JP Bold`というファミリー名は存在しない | `BoldFont`オプションで明示指定、またはBlack（ファミリー名が`Noto Serif CJK JP Black`として独立）を使用 |

#### 不採用・削除した対処

| 対処 | 理由 |
|------|------|
| Eisvogelの`titlepage-background`変数による背景画像配置 | scrbook + tikz `\node[overlay]` の組み合わせで画像が正しく全面描画されない。`\newgeometry`とscrbook内部のヘッダー/フッター領域の干渉と推定 |
| `\newgeometry{top=0pt...}` でマージンをゼロに | scrbookのページ構造が壊れ、さらに状況が悪化した |
| テストビルドでtitlepageのみ切り出し（sed） | `\end{document}` のエスケープ問題、lualatexの2パス処理でのレイアウト不整合が発生 |
| `\usepackage[letterspace=...]{microtype}` による字間調整 | CJKフォントとの相性問題でテキストが消失。`luatexja`環境ではmicrotypeのトラッキングは使えない |
| `\newfontfamily` のみでBlackウェイト指定 | 欧文フォントしか制御できず、日本語は細いまま。`\newjfontfamily`が必要 |
| ヒラギノ明朝 ProN W6 の使用 | macOSのライセンスに紐づいており、商用PDFへの埋め込み配布がグレー〜NG |

#### 表紙デザインの変遷

1. **v1（cover.jpeg）**: Eisvogelの`titlepage-background`で全面背景 → scrbook干渉で失敗 → 独立LaTeX方式に変更
2. **v2（cover_v2.png）**: 背景画像を差し替え、テキスト位置・サイズを全面調整
3. **フォント太さの調整**: SemiBold → Bold（テキスト消失）→ Black（`\newjfontfamily`で解決）
4. **副題ウェイト分離**: タイトルBlack + 副題Boldでメリハリを付ける

#### 最終的なアーキテクチャ

```
表紙:   build/cover.tex    → lualatex → cover.pdf（独立生成）
本文:   pandoc → .tex → sed → lualatex → ai-biocode-kata-full.pdf（Eisvogel）
裏表紙: build/back-cover.tex（-A オプションで本文PDFに挿入）
最終版: pdfunite cover.pdf ai-biocode-kata-full.pdf → 最終PDF（将来対応）
```

#### 表紙テキスト仕様（最終）

| 要素 | フォント | サイズ | 位置 | 色 | text width |
|------|---------|-------|------|-----|-----------|
| タイトル1行目 | Noto Serif CJK JP Black | 36pt/40pt | north -15% | #1E1E1E | 0.90 |
| タイトル2行目 | Noto Serif CJK JP Black | 24pt/30pt | north -19.5% | #1E1E1E | 0.90 |
| 副題 | Noto Sans CJK JP Bold | 16pt/22pt | north -24% | #3C3C3C | 0.85 |
| 著者 | Noto Serif CJK JP Black | 24pt/30pt | north -34% | #1E1E1E | — |

背景画像: `figures/cover_v2.png`（`eso-pic`で全面配置）

**重要な実装上の注意**: CJKフォントのウェイト指定には `\newjfontfamily`（和文用）と `\newfontfamily`（欧文用）の両方を定義し、使用箇所で両方のコマンドを呼ぶ必要がある。`\newfontfamily` だけでは日本語にウェイトが適用されない。

#### 関連ファイル

| ファイル | 役割 |
|--------|------|
| `build/cover.tex` | 表紙生成用の独立LaTeX |
| `build/back-cover.tex` | 裏表紙（本文PDFの最終ページに挿入） |
| `build/flushright.lua` | `<div align="right">` → `\begin{flushright}` 変換 |
| `build/build_cover_test.sh` | 表紙のみの高速テストビルド |
| `build/eisvogel-custom.tex` | 表紙用フォント定義（covertitlefont等） |

---

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
| 表紙 | 独立PDF（cover.tex）で生成 | 背景画像+タイトル+副題+著者。本文PDFとの結合は今後対応 |
| 裏表紙 | 本文PDFの最終ページに挿入 | back-cover.texで全面画像配置 |
| drawio図のフォントサイズ | A4想定で小さい | B5向け再エクスポートが必要 |
