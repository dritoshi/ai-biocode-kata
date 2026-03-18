# 7. テスト・品質管理

[§6 バージョン管理（Git / GitHub）](./06_git.md)では、コードの変更履歴を記録し、共有・公開する仕組みを学んだ。しかし、バージョン管理されたコードが正しく動作する保証はどこにもない。「昨日まで動いていたスクリプトが、新しい関数を追加したら壊れた」——こうした事態を防ぐには、コードが期待どおりに動くことを**自動的に検証する仕組み**が必要である。

実験科学者にとって、これはポジティブコントロールとネガティブコントロールの概念に近い。既知の結果が得られるサンプルを実験に含めることで、実験系全体が正しく機能していることを確認する。ソフトウェアにおけるテストも同じ発想である——既知の入力に対して期待どおりの出力が得られるかを自動で検証する。

本章では、**テスト駆動開発**（Test-Driven Development; TDD）の考え方、**pytest**によるテストの書き方、そして**ruff**・**mypy**・**pre-commit**によるコード品質の自動管理を学ぶ。さらに、[§6](./06_git.md)で触れたGitHub Actionsを活用して、テストとリンターをプッシュのたびに自動実行するCI/CDパイプラインを構築する。

---

## 7-1. テスト駆動開発（TDD）

### なぜテストを書くのか

「テストを書く時間がもったいない」——プログラミング初心者がしばしば抱く感想である。しかし、テストのないコードは、やがてそれ以上の時間を奪う。

テストがない場合に起こる典型的な問題:

1. **修正の副作用が検出できない** — ある関数を修正したとき、別の関数が壊れたことに気づけない
2. **リファクタリングが怖い** — コードを改善したくても「壊すかもしれない」と手が出せない
3. **バグの再発** — 一度直したはずのバグが、数ヶ月後に再び現れる

テストはこれらの問題をすべて解決する。[§1 設計原則](./01_design.md)で学んだKISS原則やDRY原則と同様に、テストを書く習慣はコードの品質を長期にわたって維持するための基盤である。

### Red → Green → Refactor サイクル

