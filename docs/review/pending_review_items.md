# 未達成レビューと未完了修正

2026-03-26 時点で本文レビュー、URL 到達性チェック、統合後に残っていた manual issue の修正は完了した。2026-07-29に、追加の品質改善としてAIエージェントの不自然な用語生成を抑える指示設計を実装し、レビューと検証を完了した。

## 進行中のレビュー

- なし

## 完了済みレビュー

- 2026-07-29に[AIエージェントの不自然な用語生成を抑える指示設計](./2026-07-29_agent_language_prompt_plan.md)を実装した。差分レビュー2回目でfinding 0件、構造・相互参照・CI相当の検証・EPUBCheckが成功した。
- 2026-07-29の原稿URL監査では440 URLを再検査し、`error = 0`, `timeout = 0` となった。`anti-bot` と `connection_error` は一次情報・過去の手動確認・別経路の取得結果で有効性を確認した。著者researchmapページ1件は[任意のブラウザ確認](./2026-07-29_url_browser_handoff.md)へ引き継いだが、原稿修正の必須残件ではない。詳細は[監査記録](./2026-07-29_url_audit.md)を参照。

## 未完了修正

- 本レビュー台帳上の未完了修正はない。AIエージェントの不自然な用語生成を抑える指示設計と、`MANUAL-0006` 〜 `MANUAL-0009` は次の対応で解消した。
- [§0-3](../../chapters/00_ai_agent.md#回答の言葉遣いを指定する)と[付録D D-5](../../chapters/appendix_d_agent_vocabulary.md#d-5-不自然な用語を減らす指示)に、ジャーゴンや不自然な訳語を減らす指示と人間による確認方法を追加した
- [error_handling.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch10/error_handling.py) の FASTA 事前検証を追加し、`BiopythonDeprecationWarning` を解消した
- [test_mylib_core.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch05/test_mylib_core.py) を追加し、[core.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch05/mylib/core.py) の個別テストを整備した
- [test_mylib_utils.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch05/test_mylib_utils.py) を追加し、[utils.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch05/mylib/utils.py) の個別テストを整備した
- [test_cli_argparse.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch11/test_cli_argparse.py) を追加し、[cli_argparse.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch11/cli_argparse.py) の個別テストを整備した

## 関連資料

- URL 到達性レビュー実行メモ: [pending_url_review.md](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_url_review.md)
- アーカイブ済みレビュー台帳: [docs_review](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/archive/review-2026-03-25/docs_review/README.md)
- 旧スナップショット: [review_results](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/archive/review-2026-03-25/review_results)
