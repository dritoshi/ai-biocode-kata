# §2 ターミナルとシェルの基本操作

[§1 設計原則 — 良いコードとは何か](./01_design.md)では、コードを「どう設計するか」の原則を学んだ。しかし原則を知っていても、コードを実行する場であるターミナルの仕組みを理解していなければ、エージェントが何をしているか把握できない。

AIコーディングエージェントは、シェルを介してコードを実行する。Claude Code や Codex CLI の動作を観察すると、ファイルの検索、パターンマッチング、内容の読み取りといったシェル操作が頻繁に行われている——内部的には `grep` や `find` の高速な代替ツールが使われることもあるが、基本概念は同じである。エージェントの行動をレビューし、問題が起きたときに原因を特定するためには、シェルの基礎知識が不可欠である。

本章では、「Linux入門書の縮小版」ではなく、**Vibe codingでエージェントの動作を理解するために必要なシェル知識**に焦点を絞る。ファイルシステムの構造、パーミッション、環境変数、テキスト処理コマンド、そしてシェルスクリプトの基礎——これらは、エージェントが日常的に操作する対象そのものである。

---

## 2-1. なぜVibe codingにシェルの知識が必要か

AIコーディングエージェントは、黒い画面の中でコマンドを叩いている。ユーザーが「このリポジトリの構成を理解して」と指示すると、エージェントは裏で以下のようなコマンドを実行する:

```bash
# エージェントが実行するコマンドの例
ls -la src/
find . -name "*.py" -type f
grep -r "import pandas" --include="*.py"
cat pyproject.toml
```

これらのコマンドの意味がわからなければ、エージェントが「何をしたか」を理解できない。エージェントが誤った場所を検索していても、不要なファイルを読んでいても、気づくことができない。

### シェルを知ることの3つの利点

1. **エージェントの行動を読める**: 思考過程に現れるコマンドの意味がわかる
2. **適切な指示ができる**: 「`grep` で探して」「`find` で `.fastq.gz` ファイルを列挙して」と具体的に伝えられる
3. **トラブルシューティングができる**: エージェントがエラーを出したとき、シェルレベルで原因を切り分けられる

### ターミナル、シェル、コマンドライン

混同されやすいこれらの用語を整理する:

- **ターミナル**（terminal）: コマンドを入力し、結果を表示するウィンドウ。macOSの「ターミナル.app」、Linuxの「GNOME Terminal」など
- **シェル**（shell）: ターミナルの中で動く、コマンドを解釈・実行するプログラム。`bash`、`zsh` などがある
- **コマンドライン**（command line）: シェルにコマンドを1行ずつ入力する操作方式。GUI（グラフィカルユーザーインターフェース）の対義語

macOSのデフォルトシェルは `zsh`、多くのLinuxディストリビューションでは `bash` がデフォルトである。本書のシェルコマンドは両方で動作するが、設定ファイルの名前が異なる（`bash` は `.bashrc`、`zsh` は `.zshrc`）。AIエージェントはどちらのシェルでも動作するため、本書では両方に言及する。

#### エージェントへの指示例

エージェントの思考過程を理解し、適切にレビューするための指示:

> 「このプロジェクトのファイル構成を調べて。どのコマンドを使ったか、なぜそのコマンドを選んだかも説明して」

> 「`data/` ディレクトリ以下にある `.fastq.gz` ファイルの一覧を、サイズ付きで表示して。使ったシェルコマンドも教えて」

> 「今の作業で使ったシェルコマンドを順番に説明して。それぞれ何をしているか理解したい」

---

## 2-2. ファイルシステムとパーミッション

### ディレクトリ構造

Linux/macOSのファイルシステムはツリー構造をしている。すべてのファイルとディレクトリは、ルート `/` を起点とする階層に配置される:

```
/
├── home/           # ユーザーのホームディレクトリ（Linuxの場合）
│   └── user/       # /home/user = ~（チルダ）
│       ├── projects/
│       │   └── rna_seq_analysis/
│       └── .bashrc
├── Users/          # macOSの場合（/home ではなく /Users）
│   └── user/
├── tmp/            # 一時ファイル（再起動で消える）
└── usr/
    └── local/
        └── bin/    # ユーザーがインストールしたコマンド
```

### 絶対パスと相対パス

ファイルの場所を指定する方法は2つある:

- **絶対パス**（absolute path）: ルートから始まるフルパス。`/home/user/projects/analysis.py`
- **相対パス**（relative path）: 現在地からの経路。`./data/reads.fastq` や `../shared/reference.fa`

