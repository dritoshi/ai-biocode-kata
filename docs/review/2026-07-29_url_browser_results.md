# URLブラウザ確認結果

- 確認日: 2026-07-29
- 確認方法: Codexアプリ内ブラウザで対象URLを直接表示
- 判定基準:
  - `manual_confirmed`: 対象ページを表示でき、URLの用途との一致を確認できた
  - `manual_review_required`: ページを表示できない、またはセキュリティ確認画面などに阻まれ、用途との一致を確認できなかった

## 優先確認

### `https://researchmap.jp/dritoshi`

- ページタイトル: `二階堂 愛 (Itoshi NIKAIDO) - マイポータル - researchmap`
- 最終URL: `https://researchmap.jp/dritoshi`
- 著者プロフィールとの一致: 一致。表示名「二階堂 愛」「Itoshi NIKAIDO」、東京科学大学教授・理化学研究所チームディレクターという所属、博士（理学）、ORCID `0000-0002-7261-2570`が`chapters/author.md`の著者情報と一致した
- ログイン要求: なし。ヘッダーにログインリンクはあるが、プロフィールは未ログインで表示された
- 削除済み表示: なし
- 別人物への転送: なし
- 判定: `manual_confirmed`

## 任意の再確認

### 名前空間・論文

#### `http://www.w3.org/2000/01/rdf-schema#`

- ページタイトル: 取得不能
- 最終URL: 取得不能（ブラウザが`ERR_BLOCKED_BY_CLIENT`で表示を中止）
- 用途との一致: 確認不能
- ログイン要求: 確認不能
- 削除済み表示: 確認不能
- 別ページへの転送: 確認不能
- 判定: `manual_review_required`

#### `https://doi.org/10.1093/comjnl/27.2.97`

- ページタイトル: `Literate Programming | The Computer Journal | Oxford Academic`
- 最終URL: `https://academic.oup.com/comjnl/article-abstract/27/2/97/343244?redirectedFrom=fulltext`
- 用途との一致: 一致。D. E. Knuthの論文「Literate Programming」の書誌情報と抄録が表示された
- ログイン要求: 書誌情報と抄録の確認にはなし。本文アクセス用のサインイン・購入案内は表示された
- 削除済み表示: なし
- 別ページへの転送: DOIから出版社の該当論文ページへの正常な転送のみ
- 判定: `manual_confirmed`

#### `https://doi.org/10.1145/3287560.3287596`

- ページタイトル: `しばらくお待ちください...`
- 最終URL: `https://dl.acm.org/doi/10.1145/3287560.3287596`
- 用途との一致: Cloudflareのセキュリティ検証画面のため確認不能
- ログイン要求: なし。セキュリティ検証で停止
- 削除済み表示: 確認不能
- 別ページへの転送: DOIからACM Digital Libraryの同一DOIページへの転送は確認したが、論文本文は確認不能
- 判定: `manual_review_required`

#### `https://doi.org/10.1162/tacl_a_00638`

- ページタイトル: `Lost in the Middle: How Language Models Use Long Contexts | Transactions of the Association for Computational Linguistics | MIT Press`
- 最終URL: `https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00638/119630/Lost-in-the-Middle-How-Language-Models-Use-Long`
- 用途との一致: 一致。論文「Lost in the Middle: How Language Models Use Long Contexts」が表示された
- ログイン要求: なし。オープンアクセス本文を表示
- 削除済み表示: なし
- 別ページへの転送: DOIからMIT Pressの該当論文ページへの正常な転送のみ
- 判定: `manual_confirmed`

### 公式文書・サービス

#### `https://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-083.html`

- ページタイトル: `Just a moment...`
- 最終URL: 指定URLにCloudflareの検証用クエリが付加されたURL
- 用途との一致: セキュリティ検証画面のため確認不能
- ログイン要求: なし。セキュリティ検証で停止
- 削除済み表示: 確認不能
- 別ページへの転送: 確認不能
- 判定: `manual_review_required`

#### `https://grants.nih.gov/policy-and-compliance/policy-topics/sharing-policies/gds`

- ページタイトル: `Just a moment...`
- 最終URL: 指定URLにCloudflareの検証用クエリが付加されたURL
- 用途との一致: セキュリティ検証画面のため確認不能
- ログイン要求: なし。セキュリティ検証で停止
- 削除済み表示: 確認不能
- 別ページへの転送: 確認不能
- 判定: `manual_review_required`

