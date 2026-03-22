# §7 Git入門 — コードのバージョン管理

[§6 Python環境の構築](./06_dev_environment.md)では、Pythonのバージョン管理や仮想環境、パッケージマネージャを使って再現可能な開発環境を整備した。`.python-version`、`requirements-lock.txt`、`environment.yml` といった環境定義ファイルも作成した。しかし、これらのファイルを作っただけでは不十分である。「いつ・何を・なぜ変えたか」を記録し、いつでも過去の状態に戻れるようにする仕組みが必要である。

AIエージェントはコードを自動生成するだけでなく、自動的にコミットする機能も持つ。コミットの意味と戻し方を知らなければ、エージェントが壊したコードを復旧できない。

実験科学者であれば、実験ノートの重要性は身に染みているだろう。どの試薬を使い、どの温度で、何分反応させたか——記録がなければ実験は再現できない。コードも同じである。昨日まで動いていたスクリプトが今日エラーを出すとき、「昨日から何を変えたか」がわからなければデバッグは手探りになる。**バージョン管理**（version control）は、コードの実験ノートに相当する仕組みである。

本章では、バージョン管理システム**Git**の基礎操作、共有プラットフォーム**GitHub**の活用法、そしてコードを論文から引用可能にするための公開手順を学ぶ。

---

## 7-1. Gitの基礎

### なぜバージョン管理か

バージョン管理のないプロジェクトでは、ファイル名による管理に陥りがちである。

```
analysis.py
analysis_v2.py
analysis_v2_final.py
analysis_v2_final_really_final.py
analysis_v2_final_really_final_20260301.py
```

どれが最新か、何が変わったのかはファイル名からは読み取れない。バージョン管理システムを使えば、ファイルは常に1つのまま、変更の履歴がすべて記録される。[§0 AIエージェントにコードを書かせる](./00_ai_agent.md)で述べた「こまめにコミットする」という習慣も、バージョン管理があって初めて実践できる。

### リポジトリの作成と初期設定

Gitでは、プロジェクトの変更履歴を保存する場所を**リポジトリ**（repository）と呼ぶ。新しいプロジェクトを始めるには `git init` でリポジトリを作成する。

```bash
# プロジェクトディレクトリの作成とGitリポジトリの初期化
mkdir my_analysis
cd my_analysis
git init

# 名前とメールアドレスの設定（初回のみ）
git config --global user.name "Taro Yamada"
git config --global user.email "taro@example.com"
```

既存のリポジトリをコピーする場合は `git clone` を使う。

```bash
# GitHubからリポジトリをコピー
git clone https://github.com/username/my_analysis.git
```

### ステージング → コミット → プッシュ

Gitには3つの「場所」がある。

```
作業ディレクトリ  →  ステージングエリア  →  リポジトリ
  （編集中）        （次のコミットの準備）   （確定した履歴）
   git add →           git commit →
```

この3段階のうち、**ステージングエリア**がGitの特徴である。変更をすべて一度にコミットするのではなく、コミットに含めるファイルを選別できる。

```bash
# ファイルの状態を確認する（常にこれから始める習慣をつける）
git status

# ファイルをステージングエリアに追加
git add analysis.py
git add .python-version requirements-lock.txt  # §6で作った環境定義ファイル

# ステージングした変更をコミット（履歴に記録）
git commit -m "GC含量計算スクリプトと環境定義ファイルを追加"

# リモートリポジトリにプッシュ（後述のGitHubと連携した場合）
git push origin main
```

`git status` を頻繁に実行する習慣は重要である。現在の状態——どのファイルが変更されているか、何がステージされているか——を常に把握しておくことで、意図しない変更のコミットを防げる。

### ブランチとマージ

**ブランチ**（branch）は、本体のコードに影響を与えずに実験的な変更を試せる仕組みである。幹（main）から枝（branch）を伸ばし、うまくいったら幹に統合（merge）するイメージである。

```bash
# 新しいブランチを作成して切り替える
git checkout -b add-gc-filter

# このブランチで自由に変更を加える
# ... ファイルを編集 ...
git add analysis.py
git commit -m "feat: GC含量でフィルタリングする機能を追加"

# mainブランチに戻る
git checkout main

# ブランチの変更をmainに統合する
git merge add-gc-filter
```

