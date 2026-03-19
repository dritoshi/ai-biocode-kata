# 4. データフォーマットの判断力

[§3 計算機科学の基礎知識](./03_cs_basics.md)では、データ構造・浮動小数点・乱数といった、プログラムの正しさと性能を左右する基礎概念を学んだ。本章では視点を「プログラムの内部」から「プログラムの外部」に移す。解析の入力と出力——つまり**ファイル**の扱いである。エージェントにデータ変換を依頼するとき、入出力フォーマットを正しく指定できるかどうかで結果の品質が決まる。

データ分析の80%はデータの整備と前処理に費やされる——Wickham (2014) が引用したこの経験則 [[8]](https://doi.org/10.18637/jss.v059.i10) [[15]](https://doi.org/10.1002/0471448354) は、CrowdFlower の2016年の調査でも裏付けられている [[16]](https://visit.figure-eight.com/data-science-report.html)。60%のデータサイエンティストがデータクリーニングに最も時間を使い、57%がそれを最も楽しくない作業と回答した。本章で学ぶフォーマット選択と機械可読データへの変換は、この「80%」を削減するための基盤技術である。

バイオインフォマティクスのパイプラインは、ファイルの受け渡しで成り立っている。FASTQ → BAM → VCF → TSV という変換連鎖の中で、「なぜこのフォーマットなのか」「なぜCSVではなくTSVなのか」「なぜバイナリなのか」を判断できることは、正しいパイプラインを設計する第一歩である。本章では、汎用フォーマットの基本から、フォーマット選択の判断基準、そしてデータを「機械が読める形」に整える技術までを扱う。

---

## 4-0. データとメタデータ

### データとメタデータの定義

データフォーマットを議論する前に、「データ」と「メタデータ」の区別を明確にしておこう。

- **データ**（data）: 解析対象そのもの。塩基配列、発現量行列、変異コールの結果など。
- **メタデータ**（metadata）: データについてのデータ。サンプル名、実験条件、シーケンサーの機種、ライブラリ調製日など。

メタデータは「データの説明書」のようなものである。同じ発現量行列でも、どの組織から・どの条件で・いつ取得したのかがわからなければ、解析結果の解釈は不可能である。

重要なのは、**データとメタデータの境界は文脈によって変わる**ことである。たとえば、サンプルの年齢情報は「発現量解析」の文脈ではメタデータだが、「年齢と遺伝子発現の関係を調べる」解析ではデータそのものになる。

### バイオインフォマティクスでの具体例

以下の表に、主要なデータ形式とそれに付随するメタデータの例を示す:

| データ | メタデータの所在 | メタデータの例 |
|--------|----------------|--------------|
| FASTQファイル（配列リード） | サンプルシート（CSV/TSV） | サンプル名、バーコード、レーン番号 |
| BAMファイル（アラインメント） | RGヘッダ（`@RG`行） | サンプルID、ライブラリ名、プラットフォーム |
| AnnData（.h5ad） | `.obs`（細胞メタデータ） | 細胞タイプ、バッチ、クラスター |
| VCFファイル（変異） | `##`ヘッダ行 | リファレンスゲノム、フィルター条件、ツールバージョン |

データ本体とメタデータが**同一ファイルに格納される**場合（BAMのRGヘッダ、VCFの`##`行）と、**別ファイルで管理する**場合（FASTQとサンプルシート）がある。どちらの設計にも一長一短があるが、共通して重要なのは「データとメタデータを常にペアで管理する」ことである。メタデータを失ったデータは、解釈不能になる。

---

## 4-1. 汎用フォーマット

バイオインフォマティクス専用のフォーマット（FASTQ, BAM, VCF等）を学ぶ前に、まず汎用的なデータフォーマットを押さえよう。これらはバイオインフォに限らず、あらゆるデータ処理の基盤となる。

### TSV / CSV — 表形式データの基本

**TSV**（Tab-Separated Values）と **CSV**（Comma-Separated Values）は、表形式データの最も基本的なフォーマットである[1](https://www.rfc-editor.org/rfc/rfc4180)。

| 特徴 | TSV | CSV |
|------|-----|-----|
| 区切り文字 | タブ（`\t`） | カンマ（`,`） |
| エスケープ | 基本不要 | フィールド内のカンマは `"` で囲む |
| バイオでの普及度 | 高い（BED, VCF, BLAST出力等） | Excel互換が必要な場面 |

バイオインフォマティクスでは**TSVが圧倒的に多い**。理由は単純で、遺伝子名やアノテーション文字列にカンマが含まれることがあるからである。タブ文字はデータ内にまず現れないため、エスケープの問題が起きにくい。

Pythonでの読み書きには標準ライブラリの `csv` モジュールを使う[2](https://docs.python.org/3/library/csv.html):

```python
from scripts.ch04.tsv_csv_handling import read_expression_tsv, write_expression_csv
from pathlib import Path

# TSVの読み込み
records = read_expression_tsv(Path("expression.tsv"))
# → [{"gene": "TP53", "sample_A": "10.5", ...}, ...]

# CSVへの書き出し
write_expression_csv(records, Path("expression.csv"))
```

**ヘッダ行**は必ず1行目に置く。ヘッダがないTSV/CSVは機械処理を困難にするだけでなく、人間にとっても列の意味が不明になる。

[§3 計算機科学の基礎知識](./03_cs_basics.md)の§3-2で学んだCSV round-tripの問題もここで再確認しよう。浮動小数点数をCSVに書き出し→読み込みを繰り返すと精度が劣化する:

```python
from scripts.ch04.tsv_csv_handling import csv_roundtrip_precision

# π の値を10回 round-trip させる
tracking = csv_roundtrip_precision([3.141592653589793], n_trips=10)
# tracking[0] と tracking[10] を比較して精度劣化を確認
```

中間データの保存にはバイナリ形式（`.npy`, `.h5ad`, `.parquet`）を使い、CSVは最終出力や他ツールとの受け渡しにのみ使うのが鉄則である。

### JSON — 構造化データ

**JSON**（JavaScript Object Notation）は、キーと値のペアやネスト構造を表現できるフォーマットである[3](https://docs.python.org/3/library/json.html)。Webの世界で広く使われており、バイオインフォマティクスでは主にAPIレスポンスの形式として登場する。

```python
import json

# NCBI E-utilities のレスポンス（例）
response_text = '{"result": {"uids": ["12345", "67890"]}}'
data = json.loads(response_text)
gene_ids = data["result"]["uids"]
# → ["12345", "67890"]
```

NCBI E-utilities、Ensembl REST API、UniProt APIなど、主要なバイオデータベースのAPIはJSONでデータを返す。[§18 データベースとAPI](./18_database_api.md)で詳しく扱う。

JSONの特徴:
- **ネスト構造**: 表形式では表現しにくい階層的なデータを自然に表現できる
- **型**: 文字列、数値、真偽値、null、配列、オブジェクトの6型
- **改行・空白**: データ的には無意味だが、`json.dumps(data, indent=2)` で人間にも読みやすくできる

### YAML / TOML — 設定ファイル

解析パイプラインの設定ファイルには、**YAML**や**TOML**が使われる。

**YAML**はインデントベースの記法で、Snakemake/Nextflowのワークフロー定義やConda環境ファイル（`environment.yml`）に広く使われる:

```yaml
# config.yaml（Snakemakeの設定例）
samples:
  - sample_A
  - sample_B
reference:
  genome: /data/ref/hg38.fa
  annotation: /data/ref/gencode.v44.gtf
threads: 8
```

**TOML**はPython 3.11以降で標準ライブラリの `tomllib` で読み込める[4](https://docs.python.org/3/library/tomllib.html)。`pyproject.toml` がその代表例である:

```toml
# pyproject.toml
[project]
name = "my-bioinfo-tool"
version = "0.1.0"
requires-python = ">=3.10"

[project.dependencies]
biopython = ">=1.83"
numpy = ">=1.26"
```

YAMLとTOMLの使い分け:
- **YAML**: ネスト構造が深い設定、リストを多用する場面。ただしインデントミスがバグの原因になりやすい
- **TOML**: 型が明確（文字列、整数、浮動小数点、日付等を区別）。Pythonプロジェクトの設定標準

### Markdown — ドキュメント記述

**Markdown**は、プレーンテキストで書けるドキュメント記述言語である。GitHubのREADME、AIコーディングエージェントの設定ファイル（CLAUDE.md, AGENTS.md等）、そして本書自体がMarkdownで書かれている。

Markdownが優れている点:
- **テキストとして読める**: レンダリングなしでも内容が把握できる
- **バージョン管理と相性が良い**: テキストファイルなのでGitのdiffが効く
- **AIエージェントが読み書きできる**: プロジェクトの設定やドキュメントをAIと共有する最も自然な手段

> **🧬 コラム: Excelと遺伝子名 — Oct4問題**
>
> Excelは、遺伝子名を日付やその他のデータ型に**自動変換**してしまうという、バイオインフォマティクス界で悪名高い問題を抱えている。
>
> 2016年、Ziemann らは主要なゲノム研究ジャーナルの論文を調査し、約20%の補足ファイルに遺伝子名の変換エラーが含まれていることを報告した[5](https://doi.org/10.1186/s13059-016-1044-7)。たとえば:
>
> - `MARCH1`（Membrane Associated Ring-CH-Type Finger 1）→ Excelが `3月1日` に変換
> - `SEPT1`（Septin 1）→ `9月1日` に変換
> - `DEC1`（Deleted In Esophageal Cancer 1）→ `12月1日` に変換
> - `OCT4`（POU5F1の別名）→ `10月4日` に変換
>
> 2021年のフォローアップ調査では、問題はまったく改善していないことが示された[6](https://doi.org/10.1371/journal.pcbi.1008984)。
>
> この問題を受けて、HUGO Gene Nomenclature Committee（HGNC）は2020年に27の遺伝子を正式にリネームした[7](https://www.genenames.org/about/guidelines/):
>
> | 旧名 | 新名 | 理由 |
> |------|------|------|
> | MARCH1 | MARCHF1 | 3月に変換される |
> | SEPT1 | SEPTIN1 | 9月に変換される |
> | DEC1 | DELEC1 | 12月に変換される |
>
> 遺伝子名が変わるほど深刻な問題であり、教訓は明確である:
>
> - **CSVファイルをExcelで開かない**。プログラム（Python, R）で処理する
> - やむを得ずExcelを使う場合は、列を「文字列」として読み込む設定にする
> - データの受け渡しにExcelファイル（`.xlsx`）を使わず、TSV/CSVをプログラムで処理する

> #### 🧬 コラム: 日本語環境の罠 — Shift_JIS, BOM, ファイル名のNFD
>
> [§3-3 文字エンコーディング](./03_cs_basics.md#3-3-文字エンコーディング)では、ASCII/UTF-8の基礎と `encoding="utf-8"` を明示する原則を学んだ。ここでは、日本の研究室で特に遭遇しやすい3つの実践的な罠を取り上げる。
>
> ---
>
> **1. Shift_JIS/CP932 レガシーデータ**
>
> Windows版Excelで「CSVとして保存」すると、デフォルトのエンコーディングはShift_JIS(CP932)になる。`open()` で `encoding` を省略すると、macOS/LinuxではUTF-8として読もうとして `UnicodeDecodeError` が発生する。
>
> ```python
> # Shift_JIS(CP932)のCSVを読み込む
> with open("excel_output.csv", encoding="cp932", newline="") as f:
>     reader = csv.DictReader(f)
>     records = list(reader)
> ```
>
> `encoding="utf-8"` で `UnicodeDecodeError` が出たら、まずShift_JIS(CP932)を疑うとよい。
>
> ---
>
> **2. UTF-8 BOM**（バイトオーダーマーク）
>
> Windows版Excelで「UTF-8でCSV保存」を選択すると、ファイル先頭にBOM(`\xef\xbb\xbf`)が付与される。このBOMをPythonの `csv.DictReader` が処理すると、先頭列名に見えない文字 `\ufeff` が紛れ込む。
>
> ```python
> # BOMの罠: 列名が "\ufeffgene" になってしまう
> with open("excel_utf8.csv", encoding="utf-8") as f:
>     reader = csv.DictReader(f)
>     row = next(reader)
>     print(list(row.keys()))  # ['\ufeffgene', 'value'] — 先頭に不可視文字
> ```
>
> 対処は `encoding="utf-8-sig"` を使うことである。BOMがあれば自動除去し、なければ通常のUTF-8として読み込む:
>
> ```python
> # BOM対応: encoding="utf-8-sig" でBOMを自動除去
> with open("excel_utf8.csv", encoding="utf-8-sig", newline="") as f:
>     reader = csv.DictReader(f)
>     row = next(reader)
>     print(list(row.keys()))  # ['gene', 'value'] — 正常
> ```
>
> ---
>
> **3. macOSのファイル名NFD正規化**
>
> macOS(APFS)は日本語ファイル名をNFD（分解形）で格納する。NFDでは濁点・半濁点が独立したコードポイントに分離されるため、「が」は「か」+「゛」の2文字として保存される。Linux/WindowsはNFC（合成形）を使うため、同じファイル名に見えても `==` で比較すると一致しない。
>
> ```python
> import unicodedata
>
> # macOSから受け取ったファイル名（NFD）
> macos_name = "\u304b\u3099"  # か + 濁点（NFD）
> linux_name = "が"            # が（NFC）
>
> print(macos_name == linux_name)  # False — 見た目は同じなのに不一致
>
> # NFC正規化で一致させる
> normalized = unicodedata.normalize("NFC", macos_name)
> print(normalized == linux_name)  # True
> ```
>
> ---
>
> **まとめ**
>
> | 罠 | 発生源 | 対処法 |
> |---|---|---|
> | Shift_JIS/CP932 | Windows Excelの「CSV保存」 | `encoding="cp932"` で読み込み |
> | UTF-8 BOM | Windows Excelの「UTF-8 CSV保存」 | `encoding="utf-8-sig"` で自動除去 |
> | ファイル名NFD | macOSのファイルシステム | `unicodedata.normalize("NFC", name)` |
>
> gzip圧縮ファイルでもエンコーディングの問題は同様に発生する。`gzip.open()` でテキストモードを使う場合は `encoding` を明示する:
>
> ```python
> import gzip
>
> # gzip + エンコーディング明示
> with gzip.open("data.csv.gz", "rt", encoding="utf-8") as f:
>     reader = csv.DictReader(f)
>     records = list(reader)
> ```
>
> **防衛策**:
>
> - ファイル名はASCIIのみにする。日本語のサンプル名はメタデータTSVの列で管理する
> - `open()` には必ず `encoding="utf-8"` を明示する（[§3-3](./03_cs_basics.md#3-3-文字エンコーディング)の原則）
> - Windows由来のCSVは `encoding="utf-8-sig"` で開くことを最初に試みる

#### エージェントへの指示例

フォーマット変換やデータ処理をエージェントに依頼する際は、入力と出力の形式を明示する:

> 「`expression.tsv` を読み込んで、遺伝子名の列を基準にlong form（tidy data）に変換するスクリプトを書いてください。出力形式はTSVで、列は `gene`, `sample`, `value` としてください」

> 「この `config.yaml` をPythonで読み込んで型チェックするバリデーション関数を書いてください。必須キー（`samples`, `reference`）の存在確認と型チェックを行い、エラーがあれば具体的なメッセージを返してください」

JSONレスポンスの処理を依頼する場合:

> 「NCBI E-utilities APIからJSON形式でレスポンスを取得し、遺伝子IDのリストを抽出するスクリプトを書いてください。エラーハンドリング（HTTPエラー、JSON解析エラー）も含めてください」

---

## 4-2. フォーマット選択の判断基準

### テキスト vs バイナリ

データフォーマットは大きく**テキスト形式**と**バイナリ形式**に分かれる。どちらを選ぶかは、以下の基準で判断する:

| 基準 | テキスト（TSV, CSV, JSON等） | バイナリ（BAM, .npy, .h5ad等） |
|------|---------------------------|------------------------------|
| 人間の可読性 | そのまま読める | 専用ツールが必要 |
| diff / grep | 直接使える | 不可（専用コマンドが必要） |
| 数値精度 | 変換時に劣化しうる | ビット単位で完全保持 |
| ファイルサイズ | 大きい（数値の桁数分の文字） | 小さい |
| デバッグしやすさ | `head`, `less` で確認可能 | `samtools view` 等が必要 |

原則として:
- **中間データ**（パイプラインのステップ間）→ **バイナリ**（精度保持、サイズ削減）
- **最終出力**（人間が確認、他ツールに渡す）→ **テキスト**（可読性、互換性）
- **設定ファイル**→ **テキスト**（Gitで差分管理、手動編集）

[§3 計算機科学の基礎知識](./03_cs_basics.md)の§3-2で学んだCSV round-trip問題は、この判断基準の具体的な実例である。浮動小数点数を繰り返しテキストに変換することで精度が劣化するため、中間データはバイナリで保存すべきなのである。

### 圧縮の選択

バイオインフォマティクスのデータは巨大である。ヒトゲノムの全ゲノムシーケンス（WGS, 30x）のFASTQファイルは非圧縮で100 GBを超える。圧縮は必須だが、どの圧縮アルゴリズムを選ぶかが重要である。

| 圧縮形式 | 拡張子 | 特徴 | 主な用途 |
|---------|--------|------|---------|
| gzip | `.gz` | 最も普及、ほぼすべてのツールが対応 | `.fastq.gz`, `.vcf.gz` |
| bgzf | `.gz` | gzip互換だがブロック分割、インデックス可能 | BAM, tabix対応VCF |
| zstd | `.zst` | gzipより高速で高圧縮率 | 新しいパイプライン |

`gzip` はバイオインフォマティクスのデファクトスタンダードである。迷ったら `gzip` を選べば間違いない。`bgzf`（Blocked GNU Zip Format）はgzipと互換性がありつつ、ブロック単位でランダムアクセスできるようにしたもので、BAMファイルやtabixでインデックスされたVCFファイルの内部で使われている。

### インデックス付きフォーマットの利点

ゲノムの特定領域だけを取り出したい場合、ファイル全体を読む必要があるだろうか？　**インデックス**があれば、目的の箇所に直接ジャンプできる。

| データ | インデックス | 作成コマンド |
|--------|------------|------------|
| FASTA | `.fai` | `samtools faidx ref.fa` |
| BAM | `.bai` | `samtools index aln.bam` |
| bgzf圧縮TSV | `.tbi` | `tabix -p bed data.bed.gz` |

インデックスなしで特定のゲノム領域を検索するには、ファイルの先頭から最後まで全走査($O(n)$)が必要である。インデックスがあれば、目的の位置に直接アクセスできる($O(\log n)$)。ファイルが大きいほど、この差は圧倒的になる。

```bash
# インデックスなし: chr1:1000000-1000100 を探すために全BAMを走査
# → 数十GBのBAMファイルで数分〜数十分

# インデックスあり: 目的の領域に直接ジャンプ
samtools view aln.bam chr1:1000000-1000100  # → 一瞬
```

**原則**: BAMファイルを生成したら、必ず `.bai` インデックスも生成する。FASTAファイルを使うなら `.fai` を作る。これはパイプラインの一部として自動化すべきである。

### 下流ツールから逆算する

フォーマット選択で最も実践的な判断基準は、**下流のツールが何を受け付けるか**から逆算することである。

| 下流の目的 | 受け付ける形式 | 出力すべき形式 |
|-----------|--------------|--------------|
| DESeq2で差異発現解析 | カウント行列（TSV） | TSV（遺伝子×サンプル） |
| IGVでアラインメント可視化 | BAM + BAI | ソート済みBAM + インデックス |
| MAFFTで多重配列アラインメント | FASTA | FASTA |
| pandasで統計解析 | CSV / TSV / Parquet | 用途に応じて選択 |

「データの変換は最小限にする」が原則である。A形式 → B形式 → C形式という変換連鎖は、各ステップで情報損失やバグ混入のリスクがある。下流ツールの入力形式を確認し、**最短経路**でその形式に到達するパイプラインを設計する。

### 機械可読なデータ形式の条件

人間が見やすいデータと、プログラムが処理しやすいデータは異なる。**機械可読**（machine-readable）なデータ形式には、以下の4つの条件がある:

1. **1行1レコード**: 1つの観測・サンプルが1行に対応する
2. **ヘッダが1行目**: 列名は最初の1行のみ。タイトル行や空行が上にない
3. **セル結合なし**: 結合されたセルはプログラムで正しく読めない
4. **型の一貫性**: 1つの列は同じデータ型（数値の列に文字列が混在しない）

以下の表で、人間向けレイアウトと機械可読形式を比較する:

| 特徴 | 人間向けレイアウト | 機械可読形式 |
|------|------------------|------------|
| タイトル行 | ファイル先頭に「実験日: 2026-01-15」等 | なし（メタデータは別管理） |
| セル結合 | グループ名を結合して見やすく | 全セルに値が入る |
| 空行 | セクション区切りに空行 | 空行なし |
| 集計行 | 末尾に「合計」「平均」行 | なし（集計はコードで行う） |
| 列名 | 「発現量 (TPM)\n(Sample A)」 | `expression_tpm_sample_a` |

### AIコーディングエージェントで機械可読形式に変換する

実験系研究者がExcelで作成したサンプルシートは、しばしば人間向けレイアウトになっている。これを機械可読形式に変換する作業は、AIコーディングエージェントが得意とするタスクである。

典型的な「人間向けExcel」の問題:
- 1行目にタイトル（「RNA-seq実験 サンプル情報」）、2行目が空、3行目からヘッダ
- グループ名が結合セル（Control が3行分結合されている）
- 列名に改行やスペースが含まれる（「Sample\nID」）

AIエージェントへの変換依頼プロンプト例:

```
このサンプルシート（messy_samples.csv）を機械可読な形式に変換してください。

要件:
- ヘッダは3行目（0-indexed で2）にある
- グループ列の結合セルを前方充填する
- 列名の空白をアンダースコアに正規化する
- 空行を除去する
- 変換後のデータを validate_tidy_table() で検証する
```

コード例:

```python
from scripts.ch04.messy_to_tidy import normalize_sample_sheet, validate_tidy_table

# 人間向けレイアウトのデータ（Excelから読んだ想定）
messy_rows = [
    ["RNA-seq実験", "", ""],           # タイトル行
    ["", "", ""],                       # 空行
    ["Group", "Sample ID", "Value"],    # ヘッダ（3行目）
    ["Control", "S001", "10.5"],
    ["", "S002", "12.3"],               # 結合セル（Group が空）
    ["Treatment", "S003", "20.1"],
    ["", "S004", "22.8"],               # 結合セル
]

# 正規化（ヘッダは index=2）
records = normalize_sample_sheet(messy_rows, header_row_index=2)
# → [{"Group": "Control", "Sample_ID": "S001", "Value": "10.5"},
#    {"Group": "Control", "Sample_ID": "S002", "Value": "12.3"},  ← 前方充填
#    {"Group": "Treatment", "Sample_ID": "S003", "Value": "20.1"},
#    {"Group": "Treatment", "Sample_ID": "S004", "Value": "22.8"}]

# バリデーション
errors = validate_tidy_table(records, ["Group", "Sample_ID", "Value"])
assert errors == [], f"バリデーションエラー: {errors}"
```

**「AIの出力を信用するな。検証せよ」**——これは[§0 AIコーディングエージェントとの協働](./00_ai_agent.md)で学んだPlan → Code → Reviewワークフローの核心である。AIエージェントが生成した変換コードは、必ずバリデーション関数で検証する。

### tidy data

**tidy data**（整然データ）は、Wickham (2014) が提唱したデータの整理原則である[8](https://doi.org/10.18637/jss.v059.i10):

1. **各変数**（variable）が1つの列に対応する
2. **各観測**（observation）が1つの行に対応する
3. **各観測単位**（observational unit）が1つの表に対応する

この原則に従ったデータは**long form**と呼ばれ、統計処理やプロットに直接使える形になる。対照的に、人間が見やすい横長の表は**wide form**と呼ばれる。

**wide form**（人間が読みやすい）:

| gene | sample_A | sample_B | sample_C |
|------|----------|----------|----------|
| TP53 | 10.5 | 20.3 | 15.1 |
| BRCA1 | 5.2 | 8.1 | 6.7 |

**long form**（tidy data）:

| gene | variable | value |
|------|----------|-------|
| TP53 | sample_A | 10.5 |
| TP53 | sample_B | 20.3 |
| TP53 | sample_C | 15.1 |
| BRCA1 | sample_A | 5.2 |
| BRCA1 | sample_B | 8.1 |
| BRCA1 | sample_C | 6.7 |

pandasの `melt()` と `pivot_table()` で相互変換できる:

```python
from scripts.ch04.tidy_data_demo import wide_to_long, long_to_wide

# wide → long
wide_data = [
    {"gene": "TP53", "sample_A": "10.5", "sample_B": "20.3"},
    {"gene": "BRCA1", "sample_A": "5.2", "sample_B": "8.1"},
]
long_data = wide_to_long(wide_data, id_col="gene", value_cols=["sample_A", "sample_B"])
# → [{"gene": "TP53", "variable": "sample_A", "value": "10.5"}, ...]

# long → wide
restored = long_to_wide(long_data, id_col="gene", variable_col="variable", value_col="value")
```

wide form と long form のどちらが適切かは、下流の処理によって決まる。seabornやggplot2でのプロットにはlong formが必要で、DESeq2のカウント行列はwide formが入力形式である。重要なのは、**両者を自由に行き来できるスキル**を持つことである。

> **🧬 コラム: バイオインフォの主要フォーマット**
>
> 自分でパーサを書く前に、各フォーマットの標準を知ること。以下はバイオインフォマティクスで日常的に扱う形式の一覧である。
>
> | カテゴリ | 形式 | 注意点 |
> |---------|------|--------|
> | 配列 | FASTA, FASTQ | FASTAインデックス（`.fai`）でランダムアクセス可能 |
> | マッピング | SAM/BAM/CRAM[9](https://doi.org/10.1093/bioinformatics/btp352) | BAM+BAIが日常使い。FLAGフィールドはビットフラグ |
> | アノテーション | BED[10](https://genome.ucsc.edu/FAQ/FAQformat.html#format1), GFF3/GTF[11](https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md) | **BED=0-based half-open**, **GFF=1-based closed** — 混同は致命的バグの元 |
> | 変異 | VCF/BCF[12](https://doi.org/10.1093/bioinformatics/btr330) | ヘッダ行（`##`）の構造を理解する |
> | MSA | FASTA, Clustal, Stockholm, PHYLIP | ツール間の変換は `Biopython AlignIO` or EMBOSS `seqret` |
> | BLAST出力 | outfmt 6/7（タブ区切り） | カラムはカスタマイズ可能。XML (outfmt 5) はプログラムパース向け |
> | シグナル | BigWig, BedGraph | ゲノムカバレッジ・ChIPシグナル等 |
> | シングルセル | AnnData (.h5ad) | `.X`（行列）, `.obs`（細胞）, `.var`（遺伝子） |
> | 系統樹 | Newick, Nexus | 括弧表記 `((A,B),C);` |
>
> **座標系の違い**は、バイオインフォマティクスで最も多いバグ源の一つである:
>
> | 座標系 | 開始位置 | 終了位置 | 例: 10番目の塩基 | 使用フォーマット |
> |--------|---------|---------|----------------|----------------|
> | 0-based half-open | 0から数える | 含まない | [9, 10) | BED, BAM, Python |
> | 1-based closed | 1から数える | 含む | [10, 10] | GFF, VCF, SAM, R |
>
> BEDファイルの `chr1 9 10` とGFFファイルの `chr1 10 10` は同じ塩基を指している。フォーマット間で座標を変換するときは、この違いを常に意識すること。

> **🧬 コラム: 座標系の罠 — 0-based vs 1-based**
>
> なぜ同じゲノム位置を指すのに2つの座標系が存在するのか。
> 歴史的に、UCSCゲノムブラウザが採用したBED形式はC言語や
> Pythonと同じ0-based indexingを使い、区間を半開区間
> [start, end) で表す。一方、GFFやVCFは生物学者にとって直感的な
> 1-based closed区間 [start, end] を採用した。
>
> 0-based half-openの利点:
> - 区間の長さ = `end - start`（引き算だけで計算可能）
> - 隣接する区間を隙間なく並べられる: [0,5) + [5,10) = [0,10)
> - Pythonのスライス `seq[start:end]` とそのまま対応する
>
> 1-based closedの利点:
> - 「10番目の塩基」を `10` と書ける（人間の直感に合う）
> - 論文やラボノートの記述と一致する
>
> 問題は、パイプライン内で**複数のフォーマットが混在する**ときに起きる。
> pysamでBAMから取得した座標は0-basedだが、それをVCFの
> POSフィールドに書くなら+1する必要がある。
> 以下は典型的なoff-by-oneバグの例である:
>
> ```python
> # ❌ 誤り: BAM（0-based）の座標をそのままGFFに書いている
> for read in pysam.AlignmentFile("input.bam"):
>     print(f"chr1\t.\tgene\t{read.reference_start}\t{read.reference_end}")
>
> # ✅ 正しい: GFF（1-based closed）に変換
> for read in pysam.AlignmentFile("input.bam"):
>     print(f"chr1\t.\tgene\t{read.reference_start + 1}\t{read.reference_end}")
> ```
>
> | ライブラリ/ツール | 内部座標系 | 注意点 |
> |-----------------|-----------|--------|
> | pysam | 0-based | `reference_start` は0-based、SAM出力時に自動で+1 |
> | pyranges | 0-based half-open | BEDと同じ。GFF読み込み時に自動変換 |
> | pybedtools | 0-based half-open | BEDToolsのラッパー |
> | Biopython SeqFeature | 0-based half-open | Pythonスライスと一致 |
>
> **実践ルール**: プロジェクト内で座標系を1つに統一し、
> CLAUDE.mdやREADMEに明記する。迷ったらBED形式（0-based half-open）を
> 選ぶ。Pythonのスライスと一致するため、変換ミスが減る。
>
> BED↔GFF座標変換の具体的な実装は [`scripts/ch04/coordinate_convert.py`](../../scripts/ch04/coordinate_convert.py) を参照。

#### エージェントへの指示例

フォーマット選択やデータ変換はエージェントが得意とする領域だが、バイオインフォ特有の罠（座標系、エンコーディング、Oct4問題）を知らないと誤った変換をすることがある。以下のように前提条件を明示する:

> 「BED形式（0-based half-open）のファイルをGFF3形式（1-based closed）に変換するスクリプトを書いてください。座標系の変換を正しく行ってください」

> 「この人間向けレイアウトのExcelサンプルシートを機械可読なTSVに変換してください。ヘッダは3行目にあり、グループ列の結合セルは前方充填してください。変換後にバリデーション関数で検証してください」

下流ツールの入力形式から逆算した設計を依頼する場合:

> 「DESeq2の入力となるカウント行列（遺伝子×サンプルのwide form TSV）を、featureCountsの出力ファイルから生成するスクリプトを書いてください」

---

## まとめ

本章で学んだデータフォーマットの判断基準を一覧にまとめる:

| 判断場面 | 推奨 | 理由 |
|---------|------|------|
| 表形式の区切り文字 | TSV | データ内にカンマが含まれうる |
| 中間データの保存 | バイナリ（.npy, .h5ad） | 精度保持、サイズ削減 |
| 最終出力 | テキスト（TSV, CSV） | 可読性、他ツールとの互換性 |
| 設定ファイル | YAML or TOML | Gitで差分管理、人間が編集 |
| 圧縮 | gzip（迷ったら） | 最も広く対応されている |
| 大規模ファイルの部分取得 | インデックス付き形式 | $O(\log n)$で目的箇所にアクセス |
| フォーマット選択の起点 | 下流ツールの入力形式 | 変換連鎖の最小化 |
| データの整理 | tidy data（long form） | 統計処理・可視化に直結 |
| データの前処理 | 機械可読形式に変換 | 4条件: 1行1レコード、ヘッダ1行目、結合なし、型統一 |

データフォーマットの「正解」はコンテキストによって変わる。重要なのは、各フォーマットの特性を理解し、**目的に応じて合理的に選択できる判断力**を身につけることである。

次章の[§5 開発環境の構築](./05_dev_environment.md)では、Pythonの環境管理やエディタの設定など、実際にコードを書き始めるための準備を整える。

---

## 参考文献

[1] Shafranovich, Y. "Common Format and MIME Type for Comma-Separated Values (CSV) Files". RFC 4180. [https://www.rfc-editor.org/rfc/rfc4180](https://www.rfc-editor.org/rfc/rfc4180) (参照日: 2026-03-18)

[2] Python Software Foundation. "csv --- CSV File Reading and Writing". *Python 3 Documentation*. [https://docs.python.org/3/library/csv.html](https://docs.python.org/3/library/csv.html) (参照日: 2026-03-18)

[3] Python Software Foundation. "json --- JSON encoder and decoder". *Python 3 Documentation*. [https://docs.python.org/3/library/json.html](https://docs.python.org/3/library/json.html) (参照日: 2026-03-18)

[4] Python Software Foundation. "tomllib --- Parse TOML files". *Python 3 Documentation*. [https://docs.python.org/3/library/tomllib.html](https://docs.python.org/3/library/tomllib.html) (参照日: 2026-03-18)

[5] Ziemann, M., Eren, Y., El-Osta, A. "Gene name errors are widespread in the scientific literature". *Genome Biology*, 17(1), 177, 2016. [https://doi.org/10.1186/s13059-016-1044-7](https://doi.org/10.1186/s13059-016-1044-7)

[6] Abeysooriya, M., Soria, M., Kasu, M. S., Ziemann, M. "Gene name errors: Lessons not learned". *PLOS Computational Biology*, 17(7), e1008984, 2021. [https://doi.org/10.1371/journal.pcbi.1008984](https://doi.org/10.1371/journal.pcbi.1008984)

[7] HUGO Gene Nomenclature Committee. "Guidelines for Human Gene Nomenclature". [https://www.genenames.org/about/guidelines/](https://www.genenames.org/about/guidelines/) (参照日: 2026-03-18)

[8] Wickham, H. "Tidy Data". *Journal of Statistical Software*, 59(10), 1–23, 2014. [https://doi.org/10.18637/jss.v059.i10](https://doi.org/10.18637/jss.v059.i10)

[9] Li, H. et al. "The Sequence Alignment/Map format and SAMtools". *Bioinformatics*, 25(16), 2078–2079, 2009. [https://doi.org/10.1093/bioinformatics/btp352](https://doi.org/10.1093/bioinformatics/btp352)

[10] UCSC Genome Browser. "BED format". [https://genome.ucsc.edu/FAQ/FAQformat.html#format1](https://genome.ucsc.edu/FAQ/FAQformat.html#format1) (参照日: 2026-03-18)

[11] The Sequence Ontology Project. "GFF3 Specification". [https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md](https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md) (参照日: 2026-03-18)

[12] Danecek, P. et al. "The variant call format and VCFtools". *Bioinformatics*, 27(15), 2156–2158, 2011. [https://doi.org/10.1093/bioinformatics/btr330](https://doi.org/10.1093/bioinformatics/btr330)

[13] SAM/BAM Format Specification Working Group. "Sequence Alignment/Map Format Specification". [https://samtools.github.io/hts-specs/SAMv1.pdf](https://samtools.github.io/hts-specs/SAMv1.pdf) (参照日: 2026-03-18)

[14] Kent, W. J. et al. "The Human Genome Browser at UCSC". *Genome Research*, 12(6), 996–1006, 2002. [https://doi.org/10.1101/gr.229102](https://doi.org/10.1101/gr.229102)

[15] Dasu, T., Johnson, T. *Exploratory Data Mining and Data Cleaning*. Wiley, 2003. [https://doi.org/10.1002/0471448354](https://doi.org/10.1002/0471448354)

[16] CrowdFlower. "2016 Data Science Report". 2016. [https://visit.figure-eight.com/data-science-report.html](https://visit.figure-eight.com/data-science-report.html) (参照日: 2026-03-18)