エージェントに指示を出すとき、**絶対パス**を使うと曖昧さがなくなる。一方、プロジェクト内部では**相対パス**を使うことで、異なるマシンでも同じ構造で動作する:

```bash
# 絶対パス — 自分のマシン固有
python /home/user/projects/rna_seq/run_analysis.py

# 相対パス — プロジェクト内で完結（推奨）
python ./run_analysis.py
```

### パーミッションと実行権限

ファイルには「誰が」「何をできるか」を制御するパーミッション（permission）が設定されている:

```bash
$ ls -l run_analysis.py
-rw-r--r--  1 user group  1234 Mar 19 10:00 run_analysis.py
```

`-rw-r--r--` の意味:

| 位置 | 文字 | 意味 |
|------|------|------|
| 1 | `-` | ファイル種別（`-` = 通常ファイル、`d` = ディレクトリ） |
| 2-4 | `rw-` | 所有者（owner）: 読み取り(r)、書き込み(w)、実行なし(-) |
| 5-7 | `r--` | グループ（group）: 読み取りのみ |
| 8-10 | `r--` | その他（other）: 読み取りのみ |

バイオインフォマティクスで最も重要なのは**実行権限**（`x`）である。Pythonスクリプトをコマンドとして直接実行するには、2つのことが必要になる:

1. **shebang行**（シバン行）をスクリプトの先頭に書く
2. **実行権限**を付与する

```python
#!/usr/bin/env python3
"""RNA-seqデータの品質チェック."""
# このスクリプトは chmod +x で実行権限を付けると、直接実行できる
```

```bash
# 実行権限を付与
chmod +x run_analysis.py

# 直接実行（shebang行でPython3が呼ばれる）
./run_analysis.py

# 実行権限がなくても python コマンド経由なら動く
python run_analysis.py
```

`#!/usr/bin/env python3` は「PATHの中から `python3` を探して実行せよ」という意味である。`#!/usr/bin/python3` と直接パスを書く方法もあるが、`env` 経由のほうが環境の違いに対応しやすい（[§6 Python環境の構築 — pyenv・venv・conda・uv](./06_dev_environment.md)で詳しく扱う）。

### プロセスの基本

ターミナルで実行したコマンドは**プロセス**（process）として動作する。暴走したプロセスを止める方法だけ知っておけば、日常的な作業では十分である:

```bash
# 実行中のプロセスを強制終了: Ctrl+C
# バックグラウンドプロセスの確認
ps aux | grep python

# 特定のプロセスを終了（PID: プロセスID）
kill 12345
```

ジョブ管理（`&`、`nohup`、`bg`、`fg`）やスケジューリングの詳細は、HPC環境で必要になったときに[§16 スパコン・クラスタでの大規模計算](./16_hpc.md)で扱う。

### 圧縮と展開

バイオインフォマティクスのデータは巨大である。FASTQファイルは数十GBに達することがあり、**gzip圧縮**（`.gz`）された状態で配布・保管されるのが標準である。

```bash
# 圧縮
gzip reads.fastq          # → reads.fastq.gz（元ファイルは消える）
gzip -k reads.fastq       # → reads.fastq.gz（元ファイルを残す）

# 展開
gunzip reads.fastq.gz     # → reads.fastq

# 展開せずに中身を確認
zcat reads.fastq.gz | head -4    # 先頭4行（= 1リード分）を表示
zless reads.fastq.gz             # ページャで閲覧
```

`tar`（tape archive）は複数のファイルをまとめるコマンドで、`gzip` と組み合わせて使う:

```bash
# ディレクトリをまとめて圧縮（.tar.gz = .tgz）
tar czf analysis_results.tar.gz results/

# 展開
tar xzf analysis_results.tar.gz
```

多くのバイオインフォマティクスツール（BWA、STAR、samtools等）は `.fastq.gz` を直接読める。Pythonでも `gzip` モジュールを使えば、展開せずに処理できる:

```python
import gzip
from pathlib import Path

from scripts.ch02.fastq_gzip import count_reads_in_gzip

# gzipファイルを直接読む
fastq_gz = Path("reads.fastq.gz")
n_reads = count_reads_in_gzip(fastq_gz)
print(f"リード数: {n_reads}")
```

#### エージェントへの指示例

ファイルシステムや圧縮に関するエージェントへの指示:

> 「`data/` 以下の `.fastq.gz` ファイルの一覧と、それぞれのファイルサイズを表示して。圧縮状態のままリード数も数えて」

> 「このスクリプトを直接実行できるようにして。shebang行を追加して、実行権限を付ける手順も教えて」

> 「`results/` ディレクトリを `.tar.gz` に圧縮するシェルコマンドを教えて。圧縮後に中身を確認するコマンドも」

