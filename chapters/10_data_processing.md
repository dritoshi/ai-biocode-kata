# §10 データ処理ライブラリ

[§9 CLIツールの設計](./09_cli.md)では、コマンドラインの引数設計、stdin/stdout対応、プログレス表示、ロギングを学んだ。CLIはツールの「外側」のインターフェースである。本章では「内側」——ツールの中で実際にデータを処理するライブラリの実践的な使い方を学ぶ。

[§3 計算機科学の基礎知識](./03_cs_basics.md)ではNumPyの数値型の罠（int32オーバーフロー、浮動小数点精度）を、[§4 データフォーマットの判断力](./04_data_formats.md)ではpandasによるtidy data変換（`melt()` / `pivot_table()`）を学んだ。本章ではそれらの知識を前提に、バイオインフォマティクスのデータを**効率的に処理するパターン**を扱う。具体的には、NumPyのベクトル化演算による高速化、pandasとpolarsによるテーブルデータの集計・フィルタリング、そしてSciPyによる統計検定と距離計算である。

---

## 10-1. NumPyによるベクトル化演算

### forループの限界

Pythonのforループは柔軟だが、大量のデータを処理するには遅い。たとえば、数千のDNA配列のGC含量を1つずつ計算するコードを考える:

```python
# forループ版 — 遅い
def gc_contents_loop(sequences: list[str]) -> list[float]:
    results = []
    for seq in sequences:
        gc = (seq.count("G") + seq.count("C")) / len(seq)
        results.append(gc)
    return results
```

これは正しく動くが、配列数が数万〜数十万になると実行時間が問題になる。

### ベクトル化とは何か

**ベクトル化**（vectorization）とは、forループを使わず、配列全体に対する一括演算として処理を記述するテクニックである。NumPyのベクトル化演算が高速な理由は2つある:

