# 未達成 URL レビュー実行メモ

## 目的

このレビューの目的は、`chapters/*.md` と `references/*.bib` に含まれる外部 URL の最終到達性を確認し、本文や参考文献に残っている古い URL や無効 URL を修正対象として特定することである。

`connection_error` は本文の誤りと同義ではない。実行環境のネットワーク制限、DNS 解決失敗、ファイアウォール、レート制限回避設定の不足でも発生しうるため、実 URL の問題かどうかは別環境での再確認が必要である。

## 現在の状態

- 現行の生データは [url_check.json](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/url_check.json) にある
- 2026-03-25 時点の結果は `summary.connection_error = 266`
- したがって、このレビューは「未実行」ではなく「実行済みだが、ネットワーク制限のため最終判定未確定」である

## 実行方法

ネットワーク制限のない環境で、プロジェクトルートから次を実行する。

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

## 再実行後に更新するファイル

- [url_check.json](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/url_check.json)
- [master_issue_log.csv](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/master_issue_log.csv)
  - `error` / `timeout` を中心に、修正が必要なものを起票またはクローズする
- [reference_registry.csv](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/reference_registry.csv)
  - 必要に応じて参照箇所の特定に使う
- [pending_review_items.md](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_review_items.md)
  - 未達成レビューの節を更新または削除する

## 完了条件

- ネットワーク制限のない環境で `check_urls_all.py` を再実行済みである
- `error` / `timeout` を確認し、必要なものを本文修正または issue 化済みである
- `connection_error` が環境要因か URL 問題か切り分け済みである
- [pending_review_items.md](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_review_items.md) から URL 到達性レビューを未達成項目として外せる状態になっている
