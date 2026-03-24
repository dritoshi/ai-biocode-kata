# §19 公共データベースとAPI — データ取得の実践

バイオインフォマティクスはデータベース駆動の学問である。ゲノム配列、タンパク質構造、遺伝子発現量——解析に使うデータのほとんどは公開データベースから取得する。エージェントとの協働においても、データベースへのアクセスは最も頻繁に発生する操作の一つである。前章までに学んできた設計・テスト・最適化・ドキュメント化の技術（[§18 コードのドキュメント化](./18_documentation.md)など）は、データベースから取得したデータに対して適用するものである。

データベースの種類（RDB/RDF/フラットファイル）やクエリ言語（SQL/SPARQL）の語彙を知っていれば、エージェントに「UniProtのSPARQLエンドポイントでヒトのキナーゼを取得するクエリを書いて」と具体的に指示できる。これらの語彙を知らなければ「データを取ってきて」という曖昧な指示に留まり、エージェントが返すコードの品質も低くなる。エージェントはSQL/SPARQLクエリの生成、ダウンロードスクリプトの作成、レスポンスのパース処理を得意とする。一方、どのデータベースが目的に適しているか（SRAかGEOか）の選択、返されたデータの科学的正確性の検証、アクセッション番号やバージョンの妥当性判断は人間が行うべきポイントである。

