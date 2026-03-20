# §12 ワークフロー管理

[§11 可視化](./11_visualization.md)では、matplotlib・seabornによるプロットの作成と、科学的可視化の原則を学んだ。しかし、データ処理と可視化のスクリプトが個別ファイルのまま増えていくと、「どのスクリプトをどの順番で実行するのか」「入力ファイルが更新されたらどこまで再実行すればよいのか」という管理上の問題が生じる。

この問題を解決するのが**ワークフロー言語**（workflow language）である。ワークフロー言語は処理ステップ間の依存関係を宣言的に記述し、実行順序の決定・並列化・途中からの再開をエンジンに委ねる仕組みである。代表的なツールとしてSnakemake、Nextflow、makeがあり、いずれもバイオインフォマティクスのパイプライン構築で広く使われている。

AIエージェントはSnakemakeやNextflowのコードを生成できる。しかし、ルール間の依存関係が正しいか、wildcard展開がサンプルリストと一致しているか、中間ファイルの管理方針が適切か——これらの設計判断は、パイプラインの全体像を把握している人間がレビューしなければならない。

本章では、ワークフロー言語（Snakemake、Nextflow、make）の基礎と、再現可能なパイプラインを設計するためのベストプラクティスを学ぶ。

---

## 12-1. なぜワークフロー言語が必要か

### シェルスクリプトの限界

RNA-seq解析を例に考える。典型的なパイプラインは以下の7ステップで構成される:

1. QC（FastQC）
2. アダプター除去・トリミング（Trimmomatic）
3. リファレンスへのマッピング（STAR）
4. BAMのソート・インデックス（samtools）
5. リードカウント（featureCounts）
6. 差次的発現解析（DESeq2）
7. 可視化（[§11 可視化](./11_visualization.md)のVolcano plot等）

これをシェルスクリプトで書くと、以下のような問題に直面する:

```bash
#!/bin/bash
# run_pipeline.sh — シェルスクリプトによるRNA-seqパイプライン（問題のある例）

SAMPLES="SRR1234501 SRR1234502 SRR1234503"

for sample in $SAMPLES; do
    fastqc data/raw/${sample}.fastq.gz -o results/qc/
    trimmomatic SE data/raw/${sample}.fastq.gz results/trimmed/${sample}_trimmed.fastq.gz \
        ILLUMINACLIP:TruSeq3-PE.fa:2:30:10 LEADING:3 TRAILING:3 MINLEN:36
    STAR --runThreadN 8 --genomeDir data/raw/genome/star_index \
         --readFilesIn results/trimmed/${sample}_trimmed.fastq.gz \
         --readFilesCommand zcat --outSAMtype BAM SortedByCoordinate \
         --outFileNamePrefix results/aligned/${sample}_
    featureCounts -T 4 -a data/raw/genome/GRCh38.gtf \
        -o results/counts/${sample}_counts.txt \
        results/aligned/${sample}_Aligned.sortedByCoord.out.bam
done
```

一見動きそうに見えるが、実用上の問題が3つある:

**部分的な再実行ができない。** STARのマッピングが3サンプル目で失敗した場合、スクリプト全体を最初から再実行するか、手動で失敗箇所を特定して部分実行するしかない。サンプル数が数十になると、この手動管理は破綻する。

**サンプル展開が手動である。** サンプルリストの変更がスクリプト先頭のハードコーディングに依存している。設定ファイルからの読み込みも可能だが、「どのサンプルが完了済みか」の追跡は自前で実装する必要がある。

**HPC並列化が困難である。** 各サンプルのマッピングは独立に実行できるが、シェルスクリプトのforループでは逐次実行になる。HPCのジョブスケジューラに投入するには、ジョブ間の依存関係を手動で記述しなければならない。

### 依存関係の自動解決 — DAGとしてのワークフロー

ワークフロー言語は、処理を**DAG**（Directed Acyclic Graph; 有向非巡回グラフ）として定義する。各処理ステップ（ノード）は入力と出力を宣言し、ワークフローエンジンがファイルの依存関係を自動的に解決する。

```
fastqc ──────────────────────────────────┐
                                         ├─→ all
trimmomatic ──→ star_align ──→ featurecounts ─┘
```

この構造には3つの利点がある:

