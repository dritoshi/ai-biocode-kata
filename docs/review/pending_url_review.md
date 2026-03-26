# URL 到達性レビュー実行メモ

## 目的

このレビューの目的は、`chapters/*.md` と `references/*.bib` に含まれる外部 URL の最終到達性を確認し、本文や参考文献に残っている古い URL や無効 URL を修正対象として特定することである。2026-03-25 と 2026-03-26 に再実行と修正を行い、本メモは実行記録として残す。

`connection_error` は本文の誤りと同義ではない。実行環境のネットワーク制限、DNS 解決失敗、ファイアウォール、レート制限回避設定の不足でも発生しうるため、実 URL の問題かどうかは別環境での再確認が必要である。

`anti-bot` については、HTTP チェックだけで確定できない場合がある。そのため、必要に応じてヘッドレスブラウザによる再確認を別手順で行う。

## 現在の状態

- 現行の生データは [url_check.json](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/url_check.json) にある
- 2026-03-26 の現行結果は `summary.ok = 306`, `summary.anti-bot = 20` であり、`error` / `timeout` / `connection_error` は 0 件である
- 2026-03-26 に Markdown のベタ書き URL も抽出対象に含めるよう修正し、現行原稿 326 URL を再チェックした
- DOI 直リンクで `anti-bot` になっていたバイオ系論文のうち、PubMed に PMID があるものは本文・参考文献の閲覧用リンクを PubMed に切り替えた
- 同日に `check_urls_browser.py` で `anti-bot` 21 件を再確認し、`browser_ok = 1`, `browser_blocked = 19`, `browser_error = 1` を記録した
- 2026-03-26 に非 DOI 系 `anti-bot` 8 件はユーザーが手動ブラウザ確認し、レビュー上の状態を `manual_confirmed` とした
- `https://doi.org/10.1002/0471448354` はブラウザ再確認で到達確認済みである
- 404 だった旧 URL と機械的 `error` は本文・参考文献側で修正済みであり、残件は手動確認待ち DOI のみである

## 今後の運用ポリシー（2026-03-26 更新）

- 原稿に出てこない文献・URL は、レビュー上 `unused_in_manuscript` とみなし、機械チェック・手動チェックの対象から外す
- 具体的には、原稿から削除済みの URL や、対応章本文に現れない `.bib` 項目に由来する URL は追跡しない
- DOI 系 URL は、まず PubMed へ変換できるかを確認し、PubMed 抄録ページへ置き換え可能ならそちらを採用する
- DOI 系 URL が PubMed に変換できない場合は、ヘッドレスブラウザ再確認で粘らず、手動確認フローへ進める
- 手動確認前の DOI 系残件は `manual_review_required`、確認後は `manual_confirmed` として扱う
- `manual_review_required` の一覧は、レビューしやすいように URL 単体ではなく、引用されているコンテキストと対応づけて出力する
- `url_check.json` と `url_check_browser.json` は生データであり、`unused_in_manuscript` や `manual_review_required` のようなレビュー運用上の状態は別途このメモで管理する

## 実行方法

再実行時は、ネットワーク制限のない環境でプロジェクトルートから次を実行する。

```bash
python3 scripts/review/check_urls_all.py
```

`anti-bot` の再確認が必要な場合は、追加で次を実行する。

```bash
.venv/bin/pip install -r scripts/review/requirements-browser.txt
.venv/bin/python -m playwright install chromium
python3 scripts/review/check_urls_browser.py
```

## 入力と出力

- 入力:
  - `chapters/*.md`
  - `references/*.bib`
- 出力:
  - `docs/review/url_check.json`
  - `docs/review/url_check_browser.json`（anti-bot をブラウザ再確認した場合）

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

`url_check_browser.json` の主要フィールドは次のとおり。

- `metadata.category_filter`: 再確認対象カテゴリ
- `metadata.total_checked`: ブラウザ再確認した URL 数
- `summary.browser_ok`: ブラウザでは到達できた件数
- `summary.browser_blocked`: ブラウザでも遮断画面だった件数
- `summary.browser_error`: タイトル取得不能や想定外応答で保留になった件数
- `urls[].source_url`: 元の anti-bot URL
- `urls[].final_url`: ブラウザ遷移後の最終 URL
- `urls[].page_title`: 取得できたページタイトル
- `urls[].body_preview`: 本文先頭の短い抜粋

## 判定基準

- `ok`
  - 通常は対応不要
