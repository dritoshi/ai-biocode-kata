# §9 デバッグの技術 — tracebackから最小再現例まで

[§8 コードの正しさを守るテスト技法](./08_testing.md)では、テストを書いて「何が壊れているか」を検出する方法を学んだ。しかし、テストが失敗したとき——あるいはテスト以前にコードがエラーで動かないとき——「なぜ壊れているか」を特定するスキルが必要になる。本章ではその技術——デバッグ——を体系的に学ぶ。

エージェントにバグ修正を依頼する場面を想像してほしい。traceback（エラーの追跡情報）を読み解くスキル、「何を期待して何が違ったか」を言語化するスキル、最小再現例（Minimal Reproducible Example; MRE）を作るスキルがあれば、エージェントにバグの文脈を正確に伝え、的確な修正コードを得られる。これらのスキルがなければ、tracebackを丸ごと貼り付けて「直して」と頼むことになり、的外れな修正が返ってくるリスクが高い。

エージェントとの役割分担はこうなる。エージェントはtracebackの解読、原因の推定、修正コードの生成を得意とする。一方、「そもそも何を期待していたか」「どの入力で再現するか」「その修正が別の機能を壊していないか」は人間が判断すべきポイントである。デバッグの技術は、まさにこの判断力を支える基盤となる。

