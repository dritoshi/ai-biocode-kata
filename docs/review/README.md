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
* 2026-03-25 にネットワーク制限のない環境で URL 到達性チェックを再実行し、`error` / `timeout` / `connection_error` が 0 件であることを確認した
* 現在の残課題は、B/C の手作業修正とテスト方針の判断のみである

## 本ディレクトリのコンテンツ

本ディレクトリには、未達成レビューと未完了修正に直接関わる現行正本だけを残す。

- [未達成レビューと未完了修正](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_review_items.md)
- [URL 到達性レビュー実行メモ](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_url_review.md)
- [参照台帳](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/reference_registry.csv)
- [未完了修正一覧](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/master_issue_log.csv)
- [URL 到達性チェック結果](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/url_check.json)
  - 生データ。目的・実行方法・判定基準は `pending_url_review.md` を参照する

将来レビューを再開する場合は、この `docs/review/` に対して各チェック用スクリプトを再実行して成果物を再生成する。