1. **変更されたルールだけ再実行**: 出力ファイルのタイムスタンプを入力と比較し、更新が必要なルールだけを実行する
2. **並列実行**: 独立したルール（上図のfastqcとtrimmomatic）を自動的に並列実行する
3. **途中再開**: `--rerun-incomplete`（Snakemake）や`-resume`（Nextflow）で、失敗箇所から再開できる

### 導入タイミング

[§8 成果物の形式とプロジェクト設計](./08_deliverables.md)のパターン4（シェルスクリプト）からパターン5（ワークフロー言語）への移行サインを思い出そう:

- サンプルごとにコマンドをコピペしている
- 途中で失敗したら最初からやり直している
- HPCのジョブ管理が手動になっている

これらに1つでも心当たりがあれば、ワークフロー言語への移行を検討する時期である。逆に、ステップが2〜3個で固定、サンプルも1つだけという場合は、シェルスクリプトやMakefileで十分である。

#### エージェントへの指示例

パイプラインの複雑化に気づいたとき、エージェントに移行の判断材料を求めることができる:

> 「`run_pipeline.sh` を読んで、ステップ間の依存関係をDAGとして図示してください。Snakemakeへの移行が妥当か、判断材料を整理してください」

> 「このシェルスクリプトの各ステップを、Snakemakeのruleに変換してください。`config.yaml` でサンプルリストとパラメータを外出しにして、各ルールに `log:` ディレクティブを付けてください」

> 「現在のパイプラインは5サンプルですが、今後50サンプルに増える予定です。スケーラビリティの観点から、シェルスクリプトのままで問題になる箇所を指摘してください」

---

## 12-2. ワークフロー言語

### Snakemake — Pythonベースのワークフロー言語

