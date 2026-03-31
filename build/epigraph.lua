-- build/epigraph.lua
-- pandoc Lua filter: blockquote のうちエピグラフ（出典行あり）を
-- LaTeX の \epigraph{}{} コマンドに変換する。
--
-- 検出ルール:
--   BlockQuote 内の Para に SoftBreak + Str("—") のパターンがある場合、
--   SoftBreak 以前を引用本文、以降を出典として分離する。
--   コラム（先頭が太字 "**" や 🧬/🤖 で始まる blockquote）は除外する。

-- SoftBreak + "—" のパターンで出典行の開始位置を探す
local function find_source_break(inlines)
  for i, el in ipairs(inlines) do
    if el.t == "SoftBreak" and i < #inlines then
      local next = inlines[i + 1]
      if next.t == "Str" and (next.text == "—" or next.text:match("^——") or next.text:match("^──")) then
        return i
      end
    end
  end
  return nil
end

-- コラム（太字見出し・絵文字コラム）を除外する
local function is_column(el)
  if #el.content == 0 then return false end
  local first = el.content[1]
  if first.t ~= "Para" then return false end
  if #first.content == 0 then return false end

  local fc = first.content[1]
  -- 🧬 🤖 📦 で始まるコラム
  if fc.t == "Str" and (fc.text:match("^🧬") or fc.text:match("^🤖") or fc.text:match("^📦")) then
    return true
  end
  -- **太字** で始まるコラム（前提知識ボックス等）
  if fc.t == "Strong" then
    return true
  end
  return false
end

function BlockQuote(el)
  -- コラムは除外
  if is_column(el) then
    return nil
  end

  -- 単一 Para のみ対応（現在の記法ではエピグラフは1つの Para）
  if #el.content ~= 1 then return nil end
  local para = el.content[1]
  if para.t ~= "Para" then return nil end

  local break_pos = find_source_break(para.content)
  if not break_pos then return nil end

  -- 引用本文 = SoftBreak の前まで
  local quote_inlines = {}
  for i = 1, break_pos - 1 do
    table.insert(quote_inlines, para.content[i])
  end

  -- 出典 = SoftBreak の後（"—" + Space をスキップ）
  local source_inlines = {}
  local skip_dash = true
  for i = break_pos + 1, #para.content do
    local el = para.content[i]
    if skip_dash then
      if el.t == "Str" and (el.text == "—" or el.text:match("^——") or el.text:match("^──")) then
        -- ダッシュ自体をスキップ
      elseif el.t == "Space" then
        -- ダッシュ直後のスペースをスキップ
        skip_dash = false
      else
        skip_dash = false
        table.insert(source_inlines, el)
      end
    else
      table.insert(source_inlines, el)
    end
  end

  -- LaTeX 出力
  if FORMAT:match("latex") or FORMAT:match("pdf") then
    local quote_doc = pandoc.Pandoc({pandoc.Para(quote_inlines)})
    local quote_text = pandoc.write(quote_doc, "latex")
    quote_text = quote_text:gsub("^%s+", ""):gsub("%s+$", "")

    local source_doc = pandoc.Pandoc({pandoc.Para(source_inlines)})
    local source_text = pandoc.write(source_doc, "latex")
    source_text = source_text:gsub("^%s+", ""):gsub("%s+$", "")

    local latex = string.format("\\epigraph{%s}{\\textemdash\\hspace{0.2em} %s}", quote_text, source_text)
    return pandoc.RawBlock("latex", latex)
  end

  -- HTML 出力（Vivliostyle / EPUB）
  if FORMAT:match("html") then
    local quote_doc = pandoc.Pandoc({pandoc.Para(quote_inlines)})
    local quote_html = pandoc.write(quote_doc, "html")

    local source_doc = pandoc.Pandoc({pandoc.Para(source_inlines)})
    local source_html = pandoc.write(source_doc, "html")
    source_html = source_html:gsub("</?p>", ""):gsub("^%s+", ""):gsub("%s+$", "")

    local html = string.format(
      '<div class="epigraph"><blockquote>%s</blockquote>'
      .. '<p class="epigraph-source">— %s</p></div>',
      quote_html,
      source_html
    )
    return pandoc.RawBlock("html", html)
  end
end