---

## 2-3. 環境変数とパス

### PATHが壊れるとエージェントがツールを見つけられない

`python` や `samtools` といったコマンドを名前だけで実行できるのは、シェルが**PATH環境変数**に登録されたディレクトリを順番に探すからである。PATHが壊れると、エージェントが `python: command not found` のようなエラーを出して動けなくなる。

```bash
# PATHの中身を確認
echo $PATH
# 出力例: /home/user/.local/bin:/usr/local/bin:/usr/bin:/bin

# コマンドがどこにあるか確認
which python3
# 出力例: /home/user/.local/bin/python3

# PATHにディレクトリを追加
export PATH="$HOME/.local/bin:$PATH"
```

PATHの仕組みを図示すると:

```
ユーザーが "python3" と入力
      ↓
シェルが PATH を左から順に検索:
  /home/user/.local/bin/python3  → ある！ → これを実行
  /usr/local/bin/python3         → （検索されない）
  /usr/bin/python3               → （検索されない）
```

### 環境変数の設定と永続化

**環境変数**（environment variable）は、シェルのセッション全体で使えるキーと値のペアである:

```bash
# 一時的な設定（ターミナルを閉じると消える）
export GENOME_DIR="/data/reference/hg38"

# 利用
echo $GENOME_DIR
# → /data/reference/hg38
```

設定を**永続化**するには、シェルの設定ファイルに書く:

```bash
# bash の場合: ~/.bashrc
# zsh の場合: ~/.zshrc

# ファイルの末尾に追加
echo 'export GENOME_DIR="/data/reference/hg38"' >> ~/.bashrc

# 設定を即座に反映
source ~/.bashrc
```

### .envファイルによるプロジェクト固有の設定

APIキーやデータベースパスなど、プロジェクト固有の設定は `.env` ファイルで管理する。**`.env` ファイルはGitにコミットしてはいけない**（[§20 コードとデータのセキュリティ・倫理](./20_security_ethics.md)で詳述する）:

```bash
# .env ファイルの例
DATABASE_URL=postgresql://localhost:5432/rnaseq
NCBI_API_KEY=abc123def456
DATA_DIR=/data/projects/rna_seq
```

```bash
# .gitignore に必ず追加
echo ".env" >> .gitignore
```

Pythonでは `python-dotenv` パッケージで `.env` ファイルを読み込める:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # .env ファイルを読み込む
api_key = os.getenv("NCBI_API_KEY")
```

### whichコマンド — 「どの」コマンドが使われているか

複数のPythonがインストールされている環境では、`which` で確認する習慣が重要である:

```bash
$ which python3
/home/user/miniconda3/envs/rnaseq/bin/python3

$ which samtools
/usr/local/bin/samtools
```

エージェントが予期しないバージョンのツールを使っている場合、`which` で原因を特定できる。

```python
from scripts.ch02.env_check import check_command_available, find_broken_path_entries

# コマンドの存在確認
check_command_available("python3")  # → True
check_command_available("samtools")  # → False（未インストールの場合）

# PATH内の壊れたエントリを検出
broken = find_broken_path_entries()
# → ['/home/user/old_conda/bin']（存在しないディレクトリ）
```

#### エージェントへの指示例

環境の問題をエージェントと一緒にデバッグする指示:

> 「`python3 --version` と `which python3` の結果を確認して。期待するバージョンは 3.10 以上」

> 「このプロジェクトで必要なコマンド（`python3`, `samtools`, `bedtools`, `fastqc`）がすべてインストールされているか確認して。見つからないものがあれば、インストール方法を教えて」

> 「`PATH` の設定を確認して、存在しないディレクトリが含まれていないかチェックして」

---

## 2-4. テキスト処理コマンド

バイオインフォマティクスのデータの多くはテキストファイルである。FASTA、FASTQ、BED、VCF、TSV——これらはすべてテキストとして処理できる。Pythonスクリプトを書く前に、シェルのワンライナーで解決できないか考える習慣は、作業効率を大きく向上させる。

また、AIエージェントの動作ログを読むと、これらの操作が頻繁に行われている。エージェントがコードベースを調査するとき、パターン検索（`grep` や高速版の `rg`）、ファイル列挙（`find` や `fd`）、行数カウント（`wc`）を実行する。コマンドの意味を知っていれば、エージェントの調査が適切かどうかを判断できる。

### コマンド一覧

| コマンド | 機能 | バイオインフォでの典型的な用途 |
|---------|------|-------------------------------|
| `grep` | パターンに一致する行を検索 | FASTAからIDを抽出: `grep "^>" sequences.fasta` |
| `awk` | フィールド単位のテキスト処理 | BEDの3列目を抽出: `awk '{print $3}' regions.bed` |
| `sed` | テキストの置換・削除 | ヘッダの形式変換: `sed 's/^>chr/>/' seq.fa` |
| `sort` | 行のソート | BEDを座標順に: `sort -k1,1 -k2,2n regions.bed` |
| `uniq` | 連続する重複行の除去 | 遺伝子名の集計: `sort genes.txt \| uniq -c` |
| `cut` | 列の抽出（区切り文字指定） | TSVの特定列: `cut -f1,3 expression.tsv` |
| `wc` | 行数・単語数・バイト数のカウント | ファイルの行数: `wc -l reads.fastq` |
| `find` | 条件に合うファイルを再帰的に検索 | 特定の拡張子: `find data/ -name "*.fastq.gz"` |
| `xargs` | 標準入力を引数として渡す | 一括処理: `find . -name "*.bam" \| xargs samtools index` |

### パイプによるコマンドの連結

シェルの真価は、パイプ（`|`）でコマンドを連結できることにある。[§1 設計原則 — 良いコードとは何か](./01_design.md#1-2-unix哲学)で学んだUNIX哲学——「1つのことをうまくやるプログラムを作り、それらを組み合わせる」——の実践そのものである。

```bash
# パターン1: FASTAのレコード数をカウント
grep -c "^>" sequences.fasta
# → 1234

