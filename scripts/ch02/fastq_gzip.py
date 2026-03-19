"""gzip圧縮されたFASTQファイルの処理 — 圧縮・展開のデモ."""

import gzip
from pathlib import Path


def count_reads_in_gzip(file_path: Path) -> int:
    """gzip圧縮されたFASTQファイルのリード数をカウントする.

    FASTQは1リードあたり4行で構成されるため、総行数を4で割る。
    シェルの ``zcat file.fastq.gz | awk 'NR%4==1' | wc -l`` に相当する。

    Parameters
    ----------
    file_path : Path
        .fastq.gz ファイルのパス

    Returns
    -------
    int
        リード数
    """
    line_count = 0
    with gzip.open(file_path, "rt") as f:
        for _line in f:
            line_count += 1
    return line_count // 4


def extract_read_ids(file_path: Path, max_reads: int | None = None) -> list[str]:
    """gzip圧縮されたFASTQファイルからリードIDを抽出する.

    FASTQの1行目（@で始まる行）からIDを取得する。
    シェルの ``zcat file.fastq.gz | awk 'NR%4==1' | head -N`` に相当する。

    Parameters
    ----------
    file_path : Path
        .fastq.gz ファイルのパス
    max_reads : int | None
        取得するリード数の上限。None の場合はすべて取得

    Returns
    -------
    list[str]
        リードIDのリスト（先頭の @ を除去済み）
    """
    ids: list[str] = []
    with gzip.open(file_path, "rt") as f:
        for i, line in enumerate(f):
            if i % 4 == 0:  # FASTQの1行目（IDライン）
                read_id = line.rstrip("\n").lstrip("@").split()[0]
                ids.append(read_id)
                if max_reads is not None and len(ids) >= max_reads:
                    break
    return ids


def head_gzip(file_path: Path, n_lines: int = 10) -> list[str]:
    """gzip圧縮ファイルの先頭N行を読む.

    シェルの ``zcat file.gz | head -N`` に相当する。

    Parameters
    ----------
    file_path : Path
        .gz ファイルのパス
    n_lines : int
        読み取る行数（デフォルト: 10）

    Returns
    -------
    list[str]
        先頭N行のリスト（改行なし）
    """
    lines: list[str] = []
    with gzip.open(file_path, "rt") as f:
        for i, line in enumerate(f):
            if i >= n_lines:
                break
            lines.append(line.rstrip("\n"))
    return lines
