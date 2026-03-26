# 未達成レビューと未完了修正

2026-03-26 時点で本文レビューと機械的な URL 到達性チェックは完了した。以下は未完了のまま残している。

## 未達成レビュー

- なし。現行 [url_check.json](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/url_check.json) は `summary.ok = 306`, `summary.anti-bot = 20` であり、`error` / `timeout` / `connection_error` は 0 件である。`anti-bot` 20 件のうち、非 DOI 系 8 件と PubMed に変換できない DOI 系 11 件は手動確認済みであり、`https://doi.org/10.1002/0471448354` はブラウザ再確認で到達確認済みである。したがって、URL 到達性レビューとしての残件はない。

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
