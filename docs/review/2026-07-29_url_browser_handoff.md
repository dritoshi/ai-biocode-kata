# URLブラウザ確認引き継ぎ

## 位置付け

この文書は、ターミナル版Codexでは利用できなかった実ブラウザ表示の確認を、ChatGPTアプリへ任意に引き継ぐための資料である。原稿URL監査の必須修正は完了しており、確認できなくてもリリースを妨げない。

## 優先確認

### `https://researchmap.jp/dritoshi`

- 出現箇所: `chapters/author.md:17`
- 用途: 著者のresearchmapプロフィール
- 機械結果: HTTP 403
- 検索サービス結果: 取得不能
- 確認事項:
  1. 著者プロフィールが表示されること
  2. 表示名と著者が一致すること
  3. サインイン要求、削除済み表示、別人物への転送がないこと

確認できた場合は `manual_confirmed`、表示できない場合や別人物の場合は `manual_review_required` と記録する。

## 任意の再確認

以下は一次情報または過去の手動確認で有効性を確認済みだが、HTTP検査ではanti-botまたは接続エラーになったURLである。

### 名前空間・論文

- `http://www.w3.org/2000/01/rdf-schema#`
  - `chapters/19_database_api.md:129,429`
  - RDF Schema名前空間であり、HTMLページではなくRDF/Turtleが返る場合がある
- `https://doi.org/10.1093/comjnl/27.2.97`
  - `chapters/18_documentation.md:191,693`
  - `references/ch18.bib:23`
- `https://doi.org/10.1145/3287560.3287596`
  - `chapters/18_documentation.md:443,705`
  - `references/ch18.bib:67`
- `https://doi.org/10.1162/tacl_a_00638`
  - `chapters/00_ai_agent.md:650,1059`
  - `references/ch00.bib:41`

### 公式文書・サービス

- `https://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-083.html`
  - `chapters/20_security_ethics.md:701,888`
  - `references/ch20.bib:235`
- `https://grants.nih.gov/policy-and-compliance/policy-topics/sharing-policies/gds`
  - `chapters/20_security_ethics.md:703,890`
  - `references/ch20.bib:243`
- `https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/`
  - `chapters/03_cs_basics.md:30,836,855`
  - `references/ch03.bib:15`
- `https://rsync.samba.org/tech_report/`
  - `chapters/16_hpc.md:390,821`
  - `references/ch16.bib:34`
- `https://www.biostars.org/`
  - `chapters/21_collaboration.md:136,155,238,878`
  - `references/ch21.bib:13`
- `https://www.collinsdictionary.com/us/woty/`
  - `chapters/hajimeni.md:18,152`
  - `references/hajimeni.bib:94`
- `https://www.hhs.gov/hipaa/for-professionals/faq/2075/may-a-hipaa-covered-entity-or-business-associate-use-cloud-service-to-store-or-process-ephi/index.html`
  - `chapters/20_security_ethics.md:371,846`
  - `references/ch20.bib:131`
- `https://zenodo.org/`
  - `chapters/07_git.md:333,647`
  - `references/ch07.bib:54`

### 手動修正済み

- `https://github.com/selfteaching/How-To-Ask-Questions-The-Smart-Way/blob/master/How-To-Ask-Questions-The-Smart-Way.md`
  - `chapters/21_collaboration.md:866`
  - `references/ch21.bib:80`
  - 旧URL `https://www.catb.org/~esr/faqs/smart-questions.html` から修正し、ユーザーの手動確認により有効性を確認した

### 接続タイムアウト

- `https://www.catb.org/~esr/writings/taoup/html/`
  - `chapters/01_design.md:200,430,448`
  - `chapters/11_cli.md:389,405,1111,1144`
  - `references/ch01.bib:23`
  - `references/ch11.bib:86`
- `https://www.gnu.org/software/bash/manual/`
  - `chapters/02_terminal.md:551,836`
  - `references/ch02.bib:54`
- `https://www.gnu.org/software/coreutils/manual/`
  - `chapters/02_terminal.md:347,834`
  - `references/ch02.bib:47`

## ChatGPTアプリへの依頼文

> 「`docs/review/2026-07-29_url_browser_handoff.md` に従い、まず `https://researchmap.jp/dritoshi` をブラウザで確認してください。ページタイトル、最終URL、著者プロフィールとの一致、ログイン・削除・別人物への転送の有無を記録し、`manual_confirmed` または `manual_review_required` を判定してください。任意確認リストは、時間に余裕がある場合だけ同じ形式で確認してください。原稿本文は変更せず、結果だけを `docs/review/2026-07-29_url_browser_results.md` に保存してください。」
