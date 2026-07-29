-- build/fix-repository-links.lua
-- EPUB 内で参照する scripts/・tests/ の相対リンクを、GitHub の恒久リンクへ変換する。
--
-- Markdown と PDF ではリポジトリ内の相対リンクを維持する。このフィルターは
-- build_epub.sh からだけ呼び出し、EPUB に収録されないコード資産を外部リンクにする。
--
-- 環境変数:
-- - EPUB_REPOSITORY_URL: https://github.com/owner/repository
-- - EPUB_SOURCE_COMMIT: 40桁のコミット SHA

local repository_url = os.getenv("EPUB_REPOSITORY_URL")
local source_commit = os.getenv("EPUB_SOURCE_COMMIT")

if not repository_url or repository_url == "" then
  error("EPUB_REPOSITORY_URL is required")
end

repository_url = repository_url:gsub("/+$", "")
if not repository_url:match("^https://github%.com/[^/]+/[^/]+$") then
  error("EPUB_REPOSITORY_URL must be a GitHub repository URL")
end

if not source_commit or not source_commit:match("^[0-9a-f]+$")
    or #source_commit ~= 40 then
  error("EPUB_SOURCE_COMMIT must be a 40-character lowercase commit SHA")
end

local function repository_path(target)
  for _, root in ipairs({"scripts", "tests"}) do
    local prefix = "../" .. root .. "/"
    if target:sub(1, #prefix) == prefix then
      local remainder = target:sub(#prefix + 1)
      local path_part = remainder:match("^([^?#]*)")
      local suffix = remainder:sub(#path_part + 1)
      return root .. "/" .. path_part, suffix
    end
  end

  for _, view in ipairs({"blob", "tree"}) do
    local prefix = repository_url .. "/" .. view .. "/main/"
    if target:sub(1, #prefix) == prefix then
      local remainder = target:sub(#prefix + 1)
      for _, root in ipairs({"scripts", "tests"}) do
        local root_prefix = root .. "/"
        if remainder:sub(1, #root_prefix) == root_prefix then
          local path_part = remainder:match("^([^?#]*)")
          local suffix = remainder:sub(#path_part + 1)
          return path_part, suffix, view
        end
      end
    end
  end

  return nil
end

function Link(el)
  local path, suffix, original_view = repository_path(el.target)
  if not path then
    return nil
  end

  local view = original_view or "blob"
  if path:sub(-1) == "/" then
    view = "tree"
    path = path:sub(1, -2)
  end

  el.target = string.format(
    "%s/%s/%s/%s%s",
    repository_url,
    view,
    source_commit,
    path,
    suffix
  )
  return el
end
