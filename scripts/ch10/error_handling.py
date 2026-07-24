"""エラーハンドリングの例 — カスタム例外・ガード節・例外連鎖・後始末パターン."""

from io import StringIO
from pathlib import Path

from Bio import SeqIO


class BiofilterError(Exception):
    """biofilterパッケージの基底例外."""


class InvalidSequenceError(BiofilterError):
    """不正な塩基配列が検出された場合の例外."""

    def __init__(self, sequence: str, position: int, char: str) -> None:
        self.sequence = sequence
        self.position = position
        self.char = char
        super().__init__(
            f"不正な塩基文字 '{char}' が位置 {position} で検出されました。"
            f"許容される文字: A, T, G, C, N"
        )


class QualityThresholdError(BiofilterError):
    """品質スコアが閾値を下回った場合の例外."""

    def __init__(self, score: float, threshold: float) -> None:
        self.score = score
        self.threshold = threshold
        super().__init__(
            f"品質スコア {score:.1f} が閾値 {threshold:.1f} を下回っています"
        )


def _load_effective_fasta_text(fasta_path: Path) -> str | None:
    """先頭の空行を除いた FASTA テキストを返す."""
    lines = fasta_path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.strip() == "":
            continue
        if not line.lstrip().startswith(">"):
            return None
        return "\n".join(lines[index:]) + "\n"
    return None


def validate_fasta(fasta_path: Path) -> list[str]:
    """FASTAファイルを検証し、配列IDのリストを返す.

    Parameters
    ----------
    fasta_path : Path
        検証対象のFASTAファイルのパス

    Returns
    -------
    list[str]
        配列IDのリスト

    Raises
    ------
    FileNotFoundError
        ファイルが存在しない場合
    ValueError
        ファイルが空、または配列が含まれていない場合
    """
    # ガード節: ファイルの存在確認
    if not fasta_path.exists():
        raise FileNotFoundError(
            f"FASTAファイルが見つかりません: {fasta_path}"
        )

    # ガード節: ファイルサイズの確認
    if fasta_path.stat().st_size == 0:
        raise ValueError(f"FASTAファイルが空です: {fasta_path}")

    # Biopython の deprecated なコメント解釈に依存しないよう、
    # 先頭の実質行が FASTA ヘッダであることを先に確認する。
    fasta_text = _load_effective_fasta_text(fasta_path)
    if fasta_text is None:
        raise ValueError(
            f"FASTAファイルに配列が含まれていません: {fasta_path}"
        )

    # 本処理
    sequence_ids: list[str] = []
    for record in SeqIO.parse(StringIO(fasta_text), "fasta"):
        sequence_ids.append(record.id)

    # ガード節: 配列の存在確認
    if len(sequence_ids) == 0:
        raise ValueError(
            f"FASTAファイルに配列が含まれていません: {fasta_path}"
        )

    return sequence_ids


def load_min_quality(config: dict[str, str]) -> float:
    """設定から最低品質スコアを読み込む.

    値を数値に変換できない場合は、元の ValueError を連鎖させて
    パッケージ固有の BiofilterError を送出する（例外の連鎖）。

    Parameters
    ----------
    config : dict[str, str]
        設定辞書。キー "min_quality" に閾値の文字列を持つ

    Returns
    -------
    float
        最低品質スコア

    Raises
    ------
    BiofilterError
        min_quality の値が数値に変換できない場合
    """
    raw = config["min_quality"]
    try:
        return float(raw)
    except ValueError as exc:
        # 元の例外 exc を原因として連鎖させる（"from exc"）
        raise BiofilterError(
            f"設定 min_quality の値 '{raw}' を数値に変換できません。"
            f"20 のような数値を指定してください"
        ) from exc


def count_records_with_cleanup(records: list[str], work_dir: Path) -> int:
    """一時ファイルを作り、処理後に必ず後始末する.

    処理の途中で例外が発生しても、finally 節によって一時ファイルの
    削除を保証する（後始末の保証）。

    Parameters
    ----------
    records : list[str]
        処理対象のレコード
    work_dir : Path
        一時ファイルを置く作業ディレクトリ

    Returns
    -------
    int
        レコード件数

    Raises
    ------
    ValueError
        records が空の場合
    """
    marker = work_dir / "processing.lock"
    marker.write_text("running", encoding="utf-8")
    try:
        if not records:
            raise ValueError("処理対象のレコードが空です")
        return len(records)
    finally:
        # 成功・失敗にかかわらず必ず後始末する
        marker.unlink(missing_ok=True)
