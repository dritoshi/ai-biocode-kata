-- build/emoji-filter.lua — 絵文字をLaTeX互換表現に変換するpandocフィルタ
-- 原稿のMarkdownは変更せず、PDF生成時のみ適用する

-- テキスト用置換マップ（LaTeXコマンド）
local text_map = {
  ["🧬"] = "\\textbf{[BIO]}",
  ["🤖"] = "\\textbf{[ML]}",
  ["📦"] = "\\textbf{[PKG]}",
  ["✅"] = "\\checkmark{}",
  ["❌"] = "\\texttimes{}",
  ["⚠️"] = "\\textbf{!}",
  ["⚠"]  = "\\textbf{!}",
  ["ℹ️"] = "\\textbf{i}",
  ["ℹ"]  = "\\textbf{i}",
}

-- コードブロック用置換マップ（プレーンテキスト）
local code_map = {
  ["✅"] = "[OK]",
  ["❌"] = "[NG]",
  ["⚠️"] = "[!]",
  ["⚠"]  = "[!]",
  ["ℹ️"] = "[i]",
  ["ℹ"]  = "[i]",
  ["🧬"] = "[BIO]",
  ["🤖"] = "[ML]",
  ["📦"] = "[PKG]",
}

-- 通常テキスト内の絵文字をLaTeXコマンドに変換
function Str(el)
  local text = el.text
  local changed = false
  for emoji, replacement in pairs(text_map) do
    if text:find(emoji, 1, true) then
      text = text:gsub(emoji, replacement)
      changed = true
    end
  end
  if changed then
    return pandoc.RawInline("latex", text)
  end
end

-- コードブロック内の絵文字をプレーンテキストに変換
function CodeBlock(el)
  local text = el.text
  for emoji, replacement in pairs(code_map) do
    text = text:gsub(emoji, replacement)
  end
  el.text = text
  return el
end

-- インラインコード内の絵文字をプレーンテキストに変換
function Code(el)
  local text = el.text
  for emoji, replacement in pairs(code_map) do
    text = text:gsub(emoji, replacement)
  end
  el.text = text
  return el
end