- `redirect`
  - 自動転送先が妥当なら対応不要。必要に応じて本文や `.bib` を最終 URL に更新する
- `anti-bot`
  - そのまま issue 化しない。サイト側制限の可能性が高い
  - 非 DOI 系は `check_urls_browser.py` や手動ブラウザ確認で再確認し、確認できたものはレビュー上 `manual_confirmed` として閉じる
  - DOI 系は PubMed 変換を優先し、PubMed へ寄せられないものは `manual_review_required` として手動確認へ進める
- `connection_error`
  - 実行環境依存の可能性があるため、そのまま issue 化しない。ネットワーク制限のない環境で再実行してから判断する
- `error`
  - 無効 URL、構造変更、404/410 などの可能性がある。本文または参考文献修正候補として優先確認する
- `timeout`
  - 一時的障害か恒久的問題かを切り分けるため、再実行後も継続するものを確認対象にする
- `unused_in_manuscript`
  - 原稿に出てこないため確認不要。機械チェック・手動チェックともに行わない
- `manual_review_required`
  - DOI 系 `anti-bot` で PubMed 変換できなかったもの。以後は手動確認で処理する

## 手動確認リストの出力ルール

- `manual_review_required` を列挙するときは、少なくとも次を 1 組で対応づけて出力する
  - URL
  - 出現箇所（章ファイルと行番号）
  - 引用されているコンテキスト
- 引用コンテキストは、章本文の要約だけでなく、どの主張・推薦文献・参考文献項目に対応するかが分かる粒度で示す
- 同一 URL が複数箇所で使われている場合は、出現箇所ごとに分けるか、少なくとも全出現箇所を列挙する
- 手動確認結果を返すときも、`manual_confirmed` / `manual_review_required` の状態だけでなく、どの URL がどの文脈を確認したものかを対応づけて残す

## 今回更新したファイル

- [url_check.json](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/url_check.json)
- [url_check_browser.json](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/url_check_browser.json)
  - 生成は任意。`anti-bot` をブラウザで再確認した場合に保存する
- [master_issue_log.csv](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/master_issue_log.csv)
  - `MANUAL-0001` から `MANUAL-0005` を解消し、残件を B/C のみとした
- [reference_registry.csv](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/reference_registry.csv)
  - 修正後の参照先に再生成した
- [pending_review_items.md](/Users/itoshi/Projects/writing/ai-biocode-kata/docs/review/pending_review_items.md)
  - URL 到達性レビューを未達成項目から外した

## 手動確認ステータス

2026-03-26 に、以下の非 DOI 系 `anti-bot` URL はユーザーがブラウザで手動確認し、有効であることを確認した。これらはレビュー上 `manual_confirmed` として扱う。

