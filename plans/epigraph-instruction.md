# pandoc PDF でエピグラフを実装する指示書

## 概要

pandoc で Markdown → PDF 変換を行っている書籍プロジェクトに、章頭エピグラフ（引用句＋出典）を美しく組版する仕組みを追加する。

GitHub 上でも自然な blockquote として表示されるよう、pandoc 独自の fenced div（`:::`）は使わず、通常の blockquote 記法を採用する。

## 前提環境

- pandoc（最新版推奨）
- LuaLaTeX（pdf-engine として使用）
- 日本語フォント環境（jlreq クラス等）

---

## 方法: blockquote の出典行パターン検出 + LaTeX `epigraph` パッケージ

### ステップ 1: Markdown での記法

通常の blockquote を使い、最後の段落を `──` で始める。これがエピグラフの識別子になる:

```markdown
> プログラムは人間が読むために書かれるべきである。
> たまたまコンピュータが実行できるだけだ。
>
> ── Harold Abelson, *計算機プログラムの構造と解釈*
```

ルール:
- 通常の Markdown blockquote（`>` ）で書く
- 引用本文を先に書く
- 出典行は引用本文との間に空行（`>`のみの行）を1つ入れる
- 出典行は `── `（全角ダッシュ2つ＋半角スペース）で始める
- 出典の著者名と作品名はカンマ区切り。作品名は `*...*` でイタリック指定
- `──` で始まる最終段落がない blockquote は通常の引用として扱い、変換しない

GitHub 上での見え方:

> プログラムは人間が読むために書かれるべきである。
> たまたまコンピュータが実行できるだけだ。
>
> ── Harold Abelson, *計算機プログラムの構造と解釈*

通常の blockquote として自然に表示される。

### ステップ 2: LaTeX ヘッダーファイルを作成

`header.tex` というファイルを作成し、以下の内容を書く:

```latex
\usepackage{epigraph}

% エピグラフの幅（本文幅に対する比率）
\setlength{\epigraphwidth}{0.75\textwidth}

% 出典の配置
\renewcommand{\epigraphflush}{flushright}
\renewcommand{\sourceflush}{flushright}

% エピグラフ前後のスペース調整
\setlength{\beforeepigraphskip}{1.5\baselineskip}
\setlength{\afterepigraphskip}{2\baselineskip}

% 区切り線なし（モダンなデザイン）
\setlength{\epigraphrule}{0pt}

% 引用文のフォントサイズ（本文より少し小さく）
\renewcommand{\epigraphsize}{\small}
```

### ステップ 3: Lua フィルターを作成

`epigraph.lua` というファイルを作成する。このフィルターは blockquote の最終段落が `──` で始まる場合にエピグラフとして検出し、LaTeX の `\epigraph{}{}` コマンドに変換する。

