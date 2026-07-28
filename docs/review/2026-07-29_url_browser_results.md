# URLブラウザ確認結果

- 確認日: 2026-07-29
- 確認方法: Codexアプリ内ブラウザで対象URLを直接表示
- 判定基準:
  - `manual_confirmed`: 対象ページを表示でき、URLの用途との一致を確認できた
  - `manual_review_required`: ページを表示できない、またはセキュリティ確認画面などに阻まれ、用途との一致を確認できなかった

## 優先確認

### [https://researchmap.jp/dritoshi](https://researchmap.jp/dritoshi)

- 原稿内の出現箇所: [著者紹介](../../chapters/author.md) 17行
- URL周辺の文章:

> - researchmap: https://researchmap.jp/dritoshi

- ページタイトル: `二階堂 愛 (Itoshi NIKAIDO) - マイポータル - researchmap`
- 最終URL: [https://researchmap.jp/dritoshi](https://researchmap.jp/dritoshi)
- 著者プロフィールとの一致: 一致。表示名「二階堂 愛」「Itoshi NIKAIDO」、東京科学大学教授・理化学研究所チームディレクターという所属、博士（理学）、ORCID `0000-0002-7261-2570`が`chapters/author.md`の著者情報と一致した
- ログイン要求: なし。ヘッダーにログインリンクはあるが、プロフィールは未ログインで表示された
- 削除済み表示: なし
- 別人物への転送: なし
- 判定: `manual_confirmed`

## 任意の再確認

### 名前空間・論文

#### [http://www.w3.org/2000/01/rdf-schema#](<http://www.w3.org/2000/01/rdf-schema#>)

- 原稿内の出現箇所: [§19 公共データベースとAPI](../../chapters/19_database_api.md) 129行・429行
- URL周辺の文章:

> `PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>`

2つのSPARQL例で同じ名前空間宣言を使用している。

- ページタイトル: 取得不能
- 最終URL: 取得不能（ブラウザが`ERR_BLOCKED_BY_CLIENT`で表示を中止）
- 用途との一致: ブラウザでは確認不能。ユーザーの手動確認では一致
- ログイン要求: 確認不能
- 削除済み表示: 確認不能
- 別ページへの転送: 確認不能
- 判定: `manual_confirmed`

#### [https://doi.org/10.1093/comjnl/27.2.97](https://doi.org/10.1093/comjnl/27.2.97)

- 原稿内の出現箇所: [§18 コードのドキュメント化](../../chapters/18_documentation.md) 191行・693行
- URL周辺の文章:

> **文芸的プログラミング**（Literate Programming）は、Donald Knuthが1984年に提唱したプログラミングのパラダイムである[3](https://doi.org/10.1093/comjnl/27.2.97)。従来の「コンピュータが実行するコードの中にコメントとしてドキュメントを埋め込む」アプローチを逆転させ、「人間が読むドキュメントの中にコードを埋め込む」という発想である。

- ページタイトル: `Literate Programming | The Computer Journal | Oxford Academic`
- 最終URL: [https://academic.oup.com/comjnl/article-abstract/27/2/97/343244?redirectedFrom=fulltext](https://academic.oup.com/comjnl/article-abstract/27/2/97/343244?redirectedFrom=fulltext)
- 用途との一致: 一致。D. E. Knuthの論文「Literate Programming」の書誌情報と抄録が表示された
- ログイン要求: 書誌情報と抄録の確認にはなし。本文アクセス用のサインイン・購入案内は表示された
- 削除済み表示: なし
- 別ページへの転送: DOIから出版社の該当論文ページへの正常な転送のみ
- 判定: `manual_confirmed`

#### [https://doi.org/10.1145/3287560.3287596](https://doi.org/10.1145/3287560.3287596)

- 原稿内の出現箇所: [§18 コードのドキュメント化](../../chapters/18_documentation.md) 443行・705行
- URL周辺の文章:

> 機械学習モデルを公開する際は、READMEに加えて**Model Card**の作成が推奨されている。Model Cardは、Mitchell et al. (2019)[9](https://doi.org/10.1145/3287560.3287596)が提唱したフレームワークで、モデルの以下の情報を体系的に記録する。

- ページタイトル: `しばらくお待ちください...`
- 最終URL: [https://dl.acm.org/doi/10.1145/3287560.3287596](https://dl.acm.org/doi/10.1145/3287560.3287596)
- 用途との一致: ブラウザではCloudflareのセキュリティ検証画面のため確認不能。ユーザーの手動確認では一致
- ログイン要求: なし。セキュリティ検証で停止
- 削除済み表示: 確認不能
- 別ページへの転送: DOIからACM Digital Libraryの同一DOIページへの転送は確認したが、論文本文は確認不能
- 判定: `manual_confirmed`

#### [https://doi.org/10.1162/tacl_a_00638](https://doi.org/10.1162/tacl_a_00638)

- 原稿内の出現箇所: [§0 AIエージェントにコードを書かせる](../../chapters/00_ai_agent.md) 650行・1059行
- BibTeX: [references/ch00.bib](../../references/ch00.bib) 41行
- URL周辺の文章:

> しかし実際には、コードの読み込み、エージェントの思考過程、ツール実行の結果などでコンテキストは急速に消費される。長いセッションでは、初期の指示を「忘れる」ことがある[4](https://doi.org/10.1162/tacl_a_00638)。これは、非常に長い会議で冒頭の議論内容が後半には忘れられるのに似ている。

- ページタイトル: `Lost in the Middle: How Language Models Use Long Contexts | Transactions of the Association for Computational Linguistics | MIT Press`
- 最終URL: [https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00638/119630/Lost-in-the-Middle-How-Language-Models-Use-Long](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00638/119630/Lost-in-the-Middle-How-Language-Models-Use-Long)
- 用途との一致: 一致。論文「Lost in the Middle: How Language Models Use Long Contexts」が表示された
- ログイン要求: なし。オープンアクセス本文を表示
- 削除済み表示: なし
- 別ページへの転送: DOIからMIT Pressの該当論文ページへの正常な転送のみ
- 判定: `manual_confirmed`

### 公式文書・サービス

#### [https://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-083.html](https://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-083.html)

- 原稿内の出現箇所: [§20 コードとデータのセキュリティ・倫理](../../chapters/20_security_ethics.md) 701行・888行
- BibTeX: [references/ch20.bib](../../references/ch20.bib) 235行
- URL周辺の文章:

> 海外の制限付きデータベースを利用する場合は、その資金機関のポリシーも確認する。とくに **NIH**（米国国立衛生研究所）は Data Management and Sharing (DMS) Policy と Genomic Data Sharing (GDS) Policy を持ち、dbGaP 等の管理アクセスデータを使う研究者に遵守を求める。近年は管理が段階的に厳格化されており、NOT-OD-25-083（2025年4月4日発効）は、懸念国に所在する機関による管理アクセスデータへのアクセスを**禁止**した（懸念国は中国・ロシア・イラン・北朝鮮・キューバ・ベネズエラ等）[37](https://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-083.html)。

- ページタイトル: `Just a moment...`
- 最終URL: 指定URLにCloudflareの検証用クエリが付加されたURL
- 用途との一致: ブラウザではセキュリティ検証画面のため確認不能。ユーザーの手動確認では一致
- ログイン要求: なし。セキュリティ検証で停止
- 削除済み表示: 確認不能
- 別ページへの転送: 確認不能
- 判定: `manual_confirmed`

#### [https://grants.nih.gov/policy-and-compliance/policy-topics/sharing-policies/gds](https://grants.nih.gov/policy-and-compliance/policy-topics/sharing-policies/gds)

- 原稿内の出現箇所: [§20 コードとデータのセキュリティ・倫理](../../chapters/20_security_ethics.md) 703行・890行
- BibTeX: [references/ch20.bib](../../references/ch20.bib) 243行
- URL周辺の文章:

> NIH は生成AIとの関係についても明確な指針を示している。管理アクセスデータやその派生データ（data derivatives）を公開の生成AIツールにプロンプトやアップロードで渡すことは**禁止**されており、そのデータで生成AIモデルを学習させるには NIH の承認が必要で、プロジェクト終了後はモデル（パラメータを含む）を保持してはならない[38](https://grants.nih.gov/policy-and-compliance/policy-topics/sharing-policies/gds)。これは[§20-2-1 ヒトデータの法規制と利用規約](../../chapters/20_security_ethics.md#20-2-1-ヒトデータの法規制と利用規約)で述べた「制限付きデータをクラウドAIに送信しない」原則が、単なる入力にとどまらず**モデルの学習・ファインチューニングにまで及ぶ**ことを意味する。

- ページタイトル: `Just a moment...`
- 最終URL: 指定URLにCloudflareの検証用クエリが付加されたURL
- 用途との一致: ブラウザではセキュリティ検証画面のため確認不能。ユーザーの手動確認では一致
- ログイン要求: なし。セキュリティ検証で停止
- 削除済み表示: 確認不能
- 別ページへの転送: 確認不能
- 判定: `manual_confirmed`

#### [https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)

- 原稿内の出現箇所: [§3 コーディングに必要な計算機科学](../../chapters/03_cs_basics.md) 30行・836行・855行
- BibTeX: [references/ch03.bib](../../references/ch03.bib) 15行
- URL周辺の文章:

> ここで登場する $O$ 記法（ビッグオー記法）は、入力サイズnに対して処理時間がどう増えるかを表す[2](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)。$O$ は "order of" の頭文字で、「オー」と読む。$O(n)$ なら「オーエヌ」、$O(n^2)$ なら「オーエヌの二乗」と発音する。

- ページタイトル: `Introduction to Algorithms`
- 最終URL: [https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- 用途との一致: タイトルとメタデータは書籍「Introduction to Algorithms」と一致した。ブラウザではページ本文を表示できなかったが、ユーザーの手動確認では一致
- ログイン要求: 確認不能
- 削除済み表示: 確認不能
- 別ページへの転送: なし
- 判定: `manual_confirmed`

#### [https://rsync.samba.org/tech_report/](https://rsync.samba.org/tech_report/)

- 原稿内の出現箇所: [§16 スパコン・クラスタでの大規模計算](../../chapters/16_hpc.md) 390行・821行
- BibTeX: [references/ch16.bib](../../references/ch16.bib) 34行
- URL周辺の文章:

> ローカルPCとHPC間のデータ転送には `rsync` が最適である。`scp` も使えるが、rsyncには以下の利点がある[3](https://rsync.samba.org/tech_report/)。

- ページタイトル: `The rsync algorithm`
- 最終URL: [https://rsync.samba.org/tech_report/](https://rsync.samba.org/tech_report/)
- 用途との一致: 一致。Andrew TridgellとPaul Mackerrasによるrsyncアルゴリズムの技術報告が表示された
- ログイン要求: なし
- 削除済み表示: なし
- 別ページへの転送: なし
- 判定: `manual_confirmed`

#### [https://www.biostars.org/](https://www.biostars.org/)

- 原稿内の出現箇所: [§21 共同開発の実践](../../chapters/21_collaboration.md) 136行・155行・238行・878行
- BibTeX: [references/ch21.bib](../../references/ch21.bib) 13行
- URL周辺の文章:

> Biostars[2](https://www.biostars.org/)はバイオインフォマティクス専門のQ&Aサイトである。ゲノム解析ツールの使い方、パイプラインの設計、データフォーマットの問題に特化している。

- ページタイトル: `Just a moment...`
- 最終URL: 指定URLにCloudflareの検証用クエリが付加されたURL
- 用途との一致: ブラウザではセキュリティ検証画面のため確認不能。ユーザーの手動確認では一致
- ログイン要求: なし。セキュリティ検証で停止
- 削除済み表示: 確認不能
- 別ページへの転送: 確認不能
- 判定: `manual_confirmed`

#### [https://www.collinsdictionary.com/us/woty/](https://www.collinsdictionary.com/us/woty/)

- 原稿内の出現箇所: [はじめに](../../chapters/hajimeni.md) 18行・152行
- BibTeX: [references/hajimeni.bib](../../references/hajimeni.bib) 94行
- URL周辺の文章:

> Andrej Karpathyはこの新しいプログラミングスタイルを**Vibe coding**（バイブコーディング）と名付けた[10](https://x.com/karpathy/status/1886192184808149383)。ソースコードを直接読み書きせず、自然言語でAIに指示を出し、生成されたコードの差分すら確認せず結果だけを見て判断する——「コードが存在することすら忘れる」手法である。この用語は瞬く間に広まり、2025年11月にはCollins Dictionaryの Word of the Year にも選ばれた[11](https://www.collinsdictionary.com/us/woty/)。

- ページタイトル: `しばらくお待ちください...`
- 最終URL: [https://www.collinsdictionary.com/us/woty/](https://www.collinsdictionary.com/us/woty/)
- 用途との一致: ブラウザではCloudflareのセキュリティ検証画面のため確認不能。ユーザーの手動確認では一致
- ログイン要求: なし。セキュリティ検証で停止
- 削除済み表示: 確認不能
- 別ページへの転送: なし
- 判定: `manual_confirmed`

#### [https://www.hhs.gov/hipaa/for-professionals/faq/2075/may-a-hipaa-covered-entity-or-business-associate-use-cloud-service-to-store-or-process-ephi/index.html](https://www.hhs.gov/hipaa/for-professionals/faq/2075/may-a-hipaa-covered-entity-or-business-associate-use-cloud-service-to-store-or-process-ephi/index.html)

- 原稿内の出現箇所: [§20 コードとデータのセキュリティ・倫理](../../chapters/20_security_ethics.md) 371行・846行
- BibTeX: [references/ch20.bib](../../references/ch20.bib) 131行
- URL周辺の文章:

> 外部クラウドやAIサービスに ePHI を渡す場合は、Business Associate 該当性と BAA の要否を事前確認する[16](https://www.hhs.gov/hipaa/for-professionals/faq/2075/may-a-hipaa-covered-entity-or-business-associate-use-cloud-service-to-store-or-process-ephi/index.html)。

- ページタイトル: `May a HIPAA covered entity or business associate use a cloud service to store or process ePHI? | HHS.gov`
- 最終URL: 指定URLと同一
- 用途との一致: 一致。HHSの該当HIPAA FAQと回答が表示された
- ログイン要求: なし
- 削除済み表示: なし
- 別ページへの転送: なし
- 判定: `manual_confirmed`

#### [https://zenodo.org/](https://zenodo.org/)

- 原稿内の出現箇所: [§7 Git入門](../../chapters/07_git.md) 333行・647行
- BibTeX: [references/ch07.bib](../../references/ch07.bib) 54行
- URL周辺の文章:

> **Zenodo連携** [7](https://zenodo.org/) — ZenodoはCERNが運営するデータリポジトリで、GitHubと連携してDOI（デジタルオブジェクト識別子。[§4 データフォーマットの選び方](../../chapters/04_data_formats.md)でも解説）を自動発行できる。手順は3ステップである。

- ページタイトル: `Zenodo`
- 最終URL: [https://zenodo.org/](https://zenodo.org/)
- 用途との一致: 一致。Zenodoのホームページ、注目コミュニティ、最近のアップロードが表示された
- ログイン要求: なし
- 削除済み表示: なし
- 別ページへの転送: なし
- 判定: `manual_confirmed`

### 手動修正

#### [https://github.com/selfteaching/How-To-Ask-Questions-The-Smart-Way/blob/master/How-To-Ask-Questions-The-Smart-Way.md](https://github.com/selfteaching/How-To-Ask-Questions-The-Smart-Way/blob/master/How-To-Ask-Questions-The-Smart-Way.md)

- 原稿内の出現箇所: [§21 共同開発の実践](../../chapters/21_collaboration.md) 866行
- BibTeX: [references/ch21.bib](../../references/ch21.bib) 80行
- URL周辺の文章:

> **Raymond, E. S. "How To Ask Questions The Smart Way". 2014.** [How-To-Ask-Questions-The-Smart-Way.md](https://github.com/selfteaching/How-To-Ask-Questions-The-Smart-Way/blob/master/How-To-Ask-Questions-The-Smart-Way.md) — 技術コミュニティでの質問の作法の原典。本章で扱った「良い質問の構造」の背景にある考え方を学べる。日本語訳も公開されている。

- ページタイトル: `How-To-Ask-Questions-The-Smart-Way/How-To-Ask-Questions-The-Smart-Way.md at master · selfteaching/How-To-Ask-Questions-The-Smart-Way · GitHub`
- 最終URL: [https://github.com/selfteaching/How-To-Ask-Questions-The-Smart-Way/blob/master/How-To-Ask-Questions-The-Smart-Way.md](https://github.com/selfteaching/How-To-Ask-Questions-The-Smart-Way/blob/master/How-To-Ask-Questions-The-Smart-Way.md)
- 用途との一致: 一致。Eric S. RaymondとRick Moenによる「How To Ask Questions The Smart Way」が表示された
- ログイン要求: なし
- 削除済み表示: なし
- 別ページへの転送: なし
- 判定: `manual_confirmed`

### 接続タイムアウト

#### [https://www.catb.org/~esr/writings/taoup/html/](https://www.catb.org/~esr/writings/taoup/html/)

- 原稿内の出現箇所:
  - [§1 設計原則](../../chapters/01_design.md) 200行・430行・448行
  - [§11 コマンドラインツールの設計と実装](../../chapters/11_cli.md) 389行・405行・1111行・1144行
- BibTeX: [references/ch01.bib](../../references/ch01.bib) 23行、[references/ch11.bib](../../references/ch11.bib) 86行
- URL周辺の文章:

> 一つのことをうまくやるプログラムを書け。協調して動くプログラムを書け。テキストストリームを扱うプログラムを書け。[7](https://www.catb.org/~esr/writings/taoup/html/)

> Unixのコマンドライン慣習では、`--`（ハイフン2つ）が**オプションの終わり**を意味する[10](https://www.catb.org/~esr/writings/taoup/html/)。`--` より後ろの引数は、たとえ `-` で始まっていても、すべて位置引数として扱われる:

- ページタイトル: 取得不能
- 最終URL: 指定URLへの移動を開始したが、接続タイムアウト
- 用途との一致: 確認不能
- ログイン要求: 確認不能
- 削除済み表示: 確認不能
- 別ページへの転送: 確認不能
- 判定: `manual_review_required`

#### [https://www.gnu.org/software/bash/manual/](https://www.gnu.org/software/bash/manual/)

- 原稿内の出現箇所: [§2 ターミナルとシェルの基本操作](../../chapters/02_terminal.md) 551行・836行
- BibTeX: [references/ch02.bib](../../references/ch02.bib) 54行
- URL周辺の文章:

> ワンライナーでは収まらない一連の処理を自動化するのが**シェルスクリプト**である。バイオインフォマティクスでは、FASTQの前処理からマッピング、定量までの一連のステップをシェルスクリプトで記述することが多い[6](https://www.gnu.org/software/bash/manual/)。

- ページタイトル: 取得不能
- 最終URL: 指定URLへの移動を開始したが、接続タイムアウト
- 用途との一致: 確認不能
- ログイン要求: 確認不能
- 削除済み表示: 確認不能
- 別ページへの転送: 確認不能
- 判定: `manual_review_required`

#### [https://www.gnu.org/software/coreutils/manual/](https://www.gnu.org/software/coreutils/manual/)

- 原稿内の出現箇所: [§2 ターミナルとシェルの基本操作](../../chapters/02_terminal.md) 347行・834行
- BibTeX: [references/ch02.bib](../../references/ch02.bib) 47行
- URL周辺の文章:

> この表のうち `sort`・`uniq`・`cut`・`wc` などは GNU Core Utilities[5](https://www.gnu.org/software/coreutils/manual/) に含まれる標準コマンドで、ほとんどのLinux/macOS環境に最初から用意されている。

- ページタイトル: 取得不能
- 最終URL: 指定URLへの移動を開始したが、接続タイムアウト
- 用途との一致: 確認不能
- ログイン要求: 確認不能
- 削除済み表示: 確認不能
- 別ページへの転送: 確認不能
- 判定: `manual_review_required`