# パターン2: TSVから遺伝子名の一覧を取得（重複除去・ソート済み）
cut -f1 counts.tsv | sort | uniq
# → BRCA1
# → TP53
# → ...

# パターン3: BEDファイルの染色体ごとの領域数を集計
awk '{print $1}' regions.bed | sort | uniq -c | sort -rn
# →  4521 chr1
# →  3892 chr2
# →  ...

# パターン4: gzip圧縮されたFASTQのリード数をカウント
zcat reads.fastq.gz | awk 'NR%4==1' | wc -l
# → 5000000

# パターン5: 全サンプルのBAMファイルにインデックスを作成
find results/ -name "*.bam" | xargs -I{} samtools index {}
```

### 「シェルで済む？」と聞く習慣

エージェントに「Pythonで実装して」と依頼する前に、一度立ち止まって考えてほしい。以下のような処理はシェルのワンライナーで十分なことが多い:

- ファイルの行数やレコード数のカウント
- 特定のパターンを含む行の抽出
- TSV/CSVの特定列の抽出
- ファイルの一覧取得とバッチ処理

一方、以下の場合はPythonのほうが適している:

- 複雑な条件分岐やエラーハンドリングが必要
- データの変換・加工が複数ステップにわたる
- 結果を再利用する（関数化・テスト可能にする）
- 他の人が読んで理解する必要がある

Pythonで同じ処理を書くとどうなるか——`scripts/ch02/text_processing.py` に対比用のコードを用意した:

```python
from pathlib import Path

from scripts.ch02.text_processing import (
    count_fasta_records,
    extract_column,
    grep_lines,
)

# grep "^>" sequences.fasta | wc -l  に相当
n_records = count_fasta_records(Path("sequences.fasta"))

# grep "BRCA" gene_list.txt  に相当
matches = grep_lines(Path("gene_list.txt"), pattern="BRCA")

# cut -f2 expression.tsv  に相当
values = extract_column(Path("expression.tsv"), column=1, delimiter="\t")
```

シェルのワンライナーは**一度きりの調査**に、Python関数は**再利用する処理**に向いている。

### 正規表現の基礎 — パターンで文字列を操る

ここまで紹介した `grep` や `sed` は、内部で**正規表現**（regular expression; regex）というパターン記述言語を使っている。正規表現は「決まった形式の文字列を探す・抽出する・置換する」ための共通言語であり、シェルコマンドだけでなくPythonの `re` モジュールでも同じ記法が使える。AIエージェントが生成するコードにも `re.search()` や `re.sub()` が頻繁に登場するため、基本的なパターンを読めるようにしておくことは重要である。

#### リテラルマッチとメタ文字

正規表現の最も単純な形は、検索したい文字列をそのまま書く**リテラルマッチ**である。`grep "BRCA" gene_list.txt` の `"BRCA"` は、文字どおり `BRCA` という文字列を探している。

これに加えて、特別な意味を持つ**メタ文字**を使うと、柔軟なパターンを記述できる:

| メタ文字 | 意味 | 例 | マッチする文字列 |
|---------|------|-----|----------------|
| `.` | 任意の1文字 | `A.G` | `ATG`, `ACG`, `AAG` |
| `*` | 直前の文字の0回以上の繰り返し | `AT*G` | `AG`, `ATG`, `ATTG` |
| `+` | 直前の文字の1回以上の繰り返し | `AT+G` | `ATG`, `ATTG`（`AG`は不一致） |
| `?` | 直前の文字の0回または1回 | `colou?r` | `color`, `colour` |
| `[]` | 文字クラス（いずれか1文字） | `[ACGT]` | `A`, `C`, `G`, `T` |
| `[^]` | 否定文字クラス | `[^ACGT]` | ACGT以外の任意の文字 |
| `^` | 行頭 | `^>` | FASTAのヘッダ行 |
| `$` | 行末 | `\*$` | 終止コドン（`*`で終わる行） |
| `\d` | 数字（`[0-9]`と同等） | `chr\d+` | `chr1`, `chr22` |
| `\s` | 空白文字（スペース、タブ等） | `gene\s+id` | `gene id`, `gene  id` |
| `\w` | 単語文字（`[a-zA-Z0-9_]`） | `\w+` | 連続する英数字 |

#### キャプチャグループ

丸括弧 `()` で囲んだ部分は**キャプチャグループ**と呼ばれ、マッチした文字列の一部を抽出できる。バイオインフォマティクスでは、ヘッダ行やアノテーションファイルから特定の情報を取り出す際に多用される。

バイオインフォマティクスでの具体例を見てみよう:

```python
import re

