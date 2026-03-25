# §21 共同開発の実践 — レビュー・質問・OSS参加

[§20 コードとデータのセキュリティ・倫理](./20_security_ethics.md)では、データとコードを安全に管理するための知識——シークレット管理、エージェントハーネス、ヒトデータの法規制と匿名化——を学んだ。本章では、その知識を土台にして、他の研究者やコミュニティとの**協働**の技術を学ぶ。

コミュニティとの対話スキル——質問の構成、Issue報告、レビューコメント、進捗報告——を身につければ、エージェントで論点整理を補助しつつ、科学的な判断とコミュニケーションの精度に集中できる。これらのスキルがあれば、質問は回答してもらいやすく、Issue報告は適切になり、共同研究者との認識齟齬が少なくなりコミュニケーションコストを下げられる。エージェントは環境情報の収集・不足情報の洗い出し・PRの説明文の下書き・進捗報告の雛形作成を得意とする。一方、「何が問題の本質か」の切り分け、レビューコメントの科学的妥当性の判断、共同研究者に何を伝えるべきかの優先順位づけは人間が行う。

本章では、まず[21-1節](#21-1-質問の技術--正しく助けを求める)で質問の構成と質問先の使い分けを学ぶ。次に[21-2節](#21-2-コードレビューとossコミュニティへの参加)でコードレビューの作法とOSSコミュニティへの参加方法を扱う。最後に[21-3節](#21-3-共同研究のコミュニケーション--piと共同研究者への共有)で共同研究者やPIへの進捗共有と解析依頼の受け取り方を解説する。

---

## 21-1. 質問の技術 — 正しく助けを求める

### 21-1-1. 良い質問の構成要素

プログラミングで問題に遭遇したとき、最も効果的な行動は「正しく助けを求める」ことである。正しい質問とは、回答者が問題を再現し、原因を特定できるだけの情報を過不足なく含む質問のことである。Stack Overflowの「How do I ask a good question?」ガイド[1](https://stackoverflow.com/help/how-to-ask)は、この原則を体系化した定番のリファレンスである。

良い質問は以下の4つの要素で構成される。

#### 環境情報の明示

問題の原因がOS、Pythonバージョン、パッケージバージョンの違いに起因するケースは非常に多い。質問の冒頭に環境情報を明記することで、回答者が「バージョン違いでは？」と確認する往復を省略できる。

最低限記載すべき環境情報:

| 項目 | 確認コマンド | 記載例 |
|------|------------|--------|
| OS | `uname -a` | macOS 15.3 / Ubuntu 24.04 |
| Python | `python3 --version` | Python 3.12.3 |
| パッケージ | `pip show パッケージ名` | biopython 1.84 |
| conda環境 | `conda list パッケージ名` | numpy 1.26.4 |

#### 最小再現例（MRE）の作成

**最小再現例**（Minimal Reproducible Example; MRE）とは、問題を再現するために必要な最小限のコードである。[§9 デバッグの技術](./09_debug.md)で学んだ「問題の局所化」技法の応用であり、自分のプロジェクト固有のコードを削ぎ落として、問題の本質だけを残す作業である。

MREの条件:

- **最小**: 問題の再現に無関係なコードを含まない
- **完全**: コピー&ペーストで実行できる（import文やサンプルデータを含む）
- **再現可能**: 実行すると問題が発生する

悪い例と良い例を比較する。

```python
# ❌ 悪い例: 再現に必要な情報が不足
# 「read_csvでエラーが出ます」
df = pd.read_csv("my_data.csv")
```

```python
# ✅ 良い例: 最小再現例（MRE）
import pandas as pd
from io import StringIO

# タブ区切りのサンプルデータ（実際のファイルを模倣）
data = StringIO("gene\tcount\nTP53\t100\nBRCA1\tNA")

# デフォルトではカンマ区切りを想定するためパースに失敗する
df = pd.read_csv(data)
print(df)
# gene\tcount と gene\tcount\nTP53\t100... が1列に読み込まれてしまう
```

バイオインフォマティクスでは、大きな入力ファイル（FASTQやBAM）が問題に関わることが多い。その場合は、問題を再現できる最小のテストデータを作成するか、公開データベースからダウンロード可能なアクセッション番号を示す。

#### 期待する結果と実際の結果の差分

「動きません」ではなく、「こうなることを期待しているが、実際にはこうなる」という差分を明示する。エラーが出る場合は、エラーメッセージの**全文**（トレースバック全体）を貼り付ける。

```
### 期待する結果
gene    count
TP53    100
BRCA1   NA

### 実際の結果
   gene\tcount
0  TP53\t100
1  BRCA1\tNA
```

#### 環境情報の自動収集

以下のスクリプトは、質問に必要な環境情報を自動的に収集し、質問テンプレートを生成する。`collect_environment`関数はOS、Pythonバージョン、指定パッケージのバージョンを辞書として返し、`format_question`関数はそれをMarkdown形式の質問テンプレートに整形する。

```python
# scripts/ch21/format_question.py — 環境情報の自動収集と質問テンプレート生成（抜粋）

def collect_environment(packages: list[str] | None = None) -> dict[str, str]:
    """OS、Pythonバージョン、指定パッケージのバージョンを収集する."""
    info: dict[str, str] = {
        "os": platform.platform(),
        "python": platform.python_version(),
        "architecture": platform.machine(),
    }
    for pkg in packages or []:
        try:
            info[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            info[pkg] = "not installed"
    return info


def format_question(
    title: str,
    description: str,
    mre: str,
    expected: str,
    actual: str,
    packages: list[str] | None = None,
) -> str:
    """質問テンプレートをMarkdown形式で生成する."""
    env = collect_environment(packages)
    env_section = "\n".join(f"- {k}: {v}" for k, v in env.items())
    return (
        f"## {title}\n\n"
        f"### 環境\n{env_section}\n\n"
        f"### 問題の説明\n{description}\n\n"
        f"### 最小再現例\n```python\n{mre}\n```\n\n"
        f"### 期待する結果\n```\n{expected}\n```\n\n"
        f"### 実際の結果\n```\n{actual}\n```\n"
    )
```

完全なコードは`scripts/ch21/format_question.py`にある。

#### エージェントへの指示例

エラーに遭遇した際、エージェントに投稿前の論点整理を任せれば、必要な情報の収集漏れを防げる。ただし、外部コミュニティに投稿する本文は各サイトの規約を確認し、自分で最終確認する。

> 「以下のエラートレースバックから、公開フォーラムに質問する前の整理メモを作成して。必要な環境情報、最小再現例、期待する結果と実際の結果、不足している情報を英語の箇条書きで整理して」

> 「このスクリプトが特定のFASTQファイルでだけ失敗する。問題を再現するための最小限のテストデータ（5リード程度）を生成して」

> 「`scripts/ch21/format_question.py`を使って、biopython、pandas、numpyのバージョン情報を含む質問テンプレートを生成して」

---

### 21-1-2. 質問先の使い分け

質問を投げる場所は、問題の性質によって異なる。場所を間違えると、回答が得られないばかりか、コミュニティから歓迎されない投稿になってしまう。

| 質問先 | 適するケース | 注意点 |
|--------|------------|--------|
| **Stack Overflow** | Pythonの一般的なプログラミング質問 | 質問の品質基準が厳格。重複質問は閉じられる |
| **Biostars**[2](https://www.biostars.org/) | バイオインフォマティクス固有の質問 | 配列データの貼り方やツールバージョンの記載が重要 |
| **GitHub Issues** | 特定ツールのバグ報告・機能要望 | 再現手順が最重要。ツールの最新版で再現するか確認する |
| **研究室Slack/Teams** | チーム内の質問・相談 | エージェントに質問を整理させてから投稿する |

ユーザの多いソフトウェアであればコミュニティへの質問で回答が得られる場合が多い。そのためQ&Aサイトや研究者用のメーリングリストなどで質問するのがよいだろう。一方で研究用のソフトウェアはユーザーが限られるため、開発チームに直接質問したほうが解決につながりやすい。その場合は論文に記載されているメールアドレスやGitHub Issuesで質問するのがよいだろう。

#### Stack Overflow

Stack Overflow[1](https://stackoverflow.com/help/how-to-ask)はプログラミング全般のQ&Aサイトである。Pythonの文法、ライブラリの使い方、アルゴリズムの実装に関する質問はここが最適である。

投稿前のチェック:

- 同じ質問が既にないか検索したか
- タイトルは具体的か（「エラーが出ます」ではなく「pandasのread_csvでタブ区切りファイルが正しくパースされない」）
- MREを含んでいるか
- 適切なタグを付けたか（`python`, `pandas`, `biopython`等）

#### Biostars

Biostars[2](https://www.biostars.org/)はバイオインフォマティクス専門のQ&Aサイトである。ゲノム解析ツールの使い方、パイプラインの設計、データフォーマットの問題に特化している。

バイオインフォ固有の質問では、一般的な環境情報に加えて以下を記載する:

- 使用ツールとバージョン（例: `STAR 2.7.11a`、`samtools 1.19`）
- データの種類とフォーマット（例: paired-end RNA-seq、FASTQ.gz）
- リファレンスゲノムのバージョン（例: GRCh38 / Ensembl release 110）

#### GitHub Issues

[§7-2 GitHubの活用](./07_git.md#7-2-githubの活用)で学んだIssueの作成は、特定のツールやライブラリのバグ報告に適している。バグ報告Issueの構造は21-1-1節の質問構成と同じだが、加えて以下を含める:

- ツールの**最新版**で再現するかどうか（古いバージョンの既知バグである場合がある）
- 関連するIssueやPRがないか検索した結果
- 可能であれば、修正案の提示

#### 研究室Slack/Teams

チーム内での質問は、外部サイトほど形式的である必要はないが、「環境情報 + 何をした + 何が起きた」の3点セットは省略しない。エージェントに質問を整理させてから投稿すると、やり取りの往復を減らせる。

#### エージェントへの指示例

質問先によって求められるフォーマットや語調が異なる。エージェントには投稿文の自動生成よりも、必要項目の洗い出しや不足情報の確認を任せるほうが安全である。特に外部コミュニティでは、AI生成文の扱いに関する規約が変わり得る点に注意する。

> 「この問題をBiostarsに相談する前提で、使用ツール（STAR 2.7.11a）、データの種類（paired-end RNA-seq）、リファレンスゲノム（GRCh38）の情報を含めるべき要点を英語の箇条書きで整理して」

> 「このバグをGitHub Issueで報告する前提で、環境情報、再現手順、期待される動作、実際の動作、最新版（v2.1.0）での再現確認を英語の箇条書きで整理して」

> 「研究室Slackに投稿する質問を日本語で整理して。何をしようとして、何を試して、何が起きたかの3点を箇条書きにして」

---

### 21-1-3. エラーメッセージでの検索習慣とXY問題の回避

#### エラーメッセージをそのまま検索する

エラーに遭遇したとき、最初にやるべきことは**エラーメッセージをそのまま検索エンジンに貼り付ける**ことである。多くのエラーは既に誰かが遭遇しており、Stack OverflowやGitHub Issuesに解決策が投稿されている。

検索のコツ:

- トレースバックの**最後の行**（エラーの種類とメッセージ）を検索する
- ファイルパスやユーザー名など、自分の環境に固有の文字列は除外する
- パッケージ名やツール名を検索キーワードに追加する

```
# ✅ 良い検索クエリ
ModuleNotFoundError: No module named 'Bio.SeqIO' Biopython

# ❌ 悪い検索クエリ（パスが固有すぎる）
/Users/tanaka/project/analysis.py line 3 ModuleNotFoundError
```

#### XY問題の回避

**XY問題**（XY Problem）とは、本当に解決したい問題Xではなく、自分が思いついた解決策Yについて質問してしまう現象である[9](https://xyproblem.info/)。

具体例を挙げる。

- **X**（本当の問題）: FASTQファイルから品質スコアが低いリードを除外したい
- **Y**（思いついた解決策）: 「Pythonで文字列の各文字のASCIIコードを取得する方法を教えてください」

Yだけを質問すると、ASCII変換の方法は教えてもらえるが、「FastpやTrimmomatic等の専用ツールを使えば一発で解決する」という本質的な回答は得られない。

XY問題を回避するために:

1. 質問文に「最終的にやりたいこと」（X）を必ず書く
2. 「そのために自分が試したこと」（Y）はその次に書く
3. エージェントにXY問題チェックを依頼する

#### エージェントへの指示例

エージェントはXY問題の検出に適している。自分の質問をエージェントに見せて、本質的な問題を見失っていないかチェックしてもらおう。

> 「この質問はXY問題になっていないか確認して。本当に解決したい問題と、質問している内容が一致しているか評価して」

> 「以下のエラーメッセージから、検索に使うべきキーワードを抽出して。自分の環境に固有の文字列を除外して、汎用的な検索クエリを3つ提案して」

> 「このエラーについてStack OverflowやGitHub Issuesで報告されている解決策を調べて。biopython 1.84とPython 3.12の組み合わせで発生するかどうかも確認して」

---

> **🧬 コラム: Biostarsの歩き方**
>
> Biostars[2](https://www.biostars.org/)は2009年に設立されたバイオインフォマティクス専門のQ&Aサイトである。Stack Overflowと同様のフォーマット（質問→回答→投票）を採用しているが、独自の文化がある。
>
> **エチケット:**
>
> - **クロスポストは原則避ける**: 同じ質問を複数の場に投げると回答者の労力が重複する。必要がある場合は、既存投稿へのリンクを明示して重複回答を避ける
> - **タグの使い方**: `rna-seq`、`variant-calling`、`biopython`など、分野やツールに関連するタグを付ける。タグが適切だと、専門家の目に留まりやすい
> - **回答の受理**: 問題が解決したら、最も役立った回答を「受理」する。コミュニティへの礼儀であり、同じ問題に遭遇した後続者の道標にもなる
> - **検索してから質問**の文化: 質問前にBiostars内で検索し、類似の質問がないか確認する。重複質問には既存のスレッドへのリンクが貼られて閉じられる
>
> **AI生成回答に関する倫理:**
>
> 2026-03-25 時点で、Stack Overflow の Help Center は、生成 AI を使って Stack Overflow 向けのコンテンツを作成すること自体を認めていない[7](https://stackoverflow.com/help/gen-ai-policy)。これは回答だけでなく、質問文の生成やリライトも含む[8](https://meta.stackoverflow.com/questions/421831)。したがって、エージェントは投稿本文の自動生成ではなく、論点整理や不足情報の洗い出しに限定して使うのが安全である。Biostarsのような専門コミュニティでも、検証していない文章の丸投げは避けるべきである。
>
> 自分の質問を整理するためにエージェントを使うことは問題ないが、エージェントの出力を検証せずにそのまま回答として投稿することは、コミュニティの信頼を損なう行為である。

---

## 21-2. コードレビューとOSSコミュニティへの参加

### 21-2-1. コードレビューのコミュニケーション

[§0-4 レビューの技法](./00_ai_agent.md)ではエージェントにコードレビューを依頼する手法を、[§7-2 GitHubの活用](./07_git.md#7-2-githubの活用)ではPull Requestの作成手順を学んだ。本節では、**人間同士の**コードレビューにおけるコミュニケーションの作法を扱う。GitHub Docs[3](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews)のPull Requestレビューガイドも参考になる。

#### レビューコメントを書く側の作法

建設的なコードレビューは、コードの品質向上だけでなく、チーム全体のスキル向上に貢献する。以下の原則を意識する。

**なぜを添える**: 変更の提案には理由を添える。「この変数名を変えて」ではなく、「この変数名を`gene_count`に変えると、他の箇所の`sample_count`と対になって意図が明確になる」と書く。

**提案と要求を区別する**: すべてのコメントが修正必須ではない。以下のプレフィックスで優先度を示す慣習がある。

| プレフィックス | 意味 | 対応 |
|--------------|------|------|
| `nit:` | 些細な指摘（命名、フォーマット） | 修正推奨だが必須ではない |
| `suggestion:` | 改善提案 | 検討の余地あり |
| `question:` | 理解のための質問 | 回答を求める |
| `blocking:` | マージ前に修正が必要 | 必須修正 |

**良い点にも言及する**: 問題の指摘ばかりでは受け手の意欲を削ぐ。優れた設計、読みやすいテスト、適切なエラーハンドリングには積極的にコメントする。

#### レビューコメントを受ける側の作法

レビューコメントを受け取った際の対応も重要である。

- **感情的にならない**: コメントはコードに対するものであり、人格への攻撃ではない。「なぜそう思うか」を冷静に確認する
- **理由を確認する**: 意図が分からないコメントには「Can you elaborate?」と尋ねる。黙って修正するよりも、理由を理解して修正するほうが学びになる
- **コードで応答する**: 議論が長引きそうな場合は、修正コミットを出して「こういう意味ですか？」と確認する。コードは言葉より正確に意図を伝える

#### PR説明文の書き方

PRの説明文は、レビュアーが変更の意図と影響範囲を素早く理解するための文書である。以下の構造が標準的である。

```markdown
## What（何を変えたか）
DEG解析スクリプトにFDR補正オプションを追加

## Why（なぜ変えたか）
Benjamini-Hochberg法以外の補正法（Bonferroni等）を
選択できるようにしたいという要望（Issue #42）

## How（どう変えたか）
- `--correction` オプションを追加（デフォルト: BH）
- `statsmodels.stats.multitest.multipletests` を使用
- 対応するテストを追加

## Test plan（テスト方法）
- `pytest tests/ch20/` で新規テスト3件がパス
- 既存テストに影響なし
```

バイオインフォマティクスのPRでは、これに加えて以下を記載するとレビューが円滑になる。

- **テストデータの出典**: 公開データベースからのアクセッション番号、または合成データである旨
- **パラメータの根拠**: 閾値やアルゴリズムの選択理由（論文引用があれば添える）

以下のヘルパースクリプトは、git diffの出力からPR説明文の下書きやレビューコメントの返答を生成するためのテンプレートを作成する。`summarize_diff`関数は変更されたファイルと変更行数を集計し、`format_pr_description`関数はテンプレートに沿った説明文を生成する。

```python
# scripts/ch21/review_helper.py — PR説明文生成ヘルパー（抜粋）

def summarize_diff(diff_text: str) -> list[DiffSummary]:
    """git diff の出力から変更ファイルと変更行数を集計する."""
    summaries: list[DiffSummary] = []
    current_file: str | None = None
    added, removed = 0, 0
    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            if current_file is not None:
                summaries.append(
                    DiffSummary(file=current_file, added=added, removed=removed)
                )
            # "diff --git a/path b/path" からファイルパスを取得
            current_file = line.split(" b/")[-1]
            added, removed = 0, 0
        elif line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    if current_file is not None:
        summaries.append(
            DiffSummary(file=current_file, added=added, removed=removed)
        )
    return summaries
```

完全なコードは`scripts/ch21/review_helper.py`にある。

#### エージェントへの指示例

レビューコメントの英語での下書きは、エージェントの得意領域である。日本語で意図を伝え、英語のレビューコメントを生成させよう。

> 「このPRの差分を読んで、レビューコメントを英語で3つ作成して。nit、suggestion、blockingのプレフィックスを使い分けて」

> 「このレビューコメントへの返答を英語で書いて。指摘を受け入れる場合と、代替案を提案する場合の2パターンを作成して」

> 「このPRのgit diffから、What/Why/How/Test planの構造に沿ったPR説明文の下書きを英語で作成して」

---

### 21-2-2. OSSコミュニティへの最初の貢献

オープンソースソフトウェア（OSS）への貢献と聞くと、高度な機能実装を想像するかもしれない。しかし、最初の一歩はもっと小さなことで十分である。Karl Fogel著 *Producing Open Source Software*[5](https://producingoss.com/)が述べるように、OSSプロジェクトの健全性は小さな貢献の積み重ねで支えられている。

#### 最初の貢献の例

- **ドキュメントのtypo修正PR**: README や docstring の誤字脱字を修正する。コードに触れないため、リスクが低く、受け入れられやすい
- **READMEの誤り訂正**: インストール手順が古くなっていたり、リンクが切れていたりする箇所の修正
- **エラーメッセージの改善**: 分かりにくいエラーメッセージを、原因と対処法が分かるように書き換える
- **テストの追加**: テストカバレッジが低い関数にテストケースを追加する

#### バグ報告Issueの書き方

バグ報告は、21-1-1節で学んだ質問技術の応用である。質問との違いは、「自分の使い方が間違っている可能性」と「ソフトウェアにバグがある可能性」の両方を公平に扱う点にある。

```markdown
## Bug report: STAR crashes with GTF containing empty gene_name

### Environment
- STAR 2.7.11a
- Ubuntu 22.04
- GRCh38 + Ensembl 110 GTF

### Steps to reproduce
1. Download GTF from Ensembl 110
2. Run `STAR --runMode genomeGenerate ...`
3. Run alignment with `--outSAMtype BAM SortedByCoordinate`

### Expected behavior
Alignment completes successfully.

### Actual behavior
STAR exits with segmentation fault at the sorting step.
Log attached: [Log.out](link)

### Additional context
- Works with Ensembl 109 GTF
- Possibly related to #1234
```

#### CONTRIBUTING.mdとCode of Conductの読み方

多くのOSSプロジェクトには**CONTRIBUTING.md**（貢献ガイド）と**Code of Conduct**（行動規範）が含まれている。PRを出す前に必ず読む。

CONTRIBUTING.mdに記載される典型的な内容:

- コーディングスタイル（フォーマッタ、リンターの指定）
- ブランチ戦略（`main`からフォークするか、`develop`ブランチを使うか）
- テストの実行方法
- コミットメッセージの形式（Conventional Commits等）
- PR送信前のチェックリスト

#### エージェントへの指示例

OSSへの貢献準備は、エージェントにCONTRIBUTING.mdの要件を読み取らせて、準備状況をチェックさせるのが効率的である。

> 「このリポジトリのCONTRIBUTING.mdを読んで、PRを出すために必要な準備項目をチェックリストにまとめて。コーディングスタイル、テスト実行方法、コミットメッセージ形式を含めて」

> 「このREADMEの『Installation』セクションに記載されたコマンドが最新版で動作するか確認して。動作しない場合は修正PRの下書きを作成して」

> 「このライブラリの`parse_gff`関数にテストが書かれていない。正常系と異常系のテストケースを3つずつ提案して」

---

### 21-2-3. バイオインフォOSSの特徴

バイオインフォマティクスのOSSは、一般的なソフトウェアプロジェクトとはいくつかの点で異なる。その特徴を理解しておくと、貢献や利用がスムーズになる。

#### アカデミア主導のプロジェクト

多くのバイオインフォツール（STAR、HISAT2、DESeq2、samtools等）は、大学や研究機関の研究者が開発・メンテナンスしている。企業のOSSとは異なり、以下の特徴がある。

- **メンテナが研究者**: 本業は研究であり、Issue対応やPRレビューに割ける時間が限られる。レスポンスに数週間かかることも珍しくない
- **少人数メンテナ**: 1〜3人でメンテナンスされているプロジェクトが大半である。丁寧なIssue報告やPRは特に歓迎される
- **論文駆動**: ツールの公開が論文として発表されることが多い。引用数がツールの評価指標となるため、使用した場合は必ず引用する

#### Biocondaレシピ貢献

[§6 Python環境の構築](./06_dev_environment.md)で学んだcondaのバイオインフォチャンネルである**Bioconda**[4](https://bioconda.github.io/contributor/index.html)は、コミュニティドリブンで運営されている。新しいツールのレシピ（パッケージ定義ファイル）を追加するPRや、既存ツールのバージョン更新PRは、初心者でも取り組みやすい貢献形態である。

Biocondaレシピの基本構造（`meta.yaml`）:

```yaml
# meta.yaml — biocondaレシピの基本構造
package:
  name: my-bio-tool              # パッケージ名
  version: "1.0.0"               # バージョン

source:
  url: https://github.com/author/tool/archive/v1.0.0.tar.gz
  sha256: abc123...               # ダウンロードファイルのハッシュ値

build:
  number: 0                      # ビルド番号（同一バージョンの再ビルド時にインクリメント）

requirements:
  host:
    - python >=3.10
    - pip
  run:
    - python >=3.10
    - biopython >=1.80

test:
  commands:
    - my-bio-tool --help          # インストール後のテストコマンド
```

#### Bioconductorのレビュープロセス

R言語のバイオインフォマティクスパッケージの集積である**Bioconductor**は、パッケージ採択に厳格なピアレビュープロセスを設けている。コードの品質、ドキュメントの充実度、ビニエット（使い方のチュートリアル）の有無が審査される。Pythonのバイオインフォマティクスエコシステムにはこのような統一的な審査プロセスは存在しないが、Bioconductorのレビュー基準は自分のパッケージの品質向上のための参考になる。

#### エージェントへの指示例

Biocondaレシピの作成は、テンプレートが定まっているためエージェントに任せやすい。
ただし、ハッシュ値の計算や依存関係の正確性は人間が確認する。

> 「このGitHubリポジトリのPythonツール用に、Biocondaのmeta.yamlレシピを作成して。source URLはGitHubリリースのtar.gzを使って。依存パッケージはpyproject.tomlから読み取って」

> 「BiocondaのCONTRIBUTING.mdを読んで、レシピPRに必要な手順をまとめて」

---

### 21-2-4. 貢献時のライセンス

OSSに貢献する際、あるいは他者のOSSを自分のプロジェクトに取り込む際には、ライセンスの理解が不可欠である。ライセンスの選択基準については[§7-2 GitHubの活用](./07_git.md#7-2-githubの活用)を参照されたい。

#### CLA（Contributor License Agreement）

大規模なOSSプロジェクトでは、PRを出す際に**CLA**（Contributor License Agreement; 貢献者ライセンス契約）への署名を求められる場合がある。CLAは、あなたの貢献物に対する著作権やライセンスの取り扱いを明確にする契約書である。

CLAに署名することの意味:

- あなたの貢献がプロジェクトのライセンスの下で配布されることに同意する
- あなたが貢献内容の著作権を持っている（または権利者の許可を得ている）ことを保証する
- プロジェクトがライセンスを変更する場合に、あなたの貢献も含まれることに同意する（CLAの内容による）

所属機関（大学・企業）に在籍している場合、CLAの署名には所属機関の許可が必要なことがある。迷ったら所属機関の知的財産部門に相談する。

#### ライセンス互換性

他者のコードを自分のプロジェクトに取り込む場合、ライセンスの**互換性**を確認する必要がある。

| 取り込むコードのライセンス | 自分のプロジェクトのライセンス | 互換性 |
|------------------------|--------------------------|--------|
| MIT | MIT | ✅ 互換 |
| MIT | GPL-3.0 | ✅ 互換（GPLの条件が適用される） |
| GPL-3.0 | MIT | ❌ 非互換（GPLコードをMITで再配布できない） |
| Apache-2.0 | MIT | △ 要注意（Apache-2.0 の NOTICE・特許条項を保持できる形で配布する必要がある。単純に MIT へ再ライセンスできるとは限らない） |
| GPL-3.0 | GPL-3.0 | ✅ 互換 |

基本的な原則は「コピーレフト（GPL等）のコードを取り込むと、自分のプロジェクトもコピーレフトにする必要がある」ということである。パーミッシブライセンス（MIT、BSD、Apache-2.0）同士でも、NOTICE や特許ライセンス条項の扱いは確認する。

#### エージェントへの指示例

> 「このプロジェクトの依存パッケージすべてのライセンスを一覧にして。GPL系のライセンスが含まれている場合は警告して」

> 「このGitHubリポジトリのCLAの内容を要約して。署名する前に確認すべきポイントを挙げて」

---

## 21-3. 共同研究のコミュニケーション — PIと共同研究者への共有

### 21-3-1. 進捗共有の資料作成

バイオインフォマティクスの解析者は、実験系の共同研究者やPI（研究室主宰者）に定期的に進捗を報告する場面が多い。Gitのコミット履歴は開発者にとっては進捗の記録だが、非プログラマの共同研究者には伝わらない。

#### git logからの進捗要約

[§18 コードのドキュメント化](./18_documentation.md)で学んだCHANGELOG管理の応用として、git logから「先週やったこと」を自動的に要約するアプローチがある。

```bash
# 直近1週間のコミットログを表示する
# --since: 期間指定、--oneline: 1行表示、--no-merges: マージコミットを除外
git log --since="1 week ago" --oneline --no-merges
```

このコマンドの出力をエージェントに渡して、非技術者向けの進捗報告に変換させる。

#### 週次報告テンプレート

以下は、進捗報告のMarkdownテンプレートである。「やったこと」「結果」「次にやること」「困っていること」の4セクションで構成する。Wilson et al. (2017)[6](https://doi.org/10.1371/journal.pcbi.1005510)が提唱する「Good enough practices」でも、定期的な進捗記録の重要性が強調されている。

```markdown
# 週次進捗報告 — 2026-03-22

## やったこと
- RNA-seqデータ（n=12）のアラインメント完了（STAR 2.7.11a）
- マッピング率: 85-92%（全サンプルで基準クリア）

## 主な結果
- DEG解析で587遺伝子が有意に変動（FDR < 0.05）
- Gene Ontologyの結果、免疫応答関連パスウェイが有意に濃縮

## 次にやること
- パスウェイ解析（GSEA）の実行
- ボルケーノプロットの作成と結果の解釈

## 困っていること / 相談事項
- サンプル3のマッピング率が他より10%低い → リシーケンス必要？
```

#### コードサンプル

以下のスクリプトは、git logの出力と追加メモから進捗報告Markdownを自動生成する。`parse_git_log`関数はgit logの`--oneline`出力をパースしてコミット一覧を返し、`generate_report`関数はテンプレートに沿った報告文書を組み立てる。

```python
# scripts/ch21/progress_report.py — 進捗報告の自動生成（抜粋）

def parse_git_log(log_text: str) -> list[CommitEntry]:
    """git log --oneline の出力をパースする."""
    entries: list[CommitEntry] = []
    for line in log_text.strip().splitlines():
        if not line.strip():
            continue
        # "abc1234 コミットメッセージ" の形式をパース
        parts = line.strip().split(" ", 1)
        if len(parts) == 2:
            entries.append(CommitEntry(hash=parts[0], message=parts[1]))
    return entries


def generate_report(
    log_text: str,
    results: str = "",
    next_steps: str = "",
    issues: str = "",
    date: str | None = None,
) -> str:
    """git logと追加情報から進捗報告Markdownを生成する."""
    commits = parse_git_log(log_text)
    report_date = date or datetime.date.today().isoformat()
    done = "\n".join(f"- {c.message}" for c in commits)
    return (
        f"# 週次進捗報告 — {report_date}\n\n"
        f"## やったこと\n{done}\n\n"
        f"## 主な結果\n{results}\n\n"
        f"## 次にやること\n{next_steps}\n\n"
        f"## 困っていること / 相談事項\n{issues}\n"
    )
```

完全なコードは`scripts/ch21/progress_report.py`にある。

#### エージェントへの指示例

進捗報告の下書きは、エージェントの自動生成能力が活きる場面である。ただし、科学的な解釈や優先度の判断は人間が加筆・修正する。

> 「直近1週間のgit logを取得して、非技術者のPI向けの進捗報告をMarkdownで作成して。コミットメッセージを生物学的な成果に翻訳して」

> 「今週のDEG解析の結果を要約して、共同研究者への報告メールの下書きを日本語で作成して。有意遺伝子数、トップ10遺伝子の機能、パスウェイ解析の結果を含めて」

> 「`scripts/ch21/progress_report.py`を使って、git logから今週の報告書を生成して」

---

### 21-3-2. 実験系研究者との橋渡し

バイオインフォマティクスの解析者にとって最も頻繁なコミュニケーション相手は、実験（ウェット）側の研究者である。彼らはプログラミングの知識を持たないことが多いが、生物学的な知見については深い専門性を持つ。この非対称な専門性を橋渡しするスキルが、解析者の価値を決める。

#### ウェット研究者が求める情報

ウェット側の研究者が知りたいのは、コードの技術的な詳細ではなく、**生物学的な意味**である。

| ウェット研究者の質問 | 解析者が提供すべき情報 |
|--------------------|--------------------|
| 「どの遺伝子が効いた？」 | DEGリスト + 機能アノテーション |
| 「差は有意？」 | 統計検定の結果 + 効果量 + 可視化 |
| 「再現性は？」 | 生物学的リプリケート間の一致度 |
| 「次に何を調べればいい？」 | パスウェイ解析 + 候補遺伝子の絞り込み |

「$p$値が0.05以下です」だけでは不十分である。「$p$値が0.05以下の遺伝子のうち、免疫応答に関連するGOタームが有意に濃縮されていた。特にIL-6シグナル経路の遺伝子3つ（IL6, STAT3, JAK2）が2倍以上発現上昇しており、この処理が炎症応答を誘導している可能性がある」——このレベルの解釈が求められる。

#### パラメータ選択根拠の記録

解析パラメータの選択根拠は、ウェット研究者との議論で頻繁に問われる。「なぜこの閾値にしたのか」に答えられなければ、結果の信頼性が揺らぐ。

記録すべき判断の例:

- **FDRの閾値**: 0.05にした理由（慣習的基準、サンプル数を考慮、探索的研究か確認的研究か）
- **fold changeの閾値**: 2倍以上にした理由（生物学的に意味のある変動量の判断）
- **アルゴリズムの選択**: DESeq2を使った理由（サンプル数が少ない場合の安定性、先行研究との比較可能性）

これらの記録には、[§18 コードのドキュメント化](./18_documentation.md)で学んだANALYSIS_LOG.mdが役立つ。

#### 生物学的解釈の添え方

解析結果を報告する際は、数値だけでなく**生物学的文脈**を添える。[§13 可視化の実践](./13_visualization.md)で学んだ図表作成技術を活用して、視覚的に分かりやすく伝える。

- **ボルケーノプロット**: fold change vs -log10(p-value) で全遺伝子の分布を示し、注目遺伝子をラベル付きでハイライトする
- **ヒートマップ**: サンプル間の発現パターンの類似性を示す
- **Gene Ontology解析**（GO解析）: 有意遺伝子の機能的傾向を解釈する

#### エージェントへの指示例

生物学的解釈の提案はエージェントの得意領域だが、その解釈が実験条件や先行研究と整合するかの判断は人間が行う。

> 「このDEG解析結果（CSVファイル）にGene Ontology情報を付加して、生物学的な解釈を提案して。免疫応答、代謝、細胞周期のどのカテゴリに多いかを要約して」

> 「このボルケーノプロットのfold changeが2以上かつFDR < 0.01の遺伝子について、各遺伝子の機能を1文で説明して。実験系研究者向けの簡潔な表を作成して」

> 「解析パラメータの選択根拠を、ANALYSIS_LOG.mdに追記する形で書いて。FDR閾値0.05、fold change閾値2の選択理由を、先行研究の引用付きで書いて」

---

### 21-3-3. 解析依頼の受け取り方

共同研究者から「このデータを解析して」と依頼される場面は、バイオインフォマティクスの日常業務の一部である。しかし、必要な情報が揃わないまま解析を始めると、やり直しや認識齟齬が発生する。[§0-2 ワークフロー](./00_ai_agent.md#0-2-plan--execute--review-ワークフロー)で学んだインタビューパターンを、共同研究者との対話に応用する。

#### 必要情報のチェックリスト

解析依頼を受けた際、以下の情報が揃っているかを確認する。

| 項目 | 確認内容 | なぜ必要か |
|------|---------|----------|
| **サンプル数** | 全サンプル数とグループごとの内訳 | 統計検定の設計と検出力の推定 |
| **生物学的リプリケート** | 技術的リプリケートとの区別 | 正しい統計モデルの選択 |
| **比較群の設計** | 何と何を比較するか | 解析の方向性を決定 |
| **リファレンスゲノム** | 種名とゲノムバージョン | アラインメントとアノテーション |
| **特殊条件** | batch effect、時系列、ペアドサンプル等 | 統計モデルへの組み込み |
| **メタデータ** | サンプル名、条件、ファイル対応表 | データの整理と品質管理 |

#### 「解析前インタビュー」パターン

エージェントとの対話で使うインタビューパターン（[§0-2](./00_ai_agent.md#0-2-plan--execute--review-ワークフロー)）を、共同研究者とのやり取りにも応用する。

```
1. 「最終的に知りたいことは何ですか？」（ゴール設定）
2. 「比較したいのはどの群とどの群ですか？」（設計確認）
3. 「サンプルの対応関係（ペアリング等）はありますか？」（統計モデル）
4. 「以前の解析で気になった点はありますか？」（既知の問題）
5. 「結果はいつまでに必要ですか？」（スケジュール）
```

#### コードサンプル

以下のスクリプトは、解析依頼の受け付け時にメタデータの充足度を検証する。`REQUIRED_COLUMNS`に定義された必須カラムがメタデータCSVに含まれているかをチェックし、欠損セルの有無も確認する。

```python
# scripts/ch21/analysis_intake.py — 解析依頼チェックリスト（抜粋）

REQUIRED_COLUMNS: list[str] = [
    "sample_id",
    "group",
    "replicate",
    "fastq_r1",
]


def validate_metadata(csv_text: str) -> IntakeResult:
    """メタデータCSVの必須カラムと欠損値を検証する."""
    reader = csv.DictReader(io.StringIO(csv_text))
    fieldnames = list(reader.fieldnames or [])

    # 必須カラムの存在チェック
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in fieldnames]

    # 各行の欠損値チェック
    rows = list(reader)
    missing_values: list[tuple[int, str]] = []
    for i, row in enumerate(rows, start=2):  # ヘッダ行を1として2行目から
        for col in REQUIRED_COLUMNS:
            if col in row and not row[col].strip():
                missing_values.append((i, col))

    return IntakeResult(
        total_samples=len(rows),
        missing_columns=missing_cols,
        missing_values=missing_values,
        is_valid=len(missing_cols) == 0 and len(missing_values) == 0,
    )
```

[§20-2 データの倫理](./20_security_ethics.md#20-2-データの倫理)のデータ管理計画（DMP）で定めた共有ルールに従い、ヒトデータの場合は倫理審査の承認やDUAの確認も解析前チェックリストに含める。

完全なコードは`scripts/ch21/analysis_intake.py`にある。

#### エージェントへの指示例

解析依頼の受け付けプロセスは、チェックリストの作成やメタデータの検証でエージェントを活用できる。ただし、研究デザインの妥当性や統計モデルの選択は人間が判断する。

> 「RNA-seq解析依頼の受け付け用チェックリストをMarkdownで作成して。サンプル数、リプリケート、比較群、リファレンスゲノム、特殊条件、メタデータの各項目を含めて」

> 「このメタデータCSVに必須カラム（sample_id, group, replicate, fastq_r1）がすべて含まれているか検証して。欠損値がある行も報告して」

> 「共同研究者に送る解析前ヒアリングの質問リストを日本語で作成して。最終的に知りたいこと、比較デザイン、サンプルの対応関係、スケジュールを含めて」

---

> **🧬 コラム: 研究室ミーティングでの解析報告 — 図1枚で伝える技術**
>
> 研究室ミーティングやラボセミナーでは、ウェット研究者はスライド1枚の図を見て判断することが多い。その1枚に何を載せるかが、解析者の腕の見せ所である。
>
> **効果的な図の選び方:**
>
> - **ボルケーノプロット**: 全遺伝子の発現変動の全体像を示す。横軸にlog2 fold change、縦軸に-log10(adjusted p-value)を取り、有意に変動した遺伝子を色分けする。注目遺伝子の名前をラベルとして付けると、ウェット研究者がすぐに生物学的意味を読み取れる
> - **ヒートマップ**: サンプル間の発現パターンの類似性を示す。クラスタリングにより、サンプルのグループ分けが発現プロファイルと一致するかを視覚的に確認できる
> - **PCA plot**: サンプル間のグローバルな関係を2次元で示す。バッチ効果やアウトライヤーの検出に有効。ウェット研究者には「サンプルが処理群ごとにまとまっているか」を直感的に示せる
>
> **読ませ方のポイント:**
>
> - タイトルに**結論**を書く（「ボルケーノプロット」ではなく「処理Aにより免疫応答遺伝子が上方制御」）
> - 軸ラベルを省略しない。バイオインフォマティクス用語ではなく、生物学の用語で書く
> - カラーバーや凡例を必ず付ける。色覚多様性に配慮したカラーパレットを使う（[§13 可視化の実践](./13_visualization.md)参照）
>
> エージェントに「この図の説明文を非専門家向けに書いて」と頼めば、技術的なjargonを避けた平易な説明が得られる。ただし、生物学的な解釈の正確性は人間が確認する。

---

## まとめ

| 概念 | 要点 |
|------|------|
| **良い質問の構成** | 環境情報 + 最小再現例（MRE）+ 期待vs実際の差分。回答者が再現できる情報を揃える |
| **質問先の使い分け** | Stack Overflow（一般）、Biostars（バイオ特化）、GitHub Issues（バグ報告）、Slack（チーム内） |
| **XY問題** | 本当の問題Xではなく、思いついた解決策Yについて質問してしまう罠。最終目的を明記する |
| **レビューコメント** | nit/suggestion/blocking で優先度を区別。「なぜ」を添え、良い点にも言及する |
| **OSSへの最初の貢献** | typo修正、ドキュメント改善、テスト追加から始める。CONTRIBUTING.mdを必ず読む |
| **バイオインフォOSS** | アカデミア主導・少人数メンテナ。丁寧なIssue報告が歓迎される。使ったら引用する |
| **CLA** | 貢献者ライセンス契約。署名前に内容を確認し、必要なら所属機関に相談する |
| **ライセンス互換性** | GPLコードを取り込むと自プロジェクトもGPLに。パーミッシブ同士は互換性あり |
| **進捗報告** | git logから非技術者向けに変換。やったこと・結果・次の予定・困りごとの4点セット |
| **実験系研究者との橋渡し** | 生物学的意味を添えて報告。パラメータ選択根拠を記録する |
| **解析依頼の受け取り方** | チェックリストで必要情報を収集。解析前インタビューで認識を合わせる |

---

## 演習問題

本章の内容を、エージェントとの協働を通じて実践する課題である。

### 演習 21-1: 質問文の作成 **[指示設計]**

`scanpy.pp.highly_variable_genes()` を実行したところ、予期しない結果が返された（高変動遺伝子が極端に少ない）。Stack OverflowまたはGitHub Issues向けの質問文を作成せよ。以下の要素をすべて含めること。

- **環境情報**: Python/scanpyのバージョン、OS
- **最小再現例**（MRE）: 問題を再現できる最小限のコード
- **期待した結果 vs 実際の結果**: 具体的な数値や出力を含む
- **最終目的**: 何を達成したいのか（XY問題の回避）

（ヒント）「良い質問の3要素」をすべて含めること。XY問題にならないよう「高変動遺伝子を選択して下流のPCA・クラスタリングに使いたい」という最終目的も記述する。

### 演習 21-2: PRレビューコメントの改善 **[レビュー]**

以下のレビューコメントを、本章で学んだ作法に従って改善せよ。

1. 「このコードは間違っている」
2. 「なぜこうした？」
3. 「全部書き直してください」

それぞれについて、改善後のコメント文を書き、なぜ改善が必要かを説明せよ。

（ヒント）nit / suggestion / blocking の分類を使い分ける。「なぜ」の理由を添え、代替案を提示する。良い点にも言及するとレビューのトーンが改善する。

### 演習 21-3: OSSライセンスの互換性 **[概念]**

MITライセンスの自作プロジェクトに、GPL-3.0ライセンスのライブラリのコードを直接取り込みたい（コピー＆ペーストで関数を利用する）。以下の問いに答えよ。

1. これは可能か
2. プロジェクト全体のライセンスはどうなるか
3. 「依存ライブラリとして `pip install` で使うだけ」の場合と何が違うか

（ヒント）GPLのコピーレフトの「伝播性」を考える。コードを直接取り込む場合とインポートして使う場合では、ライセンスの影響範囲が異なる。

### 演習 21-4: コントリビューションの実践 **[実践]**

バイオインフォマティクス関連のOSSツール（例: Biopython, Scanpy, Snakemake）のGitHubリポジトリで以下を行え。

1. `CONTRIBUTING.md`（または同等のガイドライン）を読む
2. `good first issue` ラベルの付いたIssueを1つ選ぶ
3. そのIssueに対する取り組み手順を計画する（PR提出は不要）

計画には以下を含めること: フォーク → ブランチ作成 → 変更内容 → テスト方法 → PR作成時の注意点。

（ヒント）フォーク → ブランチ作成 → 変更 → テスト → PR作成の流れを計画する。`CONTRIBUTING.md` にコーディング規約やテストの実行方法が書かれていることが多い。

---

## さらに学びたい読者へ

本章で扱った共同開発・OSS参加・質問の技術をさらに深く学びたい読者に向けて、定番の教科書とリソースを紹介する。

### OSSプロジェクトの運営

- **Fogel, K. *Producing Open Source Software: How to Run a Successful Free Software Project* (2nd ed.). O'Reilly, 2017.** — OSSプロジェクトの立ち上げと運営の教科書。全文がオンラインで無料公開されている: https://producingoss.com/ 。コードレビュー文化、Issue/PRの作法、コミュニティ運営が詳しい。

### コードレビュー

- **Bacchelli, A., Bird, C. "Expectations, Outcomes, and Challenges of Modern Code Review". *Proceedings of the 2013 International Conference on Software Engineering (ICSE '13)*, 712–721, 2013.** https://doi.org/10.1109/ICSE.2013.6606617 — コードレビューの効果と課題に関する実証研究。レビューの目的が「バグ発見」だけでなく、知識共有やコード品質向上にもあることを示す。

### 科学研究の共同作業

- **Wilson, G. et al. "Good Enough Practices in Scientific Computing". *PLOS Computational Biology*, 13(6), e1005510, 2017.** https://doi.org/10.1371/journal.pcbi.1005510 — 科学研究における共同作業のベストプラクティス。特にコード共有とデータ共有の節が本章と直結する。

### 質問の技術

- **Raymond, E. S. "How To Ask Questions The Smart Way". 2014.** http://www.catb.org/esr/faqs/smart-questions.html — 技術コミュニティでの質問の作法の原典。本章で扱った「良い質問の構造」の背景にある考え方を学べる。日本語訳も公開されている。

### GitHubでのコントリビューション

- **GitHub Docs. "Contributing to projects".** https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project — GitHubでのOSSコントリビューション（Fork、Pull Request、レビュー）の公式ガイド。

---

## 参考文献

[1] Stack Overflow. "How do I ask a good question?". https://stackoverflow.com/help/how-to-ask (参照日: 2026-03-22)

[2] Biostars. "Biostars: Pair of Scissors". https://www.biostars.org/ (参照日: 2026-03-22)

[3] GitHub Docs. "About pull request reviews". https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews (参照日: 2026-03-22)

[4] Bioconda. "Contributing to Bioconda". https://bioconda.github.io/contributor/index.html (参照日: 2026-03-22)

[5] Fogel, K. *Producing Open Source Software*. https://producingoss.com/ (参照日: 2026-03-22)

[6] Wilson, G. et al. "Good enough practices in scientific computing". *PLOS Computational Biology*, 13(6), e1005510, 2017. https://doi.org/10.1371/journal.pcbi.1005510

[7] Stack Overflow. "What is this site’s policy on content generated by generative artificial intelligence tools?". https://stackoverflow.com/help/gen-ai-policy (参照日: 2026-03-25)

[8] Stack Overflow. "Policy: Generative AI (e.g., ChatGPT) is banned". https://meta.stackoverflow.com/questions/421831 (参照日: 2026-03-25)

[9] "The XY Problem". https://xyproblem.info/ (参照日: 2026-03-25)
