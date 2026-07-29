# 未達成レビューと未完了修正

2026-03-26 時点で本文レビュー、URL 到達性チェック、統合後に残っていた manual issue の修正は完了した。2026-07-29に、追加の品質改善としてAIエージェントの不自然な用語生成を抑える指示設計を実装し、レビューと検証を完了した。最終同期では、本文に掲載済みの参考URLと BibTeX 台帳の同期候補26件を新たに記録した。

## 進行中のレビュー

- 本文・参考文献の内容レビューはない
- 書誌正規化の後続候補として、`chapter_reference_missing_in_bib` 26件を[未完了修正一覧](./master_issue_log.csv)で管理する。これらはリンク切れや引用欠落ではなく、現行の参考文献リンクは利用できる

## 完了済みレビュー

- 2026-07-29に[AIエージェントの不自然な用語生成を抑える指示設計](./2026-07-29_agent_language_prompt_plan.md)を実装した。差分レビュー2回目でfinding 0件、構造・相互参照・CI相当の検証・EPUBCheckが成功した。
- 2026-07-29の最終URL監査では446 URL、1,370出現箇所を再検査し、`ok = 416`, `redirect = 1`, `anti-bot = 26`, `connection_error = 3`, `error = 0`, `timeout = 0` となった。`anti-bot` と `connection_error` はHTTP到達性の生データであり、[運用ポリシー](./pending_url_review.md#今後の運用ポリシー2026-03-26-更新)に従って扱う。
- 31原稿について構造・相互参照の問題がないことを確認した。コード対応は分類済みの正本 `code_correspondence.json` で管理し、旧方式の `code_sync_check.json` が示す59件の棚卸し候補を未解消の E3/E5 とは数えない。

## 未完了修正

- 本文修正の未完了項目はない。書誌正規化の候補26件は別管理とする。AIエージェントの不自然な用語生成を抑える指示設計と、`MANUAL-0006` 〜 `MANUAL-0009` は次の対応で解消した。
- [§0-3](../../chapters/00_ai_agent.md#回答の言葉遣いを指定する)と[付録D D-5](../../chapters/appendix_d_agent_vocabulary.md#d-5-不自然な用語を減らす指示)に、ジャーゴンや不自然な訳語を減らす指示と人間による確認方法を追加した
- [error_handling.py](../../scripts/ch10/error_handling.py) の FASTA 事前検証を追加し、`BiopythonDeprecationWarning` を解消した
- [test_mylib_core.py](../../tests/ch05/test_mylib_core.py) を追加し、[core.py](../../scripts/ch05/mylib/core.py) の個別テストを整備した
- [test_mylib_utils.py](../../tests/ch05/test_mylib_utils.py) を追加し、[utils.py](../../scripts/ch05/mylib/utils.py) の個別テストを整備した
- [test_cli_argparse.py](../../tests/ch11/test_cli_argparse.py) を追加し、[cli_argparse.py](../../scripts/ch11/cli_argparse.py) の個別テストを整備した

## 関連資料

- URL 到達性レビュー実行メモ: [pending_url_review.md](./pending_url_review.md)
- アーカイブ済みレビュー台帳: [docs_review](../archive/review-2026-03-25/docs_review/README.md)
- 旧スナップショット: [review_results](../archive/review-2026-03-25/review_results)
