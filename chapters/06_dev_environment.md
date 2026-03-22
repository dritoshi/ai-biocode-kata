# §6 Python環境の構築 — pyenv・venv・conda・uv

[§5 ソフトウェアの構成要素 — importからpipまで](./05_software_components.md)では、ライブラリ・パッケージ・モジュールの仕組みと `import` の裏側を学んだ。しかし、これらの知識があっても、コードを書いて動かす「場」が整っていなければ解析は始まらない。本章では、Pythonの環境管理とパッケージマネージャの概念を学び、再現性のある開発環境を構築するための基盤を固める。

AIエージェントと協働する上で、環境管理の知識は不可欠である。エージェントは `pip install` や `conda install` を自動的に実行するが、環境が隔離されていなければ別プロジェクトの依存関係を壊す。`requirements.txt` や `environment.yml` をエージェントに生成させても、その内容をレビューできなければ意味がない。

「自分のPCでは動いたのに、共同研究者のPCでは動かない」——この問題の大半は、環境構築の不備に起因する。Pythonのバージョン、インストールされたパッケージのバージョン、OSレベルの依存ライブラリ。これらを明示的に管理することが、再現可能な研究の第一歩である。

---

## 6-1. Pythonの環境管理

### なぜ環境管理が必要か

バイオインフォマティクスの解析では、プロジェクトごとに異なるパッケージやバージョンを使うことが日常的に起こる。たとえば、RNA-seqパイプラインではPython 3.10とscanpy 1.9が必要だが、新しいシングルセル解析プロジェクトではPython 3.11とscanpy 1.10を使いたい、といった状況である。

これらを1つのPython環境に同居させると、バージョンの衝突が起きる。あるパッケージの更新が別のパッケージを壊す——いわゆる**依存関係地獄**（dependency hell）である。環境管理ツールは、プロジェクトごとに隔離された環境を作ることで、この問題を解決する。

### pyenv — Pythonバージョンの管理

