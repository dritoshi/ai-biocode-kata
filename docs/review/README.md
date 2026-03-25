# レビュー作業ディレクトリ

2026-03-25 時点の完了済みレビュー成果物は `docs/archive/review-2026-03-25/docs_review/` に退避した。

## これまでのレビューの経緯
* Gemini CLI, Codex CLI, Claude Code　CLIで並行レビューを実施
  * Claude Codeは予定通り review_results にレビュー結果を保存し、本文の修正をせずに終了した
  * Gemini CLIがログを残さずにレビューを本文に反映させてしまった
  * Codex CLIは docs/review にログを残しつつ修正を始めてしまった
* そのため、mainブランチからcodex-gemini-reviewブランチを作成し、Gemini, Codexの変更を管理することにした
* 次に、Codexによるレビューと修正が終了させ、codex-gemini-reviewブランチに反映した
* Codexが作成した docs/results と claude code が作成した review_results をマージし、それぞれの終了タスクを docs/archive に退避した
* 以上の結果、review_results が作成したタスクのうち残ったものを docs/reviewで管理することとし、ファイル整理をした
* ここまでの変更をcodex-gemini-reviewブランチにすべて更新した
* 残ったタスクはネットワークアクセスが必要であるが Codex でネットワークが利用できないため、Claude Codeか手動での実行が必要となる
* 今後の未達成レビューや未完了修正、未完了修正の計画書はここで管理する

## 本ディレクトリのコンテンツ

本ディレクトリには、未達成レビューと未完了修正に直接関わる現行正本だけを残す。

- [未達成レビューと未完了修正](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_review_items.md)
- [未達成 URL レビュー実行メモ](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_url_review.md)
- [参照台帳](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/reference_registry.csv)
- [未完了修正一覧](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/master_issue_log.csv)
- [URL 到達性チェック結果](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/url_check.json)
  - 生データ。目的・実行方法・判定基準は `pending_url_review.md` を参照する

将来レビューを再開する場合は、この `docs/review/` に対して各チェック用スクリプトを再実行して成果物を再生成する。