```lua
-- epigraph.lua
-- pandoc Lua filter: converts blockquotes with attribution lines into epigraphs
--
-- 検出ルール:
--   blockquote の最後の要素が Para であり、
--   その先頭の Str が "──" で始まる場合、エピグラフとして扱う。
--   それ以外の blockquote はそのまま通す。

-- 出典行の先頭から識別用の記号を除去し、インライン要素のリストを返す
local function extract_source_inlines(para)
  local inlines = para.content
  local result = {}
  local found_prefix = false

  for i, inline in ipairs(inlines) do
    if not found_prefix then
      if inline.t == "Str" then
        -- "──" "———" "---" のいずれかで始まる Str を探す
        local cleaned = inline.text
          :gsub("^──%s*", "")
          :gsub("^———%s*", "")
          :gsub("^%-%-%-%s*", "")

        found_prefix = true

        if cleaned ~= "" then
          table.insert(result, pandoc.Str(cleaned))
        end
      elseif inline.t == "Space" then
        -- 先頭スペースはスキップ
      else
        -- 記号以外が先頭に来た場合、エピグラフではない
        return nil
      end
    else
      -- 記号除去後のスペースを1つスキップ
      if #result == 0 and inline.t == "Space" then
        -- skip
      else
        table.insert(result, inline)
      end
    end
  end

  if not found_prefix then
    return nil
  end

  return result
end

-- blockquote の最後の段落が出典行かどうか判定する
local function is_epigraph(el)
  if #el.content == 0 then
    return false
  end

  local last = el.content[#el.content]
  if last.t ~= "Para" then
    return false
  end

  if #last.content == 0 then
    return false
  end

  local first = last.content[1]
  if first.t ~= "Str" then
    return false
  end

  return first.text:match("^──")
    or first.text:match("^———")
    or first.text:match("^%-%-%-")
end

function BlockQuote(el)
  if not is_epigraph(el) then
    return nil -- 通常の blockquote はそのまま
  end

  -- 最後の段落を出典として分離
  local source_para = el.content[#el.content]
  local source_inlines = extract_source_inlines(source_para)

  if not source_inlines then
    return nil
  end

  -- 引用本文 = 最後の段落を除いた残り
  local quote_blocks = {}
  for i = 1, #el.content - 1 do
    table.insert(quote_blocks, el.content[i])
  end

  -- ===== LaTeX / PDF 出力 =====
  if FORMAT:match("latex") or FORMAT:match("pdf") then
    -- 引用本文を LaTeX に変換
    local quote_doc = pandoc.Pandoc(quote_blocks)
    local quote_text = pandoc.write(quote_doc, "latex")
    quote_text = quote_text
      :gsub("\\begin{document}\n", "")
      :gsub("\n\\end{document}\n?", "")
      :gsub("^%s+", ""):gsub("%s+$", "")

    -- 出典を LaTeX に変換（イタリック等を保持）
    local source_doc = pandoc.Pandoc({pandoc.Para(source_inlines)})
    local source_text = pandoc.write(source_doc, "latex")
    source_text = source_text
      :gsub("\\begin{document}\n", "")
      :gsub("\n\\end{document}\n?", "")
      :gsub("^%s+", ""):gsub("%s+$", "")

    local latex = string.format("\\epigraph{%s}{%s}", quote_text, source_text)
    return pandoc.RawBlock("latex", latex)
  end

  -- ===== HTML / EPUB 出力 =====
  if FORMAT:match("html") then
    local quote_doc = pandoc.Pandoc(quote_blocks)
    local quote_html = pandoc.write(quote_doc, "html")

    local source_doc = pandoc.Pandoc({pandoc.Para(source_inlines)})
    local source_html = pandoc.write(source_doc, "html")
    source_html = source_html:gsub("</?p>", ""):gsub("^%s+", ""):gsub("%s+$", "")

    local html = string.format(
      '<div class="epigraph"><blockquote>%s</blockquote>'
      .. '<p class="epigraph-source">── %s</p></div>',
      quote_html,
      source_html
    )
    return pandoc.RawBlock("html", html)
  end
end
```

### ステップ 4: pandoc のビルドコマンド

```bash
pandoc \
  --pdf-engine=lualatex \
  --include-in-header=header.tex \
  --lua-filter=epigraph.lua \
  --toc \
  -o output.pdf \
  input.md
```

defaults ファイル (`defaults.yaml`) を使う場合:

```yaml
pdf-engine: lualatex
include-in-header:
  - header.tex
filters:
  - epigraph.lua
table-of-contents: true
toc-depth: 2
```

```bash
pandoc -d defaults.yaml -o output.pdf input.md
```

### ステップ 5: 動作確認用のテスト原稿

以下のテスト用 Markdown を `test-epigraph.md` として作成し、ビルドして PDF を確認する:

```markdown
---
title: "エピグラフテスト"
author: "著者名"
documentclass: ltjsbook
lang: ja
---

# 第1章 はじめに

> プログラムは人間が読むために書かれるべきである。
> たまたまコンピュータが実行できるだけだ。
>
> ── Harold Abelson, *計算機プログラムの構造と解釈*

本章では、バイオインフォマティクスにおけるプログラミングの基本的な考え方を紹介する。

## 1.1 なぜプログラミングを学ぶのか

本文がここに続く。

# 第2章 シェルの基本

> このパイプという仕組みが、コンピュータサイエンスにおける
> 最も偉大な発明であると私は考えている。
>
> ── Douglas McIlroy

本章では、シェル環境の基本操作を学ぶ。

# 第3章 通常の引用を含む章

以下は通常の blockquote であり、エピグラフとして変換されてはいけない:

> これは普通の引用文である。
> 出典行がないので通常の blockquote として表示される。

本文が続く。

# 第4章 出典に作品名を含むエピグラフ

> 早まった最適化は諸悪の根源である。
>
> ── Donald Knuth, *The Art of Computer Programming*

本章では、コードの最適化について議論する。
```

