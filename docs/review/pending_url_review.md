# URL 到達性レビュー実行メモ

## 目的

このレビューの目的は、`chapters/*.md` と `references/*.bib` に含まれる外部 URL の最終到達性を確認し、本文や参考文献に残っている古い URL や無効 URL を修正対象として特定することである。2026-03-25 に再実行と修正を完了し、本メモは実行記録として残す。

`connection_error` は本文の誤りと同義ではない。実行環境のネットワーク制限、DNS 解決失敗、ファイアウォール、レート制限回避設定の不足でも発生しうるため、実 URL の問題かどうかは別環境での再確認が必要である。

## 現在の状態

- 現行の生データは [url_check.json](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/url_check.json) にある
- 2026-03-25 の最終結果は `summary.ok = 225`, `summary.anti-bot = 39` であり、`error` / `timeout` / `connection_error` は 0 件である
- 404 だった旧 URL は本文・参考文献側で修正済みであり、URL 到達性レビューは完了済みである

## 実行方法

再実行時は、ネットワーク制限のない環境でプロジェクトルートから次を実行する。

```bash
python3 scripts/review/check_urls_all.py
```

## 入力と出力

- 入力:
  - `chapters/*.md`
  - `references/*.bib`
- 出力:
  - `docs/review/url_check.json`

`url_check.json` の主要フィールドは次のとおり。

- `metadata.timestamp`: 実行時刻
- `metadata.total_unique_urls`: 一意 URL 数
- `metadata.total_occurrences`: URL 出現総数
- `summary`: カテゴリ別件数
- `urls[].category`: 判定カテゴリ
- `urls[].status_code`: HTTP ステータスコード
- `urls[].error`: 例外メッセージ
- `urls[].final_url`: リダイレクト先
- `urls[].locations`: 出現箇所の一覧

## 判定基準

- `ok`
  - 通常は対応不要
- `redirect`
  - 自動転送先が妥当なら対応不要。必要に応じて本文や `.bib` を最終 URL に更新する
- `anti-bot`
  - そのまま issue 化しない。サイト側制限の可能性が高いので、ブラウザ確認や別手段で再確認する
- `connection_error`
  - 実行環境依存の可能性があるため、そのまま issue 化しない。ネットワーク制限のない環境で再実行してから判断する
- `error`
  - 無効 URL、構造変更、404/410 などの可能性がある。本文または参考文献修正候補として優先確認する
- `timeout`
  - 一時的障害か恒久的問題かを切り分けるため、再実行後も継続するものを確認対象にする

## 今回更新したファイル

- [url_check.json](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/url_check.json)
- [master_issue_log.csv](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/master_issue_log.csv)
  - `MANUAL-0001` から `MANUAL-0005` を解消し、残件を B/C のみとした
- [reference_registry.csv](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/reference_registry.csv)
  - 修正後の参照先に再生成した
- [pending_review_items.md](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_review_items.md)
  - URL 到達性レビューを未達成項目から外した

## 完了条件

- ネットワーク制限のない環境で `check_urls_all.py` を再実行済みである
- `error` / `timeout` / `connection_error` が 0 件である
- 404 だった旧 URL を本文または参考文献で修正済みである
- [pending_review_items.md](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_review_items.md) から URL 到達性レビューを未達成項目として外した
