# 外部実行環境skip監査

## 目的

通常の `pytest` でskipされる10件について、単なる依存漏れか、意図的な任意統合テストかを判定する。Apple Silicon搭載MacBook Proで各実行環境を一時的に用意し、実資産を使ったテストが成功すること、通常の開発依存へ含める必要がないことを確認する。

## 監査環境

- 実施日: 2026-07-29
- 基準コミット: `a30717779cfbe6811eefcc01fcdf420b474a9dd3`
- ハードウェア: MacBook Pro 17,1、Apple M1、8コア、16 GB
- OS: macOS 26.5.2
- Python: 3.14.6
- R: 4.5.2
- Java: OpenJDK 26.0.1
- Podman: クライアント・Linux VMともに6.0.2、VMは4 CPU・4 GiB

通常環境の基準結果は `1024 passed, 10 skipped` である。

## 判定結果

| 対象 | 件数 | 検証環境 | 実測結果 | 判定 |
|---|---:|---|---|---|
| Snakemake | 1 | Snakemake 9.23.1、Python 3.13隔離環境 | 1 passed、6.56秒 | 任意ランタイムスモーク |
| DESeq2 | 1 | R 4.5.3、DESeq2 1.50.2、Micromamba | 1 passed、19.19秒 | 高コストな任意ランタイムスモーク |
| Nextflow | 1 | Nextflow 26.04.2 standalone、Java 26 | 1 passed、3.77秒 | 任意ランタイムスモーク |
| CWL | 1 | cwltool 3.2.20260720092025、Python 3.13隔離環境 | 1 passed、9.58秒 | 任意ランタイムスモーク |
| Podman | 5 | Linux/arm64 VM、Podman 6.0.2、既存キャッシュあり | 5 passed、11.64秒 | 高コストなコンテナービルド |
| MkDocs | 1 | Material for MkDocs 9.7.7、mkdocstrings Python handler | 1 passed、1.80秒 | 任意ランタイムスモーク |

10件はすべて成功した。したがって、skipの原因はサンプルコードの不具合ではなく、通常のPython開発環境に外部ランタイムを含めていないことである。

## リソース評価

Snakemake、cwltool、MkDocsは`uvx`の隔離環境で実行できる。Nextflowは公式standalone配布物が約40 MiBであり、既存のJava 26で動作した。公式要件はJava 17以上26以下である。

DESeq2環境はApple Silicon向けに依存解決できた。初回ダウンロードは146パッケージ・約299 MB、展開後の環境は約1.2 GBであった。解析対象はリポジトリ内の20遺伝子fixtureだけであり、大規模データのダウンロードは発生しない。

PodmanはmacOS上でLinux VMを必要とする。今回のVMは4 CPU・4 GiB・30 GiBであり、テスト時だけ起動して終了後に停止した。初回はベースイメージやパッケージの取得時間が加わるため、常時CIには含めない。

## 運用方針

- 通常の `uv run pytest` では10件を意図的にskipし、コアテストを軽量かつ再現可能に保つ。
- 10件には `runtime_smoke` マーカーを付け、通常環境への偶然のツール導入だけでは実行しない。
- ワークフローと文書生成の5件は `RUN_EXTERNAL_RUNTIME_TESTS=1` を明示した場合だけ実行する。
- Podmanの5件は従来どおり `RUN_CONTAINER_BUILDS=1` を明示した場合だけ実行し、さらに `container_build` マーカーで選択できる。
- リリース前、ワークフロー資産変更時、固定バージョン更新時に該当スモークテストを再実行する。
- 外部ランタイムを `pyproject.toml` の通常開発依存へ追加しない。隔離環境または一時VMを使う。

## 再現コマンド

### Snakemake

```bash
RUN_EXTERNAL_RUNTIME_TESTS=1 uvx \
  --python 3.13 \
  --from 'snakemake==9.23.1' \
  --with pytest \
  --with pyyaml \
  pytest tests/ch14/test_workflow_assets.py::test_snakemake_dry_run \
  -q -p no:cacheprovider
```

### CWL

```bash
RUN_EXTERNAL_RUNTIME_TESTS=1 uvx \
  --python 3.13 \
  --from 'cwltool==3.2.20260720092025' \
  --with pytest \
  --with pyyaml \
  pytest tests/ch14/test_workflow_assets.py::test_cwl_validate_and_smoke \
  -q -p no:cacheprovider
```

### MkDocs

```bash
RUN_EXTERNAL_RUNTIME_TESTS=1 uvx \
  --python 3.13 \
  --from 'mkdocs-material==9.7.7' \
  --with 'mkdocstrings[python]' \
  --with pytest \
  --with pyyaml \
  pytest tests/ch18/test_mkdocs_example.py::test_mkdocs_build_strict \
  -q -p no:cacheprovider
```

### Nextflow

[公式リリース](https://github.com/nextflow-io/nextflow/releases/tag/v26.04.2)の `nextflow-26.04.2-dist` を使用する。監査時に確認したSHA-256は `52a2ce22be15d747369a70050339443fc325005bea59a49e0ee25d96fae9cc51` である。実行ファイルを `nextflow` という名前でPATHへ配置した後、次を実行する。

```bash
RUN_EXTERNAL_RUNTIME_TESTS=1 \
NXF_OFFLINE=true \
uv run pytest tests/ch14/test_workflow_assets.py::test_nextflow_smoke \
  -q -p no:cacheprovider
```

### DESeq2

`scripts/ch14/envs/deseq2.yaml` から一時環境を作成し、その `Rscript` をPATHの先頭へ置く。

```bash
micromamba create \
  --prefix /private/tmp/ai-biocode-kata-deseq2-env \
  --file scripts/ch14/envs/deseq2.yaml \
  --yes

micromamba run \
  --prefix /private/tmp/ai-biocode-kata-deseq2-env \
  env RUN_EXTERNAL_RUNTIME_TESTS=1 \
  .venv/bin/pytest tests/ch14/test_workflow_assets.py::test_deseq2_smoke \
  -q -p no:cacheprovider
```

### Podman

```bash
podman machine start
RUN_CONTAINER_BUILDS=1 \
uv run pytest -m container_build -q -p no:cacheprovider
podman machine stop
```

## 一次情報

- [Snakemake — PyPI](https://pypi.org/project/snakemake/)
- [cwltool — PyPI](https://pypi.org/project/cwltool/)
- [Nextflow installation](https://docs.seqera.io/nextflow/install)
- [DESeq2 — Bioconductor](https://bioconductor.org/packages/release/bioc/html/DESeq2.html)
- [Material for MkDocs — PyPI](https://pypi.org/project/mkdocs-material/)
- [Podman machine](https://docs.podman.io/en/latest/markdown/podman-machine.1.html)
