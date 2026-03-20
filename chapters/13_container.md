# §13 コンテナと再現性

[§12 ワークフロー管理](./12_workflow.md)では、Snakemake・Nextflow・makeを使ってパイプラインの処理順序と依存関係を管理する方法を学んだ。しかし、パイプラインの再現性はワークフロー定義だけでは保証されない。同じSnakefileを実行しても、STARのバージョンが異なれば出力BAMのアラインメント結果は変わり、OSのライブラリバージョンが異なればツールの挙動そのものが変わりうる。

この問題を解決するのが**コンテナ**（container）である。コンテナはアプリケーションとその依存関係（OS、ライブラリ、ツール）を丸ごとパッケージングし、どの計算機でも同一の実行環境を再現する技術である。

AIエージェントはDockerfileや`docker-compose.yml`を生成できる。しかし、ベースイメージの選択（mambaforgeかUbuntuか）、レイヤー構成の効率、HPCでのApptainer互換性、セキュリティ上のベストプラクティス——これらの設計判断は、実行環境とデータの特性を理解している人間がレビューしなければならない。

本章では、Docker・Apptainerによるコンテナの基礎から、論文投稿時の再現性パッケージングまでを学ぶ。

---

## 13-1. なぜコンテナが必要か

### 「自分の環境では動く」問題

以下の3つの場面を想像してみよう:

**場面1: 共同研究者への引き継ぎ。** 自分のMacBookで動いていたRNA-seqパイプラインを、共同研究者のLinuxサーバーに移したところ、STARが「shared library not found」エラーで起動しない。原因はlibhts.soのバージョン違いだった。

**場面2: 論文査読への対応。** 査読者から「Table 2の結果を再現できなかった」とコメントが来た。半年前に自分が解析したときのsamtoolsのバージョンを思い出せず、`conda list` の出力も残していなかった。

**場面3: 自分自身の過去の再現。** 1年前の予備実験の結果を再解析しようとしたが、`pip install -r requirements.txt` でインストールされるバージョンが当時と異なり、数値結果が微妙に変わってしまった。

これらはすべて「**依存関係の不一致**」に起因する。[§5 開発環境の構築](./05_dev_environment.md)で学んだcondaやvenvは、Pythonパッケージの隔離には有効だが、OS レベルのライブラリ（libhts、CUDA等）やシステムツール（samtools、STARのバイナリ）までは管理できない。

### Pythonパッケージの隔離 vs. OSレベルの隔離