Snakemake[1](https://doi.org/10.12688/f1000research.29032.2)[4](https://snakemake.readthedocs.io/)はPythonベースのワークフロー言語で、バイオインフォマティクス分野で最も広く使われているものの一つである。「ruleベースのMake」とも呼ばれ、GNU makeの概念をPythonの文法で拡張したものと考えるとわかりやすい。

#### ruleの基本構造

Snakemakeのワークフローは**rule**（ルール）の集合として定義する。各ルールは `input`（入力）、`output`（出力）、`shell`（実行コマンド）の3要素で構成される:

```python
rule fastqc:
    input:
        "data/raw/{sample}.fastq.gz",
    output:
        html="results/qc/{sample}_fastqc.html",
        zip="results/qc/{sample}_fastqc.zip",
    log:
        "logs/fastqc/{sample}.log",
    threads: 4
    shell:
        "fastqc {input} --outdir results/qc --threads {threads} 2> {log}"
```

このルールは以下のように読める:

- **入力**: `data/raw/{sample}.fastq.gz` — `{sample}` はwildcard（後述）
- **出力**: `results/qc/` 以下にFastQCのHTML・ZIPレポート
- **ログ**: `logs/fastqc/{sample}.log` — 標準エラー出力を保存
- **実行**: `fastqc` コマンドを4スレッドで実行

Snakemakeは「出力ファイルから逆算して」必要なルールを決定する。最終的に欲しい出力を `rule all` の `input` に列挙する:

```python
rule all:
    input:
        expand("results/counts/{sample}_counts.txt", sample=SAMPLES),
        expand("results/qc/{sample}_fastqc.html", sample=SAMPLES),
```

#### wildcards — サンプル展開の自動化

`{sample}` は**wildcard**（ワイルドカード）と呼ばれ、Snakemakeがファイル名のパターンから自動的に値を推定する。`expand()` 関数と組み合わせることで、サンプルリストからすべての出力パスを生成できる:

```python
# config.yamlからサンプルリストを読み込む
configfile: "config.yaml"
SAMPLES = config["samples"]  # ["SRR1234501", "SRR1234502", "SRR1234503"]

# expand()でサンプルごとの出力パスを生成
# → ["results/counts/SRR1234501_counts.txt",
#    "results/counts/SRR1234502_counts.txt",
#    "results/counts/SRR1234503_counts.txt"]
expand("results/counts/{sample}_counts.txt", sample=SAMPLES)
```

シェルスクリプトのforループと異なり、wildcardの利点は:

- サンプルの追加は `config.yaml` を編集するだけでよい
- 各サンプルの処理が独立に並列実行される（`snakemake -j 8` で8並列）
- 完了済みサンプルは自動的にスキップされる

#### 設定ファイル — パラメータの外出し

`configfile:` ディレクティブで設定ファイルを読み込み、パラメータをワークフロー定義から分離する:

```yaml
# config.yaml
samples:
  - SRR1234501
  - SRR1234502
  - SRR1234503

genome:
  fasta: "data/raw/genome/GRCh38.fa"
  gtf: "data/raw/genome/GRCh38.gtf"
  index: "data/raw/genome/star_index"

params:
  star:
    threads: 8
    overhang: 100
  featurecounts:
    strandedness: 2
```

Snakefileからは `config["genome"]["gtf"]` のようにアクセスする。これにより、異なるリファレンスゲノムや異なるパラメータセットでの実行が、Snakefileの修正なしに可能になる。コマンドラインから `--config samples='["s1","s2"]'` のように上書きすることもできる。

#### conda / container統合

Snakemakeはルールごとにconda環境やコンテナを指定できる:

```python
rule deseq2:
    input:
        counts=expand("results/counts/{sample}_counts.txt", sample=SAMPLES),
    output:
        "results/deg/deseq2_results.csv",
    log:
        "logs/deseq2.log",
    conda:
        "envs/deseq2.yaml"  # このルール専用のconda環境
    script:
        "scripts/run_deseq2.R"
```

`conda:` ディレクティブを使うと、`snakemake --use-conda` 実行時にルールごとに隔離された環境が自動作成される。これは[§13 コンテナと再現性](./13_container.md)で詳しく扱う再現性確保の第一歩である。`container:` ディレクティブでDockerやApptainerイメージを指定することもできる。

#### Snakefileの完全な例

本書のサンプルコード（`scripts/ch12/Snakefile`）に、QC → トリミング → マッピング → 定量の4ステップで構成されるRNA-seqワークフローの完全な例を配置している。以下にその構造を示す:

```python
configfile: "config.yaml"

SAMPLES = config["samples"]

rule all:
    input:
        expand("results/counts/{sample}_counts.txt", sample=SAMPLES),
        expand("results/qc/{sample}_fastqc.html", sample=SAMPLES),

rule fastqc:
    input:
        "data/raw/{sample}.fastq.gz",
    output:
        html="results/qc/{sample}_fastqc.html",
        zip="results/qc/{sample}_fastqc.zip",
    log:
        "logs/fastqc/{sample}.log",
    threads: config["params"]["fastqc"]["threads"]
    shell:
        "fastqc {input} --outdir results/qc --threads {threads} 2> {log}"

rule trimmomatic:
    input:
        "data/raw/{sample}.fastq.gz",
    output:
        trimmed=temp("results/trimmed/{sample}_trimmed.fastq.gz"),
    log:
        "logs/trimmomatic/{sample}.log",
    # ... パラメータはconfig.yamlから読み込み
    shell:
        "trimmomatic SE {input} {output.trimmed} ... 2> {log}"

rule star_align:
    input:
        fastq="results/trimmed/{sample}_trimmed.fastq.gz",
        index=config["genome"]["index"],
    output:
        bam=temp("results/aligned/{sample}_Aligned.sortedByCoord.out.bam"),
    log:
        "logs/star/{sample}.log",
    threads: config["params"]["star"]["threads"]
    shell:
        "STAR --runThreadN {threads} ... 2> {log}"

rule featurecounts:
    input:
        bam="results/aligned/{sample}_Aligned.sortedByCoord.out.bam",
        gtf=config["genome"]["gtf"],
    output:
        counts="results/counts/{sample}_counts.txt",
    log:
        "logs/featurecounts/{sample}.log",
    shell:
        "featureCounts -a {input.gtf} -o {output.counts} {input.bam} 2> {log}"
```

注目すべきポイント:

- **`temp()`**: trimmomatic・star_alignの出力に `temp()` を付けている。下流のルールが完了すると中間ファイルが自動削除され、ディスク使用量を抑えられる
- **`log:`**: 全ルールにlog:ディレクティブがあり、実行ログが `logs/` に保存される
- **`configfile:`**: パラメータがすべて `config.yaml` から読み込まれている

---

### Nextflow — チャネルベースのワークフロー言語

Nextflow[2](https://doi.org/10.1038/nbt.3820)[5](https://www.nextflow.io/docs/latest/)はDSL2構文を採用したワークフロー言語で、データの流れを**チャネル**（channel）として表現する。Snakemakeの「ファイルベース」の依存解決とは設計思想が異なる。

#### DSL2の基本構文

Snakemakeのfastqcルールに対応するNextflowのprocess定義を示す:

```groovy
// fastqc.nf — Nextflow DSL2

params.samples = ["SRR1234501", "SRR1234502", "SRR1234503"]
params.outdir  = "results"

process FASTQC {
    publishDir "${params.outdir}/qc", mode: 'copy'

    input:
    path(fastq)

    output:
    path("*_fastqc.html"), emit: html
    path("*_fastqc.zip"),  emit: zip

    script:
    """
    fastqc ${fastq} --outdir .
    """
}

workflow {
    ch_fastq = Channel.fromPath("data/raw/*.fastq.gz")
    FASTQC(ch_fastq)
}
```

Snakemakeとの主な違い:

| 観点 | Snakemake | Nextflow |
|------|-----------|----------|
| 依存解決 | ファイルパスのパターンマッチ | チャネルによるデータの受け渡し |
| 記法 | Python風（Snakefileの中でPythonコードが書ける） | Groovy風のDSL2 |
| 再開 | `--rerun-incomplete`（タイムスタンプ比較） | `-resume`（ハッシュベースのキャッシュ） |
| HPC対応 | `--slurm`, `--cluster` | `executor` 設定（SLURM, PBS, AWS Batch等） |

Nextflowのチャネルモデルは、データの流れが直感的に追いやすい一方で、ファイル名に基づく柔軟なパターンマッチはSnakemakeに比べてやや冗長になる場合がある。

#### nf-core — 既存パイプライン群の活用

実際のプロジェクトでは、パイプラインをゼロから書く前に、nf-core[3](https://doi.org/10.1038/s41587-020-0439-x)[8](https://nf-co.re/)の既存パイプラインを検討するべきである。たとえばRNA-seq解析であれば:

```bash
# nf-coreのRNA-seqパイプラインを実行
nextflow run nf-core/rnaseq \
    --input samplesheet.csv \
    --genome GRCh38 \
    --outdir results/ \
    -profile docker
```

この1コマンドで、QCからカウント行列生成まで——本章で扱った全ステップに加えてMultiQCレポート生成まで——が実行される。

> 🧬 **コラム: nf-coreエコシステム**
>
> nf-core[3](https://doi.org/10.1038/s41587-020-0439-x)[8](https://nf-co.re/)は、Nextflowベースのバイオインフォマティクスパイプラインを開発・共有するコミュニティ主導のプロジェクトである。2026年時点で100以上のパイプラインが公開されており、RNA-seq、ATAC-seq、メタゲノム、系統解析など主要な解析タイプをカバーしている。
>
> **ゼロから書くか、nf-coreを使うか** の判断基準:
>
> - **nf-coreを使う**: 標準的な解析パイプライン（RNA-seq, variant calling等）で、カスタマイズが最小限の場合。論文でのcitationも容易
> - **自前で書く**: 解析手法が新しくnf-coreにパイプラインがない、または独自の前処理が多い場合
> - **nf-coreをフォークして改変**: 基本構造はnf-coreを流用し、特定ステップだけカスタマイズする中間的なアプローチ
>
> nf-coreパイプラインは厳格なコーディング規約とCIテストを課しているため、品質が安定している。初めてワークフロー言語に触れる場合でも、`nf-core/rnaseq` の設計を読むことで、ベストプラクティスの実例として学べる。

---

### make — 古典的だが今も有用

GNU make はソフトウェアビルドのために設計されたツールだが、小規模なデータ処理パイプラインにも有用である[7](https://doi.org/10.1093/bib/bbw020)。リファレンスゲノムのダウンロードとインデックス構築のような準備ステップに適している:

```makefile
# Makefile — リファレンスゲノムの取得とインデックス構築
GENOME_URL := https://ftp.ensembl.org/pub/release-111/fasta/homo_sapiens/dna/...
GENOME_DIR := data/raw/genome
GENOME_FA  := $(GENOME_DIR)/GRCh38.fa

.PHONY: all clean

all: $(GENOME_FA).fai

$(GENOME_FA).gz:
	mkdir -p $(GENOME_DIR)
	curl -L -o $@ $(GENOME_URL)

$(GENOME_FA): $(GENOME_FA).gz
	gunzip -k $<

$(GENOME_FA).fai: $(GENOME_FA)
	samtools faidx $<
```

`make all` を実行するとダウンロード → 解凍 → インデックス構築が依存順に実行される。途中で止まっても、完了済みのステップはスキップされる。

makeの利点は、追加のインストールが不要で、ほぼすべてのUNIX環境で利用可能なことである。一方、wildcardの展開やconda/container統合、HPCジョブスケジューラとの連携といったバイオインフォマティクス固有の要件は自前で記述する必要があり、パイプラインが複雑化すると管理が難しくなる。

---

### ツール選択の判断基準

| 基準 | make | Snakemake | Nextflow |
|------|------|-----------|----------|
| 学習コスト | 低 | 中 | 高 |
| Python親和性 | 低 | 高（Snakefile内でPythonが書ける） | 低（Groovy/DSL2） |
| HPC対応 | 手動（ジョブスクリプト記述） | `--slurm`, `--cluster` | 組み込み（executor設定） |
| conda/container統合 | なし | `conda:`, `container:` | `container` プロファイル |
| 既存パイプライン | 少ない | Snakemake Catalog | nf-core（100+パイプライン） |
| 向いている規模 | 小規模（前処理・準備） | 中〜大規模 | 大規模・クラウド |

**迷ったらSnakemakeから始めることを推奨する。** PythonベースでありNumPy・pandasとの親和性が高く、本書の読者にとって学習コストが最も低い。プロジェクトがクラウド環境やHPCの大規模利用に移行する段階でNextflowへの乗り換えを検討すればよい。

#### エージェントへの指示例

ワークフロー言語の選択や移行をエージェントに相談できる:

> 「このプロジェクトのパイプラインをSnakemakeで実装してください。サンプルリストは `config.yaml` から読み込み、各ルールに `log:` ディレクティブと `threads:` を設定してください」

> 「既存のSnakefileを読んで、同等のNextflow DSL2コードに変換してください。チャネルの設計も提案してください」

> 「RNA-seqの解析をしたいのですが、nf-core/rnaseqで対応できますか？ 必要なsamplesheet.csvの形式と最小限の実行コマンドを教えてください」

---

## 12-3. ワークフローのベストプラクティス

ワークフロー言語を使うだけでは再現性は保証されない。以下のベストプラクティスに従うことで、自分自身が半年後に再実行でき、他の研究者が再現できるパイプラインになる。

### 入力データは読み取り専用

`data/raw/` ディレクトリの内容は決して変更しない。これは[§6 バージョン管理（Git / GitHub）](./06_git.md)で学んだ原則と同じである。ワークフローの中で入力ファイルを上書きすると、「元のデータで再実行」ができなくなる。

```
project/
├── data/
│   └── raw/          # 読み取り専用 — 生データ
├── results/          # ワークフローの出力
│   ├── qc/
│   ├── trimmed/
│   ├── aligned/
│   └── counts/
├── logs/             # 実行ログ
├── Snakefile
└── config.yaml
```

Snakemakeのルールで入力に `data/raw/` を使い、出力を `results/` に書くことで、入出力の方向を一方向に保つ。

### 中間ファイルと最終出力の分離

BAMファイルやトリミング後のFASTQファイルは中間ファイルであり、最終出力ではない。Snakemakeの `temp()` マーカーを使うと、下流のルールが完了した時点で自動削除される:

```python
rule trimmomatic:
    input:
        "data/raw/{sample}.fastq.gz",
    output:
        trimmed=temp("results/trimmed/{sample}_trimmed.fastq.gz"),
    # ...
```

`temp()` を使わない場合、RNA-seqの全中間ファイルがディスクに残り続ける。BAMファイルは1サンプルあたり数GBになることもあり、サンプル数が増えるとディスク容量を圧迫する。

`protected()` は逆に、誤って削除されないようにファイルを保護する。計算コストの高いステップの出力に付けるとよい:

```python
rule star_align:
    output:
        bam=protected("results/aligned/{sample}.bam"),
    # ...
```

### パラメータの設定ファイル化

本書全体の規約である「ハードコーディング禁止」はワークフローでも同様である。パラメータをSnakefileに直書きすると、異なる条件での再実行時にワークフロー定義自体を編集することになり、変更の追跡が困難になる。

```python
# ❌ パラメータのハードコーディング
rule star_align:
    threads: 8
    shell:
        "STAR --sjdbOverhang 100 ..."

# ✅ config.yamlからの読み込み
rule star_align:
    threads: config["params"]["star"]["threads"]
    shell:
        "STAR --sjdbOverhang {config[params][star][overhang]} ..."
```

### ログの保存

[§9 CLIツール設計](./09_cli.md)で学んだロギングの原則はワークフローにも適用される。Snakemakeの `log:` ディレクティブは、各ルールの実行ログを指定したパスに保存する:

```python
rule star_align:
    log:
        "logs/star/{sample}.log",
    shell:
        "STAR ... 2> {log}"
```

`log:` ディレクティブのないルールでは、エラー発生時に原因特定が困難になる。本書のサンプルSnakefileでは、`rule all` を除くすべてのルールに `log:` を付けている。

### `--dry-run` / `--dag` による事前確認

ワークフローを本番実行する前に、必ずドライランで確認する:

```bash
# ドライラン — 実際のコマンドは実行せず、実行計画を表示
snakemake -n

# DAGの可視化 — 依存関係グラフをSVGで出力
snakemake --dag | dot -Tsvg > dag.svg
```

`-n`（`--dry-run`）は「何が実行されるか」を確認するためのオプションで、実際のコマンドは発行されない。新しいルールを追加した後や、設定ファイルを変更した後は、まずドライランで実行計画を確認する習慣をつけるとよい。

### テスト用の小規模データ

[§7 テスト・品質管理](./07_testing.md)で学んだテストの原則はワークフローにも適用される。パイプライン全体を実データで実行すると数時間かかる場合、テスト用の小規模データセットを用意して高速にフィードバックを得る:

```bash
# テスト用のサブサンプルを作成（先頭10,000リード）
head -n 40000 data/raw/SRR1234501.fastq > test_data/SRR1234501.fastq

# テスト用configで実行
snakemake --configfile test_config.yaml -j 4
```

この方法により、ワークフローの論理的な正しさを短時間で検証できる。テスト用データと設定は[§13 コンテナと再現性](./13_container.md)で扱う再現性パッケージングにも含める。

### ベストプラクティスの自動チェック

本書のサンプルコード（`scripts/ch12/validate_workflow.py`）に、Snakefileのテキストを解析してベストプラクティス準拠を検証するバリデータを用意している:

```python
from scripts.ch12.validate_workflow import validate

snakefile_text = open("Snakefile").read()
result = validate(snakefile_text)

for item in result.passed:
    print(f"✅ {item}")
for item in result.warnings:
    print(f"⚠️  {item}")
```

このバリデータは以下の4項目をチェックする:

1. **`configfile:` の使用** — パラメータがハードコーディングされていないか
2. **`log:` ディレクティブの有無** — 全ルール（`rule all` を除く）にログ出力があるか
3. **`temp()` の使用** — 中間ファイルにディスク管理マーカーが付いているか
4. **入出力パスの分離** — 入力ディレクトリに出力を書き込んでいないか

#### エージェントへの指示例

ベストプラクティスの適用をエージェントに依頼できる:

> 「このSnakefileを読んで、`log:` ディレクティブのないルールを洗い出してください。それぞれに適切なlogパスを追加してください」

> 「ワークフローの中間ファイルを特定して、`temp()` で囲むべき出力を提案してください。最終的にユーザーが必要とする出力は `results/counts/` と `results/qc/` のファイルです」

> 「このSnakefileに `--dry-run` を実行して、結果を説明してください。想定どおりのルールが実行される計画になっているか確認してください」

> 🤖 **コラム: 機械学習パイプラインのワークフロー管理**
>
> 機械学習プロジェクトでも、データ前処理 → 特徴量エンジニアリング → モデル学習 → 評価という多段階パイプラインが発生する。SnakemakeやNextflowで管理できるが、機械学習特有の要件——ハイパーパラメータの追跡、メトリクスの比較、モデルチェックポイントの管理——にはMLOps専用ツールの方が適している場合がある。
>
> **DVC**（Data Version Control）は、大規模なデータやモデルファイルのバージョン管理を主目的とするツールであり、`dvc.yaml` によるパイプライン定義機能も備えている。一方、**MLflow** は実験のメトリクス追跡・モデルレジストリ・デプロイ管理を担うプラットフォームである。両者の性質は異なるため、以下の対照表で使い分けの指針を示す。
>
> | 要件 | Snakemake/Nextflow | DVC（データ・モデル版管理） | MLflow（実験追跡・モデル管理） |
> |------|-------------------|-----|--------|
> | ファイル依存の解決 | 得意 | 得意 | 限定的 |
> | ハイパーパラメータ追跡 | 手動（configで管理） | `dvc params` | 組み込み |
> | メトリクス比較 | なし | `dvc metrics diff` | UIで比較 |
> | モデルレジストリ | なし | なし | 組み込み |
> | バイオツール連携 | conda/container | なし | なし |
>
> バイオインフォマティクスの文脈では、配列解析パイプライン（外部ツール呼び出しが中心）はSnakemake/Nextflow、機械学習実験（Pythonコードが中心）はDVC/MLflowと使い分けるのが現実的である。両方を含むプロジェクトでは、Snakemakeのワークフロー内でMLflowのトラッキングを呼び出す組み合わせも有効である。

---

## まとめ

| 課題 | シェルスクリプト | ワークフロー言語 |
|------|----------------|-----------------|
| 部分的再実行 | 手動で特定・再実行 | 変更部分だけ自動再実行 |
| サンプル展開 | forループ・コピペ | wildcards・expand() |
| 並列実行 | 手動（`&`, `xargs`） | `-j N` で自動並列 |
| HPC連携 | ジョブスクリプト手書き | `--slurm` で自動投入 |
| 中間ファイル管理 | 手動削除 | `temp()` で自動削除 |
| ログ管理 | リダイレクト忘れがち | `log:` で強制 |
| 再現性 | 低（環境依存） | conda/container統合 |

ワークフロー言語の導入は、パイプラインが3ステップ以上・サンプルが複数ある時点で検討に値する。本章で紹介した `configfile:`、`log:`、`temp()`、入出力の分離といったベストプラクティスは、どのワークフロー言語を選んでも共通の原則である。

次章の[§13 コンテナと再現性](./13_container.md)では、ワークフロー言語で構築したパイプラインの実行環境をDockerやApptainerで固定し、**コンテナイメージ + ワークフロー + バージョン固定**の「三点セット」として論文の再現性を保証する方法を学ぶ。

---

## 参考文献

[1] Mölder, F. et al. "Sustainable data analysis with Snakemake." *F1000Research*, 10, 33, 2021. [https://doi.org/10.12688/f1000research.29032.2](https://doi.org/10.12688/f1000research.29032.2)

[2] Di Tommaso, P. et al. "Nextflow enables reproducible computational workflows." *Nature Biotechnology*, 35(4), 316–319, 2017. [https://doi.org/10.1038/nbt.3820](https://doi.org/10.1038/nbt.3820)

[3] Ewels, P. A. et al. "The nf-core framework for community-curated bioinformatics pipelines." *Nature Biotechnology*, 38(3), 276–278, 2020. [https://doi.org/10.1038/s41587-020-0439-x](https://doi.org/10.1038/s41587-020-0439-x)

[4] Snakemake Development Team. "Snakemake Documentation". [https://snakemake.readthedocs.io/](https://snakemake.readthedocs.io/) (参照日: 2026-03-20)

[5] Seqera Labs. "Nextflow Documentation". [https://www.nextflow.io/docs/latest/](https://www.nextflow.io/docs/latest/) (参照日: 2026-03-20)

[6] Grüning, B. et al. "Bioconda: sustainable and comprehensive software distribution for the life sciences." *Nature Methods*, 15(7), 475–476, 2018. [https://doi.org/10.1038/s41592-018-0046-7](https://doi.org/10.1038/s41592-018-0046-7)

[7] Leipzig, J. "A review of bioinformatic pipeline frameworks." *Briefings in Bioinformatics*, 18(3), 530–536, 2017. [https://doi.org/10.1093/bib/bbw020](https://doi.org/10.1093/bib/bbw020)

[8] nf-core Community. "nf-core — A community effort to collect a curated set of analysis pipelines". [https://nf-co.re/](https://nf-co.re/) (参照日: 2026-03-20)