本章では、まず[9-1節](#9-1-デバッグの心構え)でデバッグに臨む際の考え方と戦略を整理し、[9-2節](#9-2-デバッグツール)でPythonのデバッグツールの使い方を学び、[9-3節](#9-3-よくあるバグのパターン)でバイオインフォマティクスで頻出するバグパターンとその対処法を紹介する。

---

## 9-1. デバッグの心構え

デバッグは闇雲にコードを眺める作業ではない。体系的なアプローチを取ることで、原因の特定を大幅に効率化できる。本節では、デバッグの基本戦略を4つ紹介する。

### tracebackを読む

Pythonでエラーが発生すると、**traceback**（スタックトレース）が表示される。tracebackはエラーに至るまでの関数呼び出しの連鎖を記録したもので、デバッグの最も重要な手がかりとなる。

tracebackの構造は次のとおりである。

- **上部**: 最初に呼び出された関数（呼び出し元）
- **下部**: 実際にエラーが発生した箇所
- **最終行**: エラーの種類とメッセージ

つまり、**最終行から読む**のが最も効率的である。最終行でエラーの種類を把握し、その上の行でエラーが発生したコードの場所を確認する。

典型的なtracebackの例を見てみよう。以下の `read_fasta_records` 関数は、存在しないファイルを読もうとすると `FileNotFoundError` を発生させる。

```python
# FASTAファイルを読み込み、ヘッダと配列のリストを返す関数
def read_fasta_records(path: Path) -> list[dict[str, str]]:
    text = path.read_text()  # ← ファイルが存在しないとここでエラー
    ...
```

この関数に存在しないパスを渡すと、次のようなtracebackが表示される。

```
Traceback (most recent call last):
  File "main.py", line 5, in <module>
    records = read_fasta_records(Path("missing.fasta"))
  File "scripts/ch09/traceback_demo.py", line 30, in read_fasta_records
    text = path.read_text()
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'missing.fasta'
```

読み方の手順は以下のとおりである。

1. **最終行**を読む: `FileNotFoundError` → ファイルが見つからない
2. **その上のフレーム**を読む: `traceback_demo.py` の30行目、`path.read_text()` で発生
3. **さらに上**を読む: `main.py` の5行目から呼ばれている

もう1つ典型的な例として、`ValueError` がある。CSVから読み込んだ発現量データを数値に変換する際、変換できない文字列が混入していると発生する。

```python
# 文字列リストを浮動小数点数に変換する関数
# 変換できない値があると ValueError を送出する
def parse_gene_expression(raw_data: list[str]) -> list[float]:
    results: list[float] = []
    for i, value in enumerate(raw_data):
        try:
            results.append(float(value))
        except ValueError:
            msg = f"インデックス {i} の値 '{value}' を数値に変換できません"
            raise ValueError(msg) from None
    return results
```

`parse_gene_expression(["1.5", "N/A", "2.0"])` を呼ぶと、次のtracebackが表示される。

```
ValueError: インデックス 1 の値 'N/A' を数値に変換できません
```

同様に、辞書から存在しないキーを検索する `KeyError` も頻出する。

```python
# 遺伝子IDからアノテーション情報を検索する関数
# 存在しないIDが指定されると KeyError を送出する
def lookup_gene_annotation(gene_id: str, db: dict) -> dict:
    if gene_id not in db:
        msg = f"遺伝子ID '{gene_id}' がデータベースに見つかりません"
        raise KeyError(msg)
    return db[gene_id]
```

**ライブラリ内部フレームの読み飛ばし方**: tracebackには、自分のコードだけでなくライブラリ内部のフレームも表示される。`site-packages/` や標準ライブラリのパスが含まれるフレームは、通常読み飛ばしてよい。自分のコードが含まれるフレーム（プロジェクトのディレクトリパス）に注目しよう。

### 「何を期待して何が違ったか」を言語化する

バグ報告（自分自身への報告も含む）には、次の**3要素**を必ず含める。

1. **期待した動作**: 「この関数に配列データを渡したら、GC含量のリストが返るはず」
2. **実際の動作**: 「空のリストが返ってくる」または「ValueError が発生する」
3. **再現手順**: 「このデータファイルを入力として、この関数をこの引数で呼ぶ」

この3要素は、エージェントへの指示文としてもそのまま使える。曖昧な「動きません」ではなく、具体的な期待と現実のギャップを伝えることで、エージェントの回答精度は劇的に向上する。

特に注意すべきは**サイレントバグ**——エラーは出ないが結果が間違っているケースである。座標変換のOff-by-oneエラー（[16-3節](#9-3-よくあるバグのパターン)参照）のように、「動くが1塩基ずれている」バグは、期待値を明確にしていなければ見逃してしまう。

### 最小再現例（MRE）を作る

**最小再現例**（Minimal Reproducible Example; MRE）とは、バグを再現できる最小限のコードとデータの組み合わせである[5](https://stackoverflow.com/help/minimal-reproducible-example)。

MREが重要な理由は2つある。

1. **原因の特定が容易になる**: 不要なコードを削ぎ落とすことで、バグの原因が浮き彫りになる
2. **エージェントの回答精度が上がる**: コンテキストが小さいほど、エージェントはバグの本質に集中できる。10,000行のスクリプトを丸ごと渡すより、10行のMREを渡すほうが遥かに的確な修正が得られる

MREの作り方は次の手順で進める。

1. **入力を最小化する**: 巨大なFASTAファイルの代わりに、バグを再現できる最小限のレコード（2〜3件）を用意する
2. **処理を削減する**: バグと無関係なステップ（フィルタリング、正規化など）を取り除く
3. **再現を確認する**: 削減後のコードで同じエラーが再現することを確認する

### 二分探索デバッグ

パイプラインのどこかで結果がおかしくなっているが、どのステップが原因か分からない——そんなとき有効なのが**二分探索デバッグ**である。

手順はシンプルである。

1. パイプラインの**中間地点**で出力を確認する
2. そこまでの結果が正しければ、後半に問題がある。間違っていれば前半に問題がある
3. 問題のある半分に対して、同じ手順を繰り返す

この考え方は、[§7 Git入門](./07_git.md)で紹介した `git bisect` と同じ原理である。`git bisect` がコミット履歴を二分探索するのに対し、ここではパイプラインの処理ステップを二分探索する。

中間出力の確認には、次節で紹介する `print()` デバッグや `logging.debug()` が便利である。

#### エージェントへの指示例

デバッグの心構えをエージェントとの対話に活かす指示例を紹介する。

tracebackを貼り付けて解読を依頼するとき:

> 「以下のtracebackを解読して、原因と修正案を教えて。自分のコードは `scripts/` ディレクトリ以下のファイルだけなので、ライブラリ内部のフレームは読み飛ばして」

期待値と実測値を明示してバグ修正を依頼するとき:

> 「`calculate_gc_stats(["GCGC", "ATAT"])` の結果は `{"mean_gc": 0.5, ...}` を期待しているが、実際は `{"mean_gc": 0.0, ...}` が返る。原因を特定して修正して」

パイプラインの中間出力確認コードを生成してもらうとき:

> 「このパイプライン（FASTQ読み込み→トリミング→アライメント→カウント）の各ステップの中間出力を確認するデバッグコードを挿入して。各ステップ後にレコード数と先頭3件を表示して」

---

## 9-2. デバッグツール

### print()デバッグの作法

最も手軽なデバッグ手法は、`print()` で変数の値を表示することである。しかし、`print()` デバッグには以下の問題がある。

- デバッグ後に `print()` を消し忘れると、本番環境でも出力される
- 大量の出力の中からデバッグ用の出力を見分けにくい
- 出力のON/OFFを切り替えられない

[§11-3 ロギング](./11_cli.md#11-3-ロギング)で学んだ `logging` モジュールを使えば、これらの問題を解決できる。ここではデバッグ局面に特化した使い方を紹介する。

もし `print()` を使うなら、以下のルールを守るとよい。

```python
# print()デバッグをするなら、変数名・値・型をセットで出力する
# デバッグ後の消し忘れに注意が必要
x = some_function()
print(f"DEBUG: x={x!r}, type={type(x).__name__}")  # !r で repr 表示
```

`logging.debug()` を使えば、ログレベルの切り替えで出力を制御できる。

```python
import logging

logger = logging.getLogger(__name__)

def filter_sequences_logging_debug(
    sequences: list[str], min_length: int
) -> list[str]:
    """配列リストを長さでフィルタリングする."""
    # logging.debug() でデバッグ情報を出力
    # ログレベルが INFO 以上に設定されていれば、この出力は表示されない
    logger.debug("フィルタ開始: %d 配列, 最小長=%d", len(sequences), min_length)
    filtered: list[str] = []
    for seq in sequences:
        if len(seq) >= min_length:
            logger.debug("採用: len=%d, 先頭=%s...", len(seq), seq[:10])
            filtered.append(seq)
        else:
            logger.debug("除外: len=%d < %d", len(seq), min_length)
    logger.debug("フィルタ完了: %d → %d 配列", len(sequences), len(filtered))
    return filtered
```

`logging.debug()` は `print()` と違い、本番では出力されない。ログレベルを `DEBUG` に設定したときだけ表示される。消し忘れを心配する必要がなく、デバッグ情報をコードに残しておける。

### pdb / breakpoint() / ipdb

`print()` やログでは追いきれない複雑なバグには、**対話型デバッガ**を使う。Python 3.7以降では、組み込み関数 `breakpoint()` を呼ぶだけでデバッガが起動する[4](https://docs.python.org/3/library/sys.html#sys.breakpointhook)。

```python
def calculate_gc_stats(sequences: list[str]) -> dict[str, float]:
    """複数の塩基配列のGC含量統計を計算する."""
    gc_ratios: list[float] = []
    for seq in sequences:
        upper = seq.upper()
        gc_count = upper.count("G") + upper.count("C")
        gc_ratio = gc_count / len(upper) if upper else 0.0
        # ここでデバッガを起動し、変数の値を確認できる
        breakpoint()  # ← 実行がここで一時停止する
        gc_ratios.append(gc_ratio)
    ...
```

`breakpoint()` を挿入してスクリプトを実行すると、その行で実行が一時停止し、pdb（Python Debugger）のプロンプトが表示される[1](https://docs.python.org/3/library/pdb.html)。

pdbの基本コマンドを以下にまとめる。

| コマンド | 省略形 | 説明 |
|---------|--------|------|
| `next` | `n` | 次の行に進む（関数呼び出しの内部には入らない） |
| `step` | `s` | 次の行に進む（関数呼び出しの内部に入る） |
| `continue` | `c` | 次のブレークポイントまで実行を続ける |
| `print(expr)` | `p expr` | 式を評価して表示する |
| `list` | `l` | 現在の行の前後のソースコードを表示する |
| `where` | `w` | コールスタック（呼び出し階層）を表示する |
| `quit` | `q` | デバッガを終了する |

典型的なデバッグセッションは次のようになる。

```
> scripts/ch09/pdb_demo.py(13)calculate_gc_stats()
-> gc_ratios.append(gc_ratio)
(Pdb) p seq          # 現在の配列を確認
'GCGC'
(Pdb) p gc_count     # GC塩基数を確認
4
(Pdb) p gc_ratio     # GC含量を確認
1.0
(Pdb) n              # 次の行に進む
(Pdb) c              # 次のbreakpoint()まで続行
```

**ipdb**: pdbの機能にIPythonの便利な機能（タブ補完、シンタックスハイライト）を追加したデバッガである[9](https://github.com/gotcha/ipdb)。`pip install ipdb` でインストールし、環境変数 `PYTHONBREAKPOINT=ipdb.set_trace` を設定すると、`breakpoint()` で ipdb が起動する。

```bash
# PYTHONBREAKPOINT環境変数でデバッガを切り替えるシェルコマンド
# breakpoint() 呼び出し時に ipdb が起動するようになる
export PYTHONBREAKPOINT=ipdb.set_trace
python3 my_script.py
```

デバッガを無効化したい場合は、`PYTHONBREAKPOINT=0` と設定する。`breakpoint()` の呼び出しが無視されるため、コードを編集せずにデバッグ出力を止められる。

```bash
# breakpoint() を無効化するシェルコマンド
# コード内の breakpoint() がすべて無視される
PYTHONBREAKPOINT=0 python3 my_script.py
```

### warningsモジュール

Pythonの `warnings` モジュール[3](https://docs.python.org/3/library/warnings.html)は、エラーではないが注意が必要な状況を通知する仕組みである。バイオインフォマティクスでよく目にする警告には以下がある。

- **DeprecationWarning**: 使用中の機能が将来削除される予定。ライブラリのバージョンアップ時に頻出する
- **FutureWarning**: 将来バージョンで挙動が変わる予定。pandasで特に多い
- **SettingWithCopyWarning**（pandas固有）: DataFrameのコピーとビューの区別に関する警告

警告は通常無視されがちだが、デバッグ時には重要な手がかりになることがある。警告を例外に昇格させることで、発生箇所を特定できる。

```python
import warnings

# 警告を例外に昇格させるコード
# warnings.filterwarnings("error") で全ての警告が例外として発生する
# これにより、警告の発生箇所が traceback で特定できる
warnings.filterwarnings("error")

# この設定のもとでは、警告が出るコードを実行すると
# Warning 例外が送出され、traceback が表示される
```

特定の警告カテゴリだけを例外に昇格させることもできる。

```python
import warnings

# DeprecationWarning だけを例外に昇格させる設定
# category 引数で対象の警告クラスを指定する
warnings.filterwarnings("error", category=DeprecationWarning)
```

### デバッグ時のlogger活用

[§11-3 ロギング](./11_cli.md#11-3-ロギング)で `logging` モジュールの基本設定を学んだ。ここでは、デバッグ局面での応用パターンを紹介する。

**コマンドラインからログレベルを切り替える**: CLIツールに `--log-level` オプションを追加しておくと、デバッグ時だけ詳細なログを表示できる[10](https://docs.python.org/3/library/logging.html)。

```python
import argparse
import logging

# コマンドライン引数でログレベルを切り替えるパターン
# argparse の --log-level オプションで DEBUG/INFO/WARNING を指定できる
parser = argparse.ArgumentParser()
parser.add_argument(
    "--log-level",
    default="WARNING",
    choices=["DEBUG", "INFO", "WARNING"],
)
args = parser.parse_args()
logging.basicConfig(level=getattr(logging, args.log_level))
```

```bash
# 通常実行（WARNING以上のみ表示）
python3 my_pipeline.py --log-level WARNING

# デバッグ実行（DEBUG以上を表示 — 全ログが出力される）
python3 my_pipeline.py --log-level DEBUG
```

**条件付きログ**: 特定の条件でだけ詳細なログを出力するパターンも有用である。

```python
import logging

logger = logging.getLogger(__name__)

# 特定の条件（ここでは異常なGC含量）の場合だけ
# 詳細情報をデバッグログに出力するパターン
for record in records:
    gc = calculate_gc(record.sequence)
    if gc > 0.8 or gc < 0.2:
        # 異常値の場合だけ詳細をログ出力
        logger.debug(
            "異常GC含量: id=%s, gc=%.3f, len=%d, seq=%s...",
            record.id, gc, len(record.sequence), record.sequence[:20],
        )
```

#### エージェントへの指示例

デバッグツールをエージェントとの協働で活用する指示例を紹介する。

breakpoint()の挿入を依頼するとき:

> 「`calculate_gc_stats` 関数の forループ内に `breakpoint()` を挿入して、各イテレーションで `seq`, `gc_count`, `gc_ratio` の値を確認できるようにして」

print()をloggingに置換するとき:

> 「このスクリプトに散在する `print("DEBUG: ...")` を `logging.debug(...)` に置換して。ファイル冒頭に `logger = logging.getLogger(__name__)` のセットアップも追加して」

条件付きデバッグログの追加を依頼するとき:

> 「このVCFフィルタリング関数に、QUALが20未満のレコードだけ `logging.debug()` で詳細を出力するログを追加して。通常実行時にはパフォーマンスに影響しないように」

---

## 9-3. よくあるバグのパターン

経験豊富な開発者がデバッグを速くこなせるのは、「よくあるバグのパターン」を知っているからである。パターンを知っていれば、症状を見ただけで原因の見当がつく。本節では、バイオインフォマティクスで特に頻出するバグパターンを紹介する。

### Off-by-one: 0-based vs 1-based

バイオインフォマティクスで最も頻繁に遭遇するバグが、**座標系の不一致**によるOff-by-oneエラー（1つずれ）である。

主要なファイル形式の座標系を整理する。

| 形式 | 開始位置 | 区間 | 例: 1〜10番目の塩基 |
|------|---------|------|---------------------|
| **Python** | 0-based | 半開 `[start, end)` | `seq[0:10]` |
| **BED** | 0-based | 半開 `[start, end)` | `0  10` |
| **GFF/GTF** | 1-based | 閉 `[start, end]` | `1  10` |
| **SAM** | 1-based | 閉 `[start, end]` | `POS=1` |
| **VCF** | 1-based | — | `POS=1` |

BED座標をGFF座標に変換する**バグあり版**と**修正版**の対比を見てみよう。

```python
# バグあり版: BED→GFF変換で start に +1 を忘れている
# BED は 0-based 半開、GFF は 1-based 閉なので +1 が必要
def bed_to_gff_buggy(chrom, bed_start, bed_end):
    gff_start = bed_start    # バグ: +1 を忘れている
    gff_end = bed_end
    return (chrom, gff_start, gff_end)

# 修正版: start に +1 して座標系を正しく変換
def bed_to_gff_correct(chrom, bed_start, bed_end):
    gff_start = bed_start + 1  # BED 0-based → GFF 1-based
    gff_end = bed_end           # 半開→閉: 値は同じ
    return (chrom, gff_start, gff_end)
```

座標変換のバグを防ぐには、`assert` による検証が有効である。

```python
# 座標の妥当性を検証する関数
# 座標系ごとに開始位置の最小値と start ≤ end を確認する
def validate_coordinates(start, end, seq_length, coordinate_system="bed"):
    if coordinate_system == "bed":
        if start < 0:
            raise ValueError(f"BED start は 0 以上: {start}")
        if end > seq_length:
            raise ValueError(f"BED end が配列長 {seq_length} を超過: {end}")
    elif coordinate_system == "gff":
        if start < 1:
            raise ValueError(f"GFF start は 1 以上: {start}")
    ...
```

> 🧬 **バイオインフォ座標系の罠**
>
> ゲノム座標系の混乱は、バイオインフォマティクスにおける最大のバグ源の一つである[8](https://genome.ucsc.edu/FAQ/FAQformat.html)。主な注意点をまとめる。
>
> | 罠 | 説明 |
> |---|------|
> | **BED vs GFF** | BED `(0, 10)` = GFF `(1, 10)`。start が1ずれる |
> | **reverse_complement忘れ** | マイナス鎖の遺伝子では逆相補鎖を取る必要がある |
> | **FASTAヘッダのパース** | `>gene1 description` のスペース以降を遺伝子名に含めてしまう |
> | **N塩基の扱い** | `N` をGC含量計算に含めるか除外するかで結果が変わる |
> | **染色体名の不一致** | `chr1` vs `1`。UCSC形式とEnsembl形式の混在 |
>
> 座標変換を行うときは、必ず**往復変換テスト**（BED→GFF→BED）で元に戻ることを確認しよう。

### パス関連のバグ

ファイルパスに関するバグは、開発環境では動くが本番環境で壊れる典型例である。

**相対パスとcwd依存**: `Path("data/input.csv")` のような相対パスは、カレントディレクトリ（cwd）に依存する。スクリプトの実行場所が変わるとファイルが見つからなくなる。

```python
from pathlib import Path

# バグあり版: cwd に依存するため、実行場所で結果が変わる
def read_config_relative_buggy(name: str) -> str:
    path = Path(name)      # cwd からの相対パス
    return path.read_text()

# 修正版: __file__ を基準にして、実行場所に依存しないパスを構築する
def read_config_relative_fixed(name: str) -> str:
    script_dir = Path(__file__).resolve().parent  # このスクリプトのディレクトリ
    path = script_dir / name
    return path.read_text()
```

**チルダ展開**: `~/data/input.csv` のようなパスは、`Path` に渡しただけでは展開されない。`Path.expanduser()` を使う必要がある。

```python
from pathlib import Path

# ユーザ入力のパス文字列を安全に解決する関数
# expanduser() でチルダを展開し、resolve() で絶対パスに変換する
def resolve_data_path(path_str: str) -> Path:
    path = Path(path_str).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {path}")
    return path
```

### エンコーディングの問題

テキストファイルの文字エンコーディングの不一致は、`UnicodeDecodeError` を引き起こす。

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 42
```

主な原因と対処は以下のとおりである。

| 原因 | 対処 |
|------|------|
| ファイルがLatin-1（ISO 8859-1）で保存されている | `open(path, encoding="latin-1")` を指定 |
| BOM付きUTF-8 | `encoding="utf-8-sig"` を指定 |
| バイナリファイルをテキストとして開いている | `open(path, "rb")` でバイナリモードで開く |

確認方法として、`file` コマンドが便利である。

```bash
# file コマンドでファイルのエンコーディングを確認する
# UTF-8, ASCII, ISO 8859-1 などが表示される
file --mime-encoding data.csv
```

### 型の不一致

CSVファイルを読み込んだ際、すべての値が文字列として読み込まれることがある。数値を期待している箇所で文字列が渡されると、予期しない動作になる。

```python
# バグあり版: CSVの値が文字列のまま + で結合される
# ["1.5", "2.3", "0.8"] → "1.52.30.8"（文字列連結）
def sum_expression_values_buggy(values: list[str]) -> str:
    total = ""
    for v in values:
        total = total + v  # 文字列の + は連結
    return total

# 修正版: 明示的に float() で変換してから合計する
def sum_expression_values_fixed(values: list[str]) -> float:
    total = 0.0
    for v in values:
        total += float(v)  # 数値に変換してから加算
    return total
```

もう一つの頻出パターンが、`NaN` と `None` の混同である。pandasでは欠損値が `NaN`（Not a Number）で表現されるが、Pythonの `None` とは異なる挙動を示す。

```python
import math

# None と NaN を統一的に除外して平均を計算する関数
# math.isnan() で NaN を検出し、is not None で None を除外する
def safe_mean(values: list[float | None]) -> float | None:
    valid = [v for v in values if v is not None and not math.isnan(v)]
    if not valid:
        return None
    return sum(valid) / len(valid)
```

型の不一致バグを事前に防ぐには、[§8 コードの正しさを守るテスト技法](./08_testing.md)で紹介した型チェッカ（mypy）が有効である。

> 🤖 **機械学習コードのデバッグ**
>
> 機械学習コードには、従来のプログラミングとは異なるバグパターンがある。
>
> | パターン | 症状 | 対処 |
> |---------|------|------|
> | **NaN/Inf伝播** | 損失関数が `nan` になる | 入力データと中間出力に `np.isnan()` チェックを挿入 |
> | **shape mismatch** | `ValueError: shapes not aligned` | 各ステップで `tensor.shape` をログ出力 |
> | **データリーク** | テストスコアだけ異常に高い | train/test分割前に正規化していないか確認 |
> | **再現性の欠如** | 実行ごとに結果が変わる | `random.seed()`, `np.random.seed()`, `torch.manual_seed()` を固定 |
> | **勾配消失/爆発** | 学習が進まない、または発散する | 勾配のノルムを監視。gradient clippingを適用 |
>
> 機械学習のバグは「エラーにならないが結果が間違っている」ケースが大半である。テストデータに対する予測精度が「良すぎる」場合はデータリークを、「全く改善しない」場合は勾配の問題を、まず疑うとよい。

### メモリ不足（OOM）

大規模データを扱うバイオインフォマティクスでは、メモリ不足（Out of Memory; OOM）が頻出する。

**症状の認識**:

- `MemoryError`（Python側で検出された場合）
- プロセスが突然終了する（OSの OOM Killer に SIGKILL される場合）
- `Killed` というメッセージだけが表示される

**原因の切り分け手順**:

1. まず `free -h`（Linux）や `Activity Monitor`（macOS）でシステムの空きメモリを確認する
2. [§17-1](./17_performance.md)で紹介した `memory_profiler` で、メモリ使用量の推移を確認する
3. メモリの急増箇所が特定できたら、[§17-3](./17_performance.md)で学んだチャンク処理やジェネレータで対処する

新規コードを書く際は、データサイズの事前見積もり（レコード数 × 1レコードあたりのメモリ使用量）を行い、利用可能メモリと比較する習慣をつけよう。

### 並列処理のバグ

[§17-2](./17_performance.md)で並列処理を学んだが、並列処理固有のバグパターンも存在する。

| パターン | 症状 | 対処 |
|---------|------|------|
| **PickleError** | `Can't pickle local object` | ラムダや内部関数をトップレベル関数に変更 |
| **競合状態** | 実行ごとに結果が異なる | 共有状態を避け、各プロセスが独立に動作するよう設計 |
| **デッドロック** | プログラムが無応答になる | タイムアウトを設定。ロックの取得順序を統一 |

並列処理のバグに遭遇したら、まず**逐次版で動かす**ことを試みる。逐次版で正しく動くなら、バグは並列化のロジックにある。逐次版でも動かないなら、並列化以前の問題である。

```python
from concurrent.futures import ProcessPoolExecutor

# 並列処理のデバッグでは、まず逐次版で動作確認する
# max_workers=1 に設定すると、逐次実行になる（デバッグ用）
with ProcessPoolExecutor(max_workers=1) as executor:
    results = list(executor.map(process_record, records))
```

#### エージェントへの指示例

バグパターンの知識をエージェントとの協働に活かす指示例を紹介する。

座標変換バグの修正と回帰テストを依頼するとき:

> 「BED→GFF座標変換で start の +1 を忘れていた。修正して、BED (0, 10) → GFF (1, 10) と BED (5, 6) → GFF (6, 6) の往復変換テストを [§8](./08_testing.md)の方針に従って pytest で書いて」

パス問題の修正を依頼するとき:

> 「このスクリプトの `Path("config/settings.yaml")` が cwd 依存で壊れる。`Path(__file__).resolve().parent` 基準に修正して」

NaN混入箇所の特定を依頼するとき:

> 「このパイプラインの出力DataFrameに NaN が混入している。各処理ステップの後に `df.isna().sum()` を挿入して、どのステップで NaN が発生するか特定するデバッグコードを書いて」

### Python固有の落とし穴

ここまで紹介したバグパターンはバイオインフォマティクス固有のものが多かったが、Python言語自体にも初心者が陥りやすい落とし穴がある。AIエージェントが生成するコードにもこれらのパターンが紛れ込むことがあるため、レビュー時に見抜けるようにしておきたい。

**ミュータブルデフォルト引数**: 関数のデフォルト引数にリストや辞書を使うと、関数呼び出しをまたいで共有される。

```python
# ❌ 誤り: デフォルト引数のリストが全呼び出しで共有される
def add_gene(name: str, gene_list: list[str] = []) -> list[str]:
    gene_list.append(name)
    return gene_list

# ✅ 修正: None をデフォルトにし、関数内で新しいリストを作る
def add_gene(name: str, gene_list: list[str] | None = None) -> list[str]:
    if gene_list is None:
        gene_list = []
    gene_list.append(name)
    return gene_list
```

**浅いコピーvs深いコピー**: `list.copy()` や `dict.copy()` は最上位の要素だけをコピーする（浅いコピー）。ネストされたリストや辞書は元のオブジェクトと共有されたままである。

```python
import copy

original = {"genes": ["BRCA1", "TP53"]}
shallow = original.copy()          # 浅いコピー
shallow["genes"].append("EGFR")    # original["genes"] にも EGFR が追加される

deep = copy.deepcopy(original)     # 深いコピー
deep["genes"].append("MYC")        # original は変更されない
```

**`is` vs `==`**: `is` はオブジェクトの同一性（メモリ上の同じオブジェクトか）を、`==` は値の等価性を比較する。Pythonは小さい整数（-5〜256）をキャッシュするため、`is` が偶然動いてしまうことがある。

```python
# ❌ 危険: 小さい整数ではたまたま動くが、大きい値では壊れる
a = 256
b = 256
a is b     # True（キャッシュされている）

a = 257
b = 257
a is b     # False（別オブジェクト）

# ✅ 値の比較には常に == を使う。is は None との比較にだけ使う
if value is None: ...      # ✅ None との比較は is
if count == 257: ...       # ✅ 値の比較は ==
```

**文字列の不変性**: Pythonの文字列は不変（immutable）である。`str.replace()` や `str.upper()` は元の文字列を変更せず、新しい文字列を返す。

```python
sequence = "ATGCN"
sequence.replace("N", "")   # "ATGC" を返すが、sequence は変わらない
# ✅ 戻り値を変数に代入する
sequence = sequence.replace("N", "")  # sequence が "ATGC" に更新される
```

**pandasの`SettingWithCopyWarning`**: DataFrameのスライスに対して値を代入すると、元のDataFrameが変更されるかコピーが変更されるかが曖昧になる。

```python
import pandas as pd

df = pd.DataFrame({"gene": ["BRCA1", "TP53"], "score": [0.9, 0.3]})

# ❌ 警告が出る: チェーンインデックスによる代入
df[df["score"] > 0.5]["gene"] = "HIGH"

# ✅ .loc[] を使って明示的にアクセスする
df.loc[df["score"] > 0.5, "gene"] = "HIGH"
```

**NumPyのビューvsコピー**: NumPy配列のスライス（`a[::2]`）は元の配列のデータを共有する**ビュー**を返す。ファンシーインデックス（`a[[0, 2, 4]]`）は独立した**コピー**を返す。どちらが返るかを意識しないと、元の配列が意図せず変更される。

```python
import numpy as np

arr = np.array([10, 20, 30, 40, 50])

view = arr[::2]      # ビュー: arr とデータを共有
view[0] = 999        # arr[0] も 999 に変わる

copy = arr[[0, 2, 4]]  # コピー: 独立したデータ
copy[0] = 888          # arr は変わらない
```

#### エージェントへの指示例

Python固有の落とし穴を知っていると、エージェントが生成したコードのレビューでバグを見つけやすくなる:

> 「この関数のデフォルト引数に `results: dict = {}` が使われている。ミュータブルデフォルト引数のバグがないか確認して、必要なら修正して」

> 「エージェントが生成したコードで `df[df['padj'] < 0.05]['log2FC']` というチェーンインデックスが使われている。`SettingWithCopyWarning` が出ないように `.loc[]` に書き換えて」

> 「このNumPy配列操作がビューを返すかコピーを返すか判断がつかない。`np.shares_memory()` で確認するアサーションを追加して」

---

## まとめ

本章で学んだデバッグ技術の主要概念を整理する。

| 概念 | 要点 |
|------|------|
| **traceback読解** | 最終行（エラー種類）から読み始め、自分のコードのフレームに注目する |
| **3要素の言語化** | 期待した動作・実際の動作・再現手順を明確にする |
| **最小再現例（MRE）** | バグを再現できる最小限のコードとデータ。エージェントの回答精度が上がる |
| **二分探索デバッグ** | パイプラインの中間地点で出力を確認し、問題箇所を半分ずつ絞り込む |
| **print() vs logging** | `logging.debug()` なら消し忘れの心配なく、ログレベルで出力を制御できる |
| **breakpoint()** | 対話型デバッガ（pdb）を起動。`PYTHONBREAKPOINT` で無効化や切り替えが可能 |
| **warningsの活用** | `filterwarnings("error")` で警告を例外に昇格し、発生箇所を特定 |
| **Off-by-one** | BED(0-based半開)とGFF(1-based閉)の座標変換に注意。往復変換テストで検証 |
| **パスの安全な扱い** | `Path(__file__).resolve().parent` で cwd 非依存に。`expanduser()` でチルダ展開 |
| **型の不一致** | CSV読み込み時の str→float 変換忘れ、NaN と None の混同に注意 |

次章の[§10 ソフトウェア成果物の設計 — スクリプトからパッケージまで](./10_deliverables.md)では、「何を作るのか」——スクリプト、パッケージ、パイプラインといった成果物の形式を選び、それに適したプロジェクト構造を設計する方法を学ぶ。

---

## 演習問題

本章の内容を、エージェントとの協働を通じて実践する課題である。

### 演習 9-1: traceback の読解 **[概念]**

以下の traceback からエラーの種類、発生箇所、根本原因を特定せよ。

```
Traceback (most recent call last):
  File "filter_vcf.py", line 42, in process_record
    qual = float(record[5])
ValueError: could not convert string to float: '.'
```

具体的に、以下の3点を答えよ。

1. エラーの種類は何か
2. どのファイルの何行目で発生しているか
3. 根本原因は何か。どのように修正すべきか

（ヒント）traceback は下から上に読む。最終行がエラーの種類とメッセージ、その上の行が発生箇所である。VCF ファイルの QUAL 列が `.`（欠損値）である行が原因であり、`float()` に渡す前に `.` をチェックする必要がある。

### 演習 9-2: 最小再現例の作成 **[指示設計]**

バイオインフォマティクスのパイプライン途中で `KeyError: 'gene_name'` が発生した。エージェントにデバッグさせるための指示文を書け。指示文には「最小再現例の3要素」をすべて含めること。

- **期待した動作**: 何が起きるはずだったか
- **実際の動作**: 何が起きたか（エラーメッセージの全文を含む）
- **再現手順**: どのデータを使い、どのコマンドを実行したか

（ヒント）「期待した動作」「実際の動作」「再現手順」の3点を明確に書くことで、エージェントは的確にデバッグできる。入力データのサンプル（数行で十分）も含めると効果的である。

### 演習 9-3: 座標変換の検証 **[レビュー]**

エージェントが BED（0-based, half-open）から GFF（1-based, closed）への座標変換コードを生成した。以下の変換ロジックが正しいか検証せよ。

```python
start_gff = start_bed + 1
end_gff = end_bed
```

具体的な座標値（例: BED で `chr1  100  200` の場合）を使って変換結果を確認し、正しいかどうかを判定せよ。

（ヒント）往復変換テスト（BED → GFF → BED）で元の値に戻るかを確認する方法が有効である。BED の `100-200` は塩基 101〜200 を表し、GFF の `101-200` も塩基 101〜200 を表す。

### 演習 9-4: 二分探索デバッグ **[実践]**

10 ステップのパイプラインの最終出力が間違っている。エージェントに二分探索デバッグを指示し、問題のステップを特定させよ。以下の手順で指示文を作成せよ。

1. まずステップ 5 の中間出力が正しいかを確認させる
2. 結果に応じてステップ 1–5 またはステップ 6–10 に探索範囲を絞る
3. 問題のステップが特定されるまで繰り返す

（ヒント）「ステップ 5 の出力が正しいか確認して。正しければステップ 6–10 に問題がある」という形で指示する。各ステップの「正しい出力」の定義（期待値）をあらかじめ用意しておくことが重要である。

---

## さらに学びたい読者へ

本章で扱ったデバッグ手法を体系的に深めたい読者に向けて、デバッグの古典的教科書を紹介する。

- **Agans, D. J. *Debugging: The 9 Indispensable Rules for Finding Even the Most Elusive Software and Hardware Problems*. AMACOM, 2002.** https://www.amazon.co.jp/dp/0814474578 — デバッグの9つの鉄則を提示する実践書。「Understand the System」「Make It Fail」「Quit Thinking and Look」など、本章で紹介したアプローチと同じ精神に基づく教科書である。
- **Zeller, A. *Why Programs Fail: A Guide to Systematic Debugging* (2nd ed.). Morgan Kaufmann, 2009.** https://www.amazon.co.jp/dp/0123745152 — 科学的なデバッグ手法（デルタデバッギング、原因の系統的な絞り込み）の教科書。本章で扱った最小再現例の作成手法を理論的に裏付ける。やや学術的だが、デバッグを「勘」ではなく「方法論」として捉える視点が得られる。
- **Stack Overflow. "How to create a Minimal, Reproducible Example".** https://stackoverflow.com/help/minimal-reproducible-example — 最小再現例の作り方の簡潔なガイドライン。デバッグ時にもコミュニティでの質問時にも役立つ。

---

## 参考文献

[1] Python Software Foundation. "pdb — The Python Debugger". https://docs.python.org/3/library/pdb.html (参照日: 2026-03-21)

[2] Python Software Foundation. "traceback — Print or retrieve a stack traceback". https://docs.python.org/3/library/traceback.html (参照日: 2026-03-21)

[3] Python Software Foundation. "warnings — Warning control". https://docs.python.org/3/library/warnings.html (参照日: 2026-03-21)

[4] Python Software Foundation. "sys.breakpointhook". https://docs.python.org/3/library/sys.html#sys.breakpointhook (参照日: 2026-03-21)

[5] Stack Overflow. "How to create a Minimal, Reproducible Example". https://stackoverflow.com/help/minimal-reproducible-example (参照日: 2026-03-21)

[6] Agans, D. J. *Debugging: The 9 Indispensable Rules for Finding Even the Most Elusive Software and Hardware Problems*. AMACOM, 2002. ISBN: 978-0814474570

[7] Zeller, A. *Why Programs Fail: A Guide to Systematic Debugging*. 2nd ed. Morgan Kaufmann, 2009. ISBN: 978-0123745156

[8] UCSC Genome Browser. "FAQ: Coordinate Transforms". https://genome.ucsc.edu/FAQ/FAQformat.html (参照日: 2026-03-21)

[9] gotcha and contributors. "ipdb: IPython-enabled pdb". https://github.com/gotcha/ipdb (参照日: 2026-03-21)

[10] Python Software Foundation. "logging — Logging facility for Python". https://docs.python.org/3/library/logging.html (参照日: 2026-03-21)
