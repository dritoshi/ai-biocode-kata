# §15 コンテナによるソフトウェア環境の再現 — Docker・Apptainer

[§14 解析パイプラインの自動化](./14_workflow.md)では、Snakemake・Nextflow・makeを使ってパイプラインの処理順序と依存関係を管理する方法を学んだ。しかし、パイプラインの再現性はワークフロー定義だけでは保証されない。同じSnakefileを実行しても、STARのバージョンが異なれば出力BAMのアラインメント結果は変わり、OSのライブラリバージョンが異なればツールの挙動そのものが変わりうる。

[§6 Python環境の構築](./06_dev_environment.md)で学んだcondaやvenvは、Pythonパッケージの隔離には有効であった。しかし、バイオインフォマティクスの解析パイプラインは、PythonだけでなくOSレベルの共有ライブラリ（[§5 ソフトウェアの構成要素 — importからpipまで](./05_software_components.md#共有ライブラリso--dylib)参照）やC/C++製のバイナリツールにも依存する。別のマシンに環境を移したとたん「shared library not found」エラーに遭遇する——これがcondaやvenvだけでは解決できない壁である。

この壁を超えるのが**コンテナ**（container）である。コンテナはアプリケーションとその依存関係（OS、ライブラリ、ツール）を丸ごとパッケージングし、どの計算機でも同一の実行環境を再現する技術である。

AIエージェントはDockerfileや`docker-compose.yml`を生成できる。しかし、ベースイメージの選択（mambaforgeかUbuntuか）、レイヤー構成の効率、HPCでのApptainer互換性、セキュリティ上のベストプラクティス——これらの設計判断は、実行環境とデータの特性を理解している人間がレビューしなければならない。

本章では、コンテナの仕組みから、Docker・Apptainerの実践、論文投稿時の再現性パッケージングまでを学ぶ。

---

## 15-1. なぜコンテナが必要か

### 「自分の環境では動く」問題

以下の3つの場面を想像してみよう:

**場面1: 共同研究者への引き継ぎ。** 自分のMacBookで動いていたRNA-seqパイプラインを、共同研究者のLinuxサーバーに移したところ、STARが「shared library not found」エラーで起動しない。原因はlibhts.soのバージョン違いだった。

ここで登場した`libhts.so`は**共有ライブラリ**（shared library）と呼ばれるファイルである。共有ライブラリとは、複数のプログラムが共通して使う機能をまとめたファイルのことで、samtools や STAR のようなC/C++製バイオツールが実行時に読み込む。[§2 ターミナルとシェルの基本操作](./02_terminal.md#2-3-環境変数とパス)で学んだ`PATH`が「実行ファイルの検索場所」であるように、共有ライブラリにも検索場所がある——Linuxでは`LD_LIBRARY_PATH`、macOSでは`DYLD_LIBRARY_PATH`という環境変数で指定する。condaはsamtools等をインストールするとき、対応するバージョンの`libhts`も一緒に環境内にインストールしてくれる。しかし、conda環境の外では、OSが`libhts.so`を見つけられず「shared library not found」エラーになる。共有ライブラリの仕組みの詳細は[§5 ソフトウェアの構成要素 — importからpipまで](./05_software_components.md#共有ライブラリso--dylib)を参照してほしい。

**場面2: 論文査読への対応。** 査読者から「Table 2の結果を再現できなかった」とコメントが来た。半年前に自分が解析したときのsamtoolsのバージョンを思い出せず、`conda list` の出力も残していなかった。

**場面3: 自分自身の過去の再現。** 1年前の予備実験の結果を再解析しようとしたが、`pip install -r requirements.txt` でインストールされるバージョンが当時と異なり、数値結果が微妙に変わってしまった。

これらはすべて「**依存関係の不一致**」に起因する。[§6 Python環境の構築](./06_dev_environment.md)で学んだcondaやvenvは、Pythonパッケージの隔離には有効だが、OS レベルのライブラリ（libhts、CUDA等）やシステムツール（samtools、STARのバイナリ）までは管理できない。

### Pythonパッケージの隔離 vs. OSレベルの隔離

[§6 Python環境の構築](./06_dev_environment.md#6-1-pythonの環境管理)で学んだ環境管理ツールとコンテナの違いを整理する:

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

[§10 ソフトウェア成果物の設計](./10_deliverables.md#パターン6-dockerコンテナ--apptainerイメージ)で紹介したパターン6（Dockerコンテナ）は、単独の成果物というよりも、他のパターンの「届け方」を補強するレイヤーとして機能する。

### コンテナの仕組み — 仮想マシンとの違い

コンテナの具体的な使い方に入る前に、コンテナが技術的に何であるかを理解しておこう。コンテナはしばしば**仮想マシン**（Virtual Machine; VM）と比較される。両者は「環境を隔離する」という目的は共通だが、仕組みが大きく異なる:

```
仮想マシン（VM）                       コンテナ
┌──────────────────┐                 ┌──────────────────┐
│  アプリ  │ アプリ │                 │  アプリ  │ アプリ │
│──────────│───────│                 │──────────│───────│
│ ゲストOS │ゲストOS│                 │  ライブラリ・ツール │
│──────────│───────│                 │──────────────────│
│  ハイパーバイザー   │                 │ コンテナランタイム  │
│──────────────────│                 │──────────────────│
│    ホストOS        │                 │    ホストOS        │
│──────────────────│                 │──────────────────│
│   ハードウェア      │                 │   ハードウェア      │
└──────────────────┘                 └──────────────────┘
```

VMはゲストOS（Linux, Windows等）を丸ごと起動する。起動に数分かかり、メモリも数GBを消費する。一方、コンテナはホストOSの**カーネル**（OSの中核部分）を共有し、ライブラリやツールだけを隔離する。起動は数秒で、メモリ消費も少ない。

建物にたとえると、VMは「敷地内に別棟を建てる」方式であり、コンテナは「同じ建物内に壁を立てて部屋を区切る」方式である。部屋（コンテナ）ごとに内装（ライブラリ・ツール）は異なるが、基礎と骨組み（カーネル）は共有している。

この「カーネル共有」にはLinuxの**名前空間**（namespace）という隔離機構が使われている。プロセス・ネットワーク・ファイルシステムがコンテナごとに分離されるため、コンテナ内からはあたかも独立したLinux環境のように見える。

**macOS / Windowsユーザーへの注意:** コンテナはLinuxカーネルの機能を使うため、macOSやWindowsで`Docker Desktop`を使う場合、内部的に軽量なLinux仮想マシンが起動している。普段の利用では意識する必要はないが、パフォーマンスやファイル共有の速度がネイティブLinuxと異なる場合がある。

#### エージェントへの指示例

環境の再現性について判断を求めるとき:

> 「このプロジェクトの依存関係を確認して、condaだけで管理できるか、Dockerコンテナが必要かを判断してください。システムライブラリへの依存があるかどうかを調べてください」

> 「共同研究者にこの解析環境を渡したいのですが、再現性を保証するために最低限必要な構成を提案してください。condaのロックファイルとDockerfile、どちらが適切ですか？」

> 「この論文のMethods節に書かれているソフトウェアバージョンを元に、解析環境を再構築するDockerfileを作成してください」

---

## 15-2. Docker

### イメージとコンテナの違い

Dockerの基本概念を理解するために、料理のアナロジーで考える:

- **イメージ**（image）= レシピ。Dockerfileから`docker build`で作成される。レシピ自体は不変であり、複製・共有できる
- **コンテナ**（container）= 料理の実体。イメージから`docker run`で作り出される。食べる（実行する）ことも捨てる（削除する）こともできる

```
Dockerfile  ──build──→  イメージ  ──run──→  コンテナ（実行中）
（材料リストと手順書）   （レシピ本）          （実際の料理）
```

1つのレシピ（イメージ）から何皿でも同じ料理（コンテナ）を作れる。レシピ自体は読み取り専用であり、料理を食べてもレシピが消えることはない。コンテナ内でファイルを変更しても、元のイメージには影響しない。

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
- `environment.yml` を使った宣言的な環境定義（[§6](./06_dev_environment.md#6-1-pythonの環境管理)で学んだ形式）

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

**ダイジェスト**（digest）はイメージの内容から計算されるSHA-256ハッシュ値であり、イメージの内容が1ビットでも変われば値が変わる。タグ（`24.3.0-0`等）は後から別のイメージに付け替えられる可能性があるが、ダイジェストは内容に紐づくため改変できない。論文の再現性を保証するにはダイジェスト指定が最も確実である。

### レイヤーキャッシュの仕組みと最適化

Dockerはイメージをレイヤーの積み重ねとして構築する。各`RUN`、`COPY`、`ADD`命令が1つのレイヤーを生成し、変更のないレイヤーはキャッシュから再利用される。具体的には、ある命令の入力（COPYするファイルの内容やRUNするコマンド文字列）が前回のビルドと同一であれば、その命令を再実行せずにキャッシュ済みのレイヤーを再利用する。これにより、conda環境の構築（数分〜十数分かかる）をソースコード変更のたびに繰り返す必要がなくなる。

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

これは[§14 解析パイプラインの自動化](./14_workflow.md#入力データは読み取り専用)で学んだ「入力データは読み取り専用」の原則と同じである。

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

### エージェントとDockerの連携

#### セキュリティ制約

Dockerfileの生成はエージェントの得意分野であるが、`docker build`や`docker run`の**実行**には注意が必要である。

[§0-1 セットアップと基本操作](./00_ai_agent.md#0-1-セットアップと基本操作)で学んだとおり、AIコーディングエージェントはセキュリティのためにシステムへのアクセスを制限する仕組みを持っている。Docker操作は以下の理由から制限される場合がある:

- `docker run`はホストのファイルシステム・ネットワーク・CPU/メモリにアクセスする
- ボリュームマウント（`-v`）によりホストのファイルが読み書きされる
- コンテナ内で任意のコマンドが実行される

そのため、エージェントの設定によっては`docker`コマンドがブロックされたり、実行のたびに承認を求められたりする。

| パターン | 方法 | 適している場面 |
|---------|------|--------------|
| 読み取り専用で生成 | エージェントにDockerfile・docker-compose.ymlを生成させ、`docker build/run`は自分で実行 | 初めてのDockerfile作成、セキュリティを重視 |
| 承認ありで実行 | `docker build`のたびに承認しながら反復 | Dockerfileのデバッグ（デフォルト動作） |
| 権限を許可 | エージェントの権限設定でdockerコマンドを許可リストに追加 | 信頼できるプロジェクト内での反復作業 |

| | Claude Code CLI | Codex CLI |
|--|----------------|-----------|
| docker許可 | `/permissions` で `Bash(docker *)` を追加 | サンドボックス設定で許可 |

#### 承認ありモードでDockerfileを反復構築する

Dockerfileの構築は、一発で成功することは稀である。特にバイオインフォマティクスの環境構築では、biocondaパッケージの依存関係やシステムライブラリの不足で`docker build`が失敗することが多い。この反復的な作業にこそ、[§0-2 Plan → Execute → Reviewワークフロー](./00_ai_agent.md#0-2-plan--execute--review-ワークフロー)のサイクルが活きる:

```
1. Plan:   Dockerfileの構成を計画（読み取り専用モード）
           「mambaforgeベースでSTAR, samtools, featureCountsを
            含む環境を作りたい。Dockerfileを設計して」

2. Build:  docker build を実行（承認ありモード）
           → ビルドエラーが出る

3. Fix:    エラーメッセージをエージェントに見せて修正
           「このエラーを解析して、Dockerfileを修正して」

4. 2-3を繰り返す → ビルド成功

5. Test:   コンテナ内で解析ツールの動作確認
           「コンテナ内でsamtools --version等を実行して確認して」
```

エージェントのdockerコマンド実行を許可しておくと、「Dockerfileの修正 → ビルド → エラー確認 → 再修正」のサイクルがエージェント内で完結し、効率的である。ただし、ボリュームマウントの設定が意図通りか（特に`:ro`の有無）は必ず自分で確認する。

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
> [§14 解析パイプラインの自動化](./14_workflow.md#conda--container統合)で紹介したSnakemakeの`container:`ディレクティブと組み合わせると、ルールごとに異なるBioContainersイメージを指定できる:
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

## 15-3. Apptainer / Singularity

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

## 15-4. 再現性のレベル

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

ロックファイルの生成と管理は[§6 Python環境の構築](./06_dev_environment.md#ロックファイル--再現性の鍵)で学んだ手法をそのまま使える。

#### エージェントへの指示例

プロジェクトの再現性レベルを評価・改善するとき:

> 「このプロジェクトの現在の再現性レベルを評価してください。README、ロックファイル、Dockerfileのどれが揃っていて、何が不足しているか教えてください」

> 「conda-lockを使ってロックファイルを生成し、そのロックファイルをDockerfile内で使う構成に変更してください」

> 「論文投稿に向けて、再現性レベルを最高にしたい。ベースイメージのダイジェスト固定を含めたDockerfileに更新してください」

---

## 15-5. 論文投稿時の再現性パッケージング

### 三点セットの原則

論文の計算結果を第三者が再現するには、以下の「三点セット」が必要である:

1. **コンテナイメージ**: 実行環境の完全な定義（本章）
2. **ワークフロー**: 処理の実行順序と依存関係（[§14 解析パイプラインの自動化](./14_workflow.md)）
3. **バージョン固定**: 全依存パッケージの正確なバージョン記録（[§6 Python環境の構築](./06_dev_environment.md#ロックファイル--再現性の鍵)）

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
| `v1.0.0` | セマンティックバージョニング（[§7](./07_git.md#7-4-セマンティックバージョニング)参照） | 高 |
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
├── Snakefile                   # ワークフロー（§14）
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

本書のサンプルコード（`scripts/ch15/validate_dockerfile.py`）に、Dockerfileのベストプラクティス準拠をチェックするバリデータを用意している:

```python
from scripts.ch15.validate_dockerfile import validate

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

論文投稿前の最終確認は[付録C 論文投稿前チェックリスト](./appendix_c_checklist.md)を参照。

---

## 15-6. 🤖 実験管理（ML/計算実験の追跡）

前節まででDockerやApptainerによる実行環境の固定を学んだ。しかし、環境が同一でも「どのパラメータで実験したか」が記録されていなければ、結果を再現することはできない。

計算実験では——機械学習のハイパーパラメータ探索であれ、scRNA-seq解析のクラスタリングパラメータ調整であれ、パイプラインのフィルタリング閾値の比較であれ——条件を変えながら何度も試行する。AIエージェントはコードを生成できるが、「先週のあの結果が出た条件」を後から復元するための記録——実験の追跡——は、人間が設計し管理する必要がある。

本節では、実験管理の必要性、主要な追跡ツール（wandb、MLflow等）、そしてツール導入前に始められる最小限の実験管理パターンを学ぶ。

### なぜ実験管理が必要か

#### 「先週のあの結果」問題

以下の場面を想像してみよう:

**場面1: scRNA-seq解析のクラスタリング。** UMAPで細胞の次元削減を行い、`n_neighbors`と`min_dist`のパラメータを変えて10パターン以上試した。最も生物学的に意味のあるクラスタが得られた条件を発表に使いたいが、どのパラメータの組み合わせだったか思い出せない。Jupyter Notebookのセルを上書きしてしまい、履歴も残っていない。

**場面2: ディープラーニングのハイパーパラメータ探索。** タンパク質の機能予測モデルを学習している。learning rate、batch size、隠れ層のサイズ、ドロップアウト率を変えて数十回の学習を回した。最良の検証精度が出た組み合わせを論文に記載したいが、ターミナルの出力はスクロールして消えてしまった。

**場面3: 配列解析パイプラインのパラメータ比較。** RNA-seqのフィルタリング閾値（最小リード数、最小遺伝子数）を変えて差次的発現解析の結果を比較したい。3つの閾値セットで実行したが、どの`config.yaml`でどの結果が出たのか対応がわからなくなった。

#### 管理すべき3つの要素

実験管理とは、以下の3要素を体系的に記録・検索可能にすることである:

| 要素 | 内容 | 例 |
|------|------|-----|
| **ハイパーパラメータ**（入力条件） | 実験ごとに変化させる設定値 | learning rate, n_neighbors, フィルタリング閾値 |
| **メトリクス**（評価値） | 実験結果を定量的に評価する指標 | accuracy, loss, silhouette score, DEG数 |
| **アーティファクト**（成果物） | 実験から生成されるファイル | モデルファイル(.pkl)、UMAPプロット、結果テーブル |

#### Gitとの違い

[§7 Git入門](./07_git.md)で学んだGitは**コード**のバージョン管理ツールである。一方、実験管理は**パラメータ × 結果**のバージョン管理である。

| | Git | 実験管理 |
|--|-----|---------|
| 管理対象 | ソースコード | パラメータ、メトリクス、アーティファクト |
| 追跡単位 | コミット | 実験（ラン） |
| 比較方法 | `git diff` | メトリクスの比較表・グラフ |
| 戻し方 | `git checkout` | 同じパラメータで再実行 |

両者は排他的ではなく、併用するものである。実験管理ツールの多くは、実験時のgitコミットハッシュを自動記録し、「あの精度が出たときのコードはどのバージョンだったか」を追跡できるようにしている。

#### エージェントへの指示例

実験管理の設計についてエージェントに相談する場合:

> 「このモデル学習スクリプトに実験追跡を追加したい。記録すべきハイパーパラメータとメトリクスを提案してください」

> 「scRNA-seqのクラスタリング解析で、n_neighbors、min_dist、resolutionの組み合わせを系統的に試したい。パラメータと結果を管理する方法を提案してください」

> 「Jupyter Notebookで実験を繰り返しているが、条件と結果の対応がわからなくなる。Notebookから実験ログを記録する仕組みを追加してください」

### 実験追跡ツール

#### ツールの比較

[§14 解析パイプラインの自動化](./14_workflow.md)の🤖コラムでSnakemake/Nextflowとの使い分けを紹介した。ここでは、実験追跡に特化したツールの特徴を整理する:

| ツール | 種別 | 特徴 | 向いている場面 |
|-------|------|------|--------------|
| **wandb**（Weights & Biases） | クラウドSaaS | 可視化が美しい、チーム共有が容易、無料枠あり | ML学習実験、ハイパーパラメータ探索 |
| **MLflow** | OSS | ローカル/サーバー両対応、モデルレジストリ | モデル管理、オンプレミス環境 |
| **hydra** | OSS | 設定ファイルの構成管理（追跡そのものではない） | パラメータの組み合わせ管理 |
| **DVC**（Data Version Control） | OSS | データとモデルのバージョン管理（Git連携） | 大規模データのバージョニング |

#### wandb — クラウドベースの実験追跡

wandbは最も手軽に導入できる実験追跡ツールである。無料の個人アカウントで始められ、ブラウザ上でメトリクスの推移グラフやパラメータの比較表を確認できる。

以下は、scRNA-seqデータのクラスタリングにおいて、UMAPの次元削減パラメータ（`n_neighbors`: 近傍点の数、`min_dist`: 点間の最小距離）とクラスタリングの解像度（`resolution`）を変えて最適な細胞クラスタを探索する実験を記録する例である:

```python
import wandb

# プロジェクトと実験を初期化
wandb.init(project="rnaseq-clustering", name="umap-exp-01")

# ハイパーパラメータを記録
# n_neighbors: UMAPが参照する近傍点の数（大きいほど大域構造を重視）
# min_dist: UMAP上での点間の最小距離（小さいほどクラスタが密になる）
# resolution: Leidenクラスタリングの解像度（大きいほど細かいクラスタに分割）
wandb.config.update({
    "n_neighbors": 15,
    "min_dist": 0.1,
    "resolution": 0.5,
})

# ... scanpyによるUMAP + クラスタリング実行 ...

# メトリクスを記録
# silhouette_score: クラスタの分離度（-1〜1、高いほど良い）
# ari: Adjusted Rand Index（既知の細胞型ラベルとの一致度）
wandb.log({
    "silhouette_score": 0.72,
    "n_clusters": 5,
    "ari": 0.65,
})

# 可視化結果をアーティファクトとして保存
wandb.log({"umap_plot": wandb.Image("umap.png")})

wandb.finish()
```

#### MLflow — オンプレミス対応の実験追跡

MLflowはオープンソースの実験管理プラットフォームである。クラウドに依存せず、ローカルマシンや研究室のサーバーで完結できる。モデルレジストリ機能により、学習済みモデルのバージョン管理も可能である。

以下は、タンパク質の機能予測モデル（ニューラルネットワーク）を学習する実験で、近傍点の数や点間距離を変えながら分類精度を比較する例である:

```python
import mlflow

# 実験を開始
with mlflow.start_run(run_name="protein-func-exp-01"):
    # ハイパーパラメータを記録
    mlflow.log_param("learning_rate", 0.001)
    mlflow.log_param("batch_size", 64)
    mlflow.log_param("hidden_dim", 256)
    mlflow.log_param("dropout", 0.3)

    # ... PyTorchによるモデル学習 ...

    # メトリクスを記録
    # accuracy: テストデータでの正解率
    # f1_score: クラス不均衡を考慮した総合指標
    mlflow.log_metric("accuracy", 0.95)
    mlflow.log_metric("f1_score", 0.88)

    # アーティファクトを保存（学習済みモデルと混同行列の図）
    mlflow.log_artifact("model.pkl")
    mlflow.log_artifact("confusion_matrix.png")
```

```bash
# MLflow UIを起動してブラウザで結果を確認
mlflow ui --port 5000
```

#### ツール選択の判断基準

| 状況 | 推奨ツール |
|------|----------|
| 個人利用で手軽に始めたい | wandb（無料枠あり、セットアップが簡単） |
| オンプレミス/自前サーバーで管理したい | MLflow |
| パラメータの組み合わせが多い | hydra + wandb/MLflow |
| 大規模データ（数十GB以上のモデル等）のバージョン管理 | DVC |
| 配列解析パイプライン中心、ML要素が少ない | 次項の自前ログで十分 |

[§14 解析パイプラインの自動化](./14_workflow.md)の🤖コラムで述べたとおり、配列解析パイプライン（外部ツール呼び出しが中心）は[Snakemake/Nextflow](./14_workflow.md#14-2-ワークフロー言語)、機械学習実験（Pythonコードが中心）はwandb/MLflowと使い分けるのが現実的である。両方を含むプロジェクトでは、Snakemakeのワークフロー内でMLflowやwandbのトラッキングを呼び出す組み合わせも有効である。

#### エージェントへの指示例

実験追跡ツールの導入をエージェントに依頼する場合:

> 「この学習スクリプトにwandbの追跡を追加してください。ハイパーパラメータはconfig辞書から、メトリクスはエポックごとのlossとaccuracyを記録してください」

> 「MLflowでローカルに実験を追跡したい。セットアップ手順と、このスクリプトに組み込む最小限のコードを教えてください」

> 「hydraを使って、learning_rate=[0.001, 0.01, 0.1]、batch_size=[32, 64, 128]の組み合わせを自動的に実行する設定を作成してください」

### 最小限の実験管理パターン

#### ツール導入前に始められる自前実装

wandbやMLflowを導入する前に、まず最小限のログ記録を自前で実装することを推奨する。これにより、「実験を記録する習慣」を身につけ、ツール導入後も何を記録すべきかの判断力が養われる。

本書のサンプルコード（`scripts/ch15/experiment_logger.py`）に、JSONL形式の実験ログ記録ツールを用意している。

以下は、scRNA-seqデータのクラスタリングで、UMAPパラメータ（`n_neighbors`, `min_dist`）とクラスタリング解像度（`resolution`）の組み合わせを変えながらシルエットスコアで最良の条件を探す例である:

```python
from scripts.ch15.experiment_logger import log_experiment, load_experiments, find_best

# 実験1: 近傍点15、最小距離0.1、解像度0.5 → 5クラスタ、シルエット0.72
log_experiment(
    params={"n_neighbors": 15, "min_dist": 0.1, "resolution": 0.5},
    metrics={"silhouette": 0.72, "n_clusters": 5},
    output_dir="results/experiments",
)

# 実験2: 近傍点を30に増やし、解像度を上げる → 3クラスタ、シルエット0.68
log_experiment(
    params={"n_neighbors": 30, "min_dist": 0.2, "resolution": 0.8},
    metrics={"silhouette": 0.68, "n_clusters": 3},
    output_dir="results/experiments",
)

# ログを読み込んで、シルエットスコアが最も高い実験を検索
experiments = load_experiments("results/experiments/experiment_log.jsonl")
best = find_best(experiments, "silhouette", maximize=True)
print(f"最良パラメータ: {best.params}")  # {"n_neighbors": 15, ...}
```

以下は生成されるJSONLファイルの内容例である。JSONL（JSON Lines）は1行に1つのJSONオブジェクトを記録する形式で、ファイルへの追記が容易であり、`pandas.read_json(path, lines=True)` で直接DataFrameに読み込める。

```json
{"timestamp": "2026-03-20T10:30:00+00:00", "git_hash": "a1b2c3d", "params": {"n_neighbors": 15, "min_dist": 0.1}, "metrics": {"silhouette": 0.72}}
{"timestamp": "2026-03-20T11:00:00+00:00", "git_hash": "a1b2c3d", "params": {"n_neighbors": 30, "min_dist": 0.2}, "metrics": {"silhouette": 0.68}}
```

#### 段階的な導入パス

実験管理ツールは、必要に応じて段階的に導入するのが現実的である:

| 段階 | 手法 | 導入タイミング |
|------|------|--------------|
| 1 | 自前JSONLログ（本節で実装） | 最初から。まず記録する習慣をつける |
| 2 | wandb導入 | 実験数が数十を超え、可視化・比較が手動では困難になったとき |
| 3 | hydraで設定管理 | パラメータの組み合わせが爆発し、手動でconfig.yamlを書くのが非効率になったとき |
| 4 | DVCでデータ版管理 | データセット自体のバージョンを管理する必要が出てきたとき |

段階1から始めて、プロジェクトの成長に合わせてツールを追加していく。すべてのツールを最初から導入する必要はない。

> 🧬 **コラム: 配列解析パイプラインの実験管理**
>
> 機械学習に限らず、配列解析パイプラインでもパラメータの比較は頻繁に発生する。RNA-seqの発現量フィルタリング閾値（最小リード数、最小検出細胞数）やアライメントオプション（ミスマッチ許容数、マルチマッピング方針）を変えて結果を比較するケースである。
>
> [§14 解析パイプラインの自動化](./14_workflow.md#パラメータの設定ファイル化)で学んだSnakemakeの`config.yaml`を実験ごとに保存しておくと、簡易的な実験管理として機能する:
>
> ```bash
> # 実験ごとにconfigを保存
> cp config.yaml results/exp_01/config.yaml
> snakemake --configfile config.yaml --cores 8
>
> # パラメータを変更して再実験
> cp config_v2.yaml results/exp_02/config.yaml
> snakemake --configfile config_v2.yaml --cores 8
> ```
>
> 各実験ディレクトリに`config.yaml`のコピーを残すことで、「この結果はどのパラメータで出したか」を後から追跡できる。これは段階1（自前ログ）の一形態であり、wandb/MLflowが不要な規模のプロジェクトではこれで十分な場合も多い。

#### エージェントへの指示例

最小限の実験管理を導入する場合:

> 「この学習スクリプトに`experiment_logger.py`を組み込んで、各エポック終了時にパラメータとメトリクスを記録してください」

> 「`results/experiments/experiment_log.jsonl`に記録された実験結果を読み込んで、accuracyが最も高い実験のパラメータを表示するスクリプトを書いてください」

> 「現在は自前のJSONLログで実験管理しています。wandbに移行したいので、既存のログ記録部分をwandbの`init/config/log`に置き換えてください」

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

| 概念 | 内容 | 関連する節 |
|------|------|-----------|
| 実験管理の3要素 | パラメータ、メトリクス、アーティファクト | §15-6 |
| Gitとの違い | コード管理 vs パラメータ×結果の管理 | [§7 Git入門](./07_git.md) |
| wandb / MLflow | 専用追跡ツール | [§6 Python環境の構築](./06_dev_environment.md) |
| Snakemake連携 | ワークフロー + 実験追跡の組み合わせ | [§14 解析パイプラインの自動化](./14_workflow.md) |
| 段階的導入 | 自前ログ → wandb → hydra → DVC | §15-6 |

コンテナの導入は、condaやvenvによるパッケージ管理の上位レイヤーとして機能する。[§14 解析パイプラインの自動化](./14_workflow.md)で学んだパイプライン定義と組み合わせることで、**コンテナ + ワークフロー + バージョン固定**の三点セットが完成する。実験管理は、コードのバージョン管理（[§7 Git入門](./07_git.md)）、環境の再現性（§15-1〜15-5）と並んで、計算科学の再現性を支える3本目の柱である。

次章の[§16 スパコン・クラスタでの大規模計算](./16_hpc.md)では、HPCクラスタでの計算実行——SLURMジョブスケジューラ、GPUリソース管理、データ転送——を学ぶ。

---

## さらに学びたい読者へ

本章で扱ったコンテナ技術と研究再現性をさらに深く学びたい読者に向けて、原論文と公式ドキュメントを紹介する。

### 研究再現性とコンテナ

- **Boettiger, C. "An introduction to Docker for reproducible research." *ACM SIGOPS Operating Systems Review*, 49(1), 71–79, 2015.** — 研究再現性の観点からDockerを導入した先駆的論文。なぜコンテナが科学研究に必要かの理論的基盤を示す。
- **Nüst, D. et al. "Ten simple rules for writing Dockerfiles for reproducible data science." *PLOS Computational Biology*, 16(11), e1008316, 2020.** — 再現可能なDockerfileの書き方を10のルールで整理。本章で扱ったDockerfile設計のベストプラクティスの詳細版。

### バイオインフォマティクスのコンテナ化

- **Gruening, B. et al. "Recommendations for the packaging and containerizing of bioinformatics software." *F1000Research*, 7, 742, 2018.** — バイオインフォソフトウェアのコンテナ化とパッケージングの推奨事項をまとめた論文。BioContainersの設計思想を理解できる。

### 公式ドキュメント

- **Docker Documentation.** https://docs.docker.com/ — Dockerの公式ドキュメント。マルチステージビルド、BuildKit、Docker Compose等の詳細な機能解説。
- **Apptainer Documentation.** https://apptainer.org/docs/ — HPC環境向けコンテナランタイムの公式ドキュメント。Dockerイメージからの変換方法やHPC固有の設定が詳しい。

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

[11] Biewald, L. "Experiment Tracking with Weights and Biases." *Weights & Biases*, 2020. [https://www.wandb.com/](https://www.wandb.com/) (参照日: 2026-03-20)

[12] Zaharia, M. et al. "Accelerating the Machine Learning Lifecycle with MLflow." *IEEE Data Engineering Bulletin*, 41(4), 39–45, 2018. [https://doi.org/10.1109/DSAA.2018.00006](https://doi.org/10.1109/DSAA.2018.00006)

[13] Yadan, O. "Hydra — A framework for elegantly configuring complex applications." 2019. [https://hydra.cc/](https://hydra.cc/) (参照日: 2026-03-20)

[14] Iterative. "DVC: Data Version Control — Git for Data." [https://dvc.org/](https://dvc.org/) (参照日: 2026-03-20)

[15] Tatman, R., VanderPlas, J. & Dane, S. "A Practical Taxonomy of Reproducibility for Machine Learning Research." *Reproducibility in ML Workshop at ICML*, 2018.

[16] Weights & Biases. "W&B Documentation". [https://docs.wandb.ai/](https://docs.wandb.ai/) (参照日: 2026-03-20)

[17] MLflow Contributors. "MLflow Documentation". [https://mlflow.org/docs/latest/](https://mlflow.org/docs/latest/) (参照日: 2026-03-20)