[§5 開発環境の構築](./05_dev_environment.md#5-1-pythonの環境管理)で学んだ環境管理ツールとコンテナの違いを整理する:

| 管理レベル | venv / conda | コンテナ |
|-----------|-------------|---------|
| Pythonパッケージ | 隔離される | 隔離される |
| システムライブラリ（libhts等） | ホストに依存 | コンテナ内に固定 |
| OSバージョン | ホストに依存 | コンテナ内に固定 |
| バイナリツール（STAR等） | condaで管理可能 | コンテナ内に固定 |
| カーネル | ホストのカーネル | ホストのカーネルを共有 |

condaはbiocondaチャネルを通じてSTARやsamtoolsのバイナリも管理できるが、それらが依存するシステムライブラリまでは制御できない。コンテナはカーネル以外のすべてをパッケージングするため、「自分の環境では動く」問題を根本的に解決する。

### 再現性危機とコンテナ

2016年にNature誌が1,500名以上の研究者を対象に実施した調査[1](https://doi.org/10.1038/533452a)では、回答者の70%以上が「他の研究者の実験を再現しようとして失敗した経験がある」と回答した。計算科学においては、ソフトウェアのバージョン・環境設定の違いが再現失敗の主要因の一つである。

コンテナは、この再現性危機に対する実践的な解決策を提供する。Dockerfileに実行環境を明示的に定義し、イメージとして固定することで、論文の査読者や将来の自分が同一の環境を復元できる。

### コンテナを使うべきタイミング

すべてのプロジェクトにコンテナが必要なわけではない。以下の判断基準を参考にする:

| 状況 | 推奨 |
|------|------|
| 個人の探索的分析、ツールが1〜2個 | conda / venv で十分 |
| 共同研究者と環境を共有する | コンテナを検討 |
| 論文投稿時の再現性保証 | コンテナを強く推奨 |
| HPCクラスタで実行する | Apptainer推奨 |
| CI/CDでパイプラインを自動実行する | コンテナが前提 |

[§8 成果物の形式とプロジェクト設計](./08_deliverables.md#パターン6-dockerコンテナ--apptainerイメージ)で紹介したパターン6（Dockerコンテナ）は、単独の成果物というよりも、他のパターンの「届け方」を補強するレイヤーとして機能する。

#### エージェントへの指示例

環境の再現性について判断を求めるとき:

> 「このプロジェクトの依存関係を確認して、condaだけで管理できるか、Dockerコンテナが必要かを判断してください。システムライブラリへの依存があるかどうかを調べてください」

> 「共同研究者にこの解析環境を渡したいのですが、再現性を保証するために最低限必要な構成を提案してください。condaのロックファイルとDockerfile、どちらが適切ですか？」

> 「この論文のMethods節に書かれているソフトウェアバージョンを元に、解析環境を再構築するDockerfileを作成してください」

---

## 13-2. Docker

### イメージとコンテナの違い

Dockerの基本概念を理解するために、Pythonのクラスとインスタンスのアナロジーで考える:

- **イメージ**（image）= クラス定義。Dockerfileから`docker build`で作成される。不変であり、共有・配布できる
- **コンテナ**（container）= インスタンス。イメージから`docker run`で作成される。実行状態を持ち、停止・削除できる

```
Dockerfile  ──build──→  イメージ  ──run──→  コンテナ（実行中）
（設計図）              （テンプレート）      （実体）
```

1つのイメージから複数のコンテナを起動できる。イメージは読み取り専用であり、コンテナ内でファイルを変更してもイメージには影響しない。

### Dockerfileの書き方

Dockerfileはイメージの構築手順をテキストで定義するファイルである。RNA-seq解析環境を例に、主要な命令を説明する:

```dockerfile
# RNA-seq解析環境のDockerfile
# mambaforgeベースでbiocondaパッケージを利用する
FROM condaforge/mambaforge:24.3.0-0

LABEL maintainer="yourname@example.com"
LABEL description="RNA-seq解析パイプライン環境"

# システムパッケージのインストール（RUN命令を統合し、キャッシュを削除する）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        procps \
        curl \
    && rm -rf /var/lib/apt/lists/*

# conda環境定義ファイルを先にコピー（レイヤーキャッシュの活用）
COPY environment.yml /tmp/environment.yml

# conda環境の作成
RUN mamba env create -f /tmp/environment.yml && \
    mamba clean --all --yes

# conda環境をデフォルトに設定
ENV PATH="/opt/conda/envs/rnaseq/bin:$PATH"

# 作業ディレクトリの設定
WORKDIR /workspace

# パイプラインコードをコピー
COPY . /workspace

ENTRYPOINT ["snakemake"]
CMD ["--help"]
```

各命令の役割:

| 命令 | 役割 | 注意点 |
|------|------|--------|
| `FROM` | ベースイメージの指定 | タグを必ず固定する（`latest`は使わない） |
| `RUN` | コマンドの実行 | 複数コマンドは`&&`で統合する |
| `COPY` | ファイルのコピー | 依存定義を先にコピーしてキャッシュを活用する |
| `ENV` | 環境変数の設定 | PATHの設定に使う |
| `WORKDIR` | 作業ディレクトリの設定 | 以降の命令の基準ディレクトリ |
| `ENTRYPOINT` | コンテナ起動時のコマンド | 引数は`CMD`で上書き可能 |
| `CMD` | デフォルト引数 | `docker run`時に上書きできる |

#### ベースイメージの選択

バイオインフォマティクスのDockerfileでは、**mambaforge**（condaforge/mambaforge）をベースイメージとして推奨する。理由は以下のとおり:

- biocondaチャネルが利用でき、STAR・samtools等のバイオツールを直接インストールできる
- mambaによる高速な依存解決
- `environment.yml` を使った宣言的な環境定義（[§5](./05_dev_environment.md#5-1-pythonの環境管理)で学んだ形式）

ベースイメージのタグは必ず固定する。タグなしや`latest`は、ビルド時期によって異なるイメージが使われ、再現性が損なわれる:

```dockerfile
# ❌ タグなし — ビルド時期で異なるバージョンに
FROM python

# ❌ latest — 同上
FROM python:latest

# ✅ バージョンタグ固定
FROM condaforge/mambaforge:24.3.0-0

# ✅✅ ダイジェスト指定 — 最も再現性が高い
FROM condaforge/mambaforge:24.3.0-0@sha256:abc123...
```

### レイヤーキャッシュの仕組みと最適化

Dockerはイメージをレイヤーの積み重ねとして構築する。各`RUN`、`COPY`、`ADD`命令が1つのレイヤーを生成し、変更のないレイヤーはキャッシュから再利用される。

この仕組みを活かすには、**変更頻度の低いものを先に、高いものを後に**配置する:

```dockerfile
# ✅ キャッシュ効率の良い順序
COPY environment.yml /tmp/environment.yml    # 依存定義（変更頻度: 低）
RUN mamba env create -f /tmp/environment.yml # conda環境構築（時間がかかる）
COPY . /workspace                            # ソースコード（変更頻度: 高）

# ❌ キャッシュ効率の悪い順序
COPY . /workspace                            # コード変更のたびに以降すべて再構築
RUN mamba env create -f /tmp/environment.yml # 毎回conda環境を再構築してしまう
```

ソースコードを修正するたびに`docker build`を実行するが、`environment.yml`が変わっていなければconda環境の構築（数分かかる）はキャッシュから再利用される。

また、`RUN`命令は統合して不要なレイヤーを減らす:

```dockerfile
# ❌ 分離されたRUN — レイヤーが増え、apt-getキャッシュが残る
RUN apt-get update
RUN apt-get install -y python3
RUN rm -rf /var/lib/apt/lists/*

# ✅ 統合されたRUN — 1レイヤーでキャッシュも削除
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 \
    && rm -rf /var/lib/apt/lists/*
```

### マルチステージビルド

ビルド時に必要なツール（コンパイラ等）を最終イメージに含めないために、**マルチステージビルド**を使う:

```dockerfile
# --- ステージ1: ビルド ---
FROM condaforge/mambaforge:24.3.0-0 AS builder

COPY environment.yml /tmp/environment.yml
RUN mamba install -y conda-pack && \
    mamba env create -f /tmp/environment.yml && \
    conda-pack -n rnaseq -o /tmp/env.tar.gz

# --- ステージ2: 実行環境 ---
FROM debian:bookworm-slim AS runtime

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /tmp/env.tar.gz /tmp/env.tar.gz
RUN mkdir -p /opt/env && \
    tar -xzf /tmp/env.tar.gz -C /opt/env && \
    rm /tmp/env.tar.gz && \
    /opt/env/bin/conda-unpack

ENV PATH="/opt/env/bin:$PATH"
WORKDIR /workspace
```

`conda-pack`でconda環境をポータブルなアーカイブにし、最小限のランタイムイメージ（debian:bookworm-slim）に展開する。ビルドステージのmambaforge（約1GB）は最終イメージに含まれないため、イメージサイズを大幅に削減できる。

### ボリュームマウント — 大規模データの扱い

FASTQファイルやBAMファイルは数十GBに達することがある。これらをイメージに含めるのは非現実的であり、**ボリュームマウント**で外部からコンテナに接続する:

```bash
# -v ホスト側パス:コンテナ側パス[:オプション]
docker run -v $(pwd)/data/raw:/workspace/data/raw:ro \
           -v $(pwd)/results:/workspace/results \
           rnaseq-pipeline snakemake --cores 4
```

- `:ro`（read-only）を付けると、コンテナ内から書き込みできない。生データのディレクトリには必ず`:ro`を付ける
- 結果ディレクトリは書き込み可能にマウントする

これは[§12 ワークフロー管理](./12_workflow.md#入力データは読み取り専用)で学んだ「入力データは読み取り専用」の原則と同じである。

### docker compose

複数のマウントやオプションを毎回コマンドラインで指定するのは煩雑である。`docker-compose.yml`でこれらを宣言的に定義できる:

```yaml
# docker-compose.yml
services:
  rnaseq:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      # 生データをマウント（読み取り専用）
      - ./data/raw:/workspace/data/raw:ro
      # 結果ディレクトリをマウント（書き込み可能）
      - ./results:/workspace/results
      # ログディレクトリをマウント
      - ./logs:/workspace/logs
    working_dir: /workspace
    entrypoint: ["snakemake"]
    command: ["--dry-run", "--cores", "4"]
```

```bash
# ビルドして実行
docker compose build
docker compose run --rm rnaseq snakemake --cores 4

# ドライランのデフォルト設定で実行
docker compose up
```

`docker compose`を使うことで、チームメンバーは`docker-compose.yml`を見るだけで実行に必要なマウント構成を理解できる。

> 🧬 **コラム: BioContainersとbioconda**
>
> BioContainers[3](https://doi.org/10.1093/bioinformatics/btx192)は、biocondaパッケージに対応するDockerイメージを自動生成するプロジェクトである。biocondaに登録された1万以上のツール[4](https://doi.org/10.1038/s41592-018-0046-7)について、ツール単体のDockerイメージ・Apptainerイメージが提供されている。
>
> たとえば、samtools 1.20のイメージは以下のように取得できる:
>
> ```bash
> # BioContainersからsamtoolsイメージを取得
> docker pull quay.io/biocontainers/samtools:1.20--h50ea8bc_0
>
> # Apptainerで直接取得
> apptainer pull docker://quay.io/biocontainers/samtools:1.20--h50ea8bc_0
> ```
>
> イメージ名の構造は `quay.io/biocontainers/<パッケージ名>:<バージョン>--<ビルドハッシュ>` である。ビルドハッシュまで含めて指定することで、完全に同一のバイナリを再現できる。
>
> [§12 ワークフロー管理](./12_workflow.md#conda--container統合)で紹介したSnakemakeの`container:`ディレクティブと組み合わせると、ルールごとに異なるBioContainersイメージを指定できる:
>
> ```python
> rule samtools_sort:
>     container:
>         "docker://quay.io/biocontainers/samtools:1.20--h50ea8bc_0"
>     # ...
> ```
>
> 自前でDockerfileを書く前に、まずBioContainersに該当ツールのイメージがないか確認するとよい。

#### エージェントへの指示例

Dockerfileの作成や改善をエージェントに依頼する場合:

> 「RNA-seq解析用のDockerfileを作成してください。ベースイメージはmambaforgeで、environment.ymlからconda環境を構築する構成にしてください。レイヤーキャッシュを意識した命令順序にしてください」

> 「このDockerfileのイメージサイズを削減したい。マルチステージビルドに変換して、最終イメージにビルドツールが含まれないようにしてください」

> 「docker-compose.ymlを作成して、データディレクトリのマウント設定を含めてください。生データは読み取り専用、結果ディレクトリは書き込み可能にしてください」

> 「BioContainersでsamtools 1.20のイメージ名を調べてください。Snakefileの`container:`ディレクティブで指定する形式で教えてください」

---

## 13-3. Apptainer / Singularity

### HPCでDockerが使えない理由

多くのHPC（High-Performance Computing）クラスタでは、Dockerを使用できない。理由は**セキュリティ**である。Dockerデーモンはroot権限で動作するため、コンテナ内からホストのファイルシステムにアクセスしたり、他のユーザーのプロセスに影響を与える可能性がある。共有計算環境であるHPCでは、これは許容できないリスクである。

**Apptainer**（旧Singularity）[2](https://doi.org/10.1371/journal.pone.0177459)は、HPC向けに設計されたコンテナランタイムである。以下の特徴を持つ:

- **ユーザー権限で実行**: rootデーモン不要。一般ユーザーがそのまま実行できる
- **SIFファイル**: コンテナイメージが単一ファイル（`.sif`）にパッケージされる。コピー・移動が容易
- **ホストファイルシステムの自動マウント**: `$HOME`や`/tmp`がデフォルトでマウントされる
- **Dockerイメージとの互換性**: DockerイメージをそのままApptainerで実行できる

### Dockerイメージからの変換

Dockerイメージは`apptainer pull`で直接Apptainerイメージに変換できる:

```bash
# Docker HubのイメージをSIFファイルに変換
apptainer pull rnaseq.sif docker://condaforge/mambaforge:24.3.0-0

# BioContainersのイメージを取得
apptainer pull samtools.sif docker://quay.io/biocontainers/samtools:1.20--h50ea8bc_0

# 自分でビルドしたイメージを変換（ローカルDockerイメージから）
docker save myimage:v1.0 | apptainer build myimage.sif docker-archive:/dev/stdin
```

### Apptainer定義ファイル

Dockerfileに相当するのが`.def`ファイル（定義ファイル）である:

```
Bootstrap: docker
From: condaforge/mambaforge:24.3.0-0

%labels
    Author yourname@example.com
    Description RNA-seq解析パイプライン環境（Apptainer）

%files
    environment.yml /tmp/environment.yml

%post
    # conda環境の作成
    mamba env create -f /tmp/environment.yml
    mamba clean --all --yes
    echo ". /opt/conda/etc/profile.d/conda.sh && conda activate rnaseq" >> /etc/bash.bashrc

%environment
    export PATH="/opt/conda/envs/rnaseq/bin:$PATH"

%runscript
    exec snakemake "$@"

%help
    RNA-seq解析パイプラインのApptainerコンテナ。
    使い方:
      apptainer run rnaseq.sif --cores 4
      apptainer exec rnaseq.sif fastqc --version
```

```bash
# 定義ファイルからSIFイメージを構築
apptainer build rnaseq.sif apptainer.def
```

### Docker vs. Apptainer コマンド対照表

| 操作 | Docker | Apptainer |
|------|--------|-----------|
| イメージ取得 | `docker pull image:tag` | `apptainer pull file.sif docker://image:tag` |
| コンテナ実行 | `docker run image cmd` | `apptainer run file.sif cmd` |
| インタラクティブ | `docker run -it image bash` | `apptainer shell file.sif` |
| コマンド実行 | `docker exec container cmd` | `apptainer exec file.sif cmd` |
| イメージ構築 | `docker build -t name .` | `apptainer build file.sif def_file.def` |
| ボリュームマウント | `-v host:container` | `--bind host:container` |
| GPU利用 | `--gpus all` | `--nv` |

重要な違いとして、Apptainerは`$HOME`と`/tmp`をデフォルトでマウントする。そのため、Docker での`-v`マウントが不要な場合が多い。ただし、`$HOME`の`.bashrc`等がコンテナ内の環境に影響する可能性があるため、`--cleanenv`オプションで環境変数をクリアすることを推奨する:

```bash
# 環境変数をクリアして実行（推奨）
apptainer run --cleanenv rnaseq.sif snakemake --cores 4

# 追加のディレクトリをマウント
apptainer run --bind /scratch/data:/data rnaseq.sif snakemake --cores 4
```

### GPUコンテナ

機械学習やGPUを使う解析では、`--nv`オプション（Apptainer）または`--gpus all`（Docker）でホストのGPUをコンテナに接続する:

```bash
# Docker
docker run --gpus all myimage:v1.0 python train.py

# Apptainer
apptainer run --nv myimage.sif python train.py
```

> 🤖 **コラム: GPUコンテナとCUDAバージョンの罠**
>
> GPUを使うコンテナでは、**CUDAバージョンの互換性**が最も頻繁に問題になる。以下の3つのバージョンが一致している必要がある:
>
> 1. **ホストのNVIDIAドライバ**: `nvidia-smi`で確認
> 2. **コンテナ内のCUDA Toolkit**: `nvcc --version`で確認
> 3. **ライブラリが要求するCUDA**: PyTorchやTensorFlowのインストール時に指定
>
> ホストのドライバがサポートするCUDAバージョンの上限は決まっており、コンテナ内のCUDAがそれを超えると動作しない。たとえばドライバが CUDA 12.2までサポートしている環境で、CUDA 12.4のコンテナを実行するとエラーになる。
>
> NVIDIAが提供するNGC（NVIDIA GPU Cloud）のベースイメージを使うと、CUDA・cuDNN・NCCLの互換性が保証される:
>
> ```dockerfile
> # NGCベースイメージ（CUDA, cuDNN, NCCL同梱）
> FROM nvcr.io/nvidia/pytorch:24.01-py3
> ```
>
> GPUコンテナの構築はエージェントに任せられるが、ホストのドライババージョンとの互換性チェックは人間が行うべきである。`nvidia-smi`の出力を確認してから、適切なベースイメージを選択する。

#### エージェントへの指示例

HPC環境でのコンテナ利用をエージェントに相談する場合:

> 「このDockerfileをApptainerの定義ファイル（.def）に変換してください。HPCで実行することを想定しています」

> 「Docker HubのイメージをApptainerのSIFファイルに変換するコマンドを教えてください。キャッシュの保存場所も指定したいです」

> 「GPUを使う機械学習パイプライン用のDockerfileを作成してください。PyTorch 2.xとCUDA 12.xを使います。NGCベースイメージを使ってください」

---

## 13-4. 再現性のレベル

再現性には程度がある。コストと再現性のバランスを考え、プロジェクトの段階に応じた戦略を選択する。

### 4段階のスペクトラム

| レベル | 手法 | 再現性 | 導入コスト |
|--------|------|--------|-----------|
| 1. READMEに記述 | ソフトウェア名とバージョンをテキストで記載 | 低 — 手動インストールが必要、手順の曖昧さ | 最低 |
| 2. ロックファイル | `conda-lock`、`uv.lock`、`pip freeze`で全依存バージョンを固定 | 中 — Pythonパッケージは再現、OSレベルは未固定 | 低 |
| 3. Dockerfile | コンテナイメージで環境を固定 | 高 — OS・ライブラリ・ツールすべて固定 | 中 |
| 4. ダイジェスト固定 + ワークフロー | ベースイメージの`@sha256:`指定 + ワークフロー言語 + ロックファイル | 最高 — ビット単位の再現性 | 高 |

### コスト vs. 再現性の比較

```
再現性
  ↑
  │          ④ ダイジェスト+WF
  │        ┌──┐
  │      ③ Docker
  │    ┌──┐
  │  ② lockファイル
  │ ┌──┐
  │① README
  ├──┐
  └──────────────────→ コスト
```

多くのプロジェクトでは、レベル2（ロックファイル）とレベル3（Dockerfile）の**併用**が現実的なバランスである。論文投稿時にはレベル4を目指す。

### 両方を併用する戦略

condaのロックファイルとDockerfileは排他的ではない。Dockerfile内でロックファイルを使うことで、両方の利点を得られる:

```dockerfile
FROM condaforge/mambaforge:24.3.0-0

# conda-lockで生成したロックファイルを使用
COPY conda-lock.yml /tmp/conda-lock.yml
RUN conda-lock install -n rnaseq /tmp/conda-lock.yml && \
    mamba clean --all --yes

ENV PATH="/opt/conda/envs/rnaseq/bin:$PATH"
```

この構成では:

- `conda-lock.yml`により、conda環境内のパッケージバージョンがハッシュレベルで固定される
- Dockerfileにより、OS・システムライブラリが固定される
- ベースイメージのタグ（またはダイジェスト）により、ベースOSが固定される

ロックファイルの生成と管理は[§5 開発環境の構築](./05_dev_environment.md#ロックファイル--再現性の鍵)で学んだ手法をそのまま使える。

#### エージェントへの指示例

プロジェクトの再現性レベルを評価・改善するとき:

> 「このプロジェクトの現在の再現性レベルを評価してください。README、ロックファイル、Dockerfileのどれが揃っていて、何が不足しているか教えてください」

> 「conda-lockを使ってロックファイルを生成し、そのロックファイルをDockerfile内で使う構成に変更してください」

> 「論文投稿に向けて、再現性レベルを最高にしたい。ベースイメージのダイジェスト固定を含めたDockerfileに更新してください」

---

## 13-5. 論文投稿時の再現性パッケージング

### 三点セットの原則

論文の計算結果を第三者が再現するには、以下の「三点セット」が必要である:

1. **コンテナイメージ**: 実行環境の完全な定義（本章）
2. **ワークフロー**: 処理の実行順序と依存関係（[§12 ワークフロー管理](./12_workflow.md)）
3. **バージョン固定**: 全依存パッケージの正確なバージョン記録（[§5 開発環境の構築](./05_dev_environment.md#ロックファイル--再現性の鍵)）

この三要素が揃うことで、「論文のFigure 3を再現してください」という要求に対して、査読者は`docker run`（または`apptainer run`）一発で結果を得られる状態になる。

### コンテナイメージの公開

コンテナイメージはDocker HubまたはGitHub Container Registry（GHCR）に公開する。

```bash
# GHCRにイメージをプッシュする例
docker tag rnaseq-pipeline:v1.0 ghcr.io/username/rnaseq-pipeline:v1.0
docker push ghcr.io/username/rnaseq-pipeline:v1.0
```

タグ戦略:

| タグ | 用途 | 再現性 |
|------|------|--------|
| `v1.0.0` | セマンティックバージョニング（[§6](./06_git.md#6-4-セマンティックバージョニング)参照） | 高 |
| `v1.0.0@sha256:abc...` | ダイジェスト固定 | 最高 |
| `latest` | 開発中の最新版 | なし — 論文には使わない |

**論文に記載するのはダイジェスト付きのイメージ名である。** タグは後から別のイメージに付け替えられるが、ダイジェストは内容のハッシュ値であり改変できない。

```
# 論文のMethods節に記載する例
解析にはghcr.io/username/rnaseq-pipeline:v1.0@sha256:a1b2c3...のコンテナイメージを使用した。
```

### バージョン固定の実践

Dockerfile内でバージョン固定を徹底する:

```dockerfile
FROM condaforge/mambaforge:24.3.0-0@sha256:abc123...

# conda-lockによる完全固定
COPY conda-lock.yml /tmp/conda-lock.yml
RUN conda-lock install -n rnaseq /tmp/conda-lock.yml

# または pip freeze + requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# または uv.lock
COPY pyproject.toml uv.lock /tmp/
RUN uv sync --frozen --no-cache
```

これら3つの方法はいずれも、インストール時期によらず同一のパッケージセットを再現する。プロジェクトで使用しているパッケージマネージャに合わせて選択する。

### 論文レビュー対応

査読者は限られた時間で再現を試みる。以下の工夫で再現の障壁を下げる:

**READMEテンプレート:**

```markdown
# 再現手順

## 前提条件
- Docker 24.0+ または Apptainer 1.3+
- 8GB以上のメモリ
- 約10GBのディスク空き

## テストデータでのクイック再現（約5分）
docker run --rm -v $(pwd)/results:/workspace/results \
    ghcr.io/username/rnaseq-pipeline:v1.0 \
    snakemake --configfile test_config.yaml --cores 4

## フルデータでの再現
# 1. データのダウンロード（約30GB）
# 2. パイプライン実行（約2時間）
# ...
```

**テストデータの同梱:**

- 実データのサブセット（先頭10,000リード等）をリポジトリに含める
- テスト用の設定ファイル（`test_config.yaml`）を用意する
- テストデータでの実行時間を5分以内に抑える

### 再現性パッケージのディレクトリ構成例

```
reproducibility-package/
├── Dockerfile                  # コンテナ定義
├── docker-compose.yml          # 実行設定
├── Snakefile                   # ワークフロー（§12）
├── config.yaml                 # パイプライン設定
├── environment.yml             # conda環境定義
├── conda-lock.yml              # バージョン完全固定
├── test_data/                  # テストデータ（小規模）
│   └── SRR_subset.fastq.gz
├── test_config.yaml            # テスト用設定
├── README.md                   # 再現手順
└── results/                    # 期待される出力（テストデータ分）
    └── expected/
```

### Dockerfileのベストプラクティス検証

本書のサンプルコード（`scripts/ch13/validate_dockerfile.py`）に、Dockerfileのベストプラクティス準拠をチェックするバリデータを用意している:

```python
from scripts.ch13.validate_dockerfile import validate

dockerfile_text = open("Dockerfile").read()
result = validate(dockerfile_text)

for item in result.passed:
    print(f"✅ {item}")
for item in result.warnings:
    print(f"⚠️  {item}")
for item in result.info:
    print(f"ℹ️  {item}")
```

このバリデータは以下の4項目をチェックする:

1. **ベースイメージのタグ固定**: `FROM python:latest`やタグなしを警告。`@sha256:`は推奨として情報表示
2. **レイヤーキャッシュ順序**: `COPY . .`が依存インストールより前にないか
3. **RUN命令の統合**: `apt-get update`と`apt-get install`が分離されていないか
4. **apt-getキャッシュ削除**: `rm -rf /var/lib/apt/lists/*`の有無

Nüst et al. (2020)[7](https://doi.org/10.1371/journal.pcbi.1008316)の「Dockerfileを書くための10のルール」も併せて参照するとよい。

#### エージェントへの指示例

論文投稿の再現性パッケージングをエージェントに依頼する場合:

> 「この解析プロジェクトを論文投稿用の再現性パッケージとして整備してください。Dockerfile、docker-compose.yml、テストデータでの再現手順READMEを作成してください」

> 「このDockerfileに対して`validate_dockerfile.py`を実行して、ベストプラクティスに違反している箇所を修正してください」

> 「論文のMethods節に記載するためのソフトウェアバージョン一覧を生成してください。コンテナイメージのダイジェストも含めてください」

> 「conda-lock.ymlをDockerfile内で使用する構成に変更してください。ベースイメージのダイジェストも固定してください」

論文投稿前の最終確認は[付録D 論文投稿前チェックリスト](./appendix_d.md)を参照。

---

## まとめ

| 課題 | コンテナなし | コンテナあり |
|------|------------|-------------|
| 環境の再現 | 手動インストール、バージョン不一致の恐れ | イメージから同一環境を復元 |
| 共同研究者への共有 | 環境構築手順の説明が必要 | `docker pull`で完了 |
| HPC実行 | モジュール依存、管理者への依頼 | Apptainerで自己完結 |
| 論文査読対応 | バージョン情報の手動記録 | ダイジェスト固定で証明可能 |
| OSレベルの依存 | 管理不能 | コンテナ内に固定 |

再現性レベルの一覧:

| レベル | 構成 | 用途 |
|--------|------|------|
| 1 | README + バージョン記述 | 個人メモ |
| 2 | ロックファイル(conda-lock等) | チーム内共有 |
| 3 | Dockerfile + ロックファイル | 論文投稿 |
| 4 | ダイジェスト固定 + ワークフロー + ロックファイル | 完全再現性 |

コンテナの導入は、condaやvenvによるパッケージ管理の上位レイヤーとして機能する。[§12 ワークフロー管理](./12_workflow.md)で学んだパイプライン定義と組み合わせることで、**コンテナ + ワークフロー + バージョン固定**の三点セットが完成する。

次章の[§13A 実験管理（ML/計算実験の追跡）](./13a_experiment.md)では、機械学習や計算実験のハイパーパラメータ・メトリクスを追跡するツール（wandb、MLflow等）を学ぶ。

---

## 参考文献

[1] Baker, M. "1,500 scientists lift the lid on reproducibility." *Nature*, 533(7604), 452–454, 2016. [https://doi.org/10.1038/533452a](https://doi.org/10.1038/533452a)

[2] Kurtzer, G. M., Sochat, V. & Bauer, M. W. "Singularity: Scientific containers for mobility of compute." *PLoS ONE*, 12(5), e0177459, 2017. [https://doi.org/10.1371/journal.pone.0177459](https://doi.org/10.1371/journal.pone.0177459)

[3] da Veiga Leprevost, F. et al. "BioContainers: an open-source and community-driven framework for software standardization." *Bioinformatics*, 33(16), 2580–2582, 2017. [https://doi.org/10.1093/bioinformatics/btx192](https://doi.org/10.1093/bioinformatics/btx192)

[4] Grüning, B. et al. "Bioconda: sustainable and comprehensive software distribution for the life sciences." *Nature Methods*, 15(7), 475–476, 2018. [https://doi.org/10.1038/s41592-018-0046-7](https://doi.org/10.1038/s41592-018-0046-7)

[5] Merkel, D. "Docker: lightweight Linux containers for consistent development and deployment." *Linux Journal*, 2014(239), 2, 2014. [https://dl.acm.org/doi/10.5555/2600239.2600241](https://dl.acm.org/doi/10.5555/2600239.2600241)

[6] Boettiger, C. "An introduction to Docker for reproducible research." *ACM SIGOPS Operating Systems Review*, 49(1), 71–79, 2015. [https://doi.org/10.1145/2723872.2723882](https://doi.org/10.1145/2723872.2723882)

[7] Nüst, D. et al. "Ten simple rules for writing Dockerfiles for reproducible data science." *PLoS Computational Biology*, 16(11), e1008316, 2020. [https://doi.org/10.1371/journal.pcbi.1008316](https://doi.org/10.1371/journal.pcbi.1008316)

[8] Docker, Inc. "Docker Documentation". [https://docs.docker.com/](https://docs.docker.com/) (参照日: 2026-03-20)

[9] Apptainer Contributors. "Apptainer Documentation". [https://apptainer.org/docs/](https://apptainer.org/docs/) (参照日: 2026-03-20)

[10] GitHub. "Working with the Container registry". [https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry) (参照日: 2026-03-20)