研究のプログラミングでは、「新しい解析手法を試す」「パラメータを変えて比較する」といった場面でブランチが役立つ。mainブランチは常に動作する状態を保ち、実験的な変更はブランチで行う。

### コンフリクトの解決

同じファイルの同じ箇所を複数のブランチで変更した場合、マージ時に**コンフリクト**（conflict）が発生する。Gitはどちらの変更を採用すべきか判断できないため、人間（またはAIエージェント）の介入が必要になる。

コンフリクトが起こると、ファイル中に以下のようなマーカーが挿入される。

```
<<<<<<< HEAD
threshold = 0.5  # mainブランチの変更
=======
threshold = 0.6  # add-gc-filterブランチの変更
>>>>>>> add-gc-filter
```

解決手順は単純である。マーカーを削除し、正しいコードだけを残して、コミットする。

```bash
# ファイルを手動で編集してコンフリクトを解決した後
git add analysis.py
git commit -m "fix: GC含量閾値のコンフリクトを解決"
```

AIコーディングエージェントにコンフリクトの解決を依頼することもできる。その場合は「どちらの変更を優先すべきか」の判断基準を指示に含めると、適切に解決してくれる。

### 便利なコマンド: log, diff, stash

日常的に使う3つのコマンドを紹介する。

```bash
# コミット履歴をコンパクトに表示（ブランチの分岐も可視化）
git log --oneline --graph

# まだコミットしていない変更の差分を表示
git diff

# ステージング済みの変更の差分を表示
git diff --staged
```

`git diff` が見やすいのは、[§4 データフォーマットの選び方](./04_data_formats.md)で学んだテキスト形式のファイルである。バイナリファイル（BAM、pickle等）は差分表示できないため、テキスト形式で保存することにはバージョン管理上の利点もある。

```bash
# 作業中の変更を一時退避する（別ブランチをちょっと見たいとき）
git stash

# 退避した変更を復元する
git stash pop
```

### .gitignore — 管理すべきでないファイルの除外

すべてのファイルをGitで管理すべきではない。以下のようなファイルはリポジトリに含めるべきでない。

- **大きなデータファイル**: `.bam`, `.fastq.gz`, `.h5ad`（数百MB〜数GB）
- **秘密情報**: `.env`（APIキー）、認証トークン
- **自動生成ファイル**: `__pycache__/`, `.pyc`, `.egg-info/`
- **OS固有ファイル**: `.DS_Store`（macOS）、`Thumbs.db`（Windows）

`.gitignore` ファイルに除外パターンを記述しておけば、これらのファイルは自動的に無視される。

```gitignore
# データファイル（大きすぎるため）
*.bam
*.bai
*.fastq.gz
*.h5ad
data/

# 秘密情報
.env
credentials.json

# Python自動生成
__pycache__/
*.pyc
*.egg-info/
dist/

# OS固有
.DS_Store
Thumbs.db
```

[§0 AIエージェントにコードを書かせる](./00_ai_agent.md)で述べたように、APIキーがコードに紛れ込んでいないかコミット前に確認することは重要な習慣である。`.gitignore` はその防衛線の一つとなる。