**pyenv**は、複数のPythonバージョンをシステムに共存させ、プロジェクトごとに切り替えるためのツールである[1](https://github.com/pyenv/pyenv)。

```bash
# Pythonバージョンのインストール
pyenv install 3.11.9
pyenv install 3.12.4

# プロジェクトディレクトリでバージョンを固定
cd my-project/
pyenv local 3.11.9    # .python-version ファイルが生成される

# 現在のバージョン確認
python --version       # Python 3.11.9
```

`pyenv local` を実行すると、そのディレクトリに `.python-version` というファイルが作られる。以後、このディレクトリ内では指定したバージョンのPythonが自動的に使われる。このファイルをGitリポジトリに含めておけば、共同研究者も同じバージョンを使える（Gitについては[§7 Git入門](./07_git.md)で学ぶ）。

### venv — 標準ライブラリの仮想環境

**venv**はPython標準ライブラリに含まれる仮想環境ツールである[2](https://docs.python.org/3/library/venv.html)。追加のインストールなしに使えるため、最もシンプルな選択肢である。

```bash
# 仮想環境の作成
python -m venv .venv

# 有効化（macOS / Linux）
source .venv/bin/activate

# パッケージのインストール（仮想環境内に閉じる）
pip install biopython numpy pandas

# 無効化
deactivate
```

仮想環境を有効化すると、シェルのプロンプトに `(.venv)` が表示される。この状態で `pip install` したパッケージは `.venv/` ディレクトリ内にのみインストールされ、システムのPython環境を汚さない。

#### 仮想環境の仕組み

`activate` スクリプトが行っていることは、実はシンプルである:

1. 環境変数 `PATH` の先頭に `.venv/bin/` を追加する
2. `python` コマンドが `.venv/bin/python` を指すようになる
3. `pip install` の宛先が `.venv/lib/` 以下に変わる

Pythonスクリプト内からは `sys.prefix` で現在の仮想環境のパスを確認できる:

```python
import sys

# 仮想環境が有効な場合
print(sys.prefix)      # /path/to/project/.venv
print(sys.base_prefix)  # /path/to/python3.11（システム側）

# 仮想環境内かどうかの判定
in_venv: bool = sys.prefix != sys.base_prefix
```

### miniforge / micromamba — conda環境

バイオインフォマティクスでは**conda**が事実上の標準（de facto standard）として広く使われている。condaはPythonパッケージだけでなく、C/C++で書かれたバイナリツール（samtools, BWA等）もまとめて管理できる点が最大の強みである[3](https://docs.conda.io/projects/conda/en/latest/)。

condaを使い始めるには、**miniforge**または**micromamba**をインストールする[4](https://github.com/conda-forge/miniforge)。かつてはAnacondaやMinicondaが広く使われていたが、Anacondaのライセンス変更（商用利用の有償化）により、オープンソースのminiforgeが推奨される。

```bash
# miniforgeのインストール後の基本操作

# 新しい環境の作成
conda create -n rnaseq-env python=3.11 numpy pandas biopython

# 環境の有効化
conda activate rnaseq-env

# パッケージの追加インストール
conda install -c conda-forge scikit-learn

# 環境の一覧
conda env list

# 環境の無効化
conda deactivate
```

**micromamba**はcondaの高速な代替実装であり、同じ操作体系で動作する[5](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html)。大量のパッケージを扱うバイオインフォ環境では、依存解決の速度差が顕著になるため、micromambaの採用も検討に値する。

### uv — 高速な新世代パッケージマネージャ

**uv**はRust製の高速Pythonパッケージマネージャであり、pip, venv, pyenvの機能を統合的に提供する[6](https://docs.astral.sh/uv/)。2024年にリリースされて以降、急速に普及が進んでいる。

```bash
# uvのインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクトの初期化
uv init my-project
cd my-project

# 仮想環境の作成とパッケージインストール
uv venv
uv pip install biopython numpy

# ロックファイルの生成
# uv lock は pyproject.toml の依存定義を解決し、
# すべてのパッケージの正確なバージョンを uv.lock ファイルに記録するコマンドである
uv lock

# ロックファイルからの再現
uv sync
```

uvの特徴は速度である。pipと比較して10〜100倍の速度でパッケージを解決・インストールする。ただし、condaのようにC/C++バイナリを直接管理する機能は持たないため、バイオインフォマティクスではcondaとの併用が現実的な選択肢となる。

### 依存関係定義ファイルの比較

プロジェクトの依存関係を記述するファイルには複数の形式がある。それぞれの特徴と使い分けを以下にまとめる:

| ファイル | ツール | 特徴 | 推奨場面 |
|---------|--------|------|---------|
| `requirements.txt` | pip | シンプルなパッケージ名＋バージョン指定 | 小規模スクリプト、既存プロジェクトとの互換 |
| `pyproject.toml` | pip / uv | プロジェクトメタデータと依存関係を一元管理 | ライブラリ開発、新規プロジェクト |
| `environment.yml` | conda | Pythonバージョン＋チャネル＋パッケージを記述 | バイオインフォ解析、バイナリ依存があるとき |

```
# requirements.txt の例
biopython>=1.83
numpy>=1.26,<2.0
pandas>=2.0
```

```toml
# pyproject.toml の例（[§4 データフォーマットの選び方](./04_data_formats.md)でも登場）
[project]
name = "my-bioinfo-tool"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "biopython>=1.83",
    "numpy>=1.26",
]
```

```yaml
# environment.yml の例
name: rnaseq-env
channels:
  - conda-forge
  - bioconda
  - defaults
dependencies:
  - python=3.11
  - numpy>=1.26
  - biopython>=1.83
  - samtools=1.19
  - pip:
    - scanpy>=1.10
```

`pyproject.toml` はPythonプロジェクトの標準的な設定ファイルとして定着しつつあり[7](https://packaging.python.org/en/latest/specifications/pyproject-toml/)、新規プロジェクトではこれを使うのが望ましい。一方、samtools等のバイナリツールも含めた環境定義が必要な場合は `environment.yml` が適している。

### 依存関係の競合と解決

依存関係の競合（dependency conflict）は、2つ以上のパッケージが同じパッケージの異なるバージョンを要求するときに起こる。たとえば:

```
パッケージA が numpy>=1.26,<2.0 を要求
パッケージB が numpy>=2.0 を要求
→ 両方を同時にインストールできない
```

競合が起きた場合の対処法:

1. **エラーメッセージを読む** — pip/condaは競合の原因を表示する
2. **バージョン制約を緩和する** — 可能であれば、片方のパッケージを更新する
3. **環境を分ける** — 互換性のないツールは別の仮想環境に分離する
4. **`pip check`** で整合性を確認する — インストール済みパッケージ間の矛盾を検出する

```bash
# インストール済みパッケージの整合性チェック
pip check

# condaの場合
conda list --revisions  # 変更履歴の確認
```

環境を分けることは、競合を避ける最も確実な方法である。バイオインフォマティクスでは用途別に環境を作る（`mapping-env`, `rnaseq-env`, `ml-env` 等）のが一般的な実践である。

#### エージェントへの指示例

環境構築はAIコーディングエージェントに一括で依頼できるタスクである。プロジェクトの要件を伝えれば、適切な環境定義ファイルを生成してくれる:

> 「Python 3.11でRNA-seq解析用のconda環境を作成してください。`environment.yml` にnumpy, pandas, scanpy, biopythonを含めてください。チャネルはconda-forgeとbiocondaを使ってください」

> 「このプロジェクトに `pyproject.toml` を作成してください。Python 3.10以上を要求し、依存パッケージはbiopython, numpy, pandasです。開発用の依存には pytest, ruff, mypy を含めてください」

依存関係の競合を解決する場合:

> 「`pip install` で依存関係の競合が発生しています。エラーメッセージを読んで原因を特定し、バージョン制約の緩和または環境の分離で解決してください」

---

## 6-2. パッケージマネージャの概念

### パッケージマネージャが解決する問題

パッケージマネージャが存在しなかった時代、ソフトウェアのインストールは以下の手順を踏む必要があった:

1. ソースコードをダウンロード
2. 依存ライブラリを手動でインストール（さらにその依存も……）
3. `./configure && make && make install`
4. パスを通す

この手順を1つのツールにつき繰り返すのは非現実的である。パッケージマネージャは、依存関係の自動解決、バージョン管理、インストール・アンインストールの一元化を提供する。

### パッケージマネージャの使い分け

バイオインフォマティクスで出会う主要なパッケージマネージャを比較する:

| パッケージマネージャ | 対象 | 管理単位 | バイオでの主な用途 |
|-------------------|------|---------|-------------------|
| **pip** | Pythonパッケージ | PyPIレジストリ | Pythonライブラリのインストール |
| **conda** | 言語非依存 | conda-forge, bioconda等 | バイナリツール＋Pythonの統合管理 |
| **uv** | Pythonパッケージ | PyPIレジストリ | pipの高速代替 |
| **brew** | macOS/Linuxアプリ | Homebrew | 開発ツール（git, node等） |
| **apt** | Debian/Ubuntu | OSリポジトリ | システムライブラリ |

基本原則は「**Python関連はcondaまたはpip/uvで、OS関連はbrew/aptで**」という使い分けである。conda環境内でpipを使うことも可能だが、condaとpipを混在させるとパッケージの追跡が困難になるため、可能な限りどちらかに統一するのが望ましい。

### ロックファイル — 再現性の鍵

`requirements.txt` や `environment.yml` だけでは、完全な再現性は保証できない。たとえば `numpy>=1.26` という指定は、インストール時期によって 1.26.0 にも 1.26.4 にもなりうる。

**ロックファイル**（lock file）は、依存関係ツリーの全パッケージについて、実際にインストールされた正確なバージョンを記録するファイルである[8](https://github.com/conda/conda-lock):

| ツール | ロックの方法 | 生成されるファイル |
|--------|------------|-------------------|
| pip | `pip freeze > requirements-lock.txt` | バージョン固定のrequirements |
| conda-lock | `conda-lock -f environment.yml` | `conda-lock.yml` |
| uv | `uv lock` | `uv.lock` |

```bash
# pip freeze によるバージョン固定
pip freeze > requirements-lock.txt
# 出力例:
# biopython==1.83
# numpy==1.26.4
# pandas==2.2.1

# conda-lock による厳密なロック
# -p はロックファイルを生成する対象プラットフォームを指定する
# HPCがLinuxであれば linux-64、macOSであれば osx-64（Intel）または osx-arm64（Apple Silicon）
conda-lock -f environment.yml -p linux-64
# 出力: conda-lock.yml（プラットフォーム固有のハッシュ付き）

# uv lock
uv lock
# 出力: uv.lock（依存ツリー全体のバージョン固定）
```

ロックファイルを[§7 Git入門](./07_git.md)で学ぶGitリポジトリにコミットしておけば、共同研究者が `pip install -r requirements-lock.txt` や `conda-lock install` で同一の環境を再現できる。

### チャネルとレジストリ

パッケージマネージャは、**レジストリ**（registry）または**チャネル**（channel）と呼ばれるサーバからパッケージをダウンロードする:

| レジストリ/チャネル | 対象ツール | 特徴 |
|-------------------|-----------|------|
| **PyPI** | pip, uv | Pythonパッケージの公式レジストリ。誰でも公開可能 |
| **conda-forge** | conda | コミュニティ運営の最大のcondaチャネル |
| **bioconda** | conda | バイオインフォマティクスに特化したチャネル[9](https://doi.org/10.1038/s41592-018-0046-7) |
| **defaults** | conda | Anaconda社が管理するチャネル（ライセンスに注意） |

condaでは、チャネルの優先順位を `.condarc` ファイルで設定する:

```yaml
# ~/.condarc
channels:
  - conda-forge
  - bioconda
  - defaults
channel_priority: strict
```

`channel_priority: strict` を設定すると、上位のチャネルが優先される。バイオインフォマティクスでは conda-forge と bioconda を上位に置くのが一般的である。

#### エージェントへの指示例

パッケージの探索やインストール手順の調査はエージェントの得意分野である:

> 「samtools, BWA, fastpをbiocondaからインストールする手順を教えてください。用途別に環境を分ける構成で `environment.yml` を作成してください」

> 「`pip freeze` の出力からロックファイル（`requirements-lock.txt`）を生成してください。また、`uv lock` でより厳密なロックファイルを作る方法も示してください」

> **🧬 コラム: biocondaでのツールセットアップ**
>
> **bioconda**は、8,000以上のバイオインフォマティクスツールを提供するcondaチャネルである[9](https://doi.org/10.1038/s41592-018-0046-7)。BLAST, samtools, BWA, STAR, fastp など、日常的に使うツールの大半がbiocondaからインストールできる:
>
> `-c` はチャネル（パッケージの配布元）を指定するオプションである。biocondaはバイオインフォマティクスツール専用、conda-forgeは汎用パッケージのチャネルであり、記述順がパッケージ検索の優先順位になる。
>
> ```bash
> # biocondaからのツールインストール
> conda install -c bioconda -c conda-forge samtools minimap2 fastp
> ```
>
> **用途別に環境を分ける**のがベストプラクティスである。これにより、ツール間の依存関係の衝突を防げる:
>
> ```bash
> # マッピング用環境
> conda create -n mapping-env -c bioconda -c conda-forge \
>     bwa-mem2 samtools picard
>
> # バリアントコール用環境
> conda create -n variant-env -c bioconda -c conda-forge \
>     gatk4 bcftools tabix
>
> # RNA-seq用環境
> conda create -n rnaseq-env -c bioconda -c conda-forge \
>     star salmon fastp multiqc
> ```
>
> biocondaに収録されていないツールもある。その場合は、ソースコードからのビルド、pip install、あるいはコンテナ（[§15 コンテナによるソフトウェア環境の再現](./15_container.md)で扱う）を検討する。biocondaへの貢献（レシピの追加）も歓迎されている。
>
> **アラインメントツールの使い分け**: 同じ「配列をマッピングする」タスクでも、データの種類によって適切なツールは異なる。エージェントにパイプラインを構築させる際、ツール名を指定できるとより正確な結果が得られる:
>
> | データ種別 | 推奨ツール | 理由 |
> |---|---|---|
> | DNA-seq ショートリード | BWA-MEM2 | 連続マッピング前提。BWAの後継で高速 |
> | RNA-seq ショートリード | STAR / HISAT2 | スプライスジャンクション対応 |
> | ロングリード（ONT / PacBio） | minimap2 | 高エラー率・長いリードに対応 |
> | タンパク質相同性検索 | DIAMOND（高速） / BLAST+（標準） | 大規模データにはDIAMONDが桁違いに速い |
> | マルチプルアラインメント | MAFFT | `--auto` で自動パラメータ選択。デフォルトで十分な精度 |

> **🤖 コラム: 機械学習環境の構築**
>
> バイオインフォマティクスと機械学習の融合領域——シングルセル基盤モデル（scFoundation model）、変異の病原性予測、タンパク質構造予測（AlphaFold等）——では、GPU環境の構築が必要になる。
>
> **CUDA/PyTorchのインストール（conda推奨）:**
>
> `pytorch-cuda=12.1` はGPU対応版PyTorchに必要なCUDAランタイムである。`-c pytorch -c nvidia` はPyTorch公式とNVIDIA公式のチャネルで、これらからGPU対応バイナリが提供される。
>
> ```bash
> # ML用環境の作成
> conda create -n ml-env python=3.11
> conda activate ml-env
> conda install pytorch pytorch-cuda=12.1 -c pytorch -c nvidia
> # または pip で:
> # pip install torch --index-url https://download.pytorch.org/whl/cu121
> ```
>
> **よくあるハマりポイント:**
>
> - **CUDAドライバとCUDA Toolkitのバージョン不一致** — CUDAドライバ（OS/GPU側）とCUDA Toolkit（PyTorch側）には互換性の制約がある。`nvidia-smi` でドライバのバージョンを確認し、`torch.cuda.is_available()` でPyTorchからGPUが認識されているかを確認する
> - **HPC環境でのモジュールシステム** — 大学や研究所のHPCでは `module load cuda/12.1` のようなモジュールシステムでCUDAを管理することが多い。conda環境内のcudatoolkitとシステムのCUDAが競合しないよう注意する
> - **conda環境のcudatoolkit vs システムCUDA** — conda環境に `cudatoolkit` を入れる方法と、システムにインストールされたCUDAを使う方法の2つがある。HPCではシステムCUDAを使うのが一般的だが、ローカルマシンではconda管理が楽である
>
> **バイオインフォML系でよく使うライブラリ:**
>
> | ライブラリ | 用途 |
> |-----------|------|
> | **PyTorch** / **JAX** | 深層学習フレームワーク |
> | **scikit-learn** | 古典的機械学習（分類、クラスタリング、前処理） |
> | **Hugging Face Transformers** | 事前学習済みモデルの利用 |
> | **wandb** / **MLflow** | 実験追跡（[§15 コンテナによるソフトウェア環境の再現](./15_container.md)で詳述） |
> | **optuna** | ハイパーパラメータ最適化 |

---

## まとめ

本章で学んだ開発環境構築の判断基準を一覧にまとめる:

| 判断場面 | 推奨 | 理由 |
|---------|------|------|
| Pythonバージョン管理 | pyenv | プロジェクトごとに `.python-version` で固定 |
| Python仮想環境（シンプル） | venv | 標準ライブラリ、追加インストール不要 |
| バイナリツールを含む環境 | conda（miniforge） | samtools等のC/C++ツールも管理可能 |
| 高速なパッケージ管理 | uv | pip互換で10〜100倍高速 |
| 依存関係ファイル（新規） | pyproject.toml | Pythonプロジェクトの標準 |
| 依存関係ファイル（バイオ） | environment.yml | バイナリ＋Python＋チャネル指定 |
| バージョンの厳密な固定 | ロックファイル | 再現性の保証 |
| バイオツールのインストール | bioconda | 8,000+のツールが利用可能 |
| ツール間の依存衝突 | 環境を分ける | 用途別に隔離が最も確実 |

環境構築は地味な作業に見えるが、ここでの判断が解析の再現性を左右する。[§1 設計原則 — 良いコードとは何か](./01_design.md)で学んだ「明示は暗黙に勝る」（Explicit is better than implicit）の精神で、使用するPythonバージョン・パッケージのバージョン・インストール手順を常に明文化しておこう。

次章の[§7 Git入門](./07_git.md)では、コードと環境定義ファイルをGitで管理し、変更履歴を追跡する方法を学ぶ。

---

## 参考文献

[1] pyenv contributors. "pyenv — Simple Python version management". [https://github.com/pyenv/pyenv](https://github.com/pyenv/pyenv) (参照日: 2026-03-18)

[2] Python Software Foundation. "venv --- Creation of virtual environments". *Python 3 Documentation*. [https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html) (参照日: 2026-03-18)

[3] Conda contributors. "Conda Documentation". [https://docs.conda.io/projects/conda/en/latest/](https://docs.conda.io/projects/conda/en/latest/) (参照日: 2026-03-18)

[4] conda-forge contributors. "Miniforge". [https://github.com/conda-forge/miniforge](https://github.com/conda-forge/miniforge) (参照日: 2026-03-18)

[5] Mamba contributors. "Micromamba User Guide". [https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html) (参照日: 2026-03-18)

[6] Astral. "uv: An extremely fast Python package and project manager". [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/) (参照日: 2026-03-18)

[7] Python Packaging Authority. "pyproject.toml specification". [https://packaging.python.org/en/latest/specifications/pyproject-toml/](https://packaging.python.org/en/latest/specifications/pyproject-toml/) (参照日: 2026-03-18)

[8] conda-lock contributors. "conda-lock: Lightweight lockfile for conda environments". [https://github.com/conda/conda-lock](https://github.com/conda/conda-lock) (参照日: 2026-03-18)

[9] Grüning, B. et al. "Bioconda: sustainable and comprehensive software distribution for the life sciences". *Nature Methods*, 15(7), 475–476, 2018. [https://doi.org/10.1038/s41592-018-0046-7](https://doi.org/10.1038/s41592-018-0046-7)