- [https://dl.acm.org/doi/10.5555/2600239.2600241](https://dl.acm.org/doi/10.5555/2600239.2600241)
- [https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [https://rsync.samba.org/tech_report/](https://rsync.samba.org/tech_report/)
- [https://www.biostars.org/](https://www.biostars.org/)
- [https://www.forbes.com/sites/gilpress/2016/03/23/data-preparation-most-time-consuming-least-enjoyable-data-science-task-survey-says/](https://www.forbes.com/sites/gilpress/2016/03/23/data-preparation-most-time-consuming-least-enjoyable-data-science-task-survey-says/)
- [https://www.hhs.gov/hipaa/for-professionals/faq/2075/may-a-hipaa-covered-entity-or-business-associate-use-cloud-service-to-store-or-process-ephi/index.html](https://www.hhs.gov/hipaa/for-professionals/faq/2075/may-a-hipaa-covered-entity-or-business-associate-use-cloud-service-to-store-or-process-ephi/index.html)
- [https://x.com/karpathy/status/1886192184808149383](https://x.com/karpathy/status/1886192184808149383)
- [https://zenodo.org/](https://zenodo.org/)

`url_check.json` と `url_check_browser.json` は機械実行結果の生データなので、この手動確認ステータスは反映しない。

`https://doi.org/10.1002/0471448354` は `check_urls_browser.py` の再確認で `browser_ok` になっており、レビュー上は到達確認済みとして扱う。

## manual_review_required（0件・2026-03-26 時点）

手動確認待ちはない。PubMed へ変換できない DOI 系 11 件も、すでに URL と引用文脈を対応づけた一覧で手動確認済みである。以下は未完了タスクではなく、完了記録である。

## 手動確認完了記録（DOI 系 anti-bot）

以下の PubMed に変換できない DOI 系 `anti-bot` URL は、URL と引用文脈を対応づけた一覧をもとに手動確認済みであり、レビュー上 `manual_confirmed` として記録している。

- [https://doi.org/10.1093/comjnl/27.2.97](https://doi.org/10.1093/comjnl/27.2.97)
  出現箇所: `chapters/18_documentation.md:187`, `chapters/18_documentation.md:672`, `references/ch18.bib:23`
  文脈: 文芸的プログラミングの原典として引用している。Notebook や Quarto の思想的源流を説明する箇所と、章末の推薦文献に出現する。

- [https://doi.org/10.1142/S0218488502001648](https://doi.org/10.1142/S0218488502001648)
  出現箇所: `chapters/20_security_ethics.md:388`, `chapters/20_security_ethics.md:644`, `references/ch20.bib:87`
  文脈: `k`-匿名性の定義根拠として引用している。匿名化の説明本文と章末参考文献に出現する。

- [https://doi.org/10.1145/103162.103163](https://doi.org/10.1145/103162.103163)
  出現箇所: `chapters/03_cs_basics.md:267`, `chapters/03_cs_basics.md:813`, `chapters/03_cs_basics.md:823`, `references/ch03.bib:27`
  文脈: IEEE 754 浮動小数点の古典解説として引用している。本文の説明、補足、章末参考文献に出現する。

- [https://doi.org/10.1145/1465482.1465560](https://doi.org/10.1145/1465482.1465560)
  出現箇所: `chapters/17_performance.md:24`, `chapters/17_performance.md:1041`, `references/ch17.bib:21`
  文脈: Amdahl の法則の原典として引用している。章冒頭の説明と章末参考文献に出現する。

- [https://doi.org/10.1145/2643130](https://doi.org/10.1145/2643130)
  出現箇所: `chapters/16_hpc.md:720`, `references/ch16.bib:46`
  文脈: HPC 章の章末で挙げている補助文献 “The Network is Reliable” に対応する。

- [https://doi.org/10.1145/2723872.2723882](https://doi.org/10.1145/2723872.2723882)
  出現箇所: `chapters/15_container.md:1063`, `chapters/15_container.md:1089`, `references/ch15.bib:64`
  文脈: Docker を研究再現性に導入する先駆的論文として、章末の推薦文献と参考文献に出現する。

- [https://doi.org/10.1145/272991.272995](https://doi.org/10.1145/272991.272995)
  出現箇所: `chapters/03_cs_basics.md:462`, `chapters/03_cs_basics.md:831`, `references/ch03.bib:63`
  文脈: メルセンヌ・ツイスタの原典として引用している。乱数生成の説明本文と章末参考文献に出現する。

- [https://doi.org/10.1145/3287560.3287596](https://doi.org/10.1145/3287560.3287596)
  出現箇所: `chapters/18_documentation.md:422`, `chapters/18_documentation.md:684`, `references/ch18.bib:67`
  文脈: Model Card フレームワークの原典として引用している。ML コラム本文と章末参考文献に出現する。

- [https://doi.org/10.1145/3544548.3580919](https://doi.org/10.1145/3544548.3580919)
  出現箇所: `chapters/appendix_a_learning_patterns.md:85`, `references/appendix_a.bib:82`
  文脈: 付録 A の参考文献にある、AI コード生成が初学者学習に与える影響の論文である。

- [https://doi.org/10.1145/356635.356640](https://doi.org/10.1145/356635.356640)
  出現箇所: `chapters/17_performance.md:20`, `chapters/17_performance.md:1039`, `references/ch17.bib:11`
  文脈: 「時期尚早な最適化は諸悪の根源」の出典として引用している。章冒頭と章末参考文献に出現する。

- [https://doi.org/10.1162/tacl_a_00638](https://doi.org/10.1162/tacl_a_00638)
  出現箇所: `chapters/00_ai_agent.md:526`, `chapters/00_ai_agent.md:777`, `references/ch00.bib:41`
  文脈: 長いコンテキストでモデルが途中の情報を取りこぼす、という説明の根拠として引用している。本文と章末参考文献に出現する。

## 完了条件

- ネットワーク制限のない環境で `check_urls_all.py` を再実行済みである
- `error` / `timeout` / `connection_error` が 0 件である
- 404 だった旧 URL を本文または参考文献で修正済みである
- DOI 系 `manual_review_required` は 0 件である
