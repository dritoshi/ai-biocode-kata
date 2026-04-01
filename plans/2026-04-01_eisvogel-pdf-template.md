# Eisvogelテンプレートによるpandoc PDFビルド改善

実施日: 2026-04-01
状態: 完了

## 目的

pandoc PDFのデザインをiThenticate用（L1）からレビュー・出版用（L2〜L3）に引き上げる。

## 実施内容

### テンプレート移行
- ltjsarticle + デフォルトテンプレート → Eisvogel 3.4.0 + scrbook
- `build/templates/eisvogel.latex` にテンプレートを配置、blockquoteスタイルをパッチ

### 解決した問題（10件）
1. コードブロック背景色 → `--highlight-style=tango`
2. 章間改ページ → `--top-level-division=chapter` + `-V book=true`
3. フッター著者名 → `-V "footer-left= "` `-V "footer-right= "` で空に
4. コラムテキスト薄い → eisvogel.latexのblockquoteをフラットグレー背景にパッチ
5. リスト未レンダリング → hajimeni.mdの`:` 直後に空行追加
6. コードブロック/図の空白 → 2段階ビルド（pandoc→tex→sed figure[H]→lualatex）
7. エピグラフ未対応 → epigraph.lua Luaフィルター新規作成
8. エピグラフ出典改行 → `\epigraphwidth` を0.9\textwidthに
9. 章間リンク壊れ → fix-crossref.lua Luaフィルター新規作成
10. タイトルページなし → `-V titlepage=true`

### 不採用にした対処（4件）
- `\floatplacement{figure}{H}` — pandoc 3.9で効かない
- figure-placement.lua — pandoc 3.9のFigure型で反映されない
- `\renewenvironment{figure}` — header-includesのロード順で競合
- 直接pandocでPDF生成 — figure[H]のsed置換が必要なため2段階ビルドに

## 新規作成ファイル
- `build/templates/eisvogel.latex` — パッチ済みテンプレート
- `build/eisvogel-custom.tex` — epigraph設定、raggedbottom、tightlist
- `build/epigraph.lua` — エピグラフ変換フィルター
- `build/fix-crossref.lua` — 章間リンク変換フィルター（統合PDF用）
- `build/README.md` — PDFビルド手順書
- `build/BUILD_REPORT.md` — 問題解決ログ（更新）