#### `https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/`

- ページタイトル: `Introduction to Algorithms`
- 最終URL: `https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/`
- 用途との一致: タイトルとメタデータは書籍「Introduction to Algorithms」と一致したが、ナビゲーションがタイムアウトし、ページ本文は表示できなかった
- ログイン要求: 確認不能
- 削除済み表示: 確認不能
- 別ページへの転送: なし
- 判定: `manual_review_required`

#### `https://rsync.samba.org/tech_report/`

- ページタイトル: `The rsync algorithm`
- 最終URL: `https://rsync.samba.org/tech_report/`
- 用途との一致: 一致。Andrew TridgellとPaul Mackerrasによるrsyncアルゴリズムの技術報告が表示された
- ログイン要求: なし
- 削除済み表示: なし
- 別ページへの転送: なし
- 判定: `manual_confirmed`

#### `https://www.biostars.org/`

- ページタイトル: `Just a moment...`
- 最終URL: 指定URLにCloudflareの検証用クエリが付加されたURL
- 用途との一致: セキュリティ検証画面のため確認不能
- ログイン要求: なし。セキュリティ検証で停止
- 削除済み表示: 確認不能
- 別ページへの転送: 確認不能
- 判定: `manual_review_required`

#### `https://www.collinsdictionary.com/us/woty/`

- ページタイトル: `しばらくお待ちください...`
- 最終URL: `https://www.collinsdictionary.com/us/woty/`
- 用途との一致: Cloudflareのセキュリティ検証画面のため確認不能
- ログイン要求: なし。セキュリティ検証で停止
- 削除済み表示: 確認不能
- 別ページへの転送: なし
- 判定: `manual_review_required`

#### `https://www.hhs.gov/hipaa/for-professionals/faq/2075/may-a-hipaa-covered-entity-or-business-associate-use-cloud-service-to-store-or-process-ephi/index.html`

- ページタイトル: `May a HIPAA covered entity or business associate use a cloud service to store or process ePHI? | HHS.gov`
- 最終URL: 指定URLと同一
- 用途との一致: 一致。HHSの該当HIPAA FAQと回答が表示された
- ログイン要求: なし
- 削除済み表示: なし
- 別ページへの転送: なし
- 判定: `manual_confirmed`

#### `https://zenodo.org/`

- ページタイトル: `Zenodo`
- 最終URL: `https://zenodo.org/`
- 用途との一致: 一致。Zenodoのホームページ、注目コミュニティ、最近のアップロードが表示された
- ログイン要求: なし
- 削除済み表示: なし
- 別ページへの転送: なし
- 判定: `manual_confirmed`

### 接続タイムアウト

#### `https://www.catb.org/~esr/faqs/smart-questions.html`

- ページタイトル: 取得不能
- 最終URL: 指定URLへの移動を開始したが、接続タイムアウト
- 用途との一致: 確認不能
- ログイン要求: 確認不能
- 削除済み表示: 確認不能
- 別ページへの転送: 確認不能
- 判定: `manual_review_required`

#### `https://www.catb.org/~esr/writings/taoup/html/`

- ページタイトル: 取得不能
- 最終URL: 指定URLへの移動を開始したが、接続タイムアウト
- 用途との一致: 確認不能
- ログイン要求: 確認不能
- 削除済み表示: 確認不能
- 別ページへの転送: 確認不能
- 判定: `manual_review_required`

#### `https://www.gnu.org/software/bash/manual/`

- ページタイトル: 取得不能
- 最終URL: 指定URLへの移動を開始したが、接続タイムアウト
- 用途との一致: 確認不能
- ログイン要求: 確認不能
- 削除済み表示: 確認不能
- 別ページへの転送: 確認不能
- 判定: `manual_review_required`

#### `https://www.gnu.org/software/coreutils/manual/`

- ページタイトル: 取得不能
- 最終URL: 指定URLへの移動を開始したが、接続タイムアウト
- 用途との一致: 確認不能
- ログイン要求: 確認不能
- 削除済み表示: 確認不能
- 別ページへの転送: 確認不能
- 判定: `manual_review_required`
