-- build/column-anchor.lua
-- コラム用HTMLアンカーをPDFの名前付きリンク先へ変換する。
--
-- MarkdownとEPUBでは <a id="column-chNN-NN"></a> をそのまま使う。
-- LaTeX出力ではraw HTMLが破棄されるため、\hypertarget{}{}へ置換する。

local function column_anchor_id(text)
  return text:match('^<a%s+id="(column%-ch%d%d%-%d%d)"%s*>$')
    or text:match('^<a%s+id="(column%-ch%d%d%-%d%d)"%s*></a>$')
end

function RawInline(el)
  if not FORMAT:match("latex") or el.format ~= "html" then
    return nil
  end

  local identifier = column_anchor_id(el.text)
  if not identifier then
    return nil
  end

  return pandoc.RawInline("latex", "\\hypertarget{" .. identifier .. "}{}")
end
