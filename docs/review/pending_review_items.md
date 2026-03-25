# 未達成レビューと未完了修正

2026-03-25 時点で本文レビュー、URL 到達性レビュー、出版前優先の外部参照修正は完了した。以下は未完了のまま残している。

## 未達成レビュー

- なし。2026-03-25 にネットワーク制限のない環境で URL チェックを再実行し、現行 [url_check.json](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/url_check.json) で `error` / `timeout` / `connection_error` が 0 件であることを確認した。`anti-bot = 39` はサイト側制限として扱い、追加 issue は起票していない。

## 未完了修正

未完了項目の正本は [master_issue_log.csv](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/master_issue_log.csv) である。要点は次のとおり。

### B: 品質維持のために対応したい項目

- `MANUAL-0006` [test_error_handling.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch10/test_error_handling.py): `BiopythonDeprecationWarning` を解消するか、受容理由を明文化する

### C: テスト方針を決めて閉じたい項目

- `MANUAL-0007` [core.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch05/mylib/core.py): 個別テストを追加するか、間接カバーで十分と判断して閉じる
- `MANUAL-0008` [utils.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch05/mylib/utils.py): 個別テストを追加するか、間接カバーで十分と判断して閉じる
- `MANUAL-0009` [cli_argparse.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch11/cli_argparse.py): 最小テストを追加するか、教育用デモとして対象外と明記して閉じる

## 関連資料

- URL 到達性レビュー実行メモ: [pending_url_review.md](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_url_review.md)
- アーカイブ済みレビュー台帳: [docs_review](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/archive/review-2026-03-25/docs_review/README.md)
- 旧スナップショット: [review_results](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/archive/review-2026-03-25/review_results)
