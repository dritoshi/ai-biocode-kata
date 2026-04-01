-- build/flushright.lua
-- <div align="right">...</div> を LaTeX の flushright 環境に変換する。
-- pandoc は <div align="right"> を Div 要素（属性 align=right）として解析する。

function Div(el)
  local align = el.attributes["align"]
  if align ~= "right" then return nil end

  if FORMAT:match("latex") or FORMAT:match("pdf") then
    local blocks = el.content
    table.insert(blocks, 1, pandoc.RawBlock("latex", "\\begin{flushright}"))
    table.insert(blocks, pandoc.RawBlock("latex", "\\end{flushright}"))
    return blocks
  end
end