# FASTAヘッダからアクセッション番号を抽出する例
# (\w+\.\d+) は「英数字の連続 + ピリオド + 数字の連続」にマッチする
header = ">NM_007294.4 Homo sapiens BRCA1"
match = re.search(r">(\w+\.\d+)", header)
if match:
    accession = match.group(1)  # "NM_007294.4"

# GFF3のattributeからgene_idを抽出する例
# gene_id "([^"]+)" は「gene_id "」の後の引用符内の文字列を取得する
attribute = 'gene_id "ENSG00000012048"; transcript_id "ENST00000357654"'
match = re.search(r'gene_id "([^"]+)"', attribute)
if match:
    gene_id = match.group(1)  # "ENSG00000012048"
```

`re.search()` はパターンに最初にマッチした箇所を返す関数である。`r"..."` はPythonの**raw文字列**で、バックスラッシュをエスケープせずに書ける（正規表現ではバックスラッシュを多用するため、常にraw文字列を使う）。

#### Pythonの`re`モジュール — 最低限の3関数

Pythonで正規表現を使うには、標準ライブラリの `re` モジュールを使う。以下の3つの関数を覚えておけば大半の場面に対応できる:

| 関数 | 用途 | 戻り値 |
|------|------|--------|
| `re.search(pattern, string)` | 最初のマッチを検索 | `Match` オブジェクトまたは `None` |
| `re.findall(pattern, string)` | すべてのマッチをリストで返す | 文字列のリスト |
| `re.sub(pattern, repl, string)` | パターンにマッチした部分を置換 | 置換後の文字列 |

```python
import re

# re.findall(): FASTAファイルの全ヘッダからアクセッション番号を一括抽出
# 戻り値はキャプチャグループにマッチした文字列のリスト
fasta_text = ">NM_007294.4 BRCA1\nATGC\n>NM_000059.4 BRCA2\nGCTA\n"
accessions = re.findall(r">(\w+\.\d+)", fasta_text)
# ["NM_007294.4", "NM_000059.4"]