テスト観点:
1. 第1章・第2章・第4章: `\epigraph{}{}` に正しく変換されること
2. 第3章: 通常の blockquote がそのまま維持されること
3. 出典のイタリック（`*...*`）が LaTeX の `\emph{}` に変換されること
4. 複数行の引用文が正しく処理されること

---

## ファイル構成

プロジェクトルートに以下のファイルを配置:

```
project/
├── defaults.yaml        # pandoc のデフォルト設定
├── header.tex           # LaTeX ヘッダー（epigraph パッケージ設定）
├── epigraph.lua         # Lua フィルター
├── chapters/
│   ├── ch01.md
│   ├── ch02.md
│   └── ...
└── output/
    └── book.pdf
```

---

## カスタマイズポイント

### エピグラフの幅を変更

`header.tex` の `\epigraphwidth` を調整:
- `0.75\textwidth` — 標準（本文幅の75%）
- `0.6\textwidth` — 狭め（短い引用向き）
- `\textwidth` — 本文幅いっぱい

### 区切り線の有無

`header.tex` の `\epigraphrule`:
- `0pt` — 線なし（モダンなデザイン）
- `0.4pt` — 細い線（クラシックなデザイン）

### 出典行の識別記号を変更

Lua フィルターは以下の3パターンに対応済み:
- `──`（全角ダッシュ2つ、推奨）
- `———`（全角ダッシュ3つ）
- `---`（半角ハイフン3つ、pandoc が emダッシュに変換する場合あり）

新しいパターンを追加するには `is_epigraph` 関数と `extract_source_inlines` 関数の正規表現を編集する。

### 引用文のフォントを変更

引用文を明朝体にしたい場合、`header.tex` に追加:

```latex
\renewcommand{\epigraphsize}{\small\mcfamily}
```

---

## EPUB 出力との併用

Lua フィルターは HTML 出力にも対応している。EPUB 生成時には `<div class="epigraph">` として出力されるため、EPUB 用 CSS に以下を追加:

```css
.epigraph {
  margin: 2em 1em 2em 2em;
  font-size: 0.95em;
}
.epigraph blockquote {
  margin: 0;
  padding: 0;
  border: none;
  font-style: italic;
}
.epigraph-source {
  text-align: right;
  font-size: 0.9em;
  margin-top: 0.5em;
  color: #555;
}
```

---

## トラブルシューティング

### `epigraph.sty not found` エラー

TeX Live に epigraph パッケージがない場合:
```bash
tlmgr install epigraph
```

### 通常の blockquote がエピグラフに変換されてしまう

最終段落の先頭が `──` `———` `---` のいずれかで始まる blockquote のみがエピグラフとして扱われる。意図せず変換される場合は、出典行の書式を変えるか、Lua フィルターの `is_epigraph` 関数の判定条件を厳しくする（例: 引用本文が2ブロック以上ある場合のみ変換）。

### `---` が水平線に変換される

blockquote 内部（`>` の後）に `---` を書く場合、pandoc は水平線ではなく通常のテキストとして扱う。blockquote の外に `---` を書くと `<hr>` になるので注意。推奨は `──`（全角ダッシュ2つ）を使うこと。

### jlreq クラスとの競合

`ltjsbook` の代わりに `jlreq` クラスを使う場合は `header.tex` の設定はそのまま使える。ただし余白設定が異なるため `\epigraphwidth` の調整が必要になる場合がある。

### pandoc-crossref との併用

`defaults.yaml` でフィルターの順序に注意:

```yaml
filters:
  - pandoc-crossref
  - epigraph.lua
```

pandoc-crossref を先に実行し、epigraph.lua を後に実行する。epigraph.lua は blockquote のみを処理するため、pandoc-crossref と干渉しない。