1. **C言語レベルのループ**: NumPyの内部はCで実装されており、Pythonのインタプリタオーバーヘッドがない
2. **連続メモリアクセス**: NumPy配列はメモリ上に連続して配置される（[§3-5](./03_cs_basics.md#3-5-メモリとストレージの階層)で学んだC orderのメモリレイアウト）ため、CPUキャッシュを効率的に利用できる

### バイオインフォでの実践: GC含量の一括計算

[§7 テスト・品質管理](./07_testing.md)で作成した `gc_content()` 関数は1配列ずつ処理する設計だった。NumPyを使えば、複数配列をまとめて処理できる:

```python
import numpy as np

def gc_content_vectorized(sequences: list[str]) -> np.ndarray:
    """複数のDNA配列のGC含量をNumPyで一括計算する."""
    results = np.empty(len(sequences), dtype=np.float64)
    for i, seq in enumerate(sequences):
        if not seq:
            results[i] = 0.0
            continue
        # バイト配列に変換してベクトル比較
        arr = np.frombuffer(seq.upper().encode("ascii"), dtype=np.uint8)
        gc_mask = (arr == ord("G")) | (arr == ord("C"))
        results[i] = gc_mask.sum() / len(arr)
    return results
```

ポイントは `np.frombuffer()` で文字列をバイト配列に変換し、`==` 演算子でベクトル比較している点である。各文字をforループで比較する代わりに、配列全体に対する一括比較を行っている。

### ブロードキャスティング

**ブロードキャスティング**（broadcasting）は、異なる形状の配列間で演算を自動的に拡張するNumPyの仕組みである。スカラーと配列、1次元配列と2次元配列の演算を、明示的なループなしに記述できる。

発現量カウントのCPM（Counts Per Million）正規化は、ブロードキャスティングの典型的な応用である:

```python
def normalize_cpm(counts: np.ndarray) -> np.ndarray:
    """発現量カウント行列をCPM正規化する.

    行: 遺伝子、列: サンプル
    """
    col_sums = counts.sum(axis=0)          # 各サンプルの総カウント
    col_sums = np.where(col_sums == 0, 1, col_sums)  # ゼロ除算を防ぐ
    return (counts / col_sums) * 1_000_000  # ブロードキャスティング
```

`counts` が `(20000, 6)` の行列（2万遺伝子 × 6サンプル）のとき、`col_sums` は `(6,)` の1次元配列である。`counts / col_sums` と書くだけで、NumPyが自動的に `col_sums` を各行に適用する。forループで行ごとに割り算を書く必要はない。

### ファンシーインデックスとマスク

NumPyの**ファンシーインデックス**（fancy indexing）を使えば、条件に合う要素だけを効率的に抽出できる。Quality scoreのフィルタリングが典型例である:

```python
def filter_by_quality(scores: np.ndarray, threshold: int = 20) -> np.ndarray:
    """Quality scoreが閾値以上の要素だけを抽出する."""
    mask = scores >= threshold  # ブーリアンマスク
    return scores[mask]         # マスクによる抽出
```

`scores >= threshold` でブーリアン配列（`True` / `False`）が生成され、`scores[mask]` で `True` の位置の要素だけが抽出される。これは `[s for s in scores if s >= threshold]` のリスト内包表記と同じ結果を返すが、大規模データではNumPy版のほうがはるかに高速である。

この手法はSNPデータの抽出（`variants[variants["AF"] > 0.01]`）、発現量のフィルタリング（`genes[genes["baseMean"] > 100]`）など、バイオインフォマティクスのあらゆる場面で使える。

#### エージェントへの指示例

ベクトル化やブロードキャスティングは、エージェントが得意とする最適化パターンである。以下のように具体的に指示すると、適切な実装を得やすい:

> 「この関数はforループで1要素ずつ処理している。NumPyのベクトル化演算に書き換えて高速化してほしい」

> 「発現量カウント行列（行: 遺伝子、列: サンプル）をCPM正規化する関数を書いて。ブロードキャスティングを使い、forループは避けること」

> 「Quality scoreの配列から、閾値20以上の要素だけを抽出する関数を書いて。NumPyのブーリアンマスクを使うこと」

注意点として、エージェントにベクトル化を依頼するときは「入力と出力の形状」を明示するとよい。`(n_genes, n_samples)` のように次元の意味を伝えれば、axis引数の誤りを防げる。

---

## 10-2. pandasとpolarsによるテーブルデータ処理

### pandasの基本操作パターン

pandasはテーブルデータ操作のデファクトスタンダードである。[§4](./04_data_formats.md)では `melt()` と `pivot_table()` によるtidy data変換を学んだが、実際のデータ処理ではさらに多くの操作が必要になる。

DEG（差次的発現遺伝子; Differentially Expressed Gene）解析の結果テーブルを例に、実践的なパターンを見ていく。DESeq2やedgeRが出力する典型的なテーブルは以下のようなカラムを持つ:

| カラム | 意味 |
|--------|------|
| gene | 遺伝子名 |
| baseMean | 全サンプルの平均発現量 |
| log2FoldChange | 発現変化量（対数） |
| pvalue | p値（未補正） |
| padj | 調整済みp値（BH法等で補正済み） |

#### 読み込み: 型とNA値の指定

`pd.read_csv()` はデフォルトで型を推論するが、明示的に指定するほうが安全である:

```python
def load_deg_results(path: Path) -> pd.DataFrame:
    """DEG解析結果を読み込む."""
    sep = "\t" if path.suffix in (".tsv", ".txt") else ","
    return pd.read_csv(
        path,
        sep=sep,
        na_values=["NA", "na", ""],  # R由来のNAを明示的にNaNへ
        dtype={"gene": str},          # 遺伝子名は文字列として保持
    )
```

R由来のデータでは `NA` という文字列が欠損値を表すことが多い。`na_values` で明示しないと、文字列 `"NA"` がそのまま残ってしまう。

#### フィルタリング: `.query()` メソッド

有意遺伝子の抽出には `.query()` が読みやすい:

```python
def filter_significant_genes(
    df: pd.DataFrame,
    padj_threshold: float = 0.05,
    log2fc_threshold: float = 1.0,
) -> pd.DataFrame:
    """有意な差次的発現遺伝子をフィルタリングする."""
    return df.query(
        "padj < @padj_threshold and abs(log2FoldChange) >= @log2fc_threshold"
    ).copy()
```

`.query()` は文字列式でフィルタ条件を記述する。`@` プレフィックスでPython変数を参照でき、`abs()` などの関数も使える。ブーリアンインデックス `df[(df["padj"] < 0.05) & (df["log2FoldChange"].abs() >= 1)]` よりも可読性が高い。

#### 結合: `pd.merge()`

DEG結果に遺伝子アノテーション（GO term、パスウェイ情報など）を結合する操作は頻出する:

```python
def merge_with_metadata(
    deg_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    on: str = "gene",
) -> pd.DataFrame:
    """DEG結果にメタデータを結合する（左結合）."""
    return pd.merge(deg_df, metadata_df, on=on, how="left")
```

`how="left"` を指定すると、DEG結果のすべての行が保持され、メタデータにマッチしない遺伝子は `NaN` になる。`how="inner"`（デフォルト）にすると、マッチしない行が消えてしまうため注意が必要である。

#### 集計: `.groupby().agg()`

カテゴリ別の集計は `.groupby()` と `.agg()` の組み合わせで行う:

```python
def summarize_by_category(
    df: pd.DataFrame,
    category_col: str,
    value_col: str,
) -> pd.DataFrame:
    """カテゴリ別に件数・平均・中央値を集計する."""
    return (
        df.groupby(category_col)[value_col]
        .agg(["count", "mean", "median"])
        .reset_index()
    )
```

たとえば、遺伝子カテゴリ（がん抑制遺伝子、がん遺伝子、ハウスキーピング遺伝子）ごとにlog2FoldChangeの分布を要約できる。

### メソッドチェーン

pandasでは `.pipe()` と `.assign()` を使ったメソッドチェーンにより、中間変数を減らして処理の流れを明確にできる:

```python
result = (
    pd.read_csv("deg_results.csv")
    .pipe(lambda df: df[df["padj"] < 0.05])
    .assign(direction=lambda df: np.where(df["log2FoldChange"] > 0, "up", "down"))
    .groupby("direction")["log2FoldChange"]
    .agg(["count", "mean"])
)
```

この書き方は「読み込み → フィルタ → 列追加 → 集計」という処理の流れがそのまま読める。ただし、チェーンが長くなりすぎると逆にデバッグが難しくなるため、適度な長さに留めるのがよい。

### polars: 大規模データの高速処理

**polars**[5](https://docs.pola.rs/)はRust製のDataFrameライブラリで、pandasと同様のテーブル操作を高速に実行できる。特に数百万行を超える大規模データで威力を発揮する。

polarsの最大の特徴は**lazy evaluation**（遅延評価）である。操作を即座に実行するのではなく、クエリプランを構築してから最適化・実行する:

```python
import polars as pl

# lazy evaluation: scan_csv()で読み込みを遅延
lf = pl.scan_csv("deg_results.csv")

# フィルタと集計を「計画」として記述
result = (
    lf.filter(
        (pl.col("padj") < 0.05)
        & (pl.col("log2FoldChange").abs() >= 1.0)
    )
    .group_by("direction")
    .agg(pl.col("log2FoldChange").mean())
    .collect()  # ここで初めて実行
)
```

`scan_csv()` はファイルをすぐには読み込まず、`.collect()` が呼ばれた時点で必要な列だけを読み込む。これにより、不要な列の読み込みやフィルタ前の全行読み込みを回避できる。

#### pandas→polars 対応表

| 操作 | pandas | polars |
|------|--------|--------|
| CSV読み込み（即時） | `pd.read_csv()` | `pl.read_csv()` |
| CSV読み込み（遅延） | — | `pl.scan_csv()` |
| フィルタ | `df.query("col > 0")` | `lf.filter(pl.col("col") > 0)` |
| 列選択 | `df[["a", "b"]]` | `lf.select("a", "b")` |
| 集計 | `df.groupby("a").agg(...)` | `lf.group_by("a").agg(...)` |
| 列追加 | `df.assign(new=...)` | `lf.with_columns(...)` |
| 実行 | 即時 | `.collect()` |

#### 使い分けの指針

pandasとpolarsのどちらを使うかは、データ規模と要件で判断する:

- **数十万行以下**: pandasで十分。エコシステムが成熟しており、情報量も多い
- **数百万行超**: polarsを検討する。特にメモリ効率とスキャン速度に優れる
- **既存コードベース**: pandasで書かれた既存コードがある場合、無理にpolarsに移行する必要はない

#### エージェントへの指示例

pandasやpolarsの操作をエージェントに依頼するときは、入力テーブルのカラム構造と期待する出力形式を明示するのがコツである:

> 「DEG結果テーブル（カラム: gene, baseMean, log2FoldChange, pvalue, padj）を読み込み、padj < 0.05 かつ |log2FoldChange| > 1 の遺伝子だけをフィルタする関数を書いて。pandasの.query()を使うこと」

> 「DEG結果にGOアノテーション（カラム: gene, GO_term, category）を左結合し、カテゴリ別にlog2FoldChangeの平均を集計する処理を書いて。メソッドチェーンで記述すること」

> 「このpandasのコードをpolarsのlazy APIに書き換えて。scan_csv() → filter() → collect() のパターンで」

---

> ### 🧬 コラム: バイオインフォマティクスのPythonライブラリ
>
> バイオインフォマティクスには、特定のデータ形式や解析タスクに特化したPythonライブラリが数多く存在する。以下はその代表例である:
>
> | ライブラリ | 用途 | 代表的な使い方 |
> |-----------|------|---------------|
> | **Biopython**[8](https://doi.org/10.1093/bioinformatics/btp163) | 配列操作の万能ナイフ | `SeqIO`（FASTA/FASTQ）, `AlignIO`（MSA）, `Blast`（結果パース）, `Entrez`（NCBI API） |
> | **pysam** | SAM/BAM/VCF操作 | htslibのPythonラッパー。大規模NGSデータの高速処理 |
> | **pyBigWig** | BigWigの読み書き | ゲノムシグナルデータの操作 |
> | **scanpy**[9](https://doi.org/10.1186/s13059-017-1382-0) | シングルセル解析 | 前処理→クラスタリング→可視化の一気通貫 |
> | **anndata** | シングルセルデータ構造 | `.X`（発現量行列）, `.obs`（細胞メタデータ）, `.var`（遺伝子メタデータ） |
> | **pyranges** | ゲノム区間演算 | BED的操作をpandas風APIで。区間の交差・結合・差分 |
> | **ETE Toolkit** | 系統樹操作・可視化 | Newick/NHX形式の読み込み、系統樹の装飾・描画・解析 |
>
> 各ライブラリの代表的な1行コード例:
>
> ```python
> # Biopython: FASTAの読み込み
> from Bio import SeqIO
> records = list(SeqIO.parse("sequences.fasta", "fasta"))
>
> # pysam: BAMの読み込みとリージョン抽出
> import pysam
> bam = pysam.AlignmentFile("sample.bam", "rb")
> reads = list(bam.fetch("chr1", 1000, 2000))
>
> # scanpy: シングルセルデータの前処理
> import scanpy as sc
> adata = sc.read_h5ad("pbmc3k.h5ad")
> sc.pp.normalize_total(adata, target_sum=1e4)
>
> # pyranges: ゲノム区間の交差
> import pyranges as pr
> peaks = pr.read_bed("peaks.bed")
> genes = pr.read_bed("genes.bed")
> overlap = peaks.join(genes)
> ```
>
> エージェントに実装を頼む前に、目的のタスクに特化したライブラリが存在しないかを確認しよう。車輪の再発明を避けることは、[§0-9](./00_ai_agent.md#0-9-既存ライブラリの活用)で学んだ重要な原則である。

---

## 10-3. SciPyによる統計処理

### 統計検定の基本パターン

バイオインフォマティクスでは、「2群間に有意な差があるか」を検定する場面が頻出する。SciPy[6](https://doi.org/10.1038/s41592-019-0686-2)は統計検定の豊富な実装を提供する。

#### 2群比較: t検定

処理群とコントロール群の発現量を比較する最も基本的な検定がt検定である:

```python
from scipy import stats

def compare_expression(
    group1: np.ndarray,
    group2: np.ndarray,
) -> tuple[float, float]:
    """2群の発現量をWelchのt検定で比較する."""
    result = stats.ttest_ind(group1, group2, equal_var=False)
    return float(result.statistic), float(result.pvalue)
```

`equal_var=False` を指定すると**Welchのt検定**（等分散を仮定しない）になる。バイオインフォマティクスでは群間の分散が異なることが多いため、Welchのt検定が推奨される。

ノンパラメトリック検定が必要な場合は `scipy.stats.mannwhitneyu()` を使う。正規分布を仮定できないとき（サンプルサイズが小さい、分布が歪んでいるなど）に適用する。

#### 多重検定補正: BH法

数千〜数万の遺伝子を同時に検定する場合、**多重検定補正**（multiple testing correction）が必須である。1万回検定すれば、$p < 0.05$ の偽陽性が約500個出る計算になる。

**Benjamini-Hochberg法**（BH法）はFDR（False Discovery Rate; 偽発見率）を制御する標準的な方法である:

```python
def correct_pvalues(pvalues: np.ndarray) -> np.ndarray:
    """BH法による多重検定補正."""
    n = len(pvalues)
    if n == 0:
        return np.array([], dtype=np.float64)

    sorted_indices = np.argsort(pvalues)
    sorted_pvalues = pvalues[sorted_indices]
    ranks = np.arange(1, n + 1)

    # 補正: p_adj = p * n / rank
    adjusted = sorted_pvalues * n / ranks
    # 単調性を保証（後ろから累積最小値）
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    adjusted = np.clip(adjusted, 0.0, 1.0)

    result = np.empty(n, dtype=np.float64)
    result[sorted_indices] = adjusted
    return result
```

実務ではDESeq2やedgeRがBH補正済みの `padj` を出力するため、自分でBH法を実装する機会は多くない。しかし、複数の統計検定を自分で実行する場合（スクリーニング解析など）には、補正の仕組みを理解しておくことが重要である。

浮動小数点演算によるp値の精度については、[§3-2](./03_cs_basics.md#3-2-浮動小数点数の落とし穴)で学んだ `np.allclose()` の考え方が適用できる。非常に小さなp値（$10^{-300}$ 以下など）ではアンダーフローが発生しうるため、対数p値（`-log10(p)`）で扱うこともある。

### 距離計算と類似度

サンプル間の類似度を定量化するには距離行列を計算する。SciPyの `pdist()` と `squareform()` を使えば、効率的に正方距離行列を得られる:

```python
from scipy.spatial.distance import pdist, squareform

def expression_distance_matrix(matrix: np.ndarray) -> np.ndarray:
    """発現プロファイルの相関距離行列を計算する.

    距離 = 1 - ピアソン相関係数
    """
    distances = pdist(matrix.T, metric="correlation")
    return squareform(distances)
```

`pdist()` は condensed distance matrix（上三角行列を1次元に圧縮した形式）を返し、`squareform()` がそれを正方行列に変換する。この距離行列は、[§11 可視化](./11_visualization.md)で学ぶヒートマップや階層クラスタリングの入力として使う。

`metric` パラメータで距離の種類を変更できる。バイオインフォマティクスでよく使う距離尺度:

| metric | 意味 | 用途 |
|--------|------|------|
| `"correlation"` | 1 - ピアソン相関係数 | 発現プロファイルの類似度 |
| `"euclidean"` | ユークリッド距離 | PCA後の座標間距離 |
| `"cosine"` | 1 - コサイン類似度 | 高次元ベクトルの方向の類似度 |

### 疎行列の扱い

シングルセルRNA-seq（scRNA-seq）の発現量行列は非常に大きく（数万遺伝子 × 数十万細胞）、大部分がゼロである。このような**疎行列**（sparse matrix）を通常のNumPy配列で保持するとメモリが不足する。

SciPyの `scipy.sparse` モジュールは疎行列を効率的に扱うためのフォーマットを提供する:

```python
from scipy.sparse import csr_matrix

# 密行列から疎行列へ変換
dense = np.array([[1, 0, 0], [0, 0, 2], [0, 3, 0]])
sparse = csr_matrix(dense)

# メモリ使用量の比較
print(dense.nbytes)   # 72バイト（全要素分）
print(sparse.data.nbytes + sparse.indices.nbytes + sparse.indptr.nbytes)
# 非ゼロ要素分のみ
```

**CSR**（Compressed Sparse Row）は行方向のスライスが高速で、**CSC**（Compressed Sparse Column）は列方向のスライスが高速である。scRNA-seqデータでは遺伝子（行）方向のアクセスが多いため、CSR形式がよく使われる。🧬コラムで紹介したscanpy/anndataも内部的にCSR/CSC形式の疎行列を使用している。

#### エージェントへの指示例

統計検定や距離計算をエージェントに依頼するときは、データの構造と検定の目的を明確に伝える:

> 「処理群とコントロール群の発現量データ（それぞれNumPy配列）を受け取り、Welchのt検定でp値を返す関数を書いて。scipy.stats.ttest_ind()を使い、equal_var=Falseを指定すること」

> 「p値の配列を受け取り、BH法で多重検定補正を行う関数を書いて。結果は調整済みp値の配列として返すこと。scipy.stats.false_discovery_controlではなく手動実装にして、アルゴリズムの各ステップにコメントを入れること」

> 「発現量行列（行: 遺伝子、列: サンプル）から、サンプル間の相関距離行列を計算する関数を書いて。scipy.spatial.distance.pdist()とsquareform()を使うこと」

---

> ### 🤖 コラム: 機械学習ライブラリ
>
> バイオインフォマティクスと機械学習の融合が進んでおり、配列解析の次のステップとしてMLライブラリの知識が求められる場面が増えている。以下は代表的なライブラリである:
>
> | ライブラリ | 用途 | 代表的な使い方 |
> |-----------|------|---------------|
> | **scikit-learn** | 古典的ML | 分類、クラスタリング、前処理パイプライン、交差検証 |
> | **PyTorch** | 深層学習 | カスタムモデル定義、学習ループ、GPU計算 |
> | **JAX** | 高速数値計算 | 自動微分、JITコンパイル、関数型スタイル |
> | **Hugging Face** | 事前学習モデル | Transformers, Datasets, tokenizers。DNAモデル（DNABERT等）も利用可能 |
> | **Lightning** | 学習ループの定型化 | PyTorch Lightningでボイラープレート削減 |
> | **wandb** | 実験追跡 | 学習曲線、ハイパーパラメータ、モデルチェックポイント |
> | **optuna** | ハイパーパラメータ最適化 | ベイズ最適化ベースの自動チューニング |
>
> 配列解析からMLに踏み出す典型的な3ステップ:
>
> 1. **scikit-learn**で特徴量ベースの古典的MLを試す（まずベースラインを作る）
> 2. **PyTorch**でカスタムモデルを構築する
> 3. **Hugging Face**で事前学習モデルのfine-tuningを行う
>
> 実験管理の詳細は[§13A 実験管理](./appendix_13a_experiment.md)で扱う。

---

## まとめ

本章で学んだデータ処理ライブラリの要素を整理する:

| 概念 | ツール/手法 | 目的 |
|------|-----------|------|
| ベクトル化演算 | NumPy | forループを排除して高速化 |
| ブロードキャスティング | NumPy | 異なる形状の配列間の一括演算 |
| テーブル操作 | pandas | データの読み込み・フィルタ・結合・集計 |
| 遅延評価 | polars（lazy API） | 大規模データのクエリ最適化 |
| 統計検定 | SciPy | t検定、多重検定補正（BH法） |
| 距離計算 | SciPy | サンプル間の類似度定量化 |
| 疎行列 | SciPy sparse | scRNA-seq等の大規模疎データの効率的な保持 |

すべてに共通する原則は、**Pythonレベルのforループを避け、ライブラリのAPIで処理を記述する**ことである。ベクトル化演算、ブロードキャスティング、メソッドチェーン、lazy evaluationはいずれもこの原則の表れである。

次章の[§11 可視化](./11_visualization.md)では、本章で処理したデータを可視化する方法を学ぶ。距離行列のヒートマップ、DEG結果のVolcano plot、発現量分布のバイオリンプロットなど、バイオインフォマティクスで定番の可視化を取り上げる。

---

## 参考文献

[1] Harris, C. R. et al. "Array programming with NumPy". *Nature*, 585(7825), 357–362, 2020. [https://doi.org/10.1038/s41586-020-2649-2](https://doi.org/10.1038/s41586-020-2649-2)

[2] NumPy Developers. "NumPy Documentation". [https://numpy.org/doc/stable/](https://numpy.org/doc/stable/) (参照日: 2026-03-19)

[3] pandas Development Team. "pandas Documentation". [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/) (参照日: 2026-03-19)

[4] McKinney, W. *Python for Data Analysis*. 3rd ed., O'Reilly Media, 2022. ISBN: 978-1098104030

[5] Polars Contributors. "Polars Documentation". [https://docs.pola.rs/](https://docs.pola.rs/) (参照日: 2026-03-19)

[6] Virtanen, P. et al. "SciPy 1.0: Fundamental Algorithms for Scientific Computing in Python". *Nature Methods*, 17(3), 261–272, 2020. [https://doi.org/10.1038/s41592-019-0686-2](https://doi.org/10.1038/s41592-019-0686-2)

[7] SciPy Developers. "SciPy Documentation". [https://docs.scipy.org/doc/scipy/](https://docs.scipy.org/doc/scipy/) (参照日: 2026-03-19)

[8] Cock, P. J. A. et al. "Biopython: freely available Python tools for computational molecular biology and bioinformatics". *Bioinformatics*, 25(11), 1422–1423, 2009. [https://doi.org/10.1093/bioinformatics/btp163](https://doi.org/10.1093/bioinformatics/btp163)

[9] Wolf, F. A. et al. "SCANPY: large-scale single-cell gene expression data analysis". *Genome Biology*, 19(1), 15, 2018. [https://doi.org/10.1186/s13059-017-1382-0](https://doi.org/10.1186/s13059-017-1382-0)
