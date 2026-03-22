"""エラーハンドリングの例 — カスタム例外とガード節パターン."""

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

    # 本処理
    sequence_ids: list[str] = []
    for record in SeqIO.parse(fasta_path, "fasta"):
        sequence_ids.append(record.id)

    # ガード節: 配列の存在確認
    if len(sequence_ids) == 0:
        raise ValueError(
            f"FASTAファイルに配列が含まれていません: {fasta_path}"
        )

    return sequence_ids
