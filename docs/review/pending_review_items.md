# 未達成レビューと未完了修正

2026-03-26 時点で本文レビュー、URL 到達性チェック、統合後に残っていた manual issue の修正は完了した。現時点で未完了のレビュー・修正はない。

## 未達成レビュー

- なし。現行 [url_check.json](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/url_check.json) は `summary.ok = 306`, `summary.anti-bot = 20` であり、`error` / `timeout` / `connection_error` は 0 件である。`anti-bot` 20 件のうち、非 DOI 系 8 件と PubMed に変換できない DOI 系 11 件は手動確認済みであり、`https://doi.org/10.1002/0471448354` はブラウザ再確認で到達確認済みである。したがって、URL 到達性レビューとしての残件はない。

## 未完了修正

- なし。`MANUAL-0006` 〜 `MANUAL-0009` は次の対応で解消した。
- [error_handling.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch10/error_handling.py) の FASTA 事前検証を追加し、`BiopythonDeprecationWarning` を解消した
- [test_mylib_core.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch05/test_mylib_core.py) を追加し、[core.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch05/mylib/core.py) の個別テストを整備した
- [test_mylib_utils.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch05/test_mylib_utils.py) を追加し、[utils.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch05/mylib/utils.py) の個別テストを整備した
- [test_cli_argparse.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch11/test_cli_argparse.py) を追加し、[cli_argparse.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch11/cli_argparse.py) の個別テストを整備した

## 関連資料

- URL 到達性レビュー実行メモ: [pending_url_review.md](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_url_review.md)
- アーカイブ済みレビュー台帳: [docs_review](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/archive/review-2026-03-25/docs_review/README.md)
- 旧スナップショット: [review_results](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/archive/review-2026-03-25/review_results)
