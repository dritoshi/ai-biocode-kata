# 手動ファクトチェックメモ

2026-03-25 時点で、変化が速い記述や数値主張を優先して確認した。

## 確認結果

| 箇所 | 判定 | メモ | 主な出典 |
|---|---|---|---|
| `chapters/hajimeni.md` GPT-5.2 の SWE-bench Verified 80.0% | 確認済み | OpenAI の `Introducing GPT-5.2`（2025-12-11）で `SWE-bench Verified` 80.0% を確認した。 | https://openai.com/index/introducing-gpt-5-2/ |
| `chapters/hajimeni.md` Claude Opus 4.5 の SWE-bench Verified 最上位 | 概ね確認済み | Anthropic の `Introducing Claude Opus 4.5` は SWE-bench Verified で最上位と説明しているが、本文から 80.9% の数値自体は機械可読に確認しづらい。数値を残すなら system card か明示数値のある一次資料に寄せたい。 | https://www.anthropic.com/news/claude-opus-4-5 |
| `chapters/hajimeni.md` 「全ての人間候補者を上回る」 | 修正済み | Anthropic の `Designing AI-resistant technical evaluations`（2026-01-21）は **Claude Opus 4** が **most human applicants** を上回ったと述べる。本文はこの表現に合わせて修正した。 | https://www.anthropic.com/engineering/AI-resistant-technical-evaluations |
| `chapters/hajimeni.md` GitHub の 2025 年コミット数 | 確認済み | GitHub Octoverse 2025 で `pushed nearly 1 billion commits in 2025` を確認した。 | https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/ |
| `chapters/hajimeni.md` GitHub Copilot 20M+ users | 確認済み | GitHub 公式ブログ（2025-09-22 および 2025-10-27 周辺記事）で `20M+ users` を確認した。 | https://github.blog/ai-and-ml/github-copilot/gartner-positions-github-as-a-leader-in-the-2025-magic-quadrant-for-ai-code-assistants-for-the-second-year-in-a-row/ |
| `chapters/hajimeni.md` Copilot が平均 46% のコードを生成 | 修正済み | 46% は GitHub の 2023 年ブログで「Copilot が有効なファイルで平均 46%」という文脈の数値。本文では 2025-09-22 の `20M+ users` と切り分け、年次と測定条件を明示した。 | https://github.blog/2023-02-14-github-copilot-now-has-a-better-ai-model-and-new-capabilities/ |
| `chapters/hajimeni.md` Claude Code が公開 GitHub コミットの 4% | 二次情報 | SemiAnalysis の 2026-02-05 記事では 4% 主張を確認したが、GitHub や Anthropic の公式計測ではない。本文では「推計」または「SemiAnalysis はこう推定」と明記するのが安全。 | https://newsletter.semianalysis.com/p/claude-code-is-the-inflection-point |
| `chapters/hajimeni.md` Collins Word of the Year 2025 | 確認済み | Collins Dictionary の公式 `Word of the Year 2025` ページで `vibe coding` を確認した。本文の出典を一次ソースへ差し替えた。 | https://www.collinsdictionary.com/us/woty/ |
| `chapters/19_database_api.md` NCBI E-utilities の 3 req/s と 10 req/s | 確認済み | NCBI Insights の API key 記事で、キーなし 3 req/s、キーあり 10 req/s を確認した。 | https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/ |
| `chapters/20_security_ethics.md` 科研費 DMP とメタデータ報告 | 修正済み | JSPS 公式ページでは、令和6（2024）年度以降の課題で DMP を活用した管理が求められる一方、研究開始前の DMP 提出は不要とされている。各年度の研究終了後には、公開した研究データの情報（メタデータ等）を報告書の一部として提出する運用である。本文はこの表現に合わせて修正した。 | https://www.jsps.go.jp/j-grantsinaid/01_seido/10_datamanagement/index.html |
| `chapters/20_security_ethics.md` ローカルモデル表の `Llama-3.1` 行 | 削除済み | `Llama 3.1` は Meta 製の汎用モデルであり、コーディング用途の実務推奨モデルとして挙げる理由が弱い。本文では `gpt-oss-20b` と混線していた記述を修正したうえで、最終的に推奨一覧から除外した。 | https://openai.com/index/introducing-gpt-oss/ ; https://openai.com/es-ES/index/gpt-oss-model-card/ ; https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct |
| `chapters/21_collaboration.md` Stack Overflow の生成 AI ポリシー | 修正済み | 2026-03-25 時点の Help Center は、Stack Overflow 向けコンテンツの生成に生成 AI を用いること自体を禁じている。Meta の告知でも、質問文の生成や回答のリライトを含むことが明示されているため、本文のプロンプト例を「投稿文生成」から「論点整理」に差し替えた。 | https://stackoverflow.com/help/gen-ai-policy ; https://meta.stackoverflow.com/questions/421831 |
| `chapters/21_collaboration.md` Biostars のクロスポスト | 修正済み | Biostars で一律の「禁止」規約は確認できず、コミュニティ上では cross-posting is discouraged という扱いだった。本文は「禁止」から「原則避け、必要なら相互リンクを明示」に修正した。 | https://www.biostars.org/p/126034/ |

## 使い方

- 本メモは「時事性が高い主張」の優先確認用であり、全URLの到達確認を代替するものではない。
- 数値主張は、本文に残すなら **日付** と **測定条件** を併記する。
- 二次情報しか取れていない項目は、出版前に一次ソースへ差し替える。