# re.sub(): 染色体名の形式を変換（"chr1" → "1"）
# r"chr" は文字列 "chr" にリテラルマッチし、空文字列に置換する
chrom = "chr1"
ensembl_chrom = re.sub(r"^chr", "", chrom)  # "1"
```

grepやsedのパターンと `re` モジュールのパターンは基本的に同じ記法である。シェルで試したパターンをそのままPythonに持ち込めるのが正規表現の強みである。

#### エージェントへの指示例

正規表現は強力だが、複雑なパターンは可読性が低くなりやすい。エージェントに正規表現を書かせる際は、何を抽出したいかを自然言語で明確に伝えることが重要である:

> 「GFF3ファイルの第9カラム（attributes）から `gene_id` の値を正規表現で抽出する関数を書いて。`gene_id "ENSG00000012048"` のようなフォーマットを想定して」

> 「FASTAヘッダ行（`>`で始まる行）からアクセッション番号（`NM_007294.4`のような`英数字.数字`のパターン）を`re.findall()`で抽出するワンライナーを書いて」

> 「エージェントが生成した `re.sub(r"(?<=\\t)([^\\t]+)(?=\\t)", r"\\1_modified", line)` というコードの意味を説明して。読みやすい形に書き換えられないかも検討して」

正規表現が複雑になる場合、`re.VERBOSE` フラグを使うとパターン内にコメントを書ける。エージェントにこのフラグでの記述を依頼すると、レビューしやすいコードが得られる。

#### エージェントへの指示例

テキスト処理コマンドを活用した指示:

> 「この処理をPythonで書く前に、シェルのワンライナーで実現できないか検討して。できるならワンライナーを提案して、できないならPythonで書いて」

> 「`data/counts.tsv` の1列目にある遺伝子名の一覧を重複なしで取得するシェルコマンドを教えて。同じ処理をPythonで書いた場合との比較も見せて」

> 「エージェントが `grep -r "TODO" --include="*.py"` を実行しているのを見た。このコマンドの意味と、なぜエージェントがこれを実行したのかを説明して」

> **📦 コラム: エージェントの内部で動く高速検索ツール — ripgrepとfd**
>
> §2-4で学んだ `grep` や `find` はUNIXの古典的コマンドだが、AIコーディングエージェントはこれらの高速な代替ツールを内部で使っている。
>
> **ripgrep**（`rg`）は `grep` のRust実装で、再帰検索が10〜50倍高速である[9]。Claude Codeの検索機能（Grepツール）はripgrepで実装されており、Codex CLIもripgrepに依存している（未インストールだと起動時にエラーになる）。最大の特徴は `.gitignore` を自動で尊重する点で、不要なファイル（`node_modules/` や `.git/` 内のファイル）を検索対象から除外してくれる。
>
> ```bash
> # grep での再帰検索
> grep -r "import pandas" --include="*.py" .
>
> # ripgrep での同等操作（.gitignore を自動尊重）
> rg "import pandas" --type py
> ```
>
> **fd** は `find` のRust実装で、直感的な構文と高速な検索が特徴である[10]。Claude Codeでも利用が推奨されている。
>
> ```bash
> # find でのファイル検索
> find . -name "*.fastq.gz" -type f
>
> # fd での同等操作
> fd ".fastq.gz"
> ```
>
> いずれも macOS では `brew install ripgrep fd` でインストールできる。従来コマンドの概念を理解していれば、これらの高速版も自然に使える——`rg` は「賢い `grep -r`」、`fd` は「省略形の `find`」と考えればよい。

---

## 2-5. シェルスクリプティングの基礎

ワンライナーでは収まらない一連の処理を自動化するのが**シェルスクリプト**である。バイオインフォマティクスでは、FASTQの前処理からマッピング、定量までの一連のステップをシェルスクリプトで記述することが多い。

ただし、**本格的なCLIツールはPythonで書くべきである**（[§11 コマンドラインツールの設計と実装](./11_cli.md)参照）。シェルスクリプトは「接着剤」——既存のツールを順番に呼び出す程度に留めるのがよい。

### set -euo pipefail — 安全なスクリプトの第一行

シェルスクリプトの先頭に必ず書くべきおまじないがある:

```bash
#!/bin/bash
set -euo pipefail
```

この1行で3つの安全策が有効になる:

| オプション | 意味 | なぜ重要か |
|-----------|------|-----------|
| `-e` | コマンドが失敗したら即座にスクリプトを停止 | エラーを無視して後続処理が壊れたデータで進むのを防ぐ |
| `-u` | 未定義の変数を参照するとエラー | タイポによる `$SAMPLE_NAEM`（`NAME` のつもり）を検出 |
| `-o pipefail` | パイプの途中でエラーが起きても検出 | `cmd1 \| cmd2` で `cmd1` の失敗を見逃さない |

**`set -euo pipefail` なしのスクリプトは、サイレントに失敗する**。データ解析でこれが起きると、誤った結果に気づかないまま論文に使ってしまう危険がある。

### シェルスクリプトの基本構造

```bash
#!/bin/bash
set -euo pipefail

# === 設定 ===
SAMPLE_ID="$1"                          # 第1引数をサンプルIDとして受け取る
FASTQ_DIR="data/fastq"
OUTPUT_DIR="results/${SAMPLE_ID}"

# === 前処理 ===
mkdir -p "${OUTPUT_DIR}"

# === 品質チェック ===
echo "品質チェック: ${SAMPLE_ID}"
fastqc "${FASTQ_DIR}/${SAMPLE_ID}_R1.fastq.gz" \
       -o "${OUTPUT_DIR}"

# === 完了 ===
echo "完了: ${SAMPLE_ID}"
```

### 変数

```bash
# 変数の代入（= の前後にスペースを入れない）
GENOME="hg38"
N_THREADS=8

