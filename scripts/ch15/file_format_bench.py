"""CSV vs Parquet のファイル形式比較."""

import time
from pathlib import Path

import pandas as pd


def save_as_csv(df: pd.DataFrame, path: Path) -> None:
    """DataFrameをCSV形式で保存する.

    Parameters
    ----------
    df : pd.DataFrame
        保存するデータ
    path : Path
        出力ファイルパス（.csv）
    """
    df.to_csv(path, index=True)


def save_as_parquet(df: pd.DataFrame, path: Path) -> None:
    """DataFrameをParquet形式で保存する.

    Parquetは列指向のバイナリフォーマットで、圧縮効率が高く
    列選択読み込みが可能。大規模データの保存に適している。

    Parameters
    ----------
    df : pd.DataFrame
        保存するデータ
    path : Path
        出力ファイルパス（.parquet）
    """
    df.to_parquet(path, index=True)


def benchmark_read(path: Path) -> float:
    """ファイルの読み込み時間を計測する.

    拡張子に応じてCSVまたはParquetとして読み込む。

    Parameters
    ----------
    path : Path
        読み込むファイルのパス（.csv または .parquet）

    Returns
    -------
    float
        読み込みにかかった時間（秒）
    """
    start = time.perf_counter()
    if path.suffix == ".csv":
        pd.read_csv(path, index_col=0)
    elif path.suffix == ".parquet":
        pd.read_parquet(path)
    else:
        raise ValueError(f"未対応のファイル形式: {path.suffix}")
    elapsed = time.perf_counter() - start
    return elapsed


def compare_formats(
    df: pd.DataFrame, dir_path: Path
) -> dict[str, dict[str, float]]:
    """CSVとParquetの保存・読み込みを比較する.

    同じDataFrameを両形式で保存し、ファイルサイズと読み込み時間を比較する。

    Parameters
    ----------
    df : pd.DataFrame
        比較に使用するデータ
    dir_path : Path
        ファイルを保存するディレクトリ

    Returns
    -------
    dict[str, dict[str, float]]
        各形式の "size_bytes"（ファイルサイズ）と "read_time"（読み込み時間）
    """
    csv_path = dir_path / "data.csv"
    parquet_path = dir_path / "data.parquet"

    save_as_csv(df, csv_path)
    save_as_parquet(df, parquet_path)

    return {
        "csv": {
            "size_bytes": csv_path.stat().st_size,
            "read_time": benchmark_read(csv_path),
        },
        "parquet": {
            "size_bytes": parquet_path.stat().st_size,
            "read_time": benchmark_read(parquet_path),
        },
    }
