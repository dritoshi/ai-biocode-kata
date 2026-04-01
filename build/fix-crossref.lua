-- build/fix-crossref.lua
-- 統合PDFビルド時に章間の相互参照リンクを内部リンクに変換する。
--
-- ./filename.md#section → #section（ファイル名を除去）
-- ./filename.md（アンカーなし）→ #chapter-heading-id（章見出しのアンカーに変換）
--
-- このフィルターは統合PDFビルド時のみ使用する。
-- 章ごとPDFビルドでは使用しない（外部リンクのままでよい）。

-- ファイル名 → 章見出しアンカーのマッピングを構築
-- pandocのidentifier生成ロジックを利用
local file_to_id = {}

-- ドキュメント内の全Header(level=1)を走査してマッピングを構築
-- （統合PDFでは全章が1つのドキュメントになっている）
function Pandoc(doc)
  -- Phase 1: 全 Header level=1 の identifier を収集
  -- pandocが自動生成した identifier をそのまま使う
  for _, block in ipairs(doc.blocks) do
    if block.t == "Header" and block.level == 1 then
      local id = block.identifier
      local text = pandoc.utils.stringify(block)

      -- 見出しテキストからファイル名を推定するのは困難なので、
      -- 既知のマッピングテーブルを使用する
    end
  end

  -- Phase 2: 全 Link を走査して target を書き換え
  doc = doc:walk({
    Link = function(el)
      local target = el.target

      -- ./filename.md または ./filename.md#anchor のパターンを検出
      local filename, anchor = target:match("^%.%/([^#]+%.md)#(.+)$")
      if not filename then
        filename = target:match("^%.%/([^#]+%.md)$")
      end

      if not filename then
        return nil -- 相対リンクでなければそのまま
      end

      if anchor then
        -- ./filename.md#section → #section
        el.target = "#" .. anchor
        return el
      else
        -- ./filename.md（アンカーなし）→ 章見出しのIDを使う
        local chapter_id = FILE_TO_CHAPTER_ID[filename]
        if chapter_id then
          el.target = "#" .. chapter_id
          return el
        end
        -- マッピングがない場合はそのまま
        return nil
      end
    end
  })

  return doc
end

-- ファイル名→章見出しIDの静的マッピング
-- pandocの identifier 生成規則: 英数字・日本語はそのまま、記号はハイフン、
-- 先頭の§Nは除去される場合がある
-- 実際のIDはpandocが生成した .tex の \label{} から取得
FILE_TO_CHAPTER_ID = {
  ["hajimeni.md"] = "はじめに",
  ["00_ai_agent.md"] = "aiエージェントにコードを書かせる",
  ["01_design.md"] = "設計原則-良いコードとは何か",
  ["02_terminal.md"] = "ターミナルとシェルの基本操作",
  ["03_cs_basics.md"] = "コーディングに必要な計算機科学",
  ["04_data_formats.md"] = "データフォーマットの選び方",
  ["05_software_components.md"] = "ソフトウェアの構成要素-importからpipまで",
  ["06_dev_environment.md"] = "python環境の構築-pyenvvenvcondauv",
  ["07_git.md"] = "git入門-コードのバージョン管理",
  ["08_testing.md"] = "コードの正しさを守るテスト技法",
  ["09_debug.md"] = "デバッグの技術-tracebackから最小再現例まで",
  ["10_deliverables.md"] = "ソフトウェア成果物の設計-スクリプトからパッケージまで",
  ["11_cli.md"] = "コマンドラインツールの設計と実装",
  ["12_data_processing.md"] = "データ処理の実践-numpypandaspolars",
  ["13_visualization.md"] = "可視化の実践-matplotlibseabornplotly",
  ["14_workflow.md"] = "解析パイプラインの自動化-snakemakenextflowcwl",
  ["15_container.md"] = "コンテナによるソフトウェア環境の再現-dockerapptainer",
  ["16_hpc.md"] = "スパコンクラスタでの大規模計算",
  ["17_performance.md"] = "コードのパフォーマンス改善-プロファイリングと高速化",
  ["18_documentation.md"] = "コードのドキュメント化",
  ["19_database_api.md"] = "公共データベースとapi-データ取得の実践",
  ["20_security_ethics.md"] = "コードとデータのセキュリティ倫理",
  ["21_collaboration.md"] = "共同開発の実践-レビュー質問oss参加",
  ["appendix_a_learning_patterns.md"] = "付録a.-aiコーディングエージェントとの効果的な学習パターン",
  ["appendix_b_cli_reference.md"] = "付録b.-claude-code-cli-codex-cli-クイックリファレンス対照表",
  ["appendix_c_checklist.md"] = "付録c.-論文投稿前チェックリスト",
  ["appendix_d_agent_vocabulary.md"] = "付録d.-aiコーディングエージェント頻出用語フレーズ集",
  ["glossary.md"] = "用語集",
  ["author.md"] = "著者紹介",
}