テスト駆動開発（TDD）は、コードを書く前にテストを書く開発手法である[1](https://doi.org/10.5281/zenodo.9882)。TDDは3つのステップを繰り返すサイクルで進む。

```
1. Red     — 失敗するテストを書く（まだ実装がない）
2. Green   — テストが通る最小限のコードを書く
3. Refactor — コードを整理する（テストは通したまま）
```

この3ステップを小さな単位で繰り返す。一度に大きな機能を実装するのではなく、「テスト1つ → 実装 → 整理」の小さなサイクルを回し続ける。

#### 具体例: 配列の逆相補鎖を求める関数

バイオインフォマティクスでよく使う「逆相補鎖」（reverse complement）の関数をTDDで実装してみよう。

**Step 1: Red — 失敗するテストを書く**

```python
# tests/ch07/test_reverse_complement.py
from scripts.ch07.reverse_complement import reverse_complement

def test_simple_sequence() -> None:
    """ATGCの逆相補鎖はGCATである."""
    assert reverse_complement("ATGC") == "GCAT"
```

この時点では `reverse_complement` 関数はまだ存在しないため、テストは失敗する（Red）。

**Step 2: Green — テストが通る最小限のコードを書く**

```python
# scripts/ch07/reverse_complement.py
COMPLEMENT: dict[str, str] = {
    "A": "T", "T": "A", "G": "C", "C": "G",
}

def reverse_complement(seq: str) -> str:
    """DNA配列の逆相補鎖を返す."""
    return "".join(COMPLEMENT[base] for base in reversed(seq.upper()))
```

テストを実行すると、今度は成功する（Green）。

**Step 3: Refactor — 必要に応じて整理する**

この段階ではコードが十分にシンプルなので、大きなリファクタリングは不要である。ただし、テストケースを追加して堅牢性を高めることはできる:

```python
def test_empty_sequence() -> None:
    """空文字列には空文字列を返す."""
    assert reverse_complement("") == ""

def test_case_insensitive() -> None:
    """小文字の入力も受け付ける."""
    assert reverse_complement("atgc") == "GCAT"
```

新しいテストケースを追加したら、再びテストを実行して全てが通ることを確認する。このサイクルを繰り返しながら、エッジケース（空入力、小文字入力など）にも対応していく。

### 「テストが通る最小限のコード」を書く規律

TDDで最も重要な規律は、**テストが通る最小限のコード**だけを書くことである。テストに書いていない機能を先回りして実装しない。これは[§1](./01_design.md)で学んだYAGNI原則（You Ain't Gonna Need It）そのものである。

たとえば、最初のテストが `reverse_complement("ATGC")` だけなら、実装は文字列 `"GCAT"` をハードコードで返すところから始めてもよい。次のテストケース `reverse_complement("AAAA")` を追加したとき、初めて汎用的なロジックが必要になる。

この「小さなステップ」の積み重ねが、過剰設計を防ぎ、実際に必要な機能だけを持つクリーンなコードへと導く。

AIコーディングエージェントにTDDで開発を指示するときは、次のように伝えるとよい:

> 「テストを先に書いて、テストが通る最小限の実装をしてください。一度に1つのテストケースずつ進めてください」

---

## 7-2. テストの実践

### pytestによるユニットテスト

Pythonのテストフレームワークで最も広く使われているのが**pytest**である[2](https://docs.pytest.org/en/stable/)。標準ライブラリの `unittest` よりもシンプルな記法で、強力な機能を提供する。

#### インストールと基本的な使い方

```bash
# pytestのインストール
pip install pytest

# テストの実行（testsディレクトリ以下のtest_*.pyを自動検出）
pytest tests/

# 詳細な出力
pytest tests/ -v

# 特定のファイルだけ実行
pytest tests/ch07/test_reverse_complement.py

# 特定のテスト関数だけ実行
pytest tests/ch07/test_reverse_complement.py::test_simple_sequence
```

pytestは `test_` で始まるファイルと関数を自動的にテストとして認識する。テスト関数内で `assert` 文を使い、期待する条件を記述する。

#### テストの書き方の基本

テストは**Arrange-Act-Assert**（準備-実行-確認）のパターンで書く:

```python
def test_gc_content_typical() -> None:
    # Arrange: テストデータを準備する
    seq = "ATGCATGC"
    expected = 0.5

    # Act: テスト対象の関数を呼び出す
    result = gc_content(seq)

    # Assert: 結果を検証する
    assert result == pytest.approx(expected)
```

浮動小数点数の比較には `pytest.approx()` を使う。浮動小数点数の直接比較（`==`）は丸め誤差により失敗する場合がある（[§3 計算機科学の基礎知識](./03_cs_basics.md)で学んだとおりである）。

#### テストクラスによるグループ化

関連するテストをクラスでまとめると、テストの構造が明確になる:

```python
class TestReverseComplement:
    """reverse_complement() のテスト."""

    def test_simple(self) -> None:
        assert reverse_complement("ATGC") == "GCAT"

    def test_palindrome(self) -> None:
        # 回文配列: 逆相補鎖が元の配列と同じ
        assert reverse_complement("ATAT") == "ATAT"

    def test_empty(self) -> None:
        assert reverse_complement("") == ""
```

### テストデータの準備（fixture）

テストデータの準備が複数のテストで共通する場合、pytestの**フィクスチャ**（fixture）機能を使って準備コードを共有できる[2](https://docs.pytest.org/en/stable/):

```python
import pytest

@pytest.fixture()
def sample_sequences() -> dict[str, str]:
    """テスト用のサンプル配列."""
    return {
        "high_gc": "GCGCGCGC",   # GC=100%
        "low_gc": "AAAATTTT",    # GC=0%
        "mixed": "ATGCATGC",     # GC=50%
    }

def test_filter_high_gc(sample_sequences: dict[str, str]) -> None:
    result = filter_sequences_by_gc(sample_sequences, min_gc=0.8)
    assert set(result.keys()) == {"high_gc"}

def test_filter_all(sample_sequences: dict[str, str]) -> None:
    result = filter_sequences_by_gc(sample_sequences)
    assert len(result) == 3
```

フィクスチャはテスト関数の引数に同名のパラメータを書くだけで、pytestが自動的に注入してくれる。テストごとにフィクスチャが新しく生成されるため、テスト間でデータが干渉しない。

#### conftest.py — フィクスチャの共有

複数のテストファイルで同じフィクスチャを使いたい場合は、`conftest.py` に定義する:

```python
# tests/ch07/conftest.py
import pytest
from pathlib import Path

@pytest.fixture()
def test_data_dir() -> Path:
    """テストデータディレクトリのパスを返す."""
    return Path(__file__).parent / "data"

@pytest.fixture()
def sample_fasta(test_data_dir: Path) -> Path:
    """テスト用FASTAファイルのパスを返す."""
    return test_data_dir / "sample.fasta"
```

`conftest.py` は特別なファイル名であり、pytestが自動的に読み込む。同じディレクトリおよびサブディレクトリのすべてのテストから利用できる。

### エッジケースを意識する

堅牢なテストを書くには、正常系だけでなくエッジケースを意識する必要がある。バイオインフォマティクスでよくあるエッジケースは:

| エッジケース | 例 | テストすべき理由 |
|---|---|---|
| 空入力 | 空文字列、空のリスト | ゼロ除算やIndexErrorの防止 |
| 境界値 | 長さ1の配列、GC=0%/100% | off-by-oneエラーの検出 |
| 不正入力 | DNA配列に `N` や `X` が混入 | 実データに含まれやすい |
| 大規模入力 | 10万配列、1Mbp以上の配列 | パフォーマンスの劣化やメモリ不足 |
| 特殊文字 | 改行・空白を含むヘッダ | FASTAパーサの堅牢性 |

```python
def test_sequence_with_n() -> None:
    """N（不明塩基）を含む配列でもエラーにならない."""
    # NはGCにもATにもカウントしない想定
    result = gc_content("ATNGC")
    assert 0.0 <= result <= 1.0

def test_single_base() -> None:
    """1塩基の配列."""
    assert gc_content("G") == pytest.approx(1.0)
    assert gc_content("A") == pytest.approx(0.0)
```

### テストカバレッジの計測

テストがコードのどの程度をカバーしているかを数値で把握するには、**pytest-cov**を使う[3](https://pytest-cov.readthedocs.io/en/latest/):

```bash
# pytest-covのインストール
pip install pytest-cov

# カバレッジ付きでテストを実行
pytest tests/ --cov=scripts --cov-report=term-missing
```

出力例:

```
---------- coverage: ... ----------
Name                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
scripts/ch07/reverse_complement.py      6      0   100%
scripts/ch07/seq_stats.py             15      3    80%   22-24
-----------------------------------------------------------------
TOTAL                                  21      3    86%
```

`Missing` 列に表示される行番号が、テストで実行されていないコード行を示す。カバレッジ100%が理想だが、現実的には**80%以上**を目標にするのがよいバランスである。重要なのは、カバレッジの数値そのものよりも、**カバーされていない箇所が何か**を把握し、リスクの高い部分を優先的にテストすることである。

### 統合テスト・回帰テスト

ユニットテストが個々の関数を検証するのに対し、**統合テスト**（integration test）は複数のコンポーネントが連携して正しく動作するかを検証する。たとえば、FASTAファイルを読み込み、GC含量で配列をフィルタリングし、結果をファイルに書き出すという一連の処理を通しでテストする。

```python
def test_fasta_filter_pipeline(tmp_path: Path) -> None:
    """FASTAファイルの読み込みからフィルタリング結果の書き出しまで."""
    # テスト用FASTAファイルを作成
    input_fasta = tmp_path / "input.fasta"
    input_fasta.write_text(">seq1\nGCGCGCGC\n>seq2\nAAAATTTT\n>seq3\nATGCATGC\n")

    # パイプラインの実行
    output_fasta = tmp_path / "output.fasta"
    filter_fasta_by_gc(input_fasta, output_fasta, min_gc=0.4)

    # 結果の検証
    output_text = output_fasta.read_text()
    assert ">seq1" in output_text   # GC=100% → 含まれる
    assert ">seq3" in output_text   # GC=50%  → 含まれる
    assert ">seq2" not in output_text  # GC=0% → 除外される
```

`tmp_path` はpytestが提供する組み込みフィクスチャで、テストごとに一時ディレクトリを自動作成・自動削除してくれる。ファイルI/Oを伴うテストでは重宝する。

**回帰テスト**（regression test）は、過去に発見したバグが再発しないことを確認するテストである。バグを修正する際に、そのバグを再現するテストケースを先に書き（Red）、修正して通す（Green）というTDDのサイクルを適用する。このテストがコードベースに残り続けることで、同じバグの再発を永続的に防ぐ。

---

## 7-3. コード品質ツール

テストはコードの「正しさ」を検証するが、コードの「読みやすさ」や「一貫性」は別の仕組みで管理する。本節では、コードのスタイルと品質を自動でチェックするツールを紹介する。

### ruff — リント＋フォーマット

**ruff**はPythonのリンター（コード品質チェック）とフォーマッター（コード整形）を1つのツールに統合した高速なツールである[4](https://docs.astral.sh/ruff/)。従来は `flake8`（リント）と `black`（フォーマット）を別々にインストールしていたが、ruffはこれらの機能を1つのコマンドで提供する。

```bash
# ruffのインストール
pip install ruff

# リント（コード品質チェック）
ruff check scripts/

# フォーマット（コード整形）
ruff format scripts/

# リントの問題を自動修正（安全な修正のみ）
ruff check scripts/ --fix
```

#### pyproject.toml での設定

ruffの設定はプロジェクトルートの `pyproject.toml` に記述する:

```toml
[tool.ruff]
target-version = "py310"
line-length = 88

[tool.ruff.lint]
select = [
    "E",    # pycodestyle エラー
    "W",    # pycodestyle 警告
    "F",    # pyflakes
    "I",    # isort（import順序）
    "N",    # pep8-naming
    "D",    # pydocstyle（docstring）
    "UP",   # pyupgrade
]

[tool.ruff.lint.pydocstyle]
convention = "numpy"
```

`select` で有効にするルールセットを指定する。すべてを一度に有効にすると大量の警告が出て圧倒されるため、まずは基本的なルール（`E`, `W`, `F`, `I`）から始め、慣れたらルールを追加するのがよい。

#### ruffが検出する問題の例

```python
# ruffが指摘する問題の例

import os          # F401: 未使用のimport
import sys
import json        # I001: importの順序が不正

def Calculate_GC(seq):   # N802: 関数名はsnake_caseにすべき
    x = seq.upper()      # E501: 行が長すぎる（設定次第）
    gc = x.count("G")+x.count("C")   # E225: 演算子の前後にスペースがない
    return gc/len(x)
```

ruffのフォーマッターは、インデント、空白、改行、引用符のスタイルなどを自動的に統一する。チームでフォーマットの好みを議論する必要がなくなり、コードレビューでスタイルの指摘に時間を費やすこともなくなる。

### mypy — 型チェック

[§1 設計原則](./01_design.md)では触れなかったが、Pythonには**型ヒント**（type hint）の仕組みがある[5](https://docs.python.org/3/library/typing.html)。型ヒントはコードに型情報を付加する記法であり、**mypy**はこの型情報をもとに静的な型チェックを行うツールである[6](https://mypy.readthedocs.io/en/stable/):

```python
# 型ヒントなし — 引数や戻り値の型が不明
def gc_content(seq):
    ...

# 型ヒントあり — seq はstr、戻り値はfloat
def gc_content(seq: str) -> float:
    ...
```

型ヒントを書いておくと、mypyが実行前に型の不整合を検出してくれる:

```bash
# mypyのインストール
pip install mypy

# 型チェックの実行
mypy scripts/
```

mypyが検出するエラーの例:

```python
def gc_content(seq: str) -> float:
    if not seq:
        return 0.0
    seq_upper = seq.upper()
    gc_count = seq_upper.count("G") + seq_upper.count("C")
    return gc_count / len(seq_upper)

# mypyが検出するエラー
result: int = gc_content("ATGC")  # error: Incompatible types in assignment
#                                  #        (expression has type "float", variable has type "int")
```

型ヒントの最大の利点は、コードの意図を明示することで読みやすさが向上し、AIコーディングエージェントにとっても文脈の理解が容易になることである。

#### pyproject.toml でのmypy設定

```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

`disallow_untyped_defs = true` を設定すると、型ヒントのない関数定義を警告してくれる。最初から厳格にする必要はないが、新しく書くコードには型ヒントを付ける習慣をつけることを推奨する。

### pre-commit — コミット前の自動チェック

**pre-commit**は、`git commit` のたびにリンターやフォーマッターを自動実行するフレームワークである[7](https://pre-commit.com/)。[§6 バージョン管理](./06_git.md)で学んだGitのフック機能を活用している。

```bash
# pre-commitのインストール
pip install pre-commit

# Gitフックのセットアップ（リポジトリごとに1回）
pre-commit install
```

設定ファイル `.pre-commit-config.yaml` をプロジェクトルートに置く:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

この設定により、`git commit` を実行すると自動的にruffとmypyが走る。チェックに失敗するとコミットが中断され、問題を修正するまでコミットできない。これにより、品質の低いコードがリポジトリに入り込むのを防げる。

```
$ git commit -m "新機能を追加"
ruff.....................................................Passed
ruff-format..............................................Passed
mypy.....................................................Failed
- hook id: mypy
- exit code: 1

scripts/ch07/seq_stats.py:15: error: Missing return statement
```

### docstringの書き方

docstringはコード内のドキュメントであり、関数やクラスの使い方を記述する。本書では**NumPy style**を採用する[8](https://numpydoc.readthedocs.io/en/latest/format.html):

```python
def filter_fasta_by_gc(
    input_path: Path,
    output_path: Path,
    min_gc: float = 0.0,
    max_gc: float = 1.0,
) -> int:
    """GC含量の範囲でFASTA配列をフィルタリングする.

    Parameters
    ----------
    input_path : Path
        入力FASTAファイルのパス
    output_path : Path
        出力FASTAファイルのパス
    min_gc : float
        GC含量の下限（含む）。デフォルトは0.0
    max_gc : float
        GC含量の上限（含む）。デフォルトは1.0

    Returns
    -------
    int
        書き出した配列の数

    Raises
    ------
    FileNotFoundError
        入力ファイルが存在しない場合
    """
    ...
```

---

## 7-4. CI/CD

### GitHub Actionsの基礎

[§6 バージョン管理](./06_git.md)でGitHub Actionsの概要に触れた。ここでは、テストとリンターを自動実行する具体的なワークフローを構築する。

**CI**（Continuous Integration; 継続的インテグレーション）とは、コードの変更を頻繁にメインブランチに統合し、そのたびに自動テストを実行する開発プラクティスである[9](https://docs.github.com/en/actions/about-github-actions/understanding-github-actions)。CIにより、壊れたコードがメインブランチに入り込むのを防ぐ。

### ワークフローYAMLの書き方

GitHub Actionsのワークフローは `.github/workflows/` ディレクトリにYAML形式で定義する:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Python のセットアップ
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: 依存パッケージのインストール
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov ruff mypy

      - name: ruff によるリント
        run: ruff check .

      - name: ruff によるフォーマットチェック
        run: ruff format --check .

      - name: mypy による型チェック
        run: mypy scripts/

      - name: pytest によるテスト
        run: pytest tests/ --cov=scripts --cov-report=term-missing
```

このワークフローは以下のタイミングで実行される:

- `main` ブランチへのプッシュ時
- `main` ブランチへのプルリクエスト作成・更新時

各ステップは順番に実行され、1つでも失敗するとワークフロー全体が失敗となる。プルリクエストのページにチェック結果が表示されるため、レビュアーはコードを読む前にCIが通っているかどうかを確認できる。

### ワークフローの拡張

複数のPythonバージョンでテストを実行するには、**マトリクス戦略**を使う:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      # 以降のステップは同じ
```

この設定により、Python 3.10、3.11、3.12の3環境で並列にテストが実行される。バイオインフォマティクスのツールでは、利用者の環境が多様であるため、複数バージョンでの動作確認は実用上重要である。

---

> **🧬 コラム: バイオインフォマティクスのテストデータ**
>
> バイオインフォマティクスでは、テスト対象のデータが巨大になりがちである。全ゲノムシーケンスデータは数十GB、RNA-seqの生データも数GBに達する。こうしたデータをそのままテストに使うと、テストの実行に数時間かかったり、リポジトリが肥大化したりする。
>
> テストデータは**小さく、自己完結的**に作る:
>
> ```bash
> # FASTQからランダムに1000リードをサンプリング
> seqtk sample reads.fq 1000 > tests/data/test_reads.fq
>
> # BAMファイルを1%に間引き
> samtools view -s 0.01 input.bam -o tests/data/test.bam
>
> # VCFファイルから特定の領域だけを抽出
> bcftools view -r chr1:1000-2000 input.vcf > tests/data/test.vcf
> ```
>
> テストデータの管理原則:
>
> - テストデータは `tests/data/` に置き、リポジトリにコミットする
> - ファイルサイズは数KB〜数MB程度に抑える
> - 本番データ（患者データ等）は絶対にリポジトリに含めない（[§19 セキュリティと倫理](./19_security_ethics.md)も参照）
> - テストデータの出所と作成方法をREADMEに記録する
> - 大規模なテストデータが必要な場合は、[§6](./06_git.md)で学んだGit LFSの利用を検討する

---

## まとめ

本章では、テスト駆動開発の考え方から、pytest、ruff、mypy、pre-commit、GitHub ActionsによるCI/CDまで、コードの品質を維持するための仕組みを一通り学んだ。

| 概念 | ツール | 目的 |
|---|---|---|
| ユニットテスト | pytest | コードの正しさを自動検証する |
| テストカバレッジ | pytest-cov | テストの網羅度を計測する |
| リント・フォーマット | ruff | コードスタイルの一貫性を保つ |
| 型チェック | mypy | 型の不整合を実行前に検出する |
| コミットフック | pre-commit | コミット前に品質チェックを自動実行する |
| CI/CD | GitHub Actions | プッシュ・PRのたびにテストとリンターを実行する |

これらのツールは、導入の手間に比べて得られる安心感が大きい。「テストが通っているから大丈夫」という確信は、コードを自信を持って変更するための土台である。

次章の[§8 成果物の形式とプロジェクト設計](./08_deliverables.md)では、開発を始める前に「最終的にどういう形で提供するか」を決め、それに適したプロジェクト構造を設計する方法を学ぶ。

---

## 参考文献

[1] Beck, K. *Test Driven Development: By Example*. Addison-Wesley, 2002. [https://doi.org/10.5281/zenodo.9882](https://doi.org/10.5281/zenodo.9882)

[2] pytest. "pytest: helps you write better programs". [https://docs.pytest.org/en/stable/](https://docs.pytest.org/en/stable/) (参照日: 2026-03-18)

[3] pytest-cov. "pytest-cov documentation". [https://pytest-cov.readthedocs.io/en/latest/](https://pytest-cov.readthedocs.io/en/latest/) (参照日: 2026-03-18)

[4] Astral. "Ruff — An extremely fast Python linter and code formatter". [https://docs.astral.sh/ruff/](https://docs.astral.sh/ruff/) (参照日: 2026-03-18)

[5] Python Software Foundation. "typing — Support for type hints". [https://docs.python.org/3/library/typing.html](https://docs.python.org/3/library/typing.html) (参照日: 2026-03-18)

[6] mypy. "mypy — Optional Static Typing for Python". [https://mypy.readthedocs.io/en/stable/](https://mypy.readthedocs.io/en/stable/) (参照日: 2026-03-18)

[7] pre-commit. "A framework for managing and maintaining multi-language pre-commit hooks". [https://pre-commit.com/](https://pre-commit.com/) (参照日: 2026-03-18)

[8] numpydoc. "numpydoc — Numpy's Sphinx extensions". [https://numpydoc.readthedocs.io/en/latest/format.html](https://numpydoc.readthedocs.io/en/latest/format.html) (参照日: 2026-03-18)

[9] GitHub Docs. "Understanding GitHub Actions". [https://docs.github.com/en/actions/about-github-actions/understanding-github-actions](https://docs.github.com/en/actions/about-github-actions/understanding-github-actions) (参照日: 2026-03-18)
