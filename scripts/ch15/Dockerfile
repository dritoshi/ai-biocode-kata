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
