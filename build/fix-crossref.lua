-- build/fix-crossref.lua
-- 統合PDF/EPUB ビルド時に章間の相互参照リンクを内部リンクに変換する。
--
-- ./filename.md#section → #section（ファイル名を除去）
-- ./filename.md（アンカーなし）→ #chapter-heading-id（章見出しのアンカーに変換）
--
-- このフィルターは統合PDFビルド・統合EPUBビルドのみで使用する。
-- 章ごとPDFビルドでは使用しない（外部リンクのままでよい）。
--
-- pandocの identifier 生成規則は出力形式によって異なる:
-- - LaTeX (PDF): デフォルトの auto_identifiers (先頭の非アルファベット文字を除去)
-- - HTML/EPUB: gfm_auto_identifiers (先頭の数字も保持)
-- そのため、ファイル名→章ID のマッピングは形式ごとに別管理する。

-- LaTeX/PDF 用: pandoc デフォルトの auto_identifiers が生成する形式
FILE_TO_CHAPTER_ID_LATEX = {
  ["hajimeni.md"] = "はじめに",
  ["notice.md"] = "本書の利用について免責事項",
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

-- HTML/EPUB 用: gfm_auto_identifiers が生成する形式
-- 各章の H1 から pandoc -f markdown+gfm_auto_identifiers で算出
-- pandoc EPUB writer は数字始まりの ID に id_ プレフィックスを自動付与するため、
-- ここでは id_ プレフィックスは含めない（pandoc が自動補完する）
FILE_TO_CHAPTER_ID_HTML = {
  ["hajimeni.md"] = "はじめに",
  ["notice.md"] = "本書の利用について免責事項",
  ["00_ai_agent.md"] = "0-aiエージェントにコードを書かせる",
  ["01_design.md"] = "1-設計原則--良いコードとは何か",
  ["02_terminal.md"] = "2-ターミナルとシェルの基本操作",
  ["03_cs_basics.md"] = "3-コーディングに必要な計算機科学",
  ["04_data_formats.md"] = "4-データフォーマットの選び方",
  ["05_software_components.md"] = "5-ソフトウェアの構成要素--importからpipまで",
  ["06_dev_environment.md"] = "6-python環境の構築--pyenvvenvcondauv",
  ["07_git.md"] = "7-git入門--コードのバージョン管理",
  ["08_testing.md"] = "8-コードの正しさを守るテスト技法",
  ["09_debug.md"] = "9-デバッグの技術--tracebackから最小再現例まで",
  ["10_deliverables.md"] = "10-ソフトウェア成果物の設計--スクリプトからパッケージまで",
  ["11_cli.md"] = "11-コマンドラインツールの設計と実装",
  ["12_data_processing.md"] = "12-データ処理の実践--numpypandaspolars",
  ["13_visualization.md"] = "13-可視化の実践--matplotlibseabornplotly",
  ["14_workflow.md"] = "14-解析パイプラインの自動化--snakemakenextflowcwl",
  ["15_container.md"] = "15-コンテナによるソフトウェア環境の再現--dockerapptainer",
  ["16_hpc.md"] = "16-スパコンクラスタでの大規模計算",
  ["17_performance.md"] = "17-コードのパフォーマンス改善--プロファイリングと高速化",
  ["18_documentation.md"] = "18-コードのドキュメント化",
  ["19_database_api.md"] = "19-公共データベースとapi--データ取得の実践",
  ["20_security_ethics.md"] = "20-コードとデータのセキュリティ倫理",
  ["21_collaboration.md"] = "21-共同開発の実践--レビュー質問oss参加",
  ["appendix_a_learning_patterns.md"] = "付録a-aiコーディングエージェントとの効果的な学習パターン",
  ["appendix_b_cli_reference.md"] = "付録b-claude-code-cli--codex-cli-クイックリファレンス対照表",
  ["appendix_c_checklist.md"] = "付録c-論文投稿前チェックリスト",
  ["appendix_d_agent_vocabulary.md"] = "付録d-aiコーディングエージェント頻出用語フレーズ集",
  ["glossary.md"] = "用語集",
  ["author.md"] = "著者紹介",
}

-- 出力形式に応じてマッピングを選択
local function get_chapter_id(filename)
  if FORMAT and (FORMAT:match("epub") or FORMAT:match("html")) then
    return FILE_TO_CHAPTER_ID_HTML[filename]
  else
    return FILE_TO_CHAPTER_ID_LATEX[filename]
  end
end

-- リンク書き換え
function Link(el)
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
    local chapter_id = get_chapter_id(filename)
    if chapter_id then
      el.target = "#" .. chapter_id
      return el
    end
    -- マッピングがない場合はそのまま
    return nil
  end
end
