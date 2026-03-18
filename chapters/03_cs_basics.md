# 3. 計算機科学の基礎知識

[§1 設計原則](./01_design.md)では、コードを「どう設計するか」の判断基準を学んだ。しかし、設計原則に従って美しいコードを書いても、その下で動く計算機の仕組みを知らなければ、思わぬ落とし穴にはまる。10万件の遺伝子IDを検索するのに何分もかかる、発現量の比較が一致しない、解析結果が毎回変わる——これらはすべて、計算機科学の基礎知識があれば避けられる問題である。

本章では、バイオインフォマティクスのプログラミングで特に重要な計算機科学の概念を取り上げる。大学のCS学科で1学期かけて学ぶような内容を、実験系研究者が「踏みがちな罠」に焦点を当てて凝縮した。理論の完全な理解は求めない。「なぜこのデータ構造を選ぶのか」「なぜ浮動小数点の比較に `==` を使ってはいけないのか」——こうした判断ができるようになることがゴールである。

---

## 3-1. データ構造と計算量

### データ構造の選択が性能を決める

プログラムの性能は、アルゴリズムだけでなく**データ構造の選択**によって劇的に変わる。Pythonには複数の組み込みデータ構造があり、それぞれ得意な操作が異なる。

| データ構造 | 特徴 | 検索 | 追加 | 順序 |
|-----------|------|------|------|------|
| `list` | 順序付き配列 | $O(n)$ | $O(1)$（末尾） | あり |
| `tuple` | イミュータブルなlist | $O(n)$ | — | あり |
| `set` | 重複なし集合 | $O(1)$ | $O(1)$ | なし |
| `dict` | キーと値のマッピング | $O(1)$ | $O(1)$ | 挿入順[1](https://docs.python.org/3/tutorial/datastructures.html) |
| `deque` | 両端キュー | $O(n)$ | $O(1)$（両端） | あり |

ここで登場する $O$ 記法（ビッグオー記法）は、入力サイズnに対して処理時間がどう増えるかを表す[2](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)。$O$ は "order of" の頭文字で、「オー」と読む。$O(n)$ なら「オーエヌ」、$O(n^2)$ なら「オーエヌの二乗」と発音する。論文やミーティングで口頭で議論する場面も多いため、覚えておくとよい。

- $O(1)$（定数時間、「オーいち」）: データが何件あっても一瞬で終わる
- $O(\log n)$（対数時間、「オーログエヌ」）: データが倍になっても処理は1ステップ増えるだけ。二分探索が代表例
- $O(n)$（線形時間、「オーエヌ」）: データ件数に比例して遅くなる
- $O(n \log n)$（「オーエヌログエヌ」）: ソートの典型的な計算量
- $O(n^2)$（二次時間、「オーエヌの二乗」）: 二重ループ。1万件で重く、10万件で実用不可能

速い順に並べると $O(1) < O(\log n) < O(n) < O(n \log n) < O(n^2)$ である。次の表は、$n$ = 100,000（10万件、遺伝子数のオーダー）のときの処理回数の違いを示す:

| 計算量 | $n$ = 100,000 での処理回数 | 感覚的な目安 |
|--------|------------------------------|-------------|
| $O(1)$ | $1$ | 一瞬 |
| $O(\log n)$ | $\approx 17$ | 一瞬 |
| $O(n)$ | $10^5$ | 一瞬〜数秒 |
| $O(n \log n)$ | $\approx 1.7 \times 10^6$ | 数秒 |
| $O(n^2)$ | $10^{10}$ | 数時間〜実用不可 |

nが10万件のとき、$O(\log n)$ と $O(n^2)$ では処理回数が約6億倍異なる。バイオインフォマティクスで扱うデータは容易にこの規模に達するため、計算量の違いがスクリプトの実用性を左右する。

### 遺伝子ID検索: list vs set の決定的な違い

バイオインフォマティクスでは、数万〜数十万の遺伝子IDから特定のIDを検索する場面が頻繁にある。このとき、データ構造の選択が処理速度を桁違いに変える。

```python
# 悪い例: listの in 演算子 → O(n)
gene_list = ["GENE_000000", "GENE_000001", ..., "GENE_099999"]
"GENE_099999" in gene_list  # 最悪10万回の比較が必要

# 良い例: setの in 演算子 → O(1)
gene_set = set(gene_list)
"GENE_099999" in gene_set   # ハッシュテーブルで一発
```

listの `in` はリストの先頭から順に要素を比較するため、要素数nに比例して $O(n)$ かかる。一方、setとdictはハッシュテーブルを内部で使っており、要素数に関係なく $O(1)$ で検索できる。

以下のベンチマークで、この差を実感してみよう:

```python
from scripts.ch03.data_structure_bench import benchmark_search

results = benchmark_search(n=100_000, n_queries=1000)
for name, elapsed in results.items():
    print(f"{name:>5}: {elapsed:.4f} 秒")
```

典型的な結果:

```
 list: 1.2345 秒
  set: 0.0001 秒
 dict: 0.0001 秒
```

listが1秒以上かかるのに対し、setとdictは0.1ミリ秒未満で完了する。10万件程度でこの差なので、ヒトゲノムの数万遺伝子、メタゲノムの数百万配列といった規模では、データ構造の選択がスクリプトの実用性そのものを左右する。

### 使い分けの指針

- **「この要素が含まれるか？」の判定** → `set`
- **「IDから情報を引きたい」** → `dict`
- **「順番が重要」** → `list`
- **「変更されたくない」** → `tuple`
- **「先頭と末尾の両方から出し入れしたい」** → `deque`

AIコーディングエージェントへの指示例:

```
「この遺伝子IDリストの検索が遅い。setに変換してO(1)で検索できるようにリファクタリングして」
```

> **🧬 コラム: バイオインフォマティクスで出会うアルゴリズムの計算量**
>
> 計算量の知識があると、ツールの実行時間が妥当かどうかを判断できる。「10万リードのマッピングに何時間もかかる」のは正常か、それともどこかがおかしいのか——以下の表を目安にしてほしい。
>
> | カテゴリ | アルゴリズム・操作 | 計算量 | 備考 |
> |---------|------------------|--------|------|
> | 配列検索 | BLAST | ヒューリスティック | 全探索を避けて高速化[13](https://doi.org/10.1016/S0022-2836(05)80360-2) |
> | ペアワイズアラインメント | Smith-Waterman / Needleman-Wunsch | $O(mn)$ | m, nは配列長。動的計画法[14](https://doi.org/10.1016/0022-2836(81)90087-5) |
> | リードマッピング | BWA / Bowtie2 | $O(m)$（クエリあたり） | FM-indexで参照ゲノムを事前索引化[15](https://doi.org/10.1093/bioinformatics/btp324) |
> | 多重配列アライメント | 厳密解（動的計画法） | $O(L^k)$ | Lは配列長、kは配列数。3本以上は近似手法を使う |
> | インデックス検索 | BAM (.bai) / tabix (.tbi) | $O(\log n)$ | 二分探索ベース |
> | インデックス検索 | FASTA faidx (.fai) | $O(1)$ | ファイルオフセットで直接アクセス |
> | ソート | `samtools sort` 等 | $O(n \log n)$ | 比較ソートの理論下限 |
> | 次元削減 | PCA（特異値分解） | $O(np^2)$ | nはサンプル数、pは特徴量数 |
> | 次元削減 | t-SNE | $O(n^2)$ | Barnes-Hut近似で $O(n \log n)$[11](https://jmlr.org/papers/v9/vandermaaten08a.html) |
> | 次元削減 | UMAP | $O(n^{1.14})$ 程度 | 近似最近傍探索で高速化[10](https://doi.org/10.48550/arXiv.1802.03426) |
> | クラスタリング | k-means | $O(nkdi)$ | k: クラスタ数、d: 次元、i: 反復回数 |
> | 系統樹 | Neighbor-Joining | $O(n^3)$ | nは系統数。大規模データでは律速になる[16](https://doi.org/10.1093/oxfordjournals.molbev.a040454) |
>
> 表中の計算量は理論上の上界であり、実装の工夫やヒューリスティクスにより実際の速度は大きく異なる。たとえばBLASTはデータベース全体を総当たり比較するのではなく、短いワード一致から候補を絞り込むことで実用的な速度を実現している。ツールの実行時間が想定より極端に長い場合は、入力サイズと計算量の関係を見直す手がかりにしてほしい。

---

## 3-2. 数値表現と浮動小数点

### 整数型のビット幅

多くのプログラミング言語では、整数型にビット幅の制限がある。たとえばC言語やNumPyの `int32` は約±21億（2³¹ − 1）までしか扱えず、それを超えると**オーバーフロー**を起こして予期しない値になる。

```python
import numpy as np

# NumPyのint32はオーバーフローする
a = np.int32(2_147_483_647)  # int32の最大値
print(a + np.int32(1))       # → -2147483648（符号が反転！）

# Pythonの組み込みintは任意精度なのでオーバーフローしない
b = 2_147_483_647
print(b + 1)                 # → 2147483648（正しい）
```

Pythonの組み込み `int` は任意精度（メモリが許す限り大きな数を扱える）だが、NumPyやpandasの整数型にはビット幅の制限がある。大きなゲノム座標や配列カウントを扱うときは `int64` を明示的に指定するのが安全である。

### IEEE 754 浮動小数点 — `0.1 + 0.2 != 0.3` 問題

コンピュータは小数を**IEEE 754 浮動小数点数**として表現する[3](https://doi.org/10.1145/103162.103163)。これは2進数で小数を近似する方式であり、10進数で正確に表せる値でも、2進数では無限小数になることがある。

```python
>>> 0.1 + 0.2
0.30000000000000004

>>> 0.1 + 0.2 == 0.3
False
```

これはPythonのバグではなく、IEEE 754の仕様上避けられない挙動である。0.1は2進数では `0.0001100110011...` と無限に続くため、有限のビットで打ち切った時点で微小な誤差が生じる。

### 丸め誤差の蓄積

微小な誤差は、繰り返し計算すると蓄積する:

```python
import math

# 組み込みsum(): 丸め誤差が蓄積する
values = [0.1] * 10
print(sum(values))        # → 0.9999999999999999（1.0ではない！）

# math.fsum(): 中間結果を高精度で保持する
print(math.fsum(values))  # → 1.0（正確）
```

発現量（TPM, FPKM）の正規化計算や、大量のスコアの合計など、多くの値を足し合わせる場面では `math.fsum()` を使うべきである[4](https://docs.python.org/3/library/math.html#math.fsum)。

### CSV round-trip による丸め誤差の蓄積

丸め誤差が蓄積するもう一つの典型的な経路が、**CSVファイルを介したデータの受け渡し**である。浮動小数点数をCSVに書き出すとき、テキスト表現に変換される際に桁数が制限される。そのCSVを読み込んで計算し、再びCSVに書き出す——このround-tripを繰り返すたびに、微小な精度の劣化が蓄積していく。

バイオインフォマティクスのパイプラインでは、この問題が実際に起こりやすい。たとえば遺伝子発現解析で:

1. 正規化した発現量行列をCSVに出力
2. 別のスクリプトでCSVを読み込み、フィルタリングしてCSVに出力
3. さらに別のスクリプトでCSVを読み込み、差異解析を実行

というように、ステップごとにCSVを介してデータを受け渡す多段パイプラインを組むと、各ステップでわずかな精度劣化が生じ、最終結果に無視できない誤差が混入することがある。

**対策**: 中間データはバイナリ形式で保存する。NumPy配列なら `.npy`、シングルセル解析なら `.h5ad`（AnnData形式）、表形式データなら `.parquet` が適している。CSVは最終的に人間が確認するための出力や、他のツールとの受け渡しにのみ使う。

```python
import numpy as np

# 中間データの保存（推奨: バイナリ形式）
np.save("intermediate_matrix.npy", expression_matrix)  # 精度を完全に保持
matrix = np.load("intermediate_matrix.npy")

# 最終出力のみCSV
np.savetxt("final_results.csv", final_matrix, delimiter=",",
           header="gene1,gene2,gene3", comments="")
```

### 浮動小数点の比較

浮動小数点の等値比較に `==` を使ってはならない。代わりに `math.isclose()` または `numpy.allclose()` を使う[5](https://docs.python.org/3/library/math.html#math.isclose):

```python
import math

# 危険: == による比較
0.1 + 0.2 == 0.3           # → False

# 安全: math.isclose() による比較
math.isclose(0.1 + 0.2, 0.3)  # → True
```

`math.isclose()` はデフォルトで相対許容誤差 `1e-9` を使う。NumPyの配列には `np.allclose()` が対応する。

### 特殊な値: `inf` と `NaN`

IEEE 754は `inf`（無限大）と `NaN`（Not a Number）という特殊な値を定義している:

```python
import math

# inf: オーバーフロー等で生じる
print(float("inf") + 1)     # → inf
print(float("inf") * -1)    # → -inf

# NaN: 不正な演算で生じる
nan = float("nan")
print(nan == nan)            # → False（NaNは自分自身と等しくない！）
print(nan != nan)            # → True
print(math.isnan(nan))       # → True（判定にはisnan()を使う）
```

`NaN` の最大の罠は、**あらゆる比較演算が `False` を返す**ことである。`NaN == NaN` が `False` になるため、通常の `==` で検出できない。pandasのDataFrameでは `NaN` が欠損値として頻出するので、`pd.isna()` や `math.isnan()` での判定を習慣づけること。

> **🧬 コラム: バイオインフォで踏む浮動小数点の罠**
>
> - **正規化値の比較**: TPMやFPKMの値を `==` で比較すると、ツール間の実装差による微小な丸め誤差で「同じはずの値」が一致しない。`np.allclose()` を使う。
> - **p値のアンダーフロー**: ゲノムワイド関連解析（GWAS）等で得られる極小のp値（`1e-300`付近）は、乗算や変換の過程でアンダーフローして `0.0` になりうる。対策として**対数p値**（`-log10(p)`）で扱うのが定石である。
> - **GPU計算の精度**: GPU（float32）で発現量行列を処理すると、float64よりも精度が低いため、正規化後の微小な差が消失することがある。精度が重要な場面ではfloat64を明示する。
> - **Phredスコア**: 塩基品質スコアQ30 = 10⁻³ の対数変換など、対数スケールの計算では丸め誤差に特に注意が必要である。

---

## 3-3. 文字エンコーディング

### ASCII と UTF-8

コンピュータはテキストを数値（バイト列）として扱う。その変換規則が**文字エンコーディング**である。

- **ASCII**: 英数字と基本記号のみ（128文字）。FASTA/FASTQファイルの配列部分はASCIIの範囲で完結する。
- **UTF-8**: Unicodeの実装の一つで、ASCIIと後方互換性がある。日本語を含む多言語テキストを扱える。現在のデファクトスタンダードである[6](https://www.unicode.org/versions/Unicode16.0.0/)。

Pythonの `str` 型はUnicodeを内部表現としており、通常のテキスト処理ではエンコーディングを意識する必要はない。しかし、ファイルの読み書きでは `open()` の `encoding` パラメータに注意が必要である:

```python
# 明示的にUTF-8を指定する（推奨）
with open("annotation.txt", encoding="utf-8") as f:
    text = f.read()
```

### 改行コードの罠 — LF vs CR+LF

テキストファイルの改行コードは、OSによって異なる:

| OS | 改行コード | バイト列 |
|----|----------|---------|
| Unix / macOS | LF | `\n` |
| Windows | CR+LF | `\r\n` |

改行コード問題の典型的な発生源を知っておくと、トラブルシュートが速くなる:

- **Excel**: CSVエクスポートがOS依存の改行コードを使用する。Windows版Excelが出力したCSVは、ほぼ確実にCR+LFである。
- **解析装置の制御ソフト**: マイクロアレイスキャナー、プレートリーダー、質量分析計などの制御ソフトウェアはWindows上で動作することが多く、出力ファイルがCR+LFになる。
- **Windows版の解析ソフト**: Windows版のツールからエクスポートされたアノテーションファイルやGOterm一覧なども同様である。

これらのファイルがLinuxサーバに持ち込まれると、CR+LFの `\r` が配列データやIDの末尾に紛れ込み、「配列が一致しない」「パースエラーが出る」といった不可解なバグの原因になる。

```bash
# 改行コードの確認
file annotation.txt    # "ASCII text, with CRLF line terminators" と出たら注意

# バイト列を直接確認（\r\n が見えたらCR+LF）
od -c annotation.txt | head

# 変換
dos2unix annotation.txt  # CR+LF → LF に変換
```

`file` コマンドは改行コードの種類を教えてくれるが、`od -c` を使えばバイト列を直接確認でき、`\r\n` が実際にどこに入っているかを目視で確かめられる。

Pythonでは `open()` がデフォルトで改行コードを自動変換するが、バイナリモード（`"rb"`）で読み込む場合や、外部ツールに渡す場合は注意が必要である。

### バイトオーダー（エンディアン）

複数バイトのデータを格納する順序には、**ビッグエンディアン**（上位バイトが先）と**リトルエンディアン**（下位バイトが先）がある。BAMファイル等のバイナリフォーマットを扱う際に意識が必要になるが、通常はライブラリ（pysam等）が吸収してくれるため、自分でバイナリを直接解析しない限り問題になることは少ない。

---

## 3-4. 乱数と再現性

### 擬似乱数生成器（PRNG）

コンピュータが生成する「乱数」は、実際には決定的なアルゴリズムで計算された**擬似乱数**である。代表的なアルゴリズムにメルセンヌ・ツイスタ[7](https://doi.org/10.1145/272991.272995)やPCGがある。擬似乱数生成器（PRNG: Pseudorandom Number Generator）は、初期値（**シード**）が同じなら常に同じ数列を生成する。

この性質を利用して、ランダムな処理を含む解析でも**結果を完全に再現**できる。

### シード固定の実践

NumPyでは `np.random.default_rng(seed)` でシードを固定する[8](https://numpy.org/doc/stable/reference/random/generator.html):

```python
import numpy as np

# シード固定: 何度実行しても同じ結果
rng = np.random.default_rng(42)
sample = rng.choice(100, size=10, replace=False)
print(sample)  # 常に同じ10個の数値

# 別のシード: 異なる結果
rng2 = np.random.default_rng(123)
sample2 = rng2.choice(100, size=10, replace=False)
print(sample2)  # 上とは異なる10個の数値
```

**重要**: 古いコードでは `np.random.seed(42)` というグローバルなシード固定を見かけるが、これは非推奨である。`default_rng()` を使い、関数ごとに独立した乱数生成器を渡す設計が現在のベストプラクティスである。

```python
# 非推奨: グローバルなシード固定
np.random.seed(42)
result = np.random.choice(100, 10)  # グローバル状態に依存

# 推奨: 関数ごとに独立したRNGを渡す
def subsample(data: np.ndarray, n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(data), size=n, replace=False)
    return data[indices]
```

### 論文にシード値を記録する

再現性は科学の基本である[9](https://doi.org/10.1371/journal.pbio.1001745)。ランダムな処理を含む解析では:

1. 使用したシード値をメソッドセクションに明記する
2. スクリプト内でシード値を変数として定義する（ハードコードされたマジックナンバーにしない）
3. 可能であれば、異なるシードで結果の頑健性を確認する

```python
# 設定として明示する
RANDOM_SEED = 42

rng = np.random.default_rng(RANDOM_SEED)
```

> **🧬 コラム: バイオインフォでの乱数再現性**
>
> - **t-SNE / UMAP**: 次元削減の結果が毎回変わるのは、内部で乱数を使っているため。`random_state` パラメータにシードを渡せば固定できる[10](https://doi.org/10.48550/arXiv.1802.03426)[11](https://jmlr.org/papers/v9/vandermaaten08a.html)。
>   ```python
>   from sklearn.manifold import TSNE
>   embedding = TSNE(random_state=42).fit_transform(data)
>   ```
> - **GPU（cuDNN）の非決定的演算**: GPUでは演算順序が実行ごとに変わりうるため、シードを固定しても完全な再現性が得られないことがある。PyTorchでは `torch.use_deterministic_algorithms(True)` で強制できるが、性能が低下する場合がある。
> - **ブートストラップ法・クロスバリデーション**: リサンプリングを含む統計手法では、シード記録が必須。記録がなければ、レビュアーも著者自身も結果を再現できない。

> **コラム: なぜ42なのか**
>
> サンプルコードや機械学習のチュートリアルで `random_state=42` という記述を頻繁に見かける。この「42」の出典は、Douglas Adamsの小説『銀河ヒッチハイク・ガイド』（*The Hitchhiker's Guide to the Galaxy*）である[12](https://en.wikipedia.org/wiki/The_Hitchhiker%27s_Guide_to_the_Galaxy)。作中で、超高性能コンピュータが「生命、宇宙、そして万物についての究極の疑問の答え」として750万年の計算の末に出した答えが「42」だった。
>
> scikit-learnの公式ドキュメントやチュートリアルで `random_state=42` が慣例的に使われ、それがコミュニティ全体に広まった。しかし、42自体に数学的・統計的な意味はなく、シード値としてはどの整数を選んでも構わない。重要なのは**シードを固定すること自体**であり、値の選択ではない。

---

## 3-5. 計算機アーキテクチャの基礎

### メモリ階層

コンピュータのメモリには速度とコストのトレードオフがある:

| レベル | 種類 | 容量（典型） | アクセス時間 |
|-------|------|------------|------------|
| L1キャッシュ | CPU内蔵 | 64 KB | ~1 ns |
| L2/L3キャッシュ | CPU内蔵 | 数 MB〜数十 MB | ~10 ns |
| RAM（メインメモリ） | DRAM | 16〜512 GB | ~100 ns |
| SSD | フラッシュストレージ | 1〜4 TB | ~100 µs |
| HDD | 磁気ディスク | 数 TB〜 | ~10 ms |

プログラムが扱うデータがRAMに収まるかどうかは、バイオインフォマティクスで最初に確認すべきポイントである。シングルセルRNA-seqの発現量行列（数万遺伝子 × 数十万細胞）や全ゲノムシーケンスのBAMファイルは、数十GBに達することがある。

### 行優先（C order）vs 列優先（Fortran order）

NumPy配列のメモリレイアウトは、処理速度に直結する:

```python
import numpy as np

# 行優先（C order）: 行方向に連続してメモリに格納
c_array = np.zeros((10000, 10000), order="C")

# 列優先（Fortran order）: 列方向に連続してメモリに格納
f_array = np.zeros((10000, 10000), order="F")
```

NumPyはデフォルトでC order（行優先）である。**行方向の走査**はメモリ上で連続したアクセスとなるため高速だが、列方向の走査はメモリ上で飛び飛びのアクセスとなり遅くなる。発現量行列を遺伝子（行）ごとに処理するか、サンプル（列）ごとに処理するかで、メモリレイアウトの選択が性能に影響する。

### CPU vs GPU

- **CPU**: 汎用的な処理。コア数は少ないが、1コアあたりの性能が高い。
- **GPU**: 並列処理に特化。数千のコアで同じ演算を一斉に実行できるが、VRAM（GPU専用メモリ）の容量が制約になる。

バイオインフォマティクスでは、深層学習（AlphaFold等のタンパク質構造予測）やシングルセル解析（scVIなどのVAEモデル）でGPUが活用される。GPUを使う際は:

- モデルとデータがVRAMに収まるかを事前に確認する
- float32で十分な場面ではfloat32を使い、VRAM使用量を半減させる
- CPU ↔ GPU間のデータ転送がボトルネックにならないよう注意する

### I/Oバウンド vs コンピュートバウンド

プログラムのボトルネックは、大きく2種類に分けられる:

- **I/Oバウンド**: ファイル読み書きやネットワーク通信が律速。FASTQファイルの読み込み、データベースへのクエリなど。
- **コンピュートバウンド**: 計算そのものが律速。配列アラインメント、行列演算など。

ボトルネックの種類によって最適化の方向が異なる。I/Oバウンドなら並列読み込みや圧縮フォーマットの活用が有効で、コンピュートバウンドなら並列計算やGPU活用が有効である。[§15 パフォーマンスと最適化](./15_performance.md)でプロファイリングの方法を詳しく学ぶ。

### ネットワークファイルシステム

HPCクラスタでは、NFS（Network File System）やLustre等の分散ファイルシステムが使われる。これらはローカルSSDとは性質が大きく異なる:

- 小さなファイルの大量読み書きが極端に遅い（メタデータ操作のオーバーヘッド）
- 大きなファイルの連続読み書きは比較的高速
- 多数のジョブが同時にアクセスすると性能が劇的に低下する

対策として、一時ファイルはノードローカルの `/tmp` や `$TMPDIR` に書き出し、最終結果だけを共有ファイルシステムにコピーする、という運用が一般的である。詳細は[§14 HPC](./14_hpc.md)で扱う。

> **🧬 コラム: inode枯渇 — ディスク容量はあるのにファイルが作れない**
>
> ファイルシステムは、ファイルごとに**inode**と呼ばれるメタデータ（所有者、パーミッション、タイムスタンプ、データブロックの位置など）を管理している。inodeの総数にはファイルシステムごとに上限があり、ディスク容量に空きがあっても、inodeが枯渇するとファイルを新規作成できなくなる。
>
> バイオインフォマティクスでの典型的な事故パターン:
>
> - 遺伝子ごと・タンパク質ごとに1ファイルを生成する処理で、数万〜数十万のファイルが作られる
> - BLASTの結果を配列ごとに個別ファイルに出力する
> - 一時ファイルを大量に作るパイプラインが後片付けせずに終了する
>
> `df -i` コマンドでinode使用状況を確認できる:
>
> ```bash
> df -i /home    # IUsed, IFree, IUse% を確認
> ```
>
> 対策:
>
> - 大量の小ファイルを生成する代わりに、1ファイルにまとめる（TSV, HDF5等）
> - ディレクトリを分割して管理する（1ディレクトリに数十万ファイルを入れない）
> - 一時ファイルは処理後に確実に削除する
>
> 現代のファイルシステム（ext4, XFS）ではinode数がかなり余裕を持って設定されているため、個人の環境では問題になりにくい。しかし、HPCの共有ファイルシステムでは多数のユーザーがinodeを消費するため、依然として注意が必要である。

---

## まとめ

本章で学んだ計算機科学の基礎知識を一覧にまとめる:

| トピック | 要点 | 典型的な罠 |
|---------|------|----------|
| データ構造 | 検索には set/dict($O(1)$)を使う | listの `in` で10万件検索 → 遅い |
| 浮動小数点 | `==` ではなく `math.isclose()` で比較 | TPM値が「一致しない」 |
| 丸め誤差 | `math.fsum()` で高精度に合計 | sum()で0.1を10回足すと1.0にならない |
| CSV round-trip | 中間データはバイナリ形式で保存 | CSV出力→読込の繰返しで精度劣化 |
| NaN | `math.isnan()` で判定する | `NaN == NaN` は `False` |
| 文字エンコーディング | UTF-8を明示、改行コードに注意 | Windows由来ファイルの `\r` 混入 |
| 乱数 | `default_rng(seed)` でシード固定 | UMAPの結果が毎回変わる |
| メモリレイアウト | C order（行優先）がNumPyのデフォルト | 列方向の走査が遅い |
| I/O vs 計算 | ボトルネックの種類で最適化を変える | I/Oバウンドなのに計算を最適化 |

これらの知識は、[§4 データフォーマットの判断力](./04_data_formats.md)以降のすべての章で前提となる。とくに浮動小数点の扱いと乱数の再現性は、解析結果の正しさに直結するので、ぜひ手を動かして本章のコードサンプルを実行してほしい。

---

## 参考文献

[1] Python Software Foundation. "Data Structures". *Python 3 Documentation*. [https://docs.python.org/3/tutorial/datastructures.html](https://docs.python.org/3/tutorial/datastructures.html) (参照日: 2026-03-18)

[2] Cormen, T. H., Leiserson, C. E., Rivest, R. L., Stein, C. *Introduction to Algorithms* (4th ed.). MIT Press, 2022. [https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)

[3] Goldberg, D. "What Every Computer Scientist Should Know About Floating-Point Arithmetic". *ACM Computing Surveys*, 23(1), 5–48, 1991. [https://doi.org/10.1145/103162.103163](https://doi.org/10.1145/103162.103163)

[4] Python Software Foundation. "math.fsum". *Python 3 Documentation*. [https://docs.python.org/3/library/math.html#math.fsum](https://docs.python.org/3/library/math.html#math.fsum) (参照日: 2026-03-18)

[5] Python Software Foundation. "math.isclose". *Python 3 Documentation*. [https://docs.python.org/3/library/math.html#math.isclose](https://docs.python.org/3/library/math.html#math.isclose) (参照日: 2026-03-18)

[6] The Unicode Consortium. *The Unicode Standard, Version 16.0*. 2024. [https://www.unicode.org/versions/Unicode16.0.0/](https://www.unicode.org/versions/Unicode16.0.0/) (参照日: 2026-03-18)

[7] Matsumoto, M., Nishimura, T. "Mersenne Twister: A 623-Dimensionally Equidistributed Uniform Pseudo-Random Number Generator". *ACM Transactions on Modeling and Computer Simulation*, 8(1), 3–30, 1998. [https://doi.org/10.1145/272991.272995](https://doi.org/10.1145/272991.272995)

[8] NumPy Developers. "Random Generator". *NumPy Documentation*. [https://numpy.org/doc/stable/reference/random/generator.html](https://numpy.org/doc/stable/reference/random/generator.html) (参照日: 2026-03-18)

[9] Wilson, G. et al. "Best Practices for Scientific Computing". *PLOS Biology*, 12(1), e1001745, 2014. [https://doi.org/10.1371/journal.pbio.1001745](https://doi.org/10.1371/journal.pbio.1001745)

[10] McInnes, L., Healy, J., Melville, J. "UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction". 2018. [https://doi.org/10.48550/arXiv.1802.03426](https://doi.org/10.48550/arXiv.1802.03426)

[11] van der Maaten, L., Hinton, G. "Visualizing Data using t-SNE". *Journal of Machine Learning Research*, 9, 2579–2605, 2008. [https://jmlr.org/papers/v9/vandermaaten08a.html](https://jmlr.org/papers/v9/vandermaaten08a.html)

[12] Adams, D. *The Hitchhiker's Guide to the Galaxy*. Pan Books, 1979. [https://en.wikipedia.org/wiki/The_Hitchhiker%27s_Guide_to_the_Galaxy](https://en.wikipedia.org/wiki/The_Hitchhiker%27s_Guide_to_the_Galaxy)

[13] Altschul, S. F. et al. "Basic local alignment search tool". *J. Mol. Biol.*, 215(3), 403–410, 1990. [https://doi.org/10.1016/S0022-2836(05)80360-2](https://doi.org/10.1016/S0022-2836(05)80360-2)

[14] Smith, T. F., Waterman, M. S. "Identification of common molecular subsequences". *J. Mol. Biol.*, 147(1), 195–197, 1981. [https://doi.org/10.1016/0022-2836(81)90087-5](https://doi.org/10.1016/0022-2836(81)90087-5)

[15] Li, H., Durbin, R. "Fast and accurate short read alignment with Burrows-Wheeler transform". *Bioinformatics*, 25(14), 1754–1760, 2009. [https://doi.org/10.1093/bioinformatics/btp324](https://doi.org/10.1093/bioinformatics/btp324)

[16] Saitou, N., Nei, M. "The neighbor-joining method: a new method for reconstructing phylogenetic trees". *Mol. Biol. Evol.*, 4(4), 406–425, 1987. [https://doi.org/10.1093/oxfordjournals.molbev.a040454](https://doi.org/10.1093/oxfordjournals.molbev.a040454)