gitignore.io [3](https://www.toptal.com/developers/gitignore) やGitHub公式のテンプレート集 [4](https://github.com/github/gitignore) を活用すると、プロジェクトに合った `.gitignore` を効率的に作成できる。

#### エージェントへの指示例

Git操作の中でも、コンフリクト解決や.gitignoreの作成はエージェントに依頼しやすいタスクである:

> 「マージコンフリクトが発生しました。`add-gc-filter` ブランチの変更を優先してコンフリクトを解決してください」

> 「バイオインフォマティクスのPythonプロジェクト用の `.gitignore` を作成してください。データファイル（BAM, FASTQ, h5ad）、Python自動生成ファイル、OS固有ファイル、秘密情報を除外してください」

> 「`git log --oneline` の出力を確認して、直近10コミットの変更内容を要約してください」

---

## 7-2. GitHubの活用

### リモートリポジトリ

Gitはローカルで完結するバージョン管理システムだが、コードを他者と共有し、バックアップを取るには**リモートリポジトリ**が必要になる。GitHubは最も広く使われるホスティングサービスである。

```bash
# GitHubでリポジトリを作成した後、ローカルと紐づける
git remote add origin https://github.com/username/my_analysis.git

# 初回のプッシュ（-u でデフォルトのリモートを設定）
git push -u origin main
```

### Pull RequestとIssue管理

**Pull Request**（PR）は、ブランチの変更をmainに統合する前にレビューを依頼する仕組みである。[§1 設計原則 — 良いコードとは何か](./01_design.md)で「エージェントに `gh pr create` でPRを作らせる」と紹介したワークフローは、このPRの仕組みに基づいている。

PRの利点は、変更の差分を一覧でき、コメントで議論できることにある。[§0 AIエージェントにコードを書かせる](./00_ai_agent.md)の「エージェントにレビューさせる」ワークフローも、PRを通じて行うと効果的である。

**Issue**は、バグ報告・機能要望・タスクを記録する仕組みである。「GC含量計算が特定の配列でエラーになる」「新しいフィルタ条件を追加したい」といった項目をIssueとして管理すると、何をすべきかの全体像が把握しやすくなる。

### GitHub CLI（ghコマンド）

**GitHub CLI** [5](https://cli.github.com/) を使えば、ターミナルからGitHubの操作を行える。AIコーディングエージェントもこれらのコマンドを活用する。

```bash
# リポジトリの作成
gh repo create my_analysis --public

# Issueの作成
gh issue create --title "GC含量計算のエッジケース対応" --body "空配列の入力時にエラーが発生する"

# Pull Requestの作成
gh pr create --title "feat: GC含量フィルタを追加" --body "閾値によるフィルタリング機能を実装"
```

### GitHub Actions（CI/CDの入口）

**CI/CD**（継続的インテグレーション/継続的デリバリー）は、コードをコミットするたびにテストやリントを自動実行する仕組みである [6](https://docs.github.com/en/actions/about-github-actions/understanding-github-actions)。[§1 設計原則 — 良いコードとは何か](./01_design.md)で登場した用語を、ここで実際の仕組みとして見てみよう。

GitHub Actionsでは、リポジトリの `.github/workflows/` ディレクトリにYAMLファイルを置くだけでCIを設定できる。最小限の例を示す。

```yaml
# .github/workflows/test.yml
name: テスト実行
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest tests/
```

この設定により、プッシュやPR作成のたびに自動でテストが実行される。テストの書き方やワークフローの詳細は[§8 コードの正しさを守るテスト技法](./08_testing.md)で学ぶ。

#### エージェントへの指示例

GitHub関連の操作はエージェントが `gh` コマンドを通じて直接実行できる:

> 「このブランチの変更内容をもとにPull Requestを作成してください。タイトルはConventional Commitsの型を使い、本文に変更の要約を含めてください」

> 「Issue #3 の内容を読んで、バグ修正用のブランチを作成し、修正を実装してください」

README.mdの作成を依頼する場合:

> 「このプロジェクトの `README.md` を作成してください。プロジェクト概要、インストール方法（`environment.yml` からの再現手順）、基本的な使い方、ライセンスを含めてください」

### README.mdの書き方

リポジトリのトップに置く `README.md` は、プロジェクトの「玄関」である。最低限、以下の項目を含めるとよい。

1. **プロジェクト名と概要** — 何をするツール/解析か
2. **インストール方法** — [§6 Python環境の構築](./06_dev_environment.md)で学んだ環境構築手順
3. **使い方** — 基本的なコマンドの実行例
4. **ライセンス** — 後述するライセンスの種類

### コードの公開と引用可能性

研究コードを公開するだけでなく、論文から正しく引用できる形にすることが求められる時代になっている。3つの要素を組み合わせる。

**GitHub Releases** — リポジトリにタグを付けてバージョンを固定する。`git tag v1.0.0` でタグを打ち、GitHub上でリリースを作成する。

**Zenodo連携** [7](https://zenodo.org/) — ZenodoはCERNが運営するデータリポジトリで、GitHubと連携してDOI（デジタルオブジェクト識別子）を自動発行できる。手順は3ステップである。

1. Zenodoにログインし、GitHubアカウントを連携する
2. DOIを発行したいリポジトリを有効化する
3. GitHub Releasesでリリースを作成すると、ZenodoがDOIを自動発行する

**CITATION.cff** [8](https://citation-file-format.github.io/) — リポジトリのルートに `CITATION.cff` を置くと、GitHubが「Cite this repository」ボタンを自動生成する [9](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files)。

```yaml
# CITATION.cff
cff-version: 1.2.0
message: "このソフトウェアを引用する場合は以下の情報を使用してください。"
title: "GC Content Analyzer"
authors:
  - family-names: "Yamada"
    given-names: "Taro"
    orcid: "https://orcid.org/0000-0001-2345-6789"
version: 1.0.0
date-released: "2026-01-15"
doi: "10.5281/zenodo.XXXXXXX"
repository-code: "https://github.com/username/gc-analyzer"
license: MIT
```

### ライセンスの選択

コードを公開する際は、ライセンスを明示する必要がある [10](https://choosealicense.com/)。ライセンスがないコードは、法的にはすべての権利が著作者に留保される。

| ライセンス | 特徴 | 適する場面 |
|-----------|------|-----------|
| **MIT** | 最も緩い。商用利用可。改変・再配布自由 | 迷ったらこれ |
| **Apache 2.0** | MIT + 特許条項 | 企業との共同研究がある場合 |
| **GPL** | 派生物もオープンソースにする義務 | コミュニティ貢献を重視する場合 |

論文投稿時には、ジャーナルの**Data Availability Statement**の要件を確認する。多くのジャーナルがコードの公開を求めており、ライセンスの明示を条件とする場合もある。投稿前の具体的なチェック項目は[付録C 論文投稿前チェックリスト](./appendix_c_checklist.md)を参照されたい。

> **🧬 コラム：バイオインフォツール公開の実例**
>
> 多くのバイオインフォマティクス論文では、GitHub + Zenodo + DOI の組み合わせが標準になりつつある。典型的な公開フローは以下のとおりである。
>
> 1. GitHubでコードを開発・公開する
> 2. Zenodo連携を有効にする
> 3. GitHub Releasesでバージョンをタグ付けすると、ZenodoがDOIを自動発行する
> 4. 論文のData Availability Statementに DOI を記載する
>
> DOIとPyPI/biocondaは役割が異なることに注意する。**DOI**は論文からの引用用であり、特定バージョンの永続的なスナップショットを指す。**PyPI/bioconda**はユーザーがインストールする用であり、常に最新版を提供する。両方を用意するのがベストプラクティスである。

---

## 7-3. コミットの作法

### 意味のあるコミットメッセージ

§7-1でコミットの基本操作を学んだが、コミットメッセージの「質」にも気を配るべきである。PRで他者（または将来の自分）がコミット履歴を読むとき、メッセージが情報源となる。

悪い例を見てみよう。

```
fix
update
WIP
aaa
修正
```

これでは、何を修正したのか、なぜ変更したのかがまったくわからない。

**Conventional Commits** [11](https://www.conventionalcommits.org/) は、コミットメッセージに型（type）を付けて分類する規約である。

```
feat: GC含量でフィルタリングする機能を追加
fix: 空配列入力時のゼロ除算エラーを修正
docs: README.mdにインストール手順を追記
refactor: GC含量計算をジェネレータに変更
test: GC含量計算のエッジケーステストを追加
```

`feat:` は新機能、`fix:` はバグ修正、`docs:` はドキュメント、`refactor:` はリファクタリング、`test:` はテストの追加である。コミット履歴を一目見るだけで、プロジェクトがどのように進化してきたかがわかる。

AIコーディングエージェントが生成するコミットメッセージは詳細な傾向があるが、Conventional Commitsの型を使うよう指示すると、一貫性のある履歴が作れる。

#### エージェントへの指示例

コミットの作法をエージェントに徹底させるには、プロジェクト設定ファイル（CLAUDE.md / AGENTS.md）に記載しておくのが最も効果的である。セッション中に口頭で指示する場合:

> 「コミットメッセージはConventional Commits形式で書いてください。1コミット = 1つの論理的変更にしてください」

> 「今の変更をレビューして、論理的に独立した変更ごとに分けてコミットしてください。GC含量計算の追加と.gitignoreの更新は別コミットにしてください」

CHANGELOG.mdの生成を依頼する場合:

> 「`git log` のコミット履歴からCHANGELOG.mdを生成してください。Keep a Changelog形式で、Added/Changed/Fixedに分類してください」

### 1コミット = 1つの論理的変更

「GC含量計算関数の追加」と「.gitignoreの更新」は、論理的に独立した変更である。これらを1つのコミットにまとめるのではなく、別々にコミットするべきである。

理由は、問題の特定と巻き戻しが容易になることにある。`git bisect`（二分探索でバグの原因コミットを特定するコマンド）は、1コミットが1つの変更であるとき最も効果的に機能する。また、変更を巻き戻す `git revert` も、コミットの粒度が細かいほど使いやすい。

ファイルの一部だけをステージングしたい場合は、`git add -p`（パッチモード）で行単位の選択ができる。

### 大きなファイルの扱い — Git LFS

Gitはテキストファイルの差分管理に優れているが、大きなバイナリファイルは苦手である。数百MBのBAMファイルをそのままコミットすると、リポジトリが肥大化し、`git clone` に長時間かかるようになる。

**Git LFS**（Large File Storage） [12](https://git-lfs.com/) は、大きなファイルの実体をGitの外部に保存し、リポジトリにはポインタだけを記録する仕組みである。

`git lfs install` はGit LFSをリポジトリに設定するコマンドで、初回のみ実行する。`git lfs track` は指定パターンのファイルをLFS管理対象として `.gitattributes` に登録する。`.gitattributes` は他の共同研究者も同じLFS設定を使えるようにGitで管理する必要がある。

```bash
# Git LFSのセットアップ（初回のみ）
git lfs install

# 追跡するファイルパターンを指定
git lfs track "*.bam"
git lfs track "*.h5ad"

# .gitattributesファイルが生成されるので、これもコミットする
git add .gitattributes
git commit -m "chore: Git LFSでBAMとh5adを追跡"
```

ただし、テスト用の小さなファイル（数KB〜数MB）は通常のGitで管理して問題ない。§7-1の `.gitignore` で大きなデータファイルを除外し、テスト用の小さなサンプルだけをリポジトリに含めるのが実用的な方針である。

### 大規模データの共有 — Git LFS を超える選択肢

GitHub LFS の Free プランではストレージ 10GB・帯域 10GB/月が上限である。バイオインフォマティクスでは参照ゲノム、シングルセル解析の `.h5ad` ファイル、学習済みモデルなどが容易にこの制限を超える。そのような大規模データには、用途に応じた外部サービスを組み合わせるのが現実的である。

| データの種類 | 推奨サービス | 理由 |
|-------------|------------|------|
| 学習済みモデル（数百MB〜数十GB） | Hugging Face Hub | モデルカード・バージョン管理・ストリーミング対応 |
| 論文付随データ（〜50GB） | Zenodo | DOI 発行可。論文引用に最適 |
| 大規模リファレンス・共有データ | S3, Box, Dropbox | 機関提供ストレージ。アクセス制御が柔軟 |

**Hugging Face Hub** [16](https://huggingface.co/docs/hub/) は、Git ベースのホスティングで `git lfs` と同じ操作感を持つ。公開リポジトリは無料で、TB 級のデータにも対応する。`huggingface_hub` Python ライブラリを使えば、スクリプトからプログラマティックにデータをアップロード・ダウンロードできる。機械学習モデルだけでなく、データセットのホスティングにも広く使われている。

**Zenodo** は§7-2で紹介したコードの DOI 発行だけでなく、データセットの永続保存にも使える。1レコードあたり最大 50GB（申請により 200GB まで拡張可）で、論文付随データの公開に最適である。

**クラウドストレージ**（機関提供の Box、AWS S3 など）は DOI が発行されないが、共同研究者のみにアクセスを制限したい場合に有用である。利用する場合は、README にダウンロード手順とチェックサムを明記し、再現性を確保する。

**チェックサム**（checksum）とは、ファイルの内容から一定の長さの文字列（ハッシュ値）を生成する仕組みである。同じファイルからは常に同じハッシュ値が得られるため、ダウンロード時のファイル破損やバージョン違いを即座に検出できる。ハッシュアルゴリズムには `sha256sum` を推奨する（`md5sum` はレガシーであり、衝突耐性に問題がある）。

`sha256sum` はファイルの内容からSHA-256ハッシュ値（64文字の16進数文字列）を計算するコマンドである。`>` でハッシュ値をファイルに保存し、`-c` オプションで保存済みハッシュと現在のファイルを比較して一致（OK）または不一致（FAILED）を表示する。

```bash
# チェックサムを生成して checksums.sha256 に保存
sha256sum reference_genome.fa.gz > checksums.sha256

# ダウンロード後に検証（OK または FAILED が表示される）
sha256sum -c checksums.sha256
```

macOS には `sha256sum` が標準搭載されていないため、代わりに `shasum -a 256` を使う（`shasum -a 256 -c` で検証）。

データを共有する際は、README にチェックサムの検証手順を記載しておくとよい。

````markdown
## データのダウンロード
wget https://example.com/reference_genome.fa.gz

## 整合性の検証
sha256sum -c checksums.sha256
````

---

## 7-4. セマンティックバージョニング

### MAJOR.MINOR.PATCH

ソフトウェアのバージョン番号には、**セマンティックバージョニング**（Semantic Versioning; SemVer） [14](https://semver.org/) という広く使われる規約がある。バージョン番号を `MAJOR.MINOR.PATCH` の3桁で構成する。

- **MAJOR**（例: `1.0.0` → `2.0.0`）: 後方互換性のない破壊的変更。入力形式の変更、関数の削除など
- **MINOR**（例: `1.0.0` → `1.1.0`）: 後方互換性のある機能追加。新しいフィルタオプションの追加など
- **PATCH**（例: `1.0.0` → `1.0.1`）: バグ修正。既存の動作は変わらない

開発初期（`0.x.y`）は、破壊的変更が自由に行えるという慣習がある。バージョン `1.0.0` を公開した時点で「安定版」とみなされ、以後は破壊的変更に慎重になる。

バージョンをGitのタグとして記録するには、`git tag` を使う。

```bash
# バージョンタグを付ける
git tag v1.0.0

# タグをリモートにプッシュ
git push origin v1.0.0
```

### CHANGELOGの書き方

**CHANGELOG.md** は、バージョンごとの変更内容をまとめたファイルである。**Keep a Changelog** [15](https://keepachangelog.com/) の形式が広く採用されている。

```markdown
# Changelog

## [1.1.0] - 2026-03-15
### Added
- GC含量によるフィルタリング機能を追加

### Fixed
- 空配列入力時のゼロ除算エラーを修正

## [1.0.0] - 2026-02-01
### Added
- GC含量計算の基本機能
- FASTAファイルの読み込み
```

変更を `Added`（追加）、`Changed`（変更）、`Fixed`（修正）、`Removed`（削除）で分類する。§7-3で学んだConventional Commitsの型と対応しているため、コミット履歴からCHANGELOGを生成しやすい。

GitHub Releasesのリリースノートとしても、このCHANGELOGの内容を転記できる。§7-2で紹介したZenodo連携と合わせれば、バージョン管理から公開・引用までの一貫したワークフローが完成する。

---

## まとめ

本章では、Gitの基礎操作からGitHubでの公開、コミットの作法、セマンティックバージョニングまでを学んだ。要点を一覧にまとめる。

| 判断場面 | 推奨 | 理由 |
|---------|------|------|
| バージョン管理ツール | Git | 事実上の標準。AIエージェントも前提としている |
| リモートリポジトリ | GitHub | CI/CD、Issue、PR、Zenodo連携が揃う |
| コミットメッセージ | Conventional Commits | 変更の種類が一目で分かる |
| コミットの粒度 | 1コミット = 1つの論理変更 | レビュー・bisect・revertが容易 |
| ライセンス（迷ったら） | MIT | 最も制約が少なく広く使われる |
| 大きなバイナリ | Git LFS または `.gitignore` で除外 | リポジトリの肥大化を防ぐ |
| 大規模データの共有 | Hugging Face Hub / Zenodo / クラウドストレージ | データの種類と公開要件で使い分ける |
| 公開コードの引用 | GitHub Releases + Zenodo + CITATION.cff | DOI発行で論文から引用可能 |
| バージョン番号 | SemVer（MAJOR.MINOR.PATCH） | 破壊的変更の有無が明確 |

バージョン管理の体系は、Perez-Riverol ら (2016) の "Ten Simple Rules for Taking Advantage of Git and GitHub" [13](https://doi.org/10.1371/journal.pcbi.1004947) にも詳しくまとめられている。本章の内容をさらに深めたい読者には一読を薦める。

コードをGitで管理し、GitHubで共有する基盤が整った。しかし、管理対象のコードそのものが正しく動作することを保証する仕組みがなければ、バージョン管理の価値は半減する。次章の[§8 コードの正しさを守るテスト技法](./08_testing.md)では、pytestによるテストの書き方と、コード品質を自動でチェックする仕組みを学ぶ。

---

## 参考文献

[1] Chacon, S., Straub, B. *Pro Git* (2nd ed.). Apress, 2014. [https://git-scm.com/book/ja/v2](https://git-scm.com/book/ja/v2)

[2] Git Project. "Git Documentation". [https://git-scm.com/doc](https://git-scm.com/doc) (参照日: 2026-03-18)

[3] Toptal. "gitignore.io — Create useful .gitignore files for your project". [https://www.toptal.com/developers/gitignore](https://www.toptal.com/developers/gitignore) (参照日: 2026-03-18)

[4] GitHub. "A collection of useful .gitignore templates". [https://github.com/github/gitignore](https://github.com/github/gitignore) (参照日: 2026-03-18)

[5] GitHub CLI. [https://cli.github.com/](https://cli.github.com/) (参照日: 2026-03-18)

[6] GitHub Docs. "Understanding GitHub Actions". [https://docs.github.com/en/actions/about-github-actions/understanding-github-actions](https://docs.github.com/en/actions/about-github-actions/understanding-github-actions) (参照日: 2026-03-18)

[7] Zenodo. [https://zenodo.org/](https://zenodo.org/) (参照日: 2026-03-18)

[8] Druskat, S. et al. "Citation File Format (CFF)". [https://citation-file-format.github.io/](https://citation-file-format.github.io/) (参照日: 2026-03-18)

[9] GitHub Docs. "About CITATION files". [https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files) (参照日: 2026-03-18)

[10] Choose a License. [https://choosealicense.com/](https://choosealicense.com/) (参照日: 2026-03-18)

[11] Conventional Commits. [https://www.conventionalcommits.org/](https://www.conventionalcommits.org/) (参照日: 2026-03-18)

[12] Git LFS. [https://git-lfs.com/](https://git-lfs.com/) (参照日: 2026-03-18)

[13] Perez-Riverol, Y. et al. "Ten Simple Rules for Taking Advantage of Git and GitHub". *PLOS Computational Biology*, 12(7), e1004947, 2016. [https://doi.org/10.1371/journal.pcbi.1004947](https://doi.org/10.1371/journal.pcbi.1004947)

[14] Preston-Werner, T. "Semantic Versioning 2.0.0". [https://semver.org/](https://semver.org/) (参照日: 2026-03-18)

[15] Keep a Changelog. [https://keepachangelog.com/](https://keepachangelog.com/) (参照日: 2026-03-18)

[16] Hugging Face. "Hugging Face Hub Documentation". [https://huggingface.co/docs/hub/](https://huggingface.co/docs/hub/) (参照日: 2026-03-18)
