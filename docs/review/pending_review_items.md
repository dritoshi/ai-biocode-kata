# 未達成レビューと未完了修正

2026-03-25 時点で本文レビューと主要修正は完了したが、以下は未達成または未完了のまま残している。

## 未達成レビュー

### URL 到達性の最終確認

- 現行の URL チェック結果は [url_check.json](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/url_check.json) にある。
- 詳細な目的、実行方法、判定基準、完了条件は [pending_url_review.md](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_url_review.md) を参照する。
- ただし、実行環境のネットワーク制限により `connection_error = 266` となっており、外部 URL の最終到達性確認としては未完了である。

## 未完了修正

未完了項目の正本は [master_issue_log.csv](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/master_issue_log.csv) である。要点は次のとおり。

### A: 出版前に修正したい項目

- `MANUAL-0001` [references/ch04.bib](/Users/itoshi/Projects/writing/ai-biocode-kata/references/ch04.bib): CrowdFlower 2016 Data Science Report の旧 Figure Eight URL を現行参照先へ差し替える
- `MANUAL-0002` [16_hpc.md](/Users/itoshi/Projects/writing/ai-biocode-kata/chapters/16_hpc.md): Australian BioCommons HPC ガイドの旧 URL を現行ページまたは代替資料へ差し替える
- `MANUAL-0003` [references/ch16.bib](/Users/itoshi/Projects/writing/ai-biocode-kata/references/ch16.bib): CISA 参考文献を個別ページ URL に差し替える
- `MANUAL-0004` [references/ch16.bib](/Users/itoshi/Projects/writing/ai-biocode-kata/references/ch16.bib): Australian BioCommons の旧 URL を本文と合わせて更新する
- `MANUAL-0005` [references/ch17.bib](/Users/itoshi/Projects/writing/ai-biocode-kata/references/ch17.bib): `memory_profiler` の旧 GitHub URL を現行公開先へ差し替える

### B: 品質維持のために対応したい項目

- `MANUAL-0006` [test_error_handling.py](/Users/itoshi/Projects/writing/ai-biocode-kata/tests/ch10/test_error_handling.py): `BiopythonDeprecationWarning` を解消するか、受容理由を明文化する

### C: テスト方針を決めて閉じたい項目

- `MANUAL-0007` [core.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch05/mylib/core.py): 個別テストを追加するか、間接カバーで十分と判断して閉じる
- `MANUAL-0008` [utils.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch05/mylib/utils.py): 個別テストを追加するか、間接カバーで十分と判断して閉じる
- `MANUAL-0009` [cli_argparse.py](/Users/itoshi/Projects/writing/ai-biocode-kata/scripts/ch11/cli_argparse.py): 最小テストを追加するか、教育用デモとして対象外と明記して閉じる

## 関連資料

- アーカイブ済みレビュー台帳: [docs_review](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/archive/review-2026-03-25/docs_review/README.md)
- 旧スナップショット: [review_results](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/archive/review-2026-03-25/review_results)