本章では、まず[19-0節](#19-0-データベースの基礎知識--エージェントと同じ言語で話すために)でDB種類・フラットファイル・クエリ言語・オントロジーの基礎語彙を整理する。次に[19-1節](#19-1-バイオインフォマティクスの主要データベース)で生命科学分野の主要データベースとID体系を概観する。[19-2節](#19-2-apiによるデータ取得)ではAPIを用いたプログラムからのデータ取得を実践し、最後に[19-3節](#19-3-データのダウンロードとローカル管理)で大規模データのダウンロードとローカル管理の手法を学ぶ。

---

## 19-0. データベースの基礎知識 — エージェントと「同じ言語」で話すために

バイオインフォマティクスの解析はデータベースからのデータ取得から始まる。エージェントと共通の語彙を持ち、「SQLで」「SPARQLで」「REST APIで」のように具体的に指示するために、本節ではデータベースの基礎知識を整理する。

### DB種類と用語

#### リレーショナルデータベース（RDB）とSQL

**リレーショナルデータベース**（Relational Database; RDB）は、データを**テーブル**（表）の形式で管理するデータベースである。テーブルは**行**（レコード）と**列**（カラム/フィールド）で構成される。テーブル間を共通のキー列で結合できることが最大の特徴である。

RDBへの問い合わせ言語が**SQL**（Structured Query Language）である。バイオインフォマティクスの文脈では、たとえばサンプルメタデータと発現量データを別テーブルに格納し、サンプルIDで結合（JOIN）して条件別に集計するといった用途で使う。

```sql
-- サンプルテーブルと発現量テーブルをJOINして条件別に平均発現量を集計
SELECT s.condition, AVG(e.expression) AS mean_expr
FROM samples AS s
JOIN expression AS e ON s.sample_id = e.sample_id
WHERE s.organism = 'Homo sapiens'
GROUP BY s.condition;
```

上のSQLクエリでは、`SELECT` で取得する列を指定し、`FROM` でテーブルを指定し、`JOIN ... ON` で2つのテーブルを `sample_id` で結合している。`WHERE` で条件を絞り、`GROUP BY` でグループごとに集計する。これら5つのキーワードを知っているだけで、エージェントへの指示の具体性が大きく変わる。

主要なRDB製品として、PostgreSQL、MySQL、SQLiteがある。SQLiteはサーバ不要でファイル1つに格納されるため、個人の解析プロジェクトでメタデータを管理するのに適している（[19-3節](#19-3-データのダウンロードとローカル管理)で実践する）。

#### NoSQL

RDB以外のデータベースを総称して**NoSQL**と呼ぶ。代表的なカテゴリを以下に示す。

**キーバリューストア**（Redis等）は、キーと値のペアでデータを格納する最もシンプルな形式である。高速なキャッシュやセッション管理に使われる。バイオインフォマティクスでは、大量の配列IDと配列データの高速ルックアップに利用されることがある。

**ドキュメント型DB**（MongoDB等）は、JSONライクな柔軟な構造のドキュメントを格納する。スキーマが固定されないため、フィールドが実験ごとに異なるメタデータの管理に適している。

**グラフ型DB**（Neo4j等）は、ノード（頂点）とエッジ（辺）の関係を直接表現する。バイオインフォマティクスでは、パスウェイ（代謝経路）やPPI（Protein-Protein Interaction; タンパク質間相互作用）ネットワークの表現に使われる。「タンパク質Aがタンパク質Bと結合する」「遺伝子Cがパスウェイ Dに関与する」といった関係性の探索は、グラフ型DBが得意とする領域である。

#### フラットファイルデータベース

バイオインフォマティクスでは、テキストベースの定型フォーマットでデータを配布するデータベースを**フラットファイルDB**と呼ぶ。RDBやNoSQLのような問い合わせ機構（SQLやSPARQL）を持たず、ファイルをダウンロードして手元で処理するのが基本的な利用形態である。INSDC（GenBank, ENA, DDBJ）が歴史的にこの方式でデータを公開してきたため、生命科学の分野では広く使われる用語である。代表的なフォーマットを以下に示す。

| フォーマット | 拡張子 | 内容 |
|-------------|--------|------|
| GenBank形式 | `.gb`, `.gbk` | 配列＋アノテーション（メタデータ付き） |
| FASTA | `.fasta`, `.fa` | 配列のみ（ヘッダ行＋配列行） |
| GFF/GTF | `.gff`, `.gtf` | ゲノムアノテーション（遺伝子座標等） |
| VCF | `.vcf` | バリアント情報（SNP・InDel等） |

一般的なデータベース分野ではあまり使われない用語だが、バイオインフォマティクスの文脈では頻出する。エージェントに「GenBankのフラットファイルをパースして」と指示すれば、適切なライブラリ（Biopythonの `SeqIO` 等）を使ったコードを生成してくれる。

#### 用語整理

データベースに関連する用語を整理する。

| 用語 | 意味 | バイオインフォでの例 |
|------|------|---------------------|
| **一次データベース** | 実験データを直接格納するDB | GenBank、SRA |
| **二次データベース** | 一次DBから加工・キュレーションしたDB | RefSeq、UniProt/Swiss-Prot |
| **データマート** | 特定の分析目的向けに抽出・加工したDB | 社内の発現量集計DB |
| **データレイク** | 生データを構造化せず大量に蓄積する保管庫 | S3バケットに格納した生FASTQファイル群 |

一次DBと二次DBの区別は重要である。GenBankは研究者が提出した配列を原則そのまま格納する一次DBであり、RefSeqはNCBIのキュレーターが検証・統合した二次DBである。解析の目的に応じて、原データに近い一次DBか、品質管理された二次DBかを選ぶ判断力が必要である。

### オントロジーとセマンティックWeb

エージェントに「apoptosisに関連する遺伝子を取得して」と指示するのと、「GO:0006915（apoptotic process）でアノテーションされた遺伝子を取得して」と指示するのでは、結果の精度がまったく異なる。前者では「apoptosis」が指す範囲が曖昧であり、エージェントがどの遺伝子セットを返すかは予測できない。後者ではオントロジーIDによって概念が一意に定まるため、再現性のある結果が得られる。

オントロジーIDと構造の知識は、エージェントへの指示を正確にするだけでなく、エンリッチメント解析の結果を批判的に評価する際にも不可欠である。たとえば、GO enrichment解析で有意にヒットした用語がDAGの最上位に近い汎用カテゴリ（"biological process" や "cellular process"）であれば、それは生物学的に意味のある発見とは言えない。こうした階層性の判断は、人間が行うべきレビューポイントである。

本項では、まずこれらの技術を束ねるセマンティックWebの枠組みを紹介し、その基盤であるRDF、RDFの上に概念体系を構築するオントロジー、そしてRDFデータへの問い合わせ言語であるSPARQLを順に解説する。

#### セマンティックWebとは

**セマンティックWeb**（Semantic Web）は、Web上のデータに機械が処理できる意味を付与するための、W3Cが推進する技術体系である。通常のWebページはHTMLで人間向けに記述されているが、セマンティックWebではデータの構造と意味を機械が読み取れる形式で記述する。

セマンティックWebの技術スタックは、以下の層で構成される。

| 層 | 技術 | 役割 |
|---|---|---|
| データモデル | **RDF** | データを主語-述語-目的語のトリプルで表現する |
| 語彙・意味定義 | **RDFS / OWL** | クラス・プロパティ・階層関係を定義し、データに意味を付与する |
| 問い合わせ | **SPARQL** | RDFデータを検索・取得するクエリ言語 |

各層は下位の層を基盤として利用する——RDFがデータ構造を提供し、RDFS/OWLがその上に語彙の意味を定義し、SPARQLがRDFデータに対してクエリを実行する。バイオインフォマティクスでは、UniProt[7]がRDF形式でタンパク質データを公開しSPARQLエンドポイントを提供するなど、この技術スタックを活用したデータ公開が進んでいる。

#### RDF

**RDF**（Resource Description Framework）は、セマンティックWebの基盤となるデータモデルである。データを**主語-述語-目的語**の3つ組（**トリプル**）で表現する。各トリプルは有向グラフの辺に対応し、主語と目的語がノード、述語がノード間の関係を示す。すべての要素はURI（一意の識別子）で表現される。

```
<http://purl.uniprot.org/uniprot/P53_HUMAN>  # 主語: p53タンパク質
  <http://purl.uniprot.org/core/organism>     # 述語: 生物種
  <http://purl.uniprot.org/taxonomy/9606> .   # 目的語: ヒト（Taxonomy ID 9606）
```

RDFの強みは、異なるデータベース間のデータをURIで結び付けられることである。UniProtのタンパク質エントリから、NCBIのTaxonomy IDや、Gene OntologyのGO IDへ直接リンクできる。この仕組みを**Linked Data**と呼ぶ。

#### オントロジー

セマンティックWebの技術スタックでは、RDFの上位層としてRDFS（RDF Schema）やOWL（Web Ontology Language）が位置づけられる。RDFがデータの「構造」（何が何と関連するか）を記述するのに対し、RDFS/OWLはデータの「意味」——クラスの階層、プロパティの定義域や値域といった語彙の制約——を定義する。この語彙体系が**オントロジー**（Ontology）である。

ただし、生命科学における「オントロジー」は、W3CのRDF/OWL技術よりも広い意味で使われる。ある分野の概念とその関係を体系的に定義した語彙体系を指し、必ずしもRDF/OWL形式で記述されているとは限らない。

代表的な生命科学オントロジーであるGene Ontology（GO）は、1998年にOBO（Open Biomedical Ontologies）形式で作成された[4]（詳細はコラム参照）。OBOはテキストベースの独自形式であり、W3CのRDF/OWLとは独立に発展したものである。現在、GOはOBO形式（主要な管理・キュレーション用フォーマット）とOWL形式（セマンティックWebとの相互運用用）の両方で公開されている。エンリッチメント解析でよく使われるgoatoolsやclusterProfilerは、OBO形式のGOデータを直接扱う。

オントロジーの用語にはそれぞれ一意のID（例: GO:0006915 = apoptotic process）が割り振られており、このIDを使うことで言語や文脈に依存しない正確な概念の指定が可能になる。

#### SPARQL

**SPARQL**（SPARQL Protocol and RDF Query Language）は、セマンティックWeb技術スタックの問い合わせ層に位置する、RDFデータへのクエリ言語である。SQLに似た構文を持つが、テーブルの行ではなくトリプルパターンに対してマッチングを行う点が異なる。

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>

SELECT ?protein ?name
WHERE {
  ?protein a up:Protein ;
           up:organism taxon:9606 ;
           rdfs:label ?name .
}
LIMIT 10
```

上のSPARQLクエリは「ヒト（Taxonomy ID 9606）のタンパク質のうち、名前を持つものを10件取得する」という意味である。`PREFIX` はURIの短縮形を定義し、`WHERE` 内のトリプルパターンに一致するデータを `SELECT` で取得する。

SQLとSPARQLの対比を以下にまとめる。

| 要素 | SQL | SPARQL |
|------|-----|--------|
| データモデル | テーブル（行×列） | トリプル（主語-述語-目的語） |
| 取得する項目 | `SELECT 列名` | `SELECT ?変数名` |
| データの指定 | `FROM テーブル名` | `WHERE { トリプルパターン }` |
| フィルタ | `WHERE 条件` | `FILTER(条件)` |
| 結合 | `JOIN ... ON` | トリプルパターンの共有変数 |
| 集約 | `GROUP BY`, `COUNT()` | `GROUP BY`, `COUNT()` |

### データアクセスの2つのアプローチ

公開データベースからデータを取得する方法は大きく2つに分かれる。APIによるプログラム的アクセスと、フラットファイルのダウンロードである。どちらを使うかはデータの規模と用途で決まる。

| 観点 | API（REST / SPARQL） | ファイルダウンロード（FTP / HTTP） |
|------|----------------------|----------------------------------|
| データ量 | 少量〜中量に適する | 大量データ・ゲノム全体に適する |
| 再現性 | クエリをコードに残せば再現可能 | URL + チェックサムで再現可能 |
| 速度 | ネットワーク越しで遅い・レート制限あり | ローカルアクセスで高速（ダウンロード後） |
| 柔軟性 | 条件指定・フィルタリングが可能 | ファイル全体を取得、手元でフィルタ |
| バージョン管理 | 常に最新データを取得 | ダウンロード時点のスナップショット |
| オフライン利用 | 不可 | 可能 |
| ストレージ | 不要（オンデマンド） | ローカルに保存が必要 |

実際の解析ではこの2つを組み合わせて使うことが多い。たとえば、ヒトゲノムリファレンス配列はFTPサイトからダウンロードし、特定の遺伝子のアノテーション情報はAPIで検索する、という使い分けである。[19-2節](#19-2-apiによるデータ取得)でAPI方式を、[19-3節](#19-3-データのダウンロードとローカル管理)でダウンロード方式をそれぞれ詳しく扱う。

### Vibe codingとの接続

エージェントにデータ取得を依頼する際、以下の3つの技術のどれを使うかを指定することが重要である。

1. **SQL**: ローカルのRDB（SQLite等）やデータウェアハウスに対するクエリ
2. **SPARQL**: RDFデータを提供するエンドポイント（UniProt、TogoWS等）に対するクエリ
3. **REST API**: HTTP経由でJSON/XML/FASTAを返すエンドポイント（NCBI E-utilities等）に対するリクエスト

エージェントが生成したクエリを受け取ったとき、以下の点を確認する。

- **JOINの方向**: `INNER JOIN`（両方に存在するデータのみ）か `LEFT JOIN`（片方にしかないデータも保持）か。バイオインフォマティクスでは欠損データの扱いが重要なため、意図しないデータの欠落に注意する
- **フィルタ条件の妥当性**: 生物種の指定漏れ、バージョンの不一致、廃止IDの混入がないか
- **返り値のカラム名**: エージェントが仮定したカラム名が実際のDB/APIのレスポンスと一致しているか

オントロジーを活用した解析では、さらに以下の判断が人間に求められる。

- **オントロジーIDの指定**: 自然言語でなくGO IDやKEGG IDで概念を指定することで、曖昧さを排除する。「apoptosis関連の遺伝子」ではなく「GO:0006915でアノテーションされた遺伝子」と指示する
- **GOカテゴリの選択**: 生物学的プロセス（BP）、分子機能（MF）、細胞内構成要素（CC）のどれで解析するかは、研究の問いに依存する判断であり、エージェントに任せるべきではない
- **DAG構造の階層性**: エンリッチメント解析で上位の汎用カテゴリ（"metabolic process" 等）がヒットしても生物学的に意味のある知見とは限らない。適切な階層レベルの用語に注目する判断は人間が行う

#### エージェントへの指示例

データベースの種類とクエリ言語の語彙を知っていれば、エージェントへの指示を具体化できる。以下の指示例のように、使うべき技術を明示的に指定することが重要である。

> 「UniProtのSPARQLエンドポイントで、ヒトのキナーゼファミリーに属するタンパク質のアクセッション番号と遺伝子名を取得するクエリを書いて」

> 「このサンプルメタデータCSVと発現量TSVをSQLiteに読み込み、サンプルIDでJOINして条件別に集計するスクリプトを書いて」

> 「GenBankのFLATファイル形式とFASTA形式の違いを説明して。どちらをダウンロードすべきか判断したい」

> 「GO:0006915（apoptotic process）でアノテーションされたヒトの遺伝子リストを、UniProtのSPARQLエンドポイントから取得するスクリプトを書いて」

> 「このDEGリストに対して、goatoolsを使ってGO enrichment解析を実行するスクリプトを書いて。BPカテゴリのみに絞り、FDR < 0.05でフィルタして」

---

> **🧬 コラム: Gene OntologyとKEGG**
>
> **Gene Ontology**（GO）[4](https://doi.org/10.1038/75556)は、遺伝子産物の機能を体系的に記述するためのオントロジーである。3つのカテゴリ——**生物学的プロセス**（Biological Process; BP）、**分子機能**（Molecular Function; MF）、**細胞内構成要素**（Cellular Component; CC）——から構成され、用語間は**DAG**（有向非巡回グラフ）構造で関連付けられている。
>
> GOの主要な応用がエンリッチメント解析である。差次的発現遺伝子のリストに特定のGO用語が統計的に有意に多く含まれているかを検定する。Pythonの `goatools` やRの `clusterProfiler` がよく使われるツールである。
>
> **KEGG**（Kyoto Encyclopedia of Genes and Genomes）[5](https://doi.org/10.1093/nar/28.1.27)は、代謝パスウェイや疾患パスウェイなどの経路情報を体系化したデータベースである。KEGG REST APIでプログラムからパスウェイ情報を取得できるが、ライセンスに注意が必要である——学術目的の利用は無料だが、商用利用には有料ライセンスが必要である。
>
> このほか、生命科学で使われるオントロジーには以下がある。
> - **Sequence Ontology**（SO）: 配列の特徴（exon、intron、SNV等）を定義
> - **Disease Ontology**（DO）: ヒトの疾患を体系化
> - **Cell Ontology**（CL）: 細胞の種類を体系化

---

## 19-1. バイオインフォマティクスの主要データベース

生命科学のデータベースは数百以上存在するが、実際の解析で頻繁に利用するのは限られた主要DBである。本節では、エージェントへの指示に必要なDB名・格納データ・ID形式を整理する。

### 主要DBの全体像

| カテゴリ | DB名 | 主な格納データ | 代表的ID形式 |
|----------|------|---------------|-------------|
| NCBI系 | GenBank | 塩基配列 | NM_, NR_, XM_ |
| NCBI系 | SRA | シーケンシング生リード | SRR, ERR, DRR |
| NCBI系 | GEO | 発現量データ、マイクロアレイ | GSE, GSM, GPL |
| NCBI系 | PubMed | 文献 | PMID |
| NCBI系 | dbSNP | 一塩基多型 | rs |
| 欧州系 | Ensembl | ゲノムアノテーション | ENSG, ENST, ENSP |
| 欧州系 | UniProt | タンパク質配列・機能 | P12345, Q9UHD2 |
| 欧州系 | ENA | 塩基配列（DDBJと相互ミラー） | — |
| 日本系 | DDBJ | 塩基配列（GenBankと相互ミラー） | — |
| 日本系 | PDBj | 立体構造 | PDB ID (4文字) |
| ブラウザ | UCSC Genome Browser | ゲノム可視化 | — |
| ブラウザ | IGV | ローカルゲノム可視化 | — |
| 統合系 | TogoWS | 複数DBへの統一API | — |

GenBank（NCBI）、ENA（EBI）、DDBJ（日本）は**国際塩基配列データベース連携**（INSDC）の三極体制で相互ミラーリングしている[6](https://doi.org/10.1093/nar/gkad1044)。どのDBに登録してもデータは三者間で共有される。

### DB選択の判断力

データの種類に応じて適切なDBを選択することは、エージェントに指示する前に人間が行うべき判断である。以下のフローで考えると整理しやすい。

```
取得したいデータの種類は？
├─ 塩基配列（参照配列）    → GenBank / RefSeq
├─ シーケンシング生リード   → SRA
├─ 遺伝子発現量            → GEO
├─ タンパク質の配列・機能   → UniProt
├─ ゲノムアノテーション     → Ensembl
├─ 一塩基多型（SNP）       → dbSNP / ClinVar
├─ タンパク質立体構造       → PDB
└─ 文献                    → PubMed
```

エージェントに「このデータを取得して」と指示する前に、「どのDBの、どのID形式で、どのフォーマットで」を自分で決めておくことが重要である。エージェントはDBの網羅的な最新知識を持たない場合があり、存在しないエンドポイントや廃止されたAPIを提案することがある。

### IDの体系

バイオインフォマティクスのデータベースでは、各エントリにアクセッション番号が付与される。プレフィックスを見ればデータの種類が分かるようになっている。

| プレフィックス | 意味 | 例 |
|---------------|------|-----|
| NM_ | RefSeq mRNA | NM_001301717.2 |
| NR_ | RefSeq non-coding RNA | NR_046018.2 |
| XM_ | RefSeq predicted mRNA | XM_011541469.3 |
| ENSG | Ensembl 遺伝子 | ENSG00000141510 |
| ENST | Ensembl 転写産物 | ENST00000269305 |
| SRR / ERR / DRR | SRA シーケンシングラン | SRR1234567 |
| GSE | GEO シリーズ | GSE12345 |
| GSM | GEO サンプル | GSM123456 |
| rs | dbSNP バリアント | rs12345 |
| P / Q | UniProt タンパク質 | P04637 |

アクセッション番号には**バージョン**が付く場合がある。`NM_001301717.2` の `.2` はバージョン2を意味する。バージョンを省略すると最新版が返されるが、再現性のためにはバージョンを明示的に指定することが望ましい。

**ID変換**が必要になる場面も多い。Ensembl gene IDからUniProtアクセッション番号への変換、あるいはGene SymbolからEnsembl IDへの変換といった用途には、以下のツールが利用できる。

- **biomaRt**（R）: Ensembl BioMartへのプログラムインタフェース
- **MyGene.info**: 遺伝子情報のREST API。Pythonからは `mygene` パッケージで利用
- **UniProt ID mapping**: UniProtの公式ID変換サービス

エージェントにID変換を依頼する際は、以下の点に注意する。

- **生物種の明示**: ヒトのTP53とマウスのTrp53は同じ遺伝子だがIDは異なる
- **バージョンの指定**: バージョン付き・なしで結果が変わる場合がある
- **廃止IDの存在**: データベースの更新でIDが統合・廃止されることがある。古い論文のIDは変換できない場合がある

#### エージェントへの指示例

データベースの名前とID形式を正確に指定することで、エージェントの出力精度が向上する。

> 「GSE12345のサンプルメタデータをNCBI GEOからダウンロードし、条件ごとのサンプル数を集計するスクリプトを書いて」

> 「Ensembl gene ID（ENSG形式）のリストをUniProtアクセッション番号に変換するスクリプトを、MyGene.info APIを使って書いて」

> 「SRRアクセッション番号のリストからSRA Run Selectorの情報を取得し、シーケンサー機種とリード長を一覧にするスクリプトを書いて」

---

## 19-2. APIによるデータ取得

プログラムからデータベースのデータを取得するには、API（Application Programming Interface）を使う。手動でWebブラウザからダウンロードするのではなく、APIを使うことで再現性のあるデータ取得パイプラインを構築できる。

データ取得の手段を選ぶ際、Webスクレイピングや全データダウンロードに手を伸ばす前に、対象データベースが公式APIを提供していないかを確認するとよいだろう。APIはDB提供元が設計した正式なアクセス手段であり、レスポンス形式が安定しておりバージョン管理もされている。一方、APIを介さないWebスクレイピングはサーバへの過度な負荷となり利用規約に抵触するリスクがあり、HTMLの構造変更で容易に壊れる。全データのFTPダウンロードは不要なデータまで取得する非効率を生む。

公式APIの有無は、DB名に "REST API" や "API documentation" を添えて検索するか、公式サイトの "For Developers" セクションを確認するのが早い。エージェントに「このDBのREST APIドキュメントを探して」と指示するのも有効だが、エージェントが存在しないAPIを提案する場合があるため、公式ドキュメントで必ず裏付けを取る。またAPIが提供されているものの十分にメンテされずに動かない場合もある。パイプライン処理の途中でAPIを利用する際に、アクセスの成否やレイテンシを意識した実装を行うべきである

### HTTPの仕組み — API利用に必要な最低限

APIを使うには、その土台となる**HTTP**（HyperText Transfer Protocol）の基本的な仕組みを理解しておく必要がある。HTTPは、クライアント（自分のプログラム）がサーバ（データベースの提供元）にリクエストを送り、サーバがレスポンスを返す、という単純なモデルで動作する。

**URL**（Uniform Resource Locator） はリソースの場所を指定する文字列で、以下の構造を持つ:

```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term=BRCA1
├─────┤├───────────────────────┤├───────────────────────────┤├──────────────────┤
スキーム         ホスト                       パス               クエリパラメータ
```

- **スキーム**: `https`（暗号化あり）または `http`（暗号化なし）
- **ホスト**: サーバのアドレス
- **パス**: サーバ上のリソースの位置
- **クエリパラメータ**: `?` 以降の `キー=値` ペア。`&` で複数指定

**ステータスコード**は、サーバがリクエストの結果を3桁の数字で返すものである。APIを利用するプログラムでは、ステータスコードに応じて処理を分岐させる必要がある:

| コード | 意味 | 対処 |
|--------|------|------|
| 200 | 成功 | レスポンスを処理する |
| 404 | Not Found（リソースが存在しない） | IDやパスを確認する |
| 403 | Forbidden（アクセス権なし） | APIキーや認証を確認する |
| 429 | Too Many Requests（レート制限） | 待機してリトライする |
| 500 | Internal Server Error（サーバ側エラー） | 時間を置いてリトライする |

バイオインフォマティクスのAPI利用で最も頻繁に遭遇するのが **429**（レート制限）である。NCBI E-utilitiesはAPIキーなしでは1秒あたり3リクエスト、APIキーありで10リクエストに制限されている。大量のアクセッション番号を問い合わせる際は、APIキーの取得とリトライ機構の実装が不可欠である。

リクエストとレスポンスの形式として最も一般的なのが**JSON**（JavaScript Object Notation）である。JSONの構造については[§4-1](./04_data_formats.md)で学んだ。APIのレスポンスとして返されるJSONをPythonの辞書やリストに変換して処理するのが、API利用の基本パターンである。

### REST APIの基礎

**REST API**（Representational State Transfer）は、HTTPプロトコルを使ってデータを取得・操作するAPI設計のスタイルである。

主要なHTTPメソッドは以下の2つである。

- **GET**: データを取得する。URLにパラメータを含める。ブラウザでURLにアクセスするのと同じ
- **POST**: データを送信する。リクエストボディにパラメータを含める。長いクエリ文字列を送る場合に使う

**エンドポイント**とは、APIが公開するURLのことである。たとえばNCBI E-utilitiesのエンドポイントは `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/` で始まる。

レスポンスの形式はAPIによって異なる。

| 形式 | 特徴 | 用途例 |
|------|------|--------|
| JSON | 軽量、Pythonで扱いやすい | 多くのモダンAPI |
| XML | 構造的、冗長 | NCBI E-utilities |
| FASTA | 配列専用 | 配列取得API |
| TSV | タブ区切り | UniProt一括取得 |

#### レート制限とAPIキー

公開APIには**レート制限**（Rate Limit）が設けられている。NCBI E-utilitiesでは、APIキーなしの場合は1秒あたり3リクエスト、APIキーありの場合は1秒あたり10リクエストまで許可される[1](https://www.ncbi.nlm.nih.gov/books/NBK25501/)。

APIキーの管理については[§10 ソフトウェア成果物の設計](./10_deliverables.md)で述べたように、コードにハードコーディングせず環境変数で管理する。NCBI E-utilitiesでは `api_key` パラメータに加えて、`tool`（ツール名）と `email`（連絡先メールアドレス）の指定が求められる。

#### エラーハンドリング

APIを呼び出す際は、HTTPステータスコードを確認してエラーに対処する。

| ステータスコード | 意味 | 対処 |
|-----------------|------|------|
| 200 | 成功 | そのまま処理 |
| 404 | 未検出 | IDの誤りを確認 |
| 429 | リクエスト過多 | レート制限を守る。リトライ間隔を空ける |
| 500 | サーバエラー | 時間を置いてリトライ |

429エラー（Too Many Requests）は、レート制限を超えた場合に返される。リトライする際は**エクスポネンシャルバックオフ**（1秒、2秒、4秒…と間隔を倍増）が推奨される。

### NCBI Entrez API

NCBI E-utilities[1](https://www.ncbi.nlm.nih.gov/books/NBK25501/)は、NCBIの各データベースにプログラムからアクセスするためのAPIである。典型的なフローは以下の3ステップで構成される。

```
1. esearch  →  キーワードでIDリストを検索
       ↓
2. efetch   →  IDリストから実データ（FASTA、GenBank形式等）を取得
       ↓
3. elink    →  関連するDB間でIDをリンク（例: 遺伝子→文献）
```

Biopythonの `Entrez` モジュール[3](https://biopython.org/wiki/Documentation)を使うと、これらのステップをPythonから簡潔に記述できる。以下のコードはアクセッション番号からFASTA配列を取得する例である。

```python
from Bio import Entrez, SeqIO
from io import StringIO

# 認証情報の設定（環境変数から読み込む）
Entrez.email = os.environ["NCBI_EMAIL"]
Entrez.api_key = os.environ.get("NCBI_API_KEY")
Entrez.tool = "biocode-kata"

# efetchでFASTA配列を取得
handle = Entrez.efetch(
    db="nucleotide",            # 検索対象DB
    id="NM_001301717.2",        # アクセッション番号
    rettype="fasta",            # 取得形式
    retmode="text",             # テキストモード
)
text = handle.read()
handle.close()

# BioPythonのSeqIOでパース
record = SeqIO.read(StringIO(text), "fasta")
print(f"{record.id}: {len(record.seq)} bp")
```

`Entrez.efetch` は、`db` で対象データベース、`id` でアクセッション番号、`rettype` で取得フォーマットを指定する。返り値はファイルライクオブジェクトなので、`.read()` でテキストを取得し、`SeqIO.read()` でパースする。

キーワード検索から一括取得する場合は、`esearch` → `efetch` の2ステップになる。完全な実装は `scripts/ch19/entrez_fetch.py` を参照されたい。

### SPARQLエンドポイント

UniProtはSPARQLエンドポイント[2](https://sparql.uniprot.org/)を公開しており、RDFデータに対して柔軟なクエリを投げることができる。以下のPythonコードは、`requests` ライブラリを使ってSPARQLクエリを実行する例である。

```python
import requests

ENDPOINT = "https://sparql.uniprot.org/sparql"

# ヒトのミトコンドリア局在タンパク質を取得するクエリ
query = """
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>

SELECT ?protein ?name
WHERE {
  ?protein a up:Protein ;
           up:organism taxon:9606 ;
           up:classifiedWith <http://purl.uniprot.org/go/0005739> ;
           rdfs:label ?name .
}
LIMIT 10
"""

# GETリクエストでクエリを送信
response = requests.get(
    ENDPOINT,
    headers={"Accept": "application/sparql-results+json"},
    params={"query": query, "format": "json"},
    timeout=30,
)
response.raise_for_status()  # HTTPエラーがあれば例外

# JSON結果をパース
data = response.json()
for row in data["results"]["bindings"]:
    print(f"{row['protein']['value']}: {row['name']['value']}")
```

`requests.get` の `headers` で受け取りたいフォーマット（JSON）を指定し、`params` にSPARQLクエリを渡す。`.raise_for_status()` はHTTPエラー時に例外を発生させるメソッドである。

エージェントにSPARQLクエリを生成させた場合、以下を確認する。

- **PREFIXの正確性**: URIが実在するか
- **トリプルパターンの論理**: 主語-述語-目的語の関係が意味的に正しいか
- **LIMIT句の有無**: 大量の結果が返る可能性がある場合、LIMITで制限しているか

完全な実装は `scripts/ch19/sparql_query.py` を参照されたい。

### Pythonライブラリ

データ取得に使う主要なPythonライブラリを整理する。

| ライブラリ | 用途 | 特徴 |
|-----------|------|------|
| `requests` | 汎用HTTP通信 | REST API全般に使える |
| `Biopython`（Entrez/SeqIO） | NCBI E-utilities | 認証情報管理・パース一体化 |
| `bioservices` | 複数DBの統一インタフェース | UniProt、KEGG、BioMart等に対応 |

`requests` は最も汎用的なHTTPライブラリで、JSON/XMLを返す任意のAPIに使える。Biopython[3](https://biopython.org/wiki/Documentation)はNCBI特化で、`Entrez` モジュールによる検索・取得と `SeqIO` によるパースが一体化している。`bioservices` は複数のバイオインフォマティクスDBへの統一的なアクセスを提供するが、依存関係が多い点に注意する。

#### エージェントへの指示例

APIを使ったデータ取得では、使用するライブラリとエンドポイントを明示的に指定すると、エージェントの出力精度が高まる。

> 「Biopython Entrezモジュールを使って、指定したアクセッション番号リストからFASTA配列をバッチ取得するスクリプトを書いて。レート制限を守り、api_keyを環境変数から読むようにして」

> 「UniProtのSPARQLエンドポイントに対して、ヒトのミトコンドリア局在タンパク質を取得するクエリを実行するPythonスクリプトを書いて」

> 「このNCBI検索結果のJSON応答から、PubMed IDとタイトルを抽出してTSVに保存するパーサを書いて」

---

> **🧬 コラム: NCBI系コマンドラインツール**
>
> Pythonスクリプトを書かずとも、NCBI はコマンドラインツールを提供している。シェルスクリプトやワークフロー管理ツール（[§14 解析パイプラインの自動化](./14_workflow.md)）との相性がよい。
>
> **Entrez Direct**（EDirect）[12](https://www.ncbi.nlm.nih.gov/books/NBK179288/)は、シェルからNCBIを検索するツールセットである。パイプラインで繋げて使う。
>
> ```bash
> # ヒトのBRCA1遺伝子のFASTAを取得
> esearch -db nucleotide -query "BRCA1[Gene] AND Homo sapiens[Organism]" \
>   | efetch -format fasta \
>   > brca1.fasta
> ```
>
> **SRA Toolkit**[10](https://github.com/ncbi/sra-tools)は、SRAからシーケンシングリードをダウンロードするツールである。`prefetch` でSRAファイルをダウンロードし、`fasterq-dump` でFASTQ形式に変換する2段階の手順が推奨される。
>
> ```bash
> # SRAファイルをダウンロード → FASTQに変換
> prefetch SRR1234567
> fasterq-dump SRR1234567 --split-3  # ペアエンドを分割
> ```
>
> **NCBI Datasets CLI**[11](https://www.ncbi.nlm.nih.gov/datasets/)は、ゲノムや遺伝子の情報を一括でダウンロードするための新しいツールである。JSON形式のメタデータとデータファイルをまとめて取得できる。
>
> **BLAST+** は、ローカル環境でBLAST検索を実行するためのツールセットである。`makeblastdb` でFASTAからデータベースを作成し、`blastn`（塩基配列）や `blastp`（アミノ酸配列）で検索する。

---

> **🧬 コラム: Entrez以外の主要バイオインフォマティクスAPI**
>
> 本文ではNCBI Entrez APIとUniProt SPARQLを扱ったが、バイオインフォマティクスには他にも多くの公開APIが存在する。[19-1節](#19-1-バイオインフォマティクスの主要データベース)で紹介したデータベースのうち、プログラムからのアクセスに利用できる代表的なAPIを紹介する。
>
> **Ensembl REST API**[13](https://doi.org/10.1093/nar/gkac958)は、ゲノムアノテーション・バリアント情報をJSONで取得できるRESTful APIである。エンドポイント `https://rest.ensembl.org` に対してGETリクエストを送るだけで、遺伝子情報、配列、バリアント、ID変換などの操作が可能である。認証不要で手軽に試せるため、Entrezと並んで最初に覚えたいAPIの一つである。
>
> **Ensembl BioMart** は、大量の遺伝子IDやアノテーションの一括取得・フィルタリングに特化したサービスである。Pythonからは `pybiomart`、Rからは `biomaRt`（[19-1節](#19-1-バイオインフォマティクスの主要データベース)で既出）で利用できる。「Ensembl gene IDのリスト1万件をUniProt IDに一括変換したい」といったID変換のユースケースで威力を発揮する。
>
> **UCSC Genome Browser REST API**[14](https://doi.org/10.1093/nar/gkac1072)は、UCSC Genome BrowserのトラックデータにプログラムからアクセスするためのAPIである。エンドポイント `https://api.genome.ucsc.edu` から、座標範囲を指定してアノテーションを取得したり、利用可能なトラックの一覧を取得したりできる。
>
> **TogoWS**[9](http://togows.org/)は、DBCLS（ライフサイエンス統合データベースセンター）が提供する複数データベースへの統一RESTゲートウェイである。`/entry/DB名/ID` 形式の統一URLでGenBank、UniProt、PDB等の異なるDBにアクセスできるため、DB固有のAPI仕様を個別に学ぶ手間を省ける。
>
> このほか、[19-1節](#19-1-バイオインフォマティクスの主要データベース)で触れた**MyGene.info**もREST APIとして利用可能であり、遺伝子情報の検索・ID変換をJSON形式で手軽に行える。目的のデータに応じてこれらのAPIを使い分けることで、データ取得の効率と再現性が向上する。

> 🧬 **コラム: バイオインフォマティクス向けMCPサーバーとAIエージェント**
>
> [§5-5](./05_software_components.md#5-5-mcpmodel-context-protocolエージェントの能力を拡張する)で、MCP（Model Context Protocol）によってエージェントに外部ツールへのアクセス能力を追加できることを学んだ。§5-5ではGitHubやNotionといった汎用的なMCPサーバーを紹介したが、バイオインフォマティクスに特化したMCPサーバーも開発が進んでいる。
>
> **BioMCP**（https://biomcp.org/ ）[15](https://github.com/genomoncology/biomcp)は、遺伝子・変異・論文・臨床試験・医薬品・疾患・パスウェイなど12種のバイオメディカルエンティティを統一的なコマンド文法でクエリできるCLIツール兼MCPサーバーである。
>
> ```bash
> # BioMCPのインストール
> uv tool install biomcp-cli
>
> # 遺伝子に関連する論文を検索
> biomcp search article -g BRAF --limit 5
>
> # 遺伝子のパスウェイ情報を取得
> biomcp get gene BRAF pathways
> ```
>
> BioMCPをMCPサーバーとしてエージェントに追加すれば、上記のクエリを自然言語の指示で実行できる。「BRAF遺伝子に関連する最新の臨床試験を検索して」と指示するだけで、エージェントがBioMCPを呼び出して結果を返してくれる。
>
> **PubMed MCP**[16](https://github.com/JackKuo666/PubMed-MCP-Server)は、PubMedの論文検索に特化したMCPサーバーである。キーワード検索、詳細なメタデータ取得、全文PDFのダウンロード、論文の包括的解析といった機能を提供する。
>
> ```bash
> # PubMed MCPの追加例（Claude Code CLI）
> npx -y @smithery/cli install @JackKuo666/pubmed-mcp-server --client claude
> ```
>
> このほか、GEO（Gene Expression Omnibus）データセットを検索するGEOmcp[17](https://github.com/MCPmed/GEOmcp)、UniProtのタンパク質情報に26種のツールでアクセスするUniProt MCP[18](https://github.com/Augmented-Nature/Augmented-Nature-UniProt-MCP-Server)、BLAST・AlphaFold・COSMIC等の遺伝学・ゲノミクスツールを統合するgget-MCP[19](https://github.com/longevity-genie/gget-mcp)など、バイオ特化のMCPサーバーが続々と開発されている。
>
> バイオ向けMCPサーバーを導入することで、本節で学んだREST APIやSPARQLエンドポイントへのアクセスが、Pythonコードを書くことなくエージェントへの自然言語の指示だけで可能になる。ただし、MCPは魔法ではない——裏ではこの節で学んだHTTPリクエストやEntrez APIの呼び出しが行われている。仕組みを理解した上でMCPを使えば、エージェントの出力の妥当性を判断できる。
>
> **Biomni — バイオメディカル特化のAIエージェント**
>
> MCPサーバーとは異なるアプローチとして、Stanford大学のSNAPグループが開発した**Biomni**（https://biomni.stanford.edu/ ）[20](https://doi.org/10.1101/2025.05.30.656746)がある。Biomniは150以上の専門ツールと59のデータベースを統合した汎用バイオメディカルAIエージェントであり、LLMの推論能力と検索ベースの計画策定、コード実行を組み合わせて、研究タスクを自律的に遂行する。
>
> Biomniの検証済みの実績には、ウェアラブルデバイスのデータから食後の熱産生応答を特定した解析、33万個以上のシングルセルRNA-seq・ATAC-seqデータセットからの遺伝子制御ネットワーク解析、さらにはウェットラボで実際に検証された分子クローニングプロトコルの設計がある。LAB-Benchベンチマークでは専門家と同等の精度を達成している。
>
> ```python
> from biomni.agent import A1
> agent = A1(path='./data', llm='claude-sonnet-4-20250514')
> agent.go("Plan a CRISPR screen for T cell exhaustion genes")
> ```
>
> BiomniはMCPサーバーへの接続もサポートしており、本コラムで紹介したBioMCPやPubMed MCPと組み合わせることも可能である。MCPサーバーが「エージェントに個別の能力を追加する部品」であるのに対し、Biomniは「バイオメディカル研究のための統合エージェント環境」という位置づけである。
>
> **活用の指示例:**
>
> > 「BioMCPを使って、BRAF V600E変異に関連する臨床試験を検索して。Phase III以降の試験に絞って、使用されている薬剤をまとめて」
>
> > 「PubMed MCPで、CRISPR screenとsingle-cell RNA-seqを組み合わせた論文を2024年以降で検索して。各論文の手法の概要をまとめて」

---

## 19-3. データのダウンロードとローカル管理

API経由で少量のデータを取得する方法を学んだ。本節では、大規模データのダウンロードとローカル環境での管理方法を扱う。

### 大規模データのダウンロード

#### wget / curl

`wget` と `curl` は、URLからファイルをダウンロードする基本的なコマンドラインツールである。

```bash
# wgetでFASTAファイルをダウンロード
# --retry=3: 失敗時に3回リトライ
# --limit-rate=1m: 帯域を1MB/sに制限（サーバへの負荷軽減）
wget --retry-connrefused --tries=3 --limit-rate=1m \
  "https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/latest_assembly_versions/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.fna.gz" \
  -O GRCh38.fna.gz
```

`--retry-connrefused` は接続拒否時にもリトライする。`--limit-rate` はサーバへの負荷を考慮した帯域制限である。

#### SRA Toolkit

SRAからシーケンシングデータを取得する場合は、SRA Toolkit[10](https://github.com/ncbi/sra-tools)の `prefetch` + `fasterq-dump` を使う。

```bash
# Step 1: SRAファイルをダウンロード（キャッシュに保存）
prefetch SRR1234567

# Step 2: FASTQに変換（--split-3はペアエンドリードを分割）
fasterq-dump SRR1234567 --split-3 --threads 4
```

`prefetch` はSRAファイルをローカルキャッシュにダウンロードし、`fasterq-dump` はそのキャッシュからFASTQファイルを生成する。直接 `fasterq-dump` を実行することもできるが、`prefetch` を挟むことでネットワークエラー時のリトライが容易になる。`--split-3` オプションはペアエンドリードをR1/R2に分割し、ペアにならなかったリードを別ファイルに出力する。

#### Aspera

**Aspera**（`ascp`）は、FTPより高速にファイルを転送できるプロトコルである。NCBIやEBIは Aspera によるダウンロードをサポートしている。大量のSRAファイルをダウンロードする場合に有効である。

```bash
# Asperaでのダウンロード例
ascp -QT -l 300m -P 33001 \
  -i ~/.aspera/connect/etc/asperaweb_id_dsa.openssh \
  anonftp@ftp.ncbi.nlm.nih.gov:/sra/sra-instant/reads/ByRun/sra/SRR/SRR123/SRR1234567/SRR1234567.sra \
  ./
```

エージェントにダウンロードスクリプトの一括生成を依頼するのは有効なパターンである。アクセッション番号のリストを渡して「50件をprefetch + fasterq-dumpで並列ダウンロードするbashスクリプトを書いて」のように指示すれば、ループ処理やリトライロジックを含むスクリプトを生成してくれる。

### チェックサム検証

ダウンロードしたファイルが正しく転送されたかを確認するために、**チェックサム検証**を行う。ファイルのハッシュ値（MD5やSHA256）を計算し、提供元が公開している値と比較する。

```bash
# MD5チェックサムの計算と検証
md5sum downloaded_file.fastq.gz
# 出力例: d41d8cd98f00b204e9800998ecf8427e  downloaded_file.fastq.gz

# チェックサムファイルと一括照合
md5sum -c checksums.md5
```

`md5sum` はファイルのMD5ハッシュ値を計算する。`-c` オプションはチェックサムファイルに記載されたハッシュ値とファイルを照合する。SHA256を使う場合は `sha256sum` コマンドに置き換える。

Pythonでのチェックサム検証の実装は `scripts/ch19/checksum_verify.py` を参照されたい。`hashlib` モジュールを使い、ファイルをバッファ単位で読み込んでハッシュ値を計算する。

ダウンロード→検証→解凍の一連の流れを自動化することで、データの整合性を保証できる。

```bash
# ダウンロード → チェックサム検証 → 解凍の自動化パイプライン
wget -q "$URL" -O "$FILE" && \
  echo "$EXPECTED_MD5  $FILE" | md5sum -c - && \
  gunzip "$FILE"
```

### フラットファイルのパース

ダウンロードしたフラットファイルを解析に使うには、フォーマットに応じた**パーサ**（構文解析器）が必要である。バイオインフォマティクスのファイル形式は独自の仕様を持つため、パーサを自作するのではなく、実績あるライブラリを使うのが鉄則である（[§0 AIエージェントにコードを書かせる](./00_ai_agent.md)で述べた「車輪の再発明をしない」原則）。主要なフォーマットとライブラリの対応を以下に示す。

| フォーマット | ライブラリ | 関数/メソッド |
|---|---|---|
| GenBank (.gb/.gbk) | Biopython SeqIO | `SeqIO.parse(fh, "genbank")` |
| FASTA (.fasta/.fa) | Biopython SeqIO | `SeqIO.parse(fh, "fasta")` |
| GFF/GTF | gffutils / BCBio.GFF | `gffutils.create_db()` |
| VCF | pysam / cyvcf2 | `pysam.VariantFile()` |

[19-0節](#19-0-データベースの基礎知識--エージェントと同じ言語で話すために)で紹介したように、GenBank形式はFASTAと異なりfeature情報（CDS、gene、mRNA等のアノテーション）を含む。配列だけでなく遺伝子の座標や機能アノテーションが必要な場合はGenBank形式を選ぶ。

以下のコードは、GenBank形式のファイルをBiopythonの `SeqIO` でパースし、CDS（タンパク質をコードする領域）の遺伝子名と産物名を抽出する例である。`SeqIO.parse()` はファイルハンドルとフォーマット名を受け取り、`SeqRecord` オブジェクトを順に返すジェネレータである。各 `SeqRecord` の `features` 属性にアノテーション情報がリストとして格納されている。

```python
from Bio import SeqIO

# GenBankファイルを開いてパースする
# "genbank" はフォーマット指定（"fasta", "gff" 等も指定可能）
with open("sequence.gb") as fh:
    for record in SeqIO.parse(fh, "genbank"):
        print(f"ID: {record.id}, 長さ: {len(record.seq)} bp")

        # feature情報を走査してCDS（コーディング領域）を抽出
        for feature in record.features:
            if feature.type == "CDS":
                gene = feature.qualifiers.get("gene", ["N/A"])[0]
                product = feature.qualifiers.get("product", ["N/A"])[0]
                print(f"  CDS: {gene} — {product}")
```

`feature.qualifiers` は辞書型で、キーがqualifier名（`"gene"`, `"product"`, `"translation"` 等）、値が文字列のリストである。リストになっているのは同一qualifierが複数回出現し得るためであり、`.get("gene", ["N/A"])[0]` で最初の値を安全に取得している。

スクリプト `scripts/ch19/parse_flatfile.py` に、GenBankファイルからCDS情報を抽出する再利用可能な関数を実装した。この関数は `SeqRecord` から遺伝子名・産物名・位置情報を `dataclass` にまとめて返す。

#### エージェントへの指示例

ダウンロードしたフラットファイルのパースは、エージェントが得意とするタスクである。ただしフォーマットの選択と抽出結果の科学的妥当性は人間が確認すべきポイントである。

> 「FTPからダウンロードしたGenBankファイル（.gb）をBiopythonのSeqIOでパースし、全CDSの遺伝子名・産物名・座標をTSVに出力するスクリプトを書いて」

> 「GFF3ファイルからexonの座標を抽出してBED形式に変換するスクリプトを、gffutilsを使って書いて」

> 「VCFファイルをpysamで読み込み、染色体ごとのバリアント数を集計してCSV出力するスクリプトを書いて。フィルタ条件としてQUAL>=30を指定して」

### ローカルDB構築

ダウンロードしたデータを効率的に利用するために、ローカル環境にデータベースやインデックスを構築する。

#### BLASTデータベース

BLAST+の `makeblastdb` コマンドは、FASTAファイルからローカルBLASTデータベースを作成する。

```bash
# 塩基配列のBLASTデータベースを作成
# -dbtype nucl: 塩基配列（アミノ酸なら prot）
# -in: 入力FASTAファイル
# -out: 出力DB名
makeblastdb -in reference.fasta -dbtype nucl -out blastdb/reference

# 作成したDBに対してBLAST検索
blastn -query query.fasta -db blastdb/reference -outfmt 6 -evalue 1e-10
```

#### ゲノムインデックス

リードのアラインメントツールは、参照ゲノムのインデックスを事前に構築する必要がある。

```bash
# BWA: ゲノムインデックスの作成（DNA-seq用）
bwa index reference.fasta

# STAR: ゲノムインデックスの作成（RNA-seq用、メモリ大量消費に注意）
STAR --runMode genomeGenerate \
     --genomeDir star_index/ \
     --genomeFastaFiles reference.fasta \
     --sjdbGTFfile genes.gtf \
     --runThreadN 8

# HISAT2: ゲノムインデックスの作成（RNA-seq用、STARより省メモリ）
hisat2-build reference.fasta hisat2_index/reference
```

これらのインデックス構築は時間とディスク容量を消費するため、一度構築したら `data/reference/` ディレクトリに保管し、複数の解析で共有する。

#### SQLiteによるメタデータ管理

サンプルメタデータをCSVファイルで管理する方法は手軽だが、サンプル数が増えると検索やフィルタリングが煩雑になる。SQLiteを使えば、SQLクエリで柔軟にデータを操作できる。

以下は、CSVファイルからSQLiteデータベースにメタデータを読み込み、条件別に集計する例である（[§4 データフォーマットの選び方](./04_data_formats.md)で学んだCSVの扱いの発展形）。

```python
import sqlite3
import csv
from pathlib import Path

# SQLiteデータベースに接続（ファイルが存在しなければ新規作成）
conn = sqlite3.connect("samples.db")
conn.row_factory = sqlite3.Row  # 列名でアクセス可能にする

# テーブル作成
conn.execute("""
    CREATE TABLE IF NOT EXISTS samples (
        sample_id   TEXT PRIMARY KEY,
        accession   TEXT NOT NULL,
        organism    TEXT NOT NULL,
        condition   TEXT NOT NULL,
        replicate   INTEGER
    )
""")

# CSVから読み込み
with open("samples.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        conn.execute(
            "INSERT OR REPLACE INTO samples VALUES (?, ?, ?, ?, ?)",
            (row["sample_id"], row["accession"], row["organism"],
             row["condition"], int(row["replicate"])),
        )
conn.commit()

# 条件別にサンプル数を集計
for row in conn.execute(
    "SELECT condition, COUNT(*) as cnt FROM samples GROUP BY condition"
):
    print(f"{row['condition']}: {row['cnt']}件")
```

`sqlite3.connect` はファイルが存在しなければ新規作成する。`conn.row_factory = sqlite3.Row` を設定すると、結果を `row["列名"]` で辞書的にアクセスできる。`INSERT OR REPLACE` は同一主キーが存在する場合に上書きする。

完全な実装は `scripts/ch19/local_db.py` を参照されたい。

#### ディレクトリ構成のベストプラクティス

ダウンロードデータとローカルDBを管理するディレクトリ構成の推奨パターンを示す。

```
project/
├── data/
│   ├── raw/              # ダウンロードした生データ（変更禁止）
│   │   ├── fastq/
│   │   └── checksums.md5
│   ├── processed/        # 加工後のデータ
│   │   └── counts/
│   └── reference/        # 参照ゲノム、インデックス、BLASTdb
│       ├── GRCh38.fna
│       ├── star_index/
│       └── blastdb/
├── metadata/
│   ├── samples.csv       # サンプルメタデータ（テキスト）
│   └── samples.db        # SQLiteデータベース
└── results/
```

`data/raw/` は**読み取り専用**として扱い、ダウンロードした生データを変更しないことが鉄則である。加工後のデータは `data/processed/` に出力する。この原則を守ることで、いつでも生データからやり直すことができる。

#### エージェントへの指示例

大規模データのダウンロードとローカル管理は、定型的な処理が多いためエージェントとの協働に適している。

> 「このSRRアクセッション番号リスト（50件）から、prefetch + fasterq-dumpで並列ダウンロードするbashスクリプトを書いて。リトライとチェックサム検証も含めて」

> 「ダウンロードしたFASTAファイル群からBLASTデータベースを構築するMakefileを書いて」

> 「このサンプルメタデータCSVをSQLiteデータベースに格納し、条件でフィルタリングするPythonスクリプトを書いて」

---

> **🧬 コラム: データベースへの登録 — Vibe codingで登録準備を効率化する**
>
> 研究データの公開はFAIR原則[8](https://doi.org/10.1038/sdata.2016.18)（Findable, Accessible, Interoperable, Reusable）に従うことが求められる。ここでは、データベースへの登録の全体フローと、エージェントに依頼できる部分・人間が判断すべき部分を整理する。
>
> **登録の全体フロー**:
> 1. **DB選択**: データの種類に応じた登録先を選ぶ（配列→DDBJ/GenBank、リード→SRA/DRA、発現→GEO）
> 2. **メタデータ整備**: サンプル情報、実験条件、シーケンシングパラメータを所定の形式で記述
> 3. **ファイル準備**: データファイルの形式変換、ファイル名の整理
> 4. **アップロード**: FTPまたはWeb UIでファイルを転送
> 5. **公開設定**: 即時公開か、論文掲載まで非公開（hold）か
>
> **エージェントに依頼できること**:
> - GEOテンプレートのExcel/TSVへの変換スクリプト
> - ファイル名とメタデータの整合性チェックスクリプト
> - FTPアップロードスクリプトの生成
>
> **人間が判断すること**:
> - メタデータの科学的正確性（実験条件、生物種、組織型の正確な記述）
> - 公開範囲とタイミング（共同研究者との合意、論文投稿との調整）
> - 利用規約の確認（データ利用制限の有無）
>
> DOI付きでデータを公開する場合は、**Zenodo**（GitHubリポジトリとの連携が容易。[§7 Git入門](./07_git.md)参照）や **figshare** が利用できる。Zenodoは汎用的なデータリポジトリで、GitHubのリリースと連動してDOIを自動発行できる。figshareは図表やデータセットの公開に特化している。
>
> メタデータの設計については[§4 データフォーマットの選び方](./04_data_formats.md)、投稿前の最終チェックについては[付録C 論文投稿前チェックリスト](./appendix_c_checklist.md)も参照されたい。

---

## まとめ

本章では、公開データベースの基礎知識からAPI経由のデータ取得、ローカル環境でのデータ管理までを学んだ。

| 概念 | 要点 |
|------|------|
| **RDBとSQL** | テーブル形式のデータ管理。SELECT/JOIN/WHEREの語彙でエージェントへの指示を具体化 |
| **NoSQL** | キーバリュー・ドキュメント・グラフ型。パスウェイやPPIにはグラフ型が適する |
| **RDFとSPARQL** | トリプル形式のデータ表現とクエリ言語。UniProt等がSPARQLエンドポイントを公開 |
| **オントロジー** | GO IDで指示を正確化し、エンリッチメント結果の階層性を人間が判断 |
| **一次DB vs 二次DB** | GenBank（提出データそのまま）とRefSeq（キュレーション済み）の違い |
| **主要バイオDB** | NCBI系・欧州系・日本系。目的に応じたDB選択が人間の判断ポイント |
| **ID体系** | アクセッション番号のプレフィックスでデータ種類が分かる。バージョン指定で再現性確保 |
| **REST API** | HTTP経由のデータ取得。レート制限とAPIキー管理が必須 |
| **API firstの原則** | スクレイピングや全データDL前にREST APIの有無を確認。Entrez以外にもEnsembl・UCSC・TogoWS等が公開 |
| **NCBI Entrez** | esearch→efetch→elinkの3ステップ。Biopythonで簡潔に記述 |
| **チェックサム検証** | MD5/SHA256でダウンロードデータの整合性を保証 |
| **フラットファイルのパース** | GenBank/FASTA/GFF/VCF等のテキスト形式。SeqIO等の既存ライブラリでパース |
| **ローカルDB構築** | BLASTdb、ゲノムインデックス、SQLiteメタデータ管理 |
| **FAIR原則** | Findable, Accessible, Interoperable, Reusable。データ公開の基本方針 |

次章の[§20 コードとデータのセキュリティ・倫理](./20_security_ethics.md)では、APIキーの安全な管理方法や、患者データ・ヒトゲノムデータの取り扱いにおける倫理的配慮を学ぶ。

---

## さらに学びたい読者へ

本章で扱った公共データベースとAPIの利用をさらに深く学びたい読者に向けて、レビュー論文と公式リソースを紹介する。

### バイオデータベースの全体像

- **Sayers, E. W. et al. "Database resources of the National Center for Biotechnology Information". *Nucleic Acids Research*, 52(D1), D33–D43, 2024.** — NCBIのデータベースリソース全体を概説する年次レビュー。毎年更新されるため、最新の機能やデータベースの変更を把握できる。
- **Manzoni, C. et al. "Genome, transcriptome and proteome: the rise of omics data and their integration in biomedical sciences". *Briefings in Bioinformatics*, 19(2), 286–302, 2018.** — オミクスデータとデータベースの全体像を俯瞰するレビュー。各データベースの位置づけと統合の方向性を理解できる。

### APIの公式リファレンス

- **NCBI. "Entrez Programming Utilities Help".** https://www.ncbi.nlm.nih.gov/books/NBK25501/ — E-utilitiesの公式マニュアル。APIのパラメータ、レート制限、クエリ構文の完全なリファレンス。
- **Ensembl REST API Documentation.** https://rest.ensembl.org/ — EnsemblのREST APIドキュメント。エンドポイント一覧と使用例が対話的に試せる。

### プログラムからのデータアクセス

- **Biopython Tutorial and Cookbook.** https://biopython.org/wiki/Documentation — Biopythonの包括的チュートリアル。Entrez、SeqIO、Blast等のモジュールを使った公共データベースへのプログラマティックなアクセス方法が実践的に解説されている。

---

## 参考文献

[1] NCBI. "Entrez Programming Utilities (E-utilities)". https://www.ncbi.nlm.nih.gov/books/NBK25501/ (参照日: 2026-03-21)

[2] UniProt Consortium. "UniProt SPARQL endpoint". https://sparql.uniprot.org/ (参照日: 2026-03-21)

[3] Biopython Contributors. "Biopython Tutorial and Cookbook". https://biopython.org/wiki/Documentation (参照日: 2026-03-21)

[4] Ashburner, M. et al. "Gene Ontology: tool for the unification of biology". *Nature Genetics*, 25(1), 25-29, 2000. https://doi.org/10.1038/75556

[5] Kanehisa, M. & Goto, S. "KEGG: Kyoto Encyclopedia of Genes and Genomes". *Nucleic Acids Research*, 28(1), 27-30, 2000. https://doi.org/10.1093/nar/28.1.27

[6] Sayers, E. W. et al. "Database resources of the National Center for Biotechnology Information". *Nucleic Acids Research*, 52(D1), D33-D43, 2024. https://doi.org/10.1093/nar/gkad1044

[7] The UniProt Consortium. "UniProt: the Universal Protein Knowledgebase in 2023". *Nucleic Acids Research*, 51(D1), D523-D531, 2023. https://doi.org/10.1093/nar/gkac1052

[8] Wilkinson, M. D. et al. "The FAIR Guiding Principles for scientific data management and stewardship". *Scientific Data*, 3, 160018, 2016. https://doi.org/10.1038/sdata.2016.18

[9] DBCLS. "TogoWS: integrated SOAP/REST service for accessing biological databases". http://togows.org/ (参照日: 2026-03-21)

[10] NCBI. "SRA Toolkit". https://github.com/ncbi/sra-tools (参照日: 2026-03-21)

[11] NCBI. "NCBI Datasets". https://www.ncbi.nlm.nih.gov/datasets/ (参照日: 2026-03-21)

[12] NCBI. "Entrez Direct: E-utilities on the Unix Command Line". https://www.ncbi.nlm.nih.gov/books/NBK179288/ (参照日: 2026-03-21)

[13] Martin, F. J. et al. "Ensembl 2023". *Nucleic Acids Research*, 51(D1), D933-D941, 2023. https://doi.org/10.1093/nar/gkac958

[14] Nassar, L. R. et al. "The UCSC Genome Browser database: 2023 update". *Nucleic Acids Research*, 51(D1), D1188-D1195, 2023. https://doi.org/10.1093/nar/gkac1072

[15] Genomoncology. "BioMCP". https://github.com/genomoncology/biomcp (参照日: 2026-03-23)

[16] Kuo, J. "PubMed MCP Server". https://github.com/JackKuo666/PubMed-MCP-Server (参照日: 2026-03-23)

[17] MCPmed. "GEOmcp". https://github.com/MCPmed/GEOmcp (参照日: 2026-03-23)

[18] Augmented Nature. "UniProt MCP Server". https://github.com/Augmented-Nature/Augmented-Nature-UniProt-MCP-Server (参照日: 2026-03-23)

[19] Longevity Genie. "gget-MCP". https://github.com/longevity-genie/gget-mcp (参照日: 2026-03-23)

[20] Liu, Z. et al. "Biomni: A Generalist Biomedical AI Agent with 150+ Tools and Databases". *bioRxiv*, 2025. https://doi.org/10.1101/2025.05.30.656746