# 変数の参照（${} で囲む — 安全のため常にこの形式を使う）
echo "ゲノム: ${GENOME}"
echo "スレッド数: ${N_THREADS}"

# コマンド置換 — コマンドの結果を変数に格納
TODAY=$(date +%Y%m%d)
N_READS=$(zcat reads.fastq.gz | awk 'NR%4==1' | wc -l)
```

### 条件分岐

```bash
# ファイルの存在確認
if [[ -f "${FASTQ_DIR}/${SAMPLE_ID}_R1.fastq.gz" ]]; then
    echo "FASTQファイルが見つかった"
else
    echo "エラー: FASTQファイルが見つからない" >&2
    exit 1
fi

# ディレクトリの存在確認
if [[ ! -d "${OUTPUT_DIR}" ]]; then
    mkdir -p "${OUTPUT_DIR}"
fi
```

### ループ

```bash
# 複数サンプルの一括処理
for SAMPLE in sample_A sample_B sample_C; do
    echo "処理中: ${SAMPLE}"
    fastqc "data/${SAMPLE}_R1.fastq.gz" -o results/
done

# ファイルを列挙してループ
for BAM_FILE in results/*.bam; do
    samtools index "${BAM_FILE}"
done
```

### シェルスクリプトとPythonの使い分け

| 観点 | シェルスクリプト | Python |
|------|----------------|--------|
| 適した用途 | 既存ツールの順次呼び出し | データの加工・解析ロジック |
| エラーハンドリング | 限定的（`set -e` 程度） | 充実（`try/except`、型チェック） |
| テストのしやすさ | 難しい | 容易（pytest） |
| 引数処理 | `$1`, `$2`（簡易） | argparse/click/typer（堅牢） |
| 可読性 | 短いなら良い、長いと辛い | 長くても構造化できる |

**目安: 50行を超えるシェルスクリプトはPythonで書き直すことを検討する。** [§11 コマンドラインツールの設計と実装](./11_cli.md)でargparseやtyperを使った本格的なCLI開発を学ぶ。

#### エージェントへの指示例

シェルスクリプトの作成・レビューに関する指示:

> 「この解析パイプラインをシェルスクリプトにまとめて。`set -euo pipefail` を含めて、各ステップにコメントを付けて」

> 「このシェルスクリプトをレビューして。`set -euo pipefail` が抜けていないか、未定義変数の参照がないか、パイプの途中でエラーが握りつぶされていないか確認して」

> 「このシェルスクリプトは100行を超えている。Pythonのtyper CLIに書き直す価値はあるか判断して。書き直すなら設計案を見せて」

---

> **📦 コラム: SSH・tmux・Vim — サーバ上でのVibe coding**
>
> バイオインフォマティクスの解析は、ローカルPCではなくリモートサーバやHPCクラスタ上で行うことが多い。ここでは、リモート作業に最低限必要な3つのツールを紹介する。詳細な設定やジョブ管理は[§16 スパコン・クラスタでの大規模計算](./16_hpc.md)で扱う。
>
> ### SSH — リモートサーバへの接続
>
> **SSH**（Secure Shell）は、リモートサーバに暗号化された接続を確立するプロトコルである:
>
> ```bash
> # 基本的な接続
> ssh user@server.example.com
>
> # SSH鍵の生成（パスワード認証より安全）
> ssh-keygen -t ed25519 -C "user@example.com"
> # → ~/.ssh/id_ed25519（秘密鍵）と ~/.ssh/id_ed25519.pub（公開鍵）が生成される
>
> # 公開鍵をサーバに登録
> ssh-copy-id user@server.example.com
> ```
>
> 接続先が多い場合は `~/.ssh/config` で管理すると便利である:
>
> ```
> # ~/.ssh/config
> Host hpc
>     HostName hpc.university.ac.jp
>     User tanaka
>     IdentityFile ~/.ssh/id_ed25519
> ```
>
> これで `ssh hpc` だけで接続できるようになる。
>
> ### tmux — 接続断からの復帰
>
> **tmux**（terminal multiplexer）は、ターミナルセッションをサーバ側に保持するツールである。SSH接続が切れても、tmuxセッション内のプロセスは動き続ける:
>
> ```bash
> # 新しいセッションを開始
> tmux new -s analysis
>
> # セッションから離脱（detach）: Ctrl+B, D
> # ← SSHが切れてもセッションは生きている
>
> # セッションに再接続（attach）
> tmux attach -t analysis
>
> # セッション一覧
> tmux ls
> ```
>
> 長時間かかるバイオインフォの解析（マッピング、アセンブリなど）は、必ずtmux内で実行する。
>
> ### Vim — サーバ上でのファイル編集
>
> サーバ上でちょっとした設定ファイルの編集が必要になることがある。**Vim** は、ほぼすべてのLinuxサーバにプリインストールされているテキストエディタである。最低限の操作だけ覚えておく:
>
> | 操作 | キー | 説明 |
> |------|------|------|
> | 編集開始 | `i` | 挿入モードに入る（文字を入力できる） |
> | 編集終了 | `Esc` | ノーマルモードに戻る |
> | 保存して終了 | `:wq` + `Enter` | write & quit |
> | 保存せず終了 | `:q!` + `Enter` | 変更を破棄して終了 |
>
> Vimに不慣れな場合は `nano` エディタのほうが直感的である。`nano ~/.bashrc` のように使える。

---

## さらに学びたい読者へ

本章で扱ったターミナル操作やシェルの仕組みをさらに深く学びたい読者に向けて、定番の教科書とオンラインリソースを紹介する。

### シェル・コマンドラインの教科書

- **Shotts, W. E. *The Linux Command Line: A Complete Introduction* (5th Internet Edition). 2019.** — 本章の参考文献 [1] で引用。全文が無料公開されている（https://linuxcommand.org/tlcl.php）。本章で扱ったコマンドの背景知識（パーミッション、プロセス管理、シェルスクリプト）を体系的に学べる。
- **Janssens, J. *Data Science at the Command Line* (2nd ed.). O'Reilly, 2021.** — 本章の参考文献 [2] で引用。コマンドラインをデータ分析ツールとして使い倒す手法を紹介する。全文がオンラインで無料公開されている（https://jeroenjanssens.com/dsatcl/）。

### バイオインフォマティクスのコマンドライン実践

- **Buffalo, V. *Bioinformatics Data Skills*. O'Reilly, 2015.** — バイオインフォマティクス研究者のための計算スキルの教科書。特に Part I（Ideology: Data Skills for Robust and Reproducible Bioinformatics）と Part II（Prerequisites: Essential Skills for Getting Started with a Bioinformatics Project）が本章と直結する。awk/sed の実践例が豊富。
- **Haddock, S. H. D., Dunn, C. W. *Practical Computing for Biologists*. Sinauer Associates, 2011.** — 正規表現の解説が特に手厚い教科書。本章で概要を扱った正規表現をFASTAヘッダーのパースやパターンマッチングに実践的に応用する際に最適である。

### オンライン講義

- **MIT. "The Missing Semester of Your CS Education".** https://missing.csail.mit.edu/ — シェル、エディタ、データ加工（Data Wrangling）、コマンドライン環境に関する講義動画と演習問題がすべて無料公開されている。

---

## 参考文献

[1] Shotts, W. E. *The Linux Command Line: A Complete Introduction*. 5th Internet Edition, 2019. [https://linuxcommand.org/tlcl.php](https://linuxcommand.org/tlcl.php)

[2] Janssens, J. *Data Science at the Command Line*. 2nd ed., O'Reilly Media, 2021. [https://jeroenjanssens.com/dsatcl/](https://jeroenjanssens.com/dsatcl/)

[3] Buffalo, V. *Bioinformatics Data Skills*. O'Reilly Media, 2015. ISBN 978-1449367374

[4] Wilson, G. et al. "Best Practices for Scientific Computing". *PLOS Biology*, 12(1), e1001745, 2014. [https://doi.org/10.1371/journal.pbio.1001745](https://doi.org/10.1371/journal.pbio.1001745)

[5] Anthropic. "Claude Code Documentation". [https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) (参照日: 2026-03-19)

[6] GNU Coreutils. "GNU Core Utilities". [https://www.gnu.org/software/coreutils/manual/](https://www.gnu.org/software/coreutils/manual/) (参照日: 2026-03-19)

[7] "Bash Reference Manual". GNU Project. [https://www.gnu.org/software/bash/manual/](https://www.gnu.org/software/bash/manual/) (参照日: 2026-03-19)

[8] Heng Li. "lh3/seqtk: Toolkit for processing sequences in FASTA/Q formats". GitHub. [https://github.com/lh3/seqtk](https://github.com/lh3/seqtk) (参照日: 2026-03-19)

[9] Gallant, A. "ripgrep is faster than {grep, ag, git grep, ucg, pt, sift}". 2016. [https://blog.burntsushi.net/ripgrep/](https://blog.burntsushi.net/ripgrep/) (参照日: 2026-03-19)

[10] Peterka, D. "sharkdp/fd: A simple, fast and user-friendly alternative to 'find'". GitHub. [https://github.com/sharkdp/fd](https://github.com/sharkdp/fd) (参照日: 2026-03-19)
