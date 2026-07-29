# 未達成レビューと未完了修正

2026-03-26 時点で本文レビュー、URL 到達性チェック、統合後に残っていた manual issue の修正は完了した。2026-07-29から、追加の品質改善としてAIエージェントの不自然な用語生成を抑える指示設計のレビューを進める。

## 進行中のレビュー

- [AIエージェントの不自然な用語生成を抑える指示設計計画](./2026-07-29_agent_language_prompt_plan.md)

## 完了済みレビュー

- 2026-07-29の原稿URL監査では440 URLを再検査し、`error = 0`, `timeout = 0` となった。`anti-bot` と `connection_error` は一次情報・過去の手動確認・別経路の取得結果で有効性を確認した。著者researchmapページ1件は[任意のブラウザ確認](./2026-07-29_url_browser_handoff.md)へ引き継いだが、原稿修正の必須残件ではない。詳細は[監査記録](./2026-07-29_url_audit.md)を参照。

## 未完了修正

- AIエージェントの不自然な用語生成を抑える指示設計は計画レビュー中である。それ以外の未完了修正はない。`MANUAL-0006` 〜 `MANUAL-0009` は次の対応で解消した。
- [error_handling.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch10/error_handling.py) の FASTA 事前検証を追加し、`BiopythonDeprecationWarning` を解消した
- [test_mylib_core.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch05/test_mylib_core.py) を追加し、[core.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch05/mylib/core.py) の個別テストを整備した
- [test_mylib_utils.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch05/test_mylib_utils.py) を追加し、[utils.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch05/mylib/utils.py) の個別テストを整備した
- [test_cli_argparse.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch11/test_cli_argparse.py) を追加し、[cli_argparse.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch11/cli_argparse.py) の個別テストを整備した

## 関連資料

- URL 到達性レビュー実行メモ: [pending_url_review.md](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_url_review.md)
- アーカイブ済みレビュー台帳: [docs_review](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/archive/review-2026-03-25/docs_review/README.md)
- 旧スナップショット: [review_results](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/archive/review-2026-03-25/review_results)
