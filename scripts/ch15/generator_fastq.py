"""ジェネレータによるFASTQフィルタリング — メモリ効率の良いパイプライン処理."""

from collections.abc import Generator
from pathlib import Path

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord


def read_fastq_records(path: Path) -> Generator[SeqRecord, None, None]:
    """FASTQファイルからレコードを1件ずつ読み出すジェネレータ.

    Bio.SeqIO.parse はイテレータを返すが、ここではジェネレータとして
    ラップすることで、フィルタチェーンの入口として使いやすくする。

    Parameters
    ----------
    path : Path
        FASTQファイルのパス（.fastq または .fq）

    Yields
    ------
    SeqRecord
        FASTQのリードレコード（配列、品質スコア、IDを含む）
    """
    yield from SeqIO.parse(path, "fastq")


def filter_by_length(
    records: Generator[SeqRecord, None, None], min_length: int
) -> Generator[SeqRecord, None, None]:
    """配列長でフィルタリングするジェネレータ.

    リスト版と異なり、全レコードをメモリに保持せず1件ずつ処理する。

    Parameters
    ----------
    records : Generator[SeqRecord, None, None]
        SeqRecordのジェネレータ
    min_length : int
        最小配列長（この値以上のレコードのみ通過）

    Yields
    ------
    SeqRecord
        条件を満たすレコード
    """
    for record in records:
        if len(record.seq) >= min_length:
            yield record


def filter_by_quality(
    records: Generator[SeqRecord, None, None], min_avg_quality: float
) -> Generator[SeqRecord, None, None]:
    """平均品質スコアでフィルタリングするジェネレータ.

    FASTQの品質スコア（Phred score）の平均値が閾値以上のレコードのみ通過させる。

    Parameters
    ----------
    records : Generator[SeqRecord, None, None]
        SeqRecordのジェネレータ
    min_avg_quality : float
        最小平均品質スコア（Phred）

    Yields
    ------
    SeqRecord
        条件を満たすレコード
    """
    for record in records:
        qualities = record.letter_annotations["phred_quality"]
        if qualities and sum(qualities) / len(qualities) >= min_avg_quality:
            yield record


def process_pipeline(
    path: Path, min_length: int, min_avg_quality: float
) -> list[SeqRecord]:
    """ジェネレータチェーンでFASTQフィルタリングパイプラインを実行する.

    read → 長さフィルタ → 品質フィルタ の順にジェネレータを連結し、
    メモリ使用量を一定に保ちながら処理する。最終結果のみリスト化する。

    Parameters
    ----------
    path : Path
        FASTQファイルのパス
    min_length : int
        最小配列長
    min_avg_quality : float
        最小平均品質スコア

    Returns
    -------
    list[SeqRecord]
        すべてのフィルタを通過したレコードのリスト
    """
    records = read_fastq_records(path)
    filtered_length = filter_by_length(records, min_length)
    filtered_quality = filter_by_quality(filtered_length, min_avg_quality)
    return list(filtered_quality)
