"""6フレームORF検出 — 標準ライブラリのみで実装."""

from dataclasses import dataclass

# 標準コドンテーブル（NCBI Translation Table 11 — 細菌・古細菌）
CODON_TABLE: dict[str, str] = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}

STOP_CODONS: set[str] = {"TAA", "TAG", "TGA"}


@dataclass(frozen=True)
class ORF:
    """Open Reading Frameを表すデータクラス."""

    start: int   # 開始位置（0-based、元の配列上の座標）
    end: int     # 終了位置（0-based、終止コドンの末端）
    frame: int   # 読み枠（+1, +2, +3: 順鎖、-1, -2, -3: 逆鎖）
    protein: str  # 翻訳後のアミノ酸配列

    @property
    def length_nt(self) -> int:
        """ORFの塩基長."""
        return self.end - self.start

    @property
    def length_aa(self) -> int:
        """翻訳後のアミノ酸数."""
        return len(self.protein)


def reverse_complement(seq: str) -> str:
    """逆相補鎖を返す."""
    comp = {"A": "T", "T": "A", "G": "C", "C": "G", "N": "N"}
    return "".join(comp.get(c, "N") for c in reversed(seq.upper()))


def _translate(seq: str) -> str:
    """DNA配列をタンパク質配列に翻訳する（終止コドンで停止）."""
    protein: list[str] = []
    for i in range(0, len(seq) - 2, 3):
        codon = seq[i : i + 3]
        aa = CODON_TABLE.get(codon, "X")
        if aa == "*":
            break
        protein.append(aa)
    return "".join(protein)


def find_all_orfs(sequence: str, min_length: int = 100) -> list[ORF]:
    """6フレームすべてのORFを検出する.

    Parameters
    ----------
    sequence : str
        DNA配列（A, T, G, Cのみ）
    min_length : int
        最小ORF長（塩基数）。デフォルト100 bp。

    Returns
    -------
    list[ORF]
        検出されたORFのリスト（開始位置でソート）
    """
    if not sequence:
        return []

    seq = sequence.upper()
    genome_len = len(seq)
    orfs: list[ORF] = []

    # 順鎖（+1, +2, +3フレーム）
    for offset in range(3):
        frame = offset + 1
        orfs.extend(_scan_frame(seq, offset, frame, genome_len, min_length))

    # 逆鎖（-1, -2, -3フレーム）
    rc = reverse_complement(seq)
    for offset in range(3):
        frame = -(offset + 1)
        orfs.extend(
            _scan_frame_reverse(rc, offset, frame, genome_len, min_length)
        )

    return sorted(orfs, key=lambda o: o.start)


def _scan_frame(
    seq: str, offset: int, frame: int, genome_len: int, min_length: int
) -> list[ORF]:
    """順鎖の1つの読み枠をスキャンしてORFを検出する."""
    orfs: list[ORF] = []
    pos = offset

    while pos + 3 <= genome_len:
        codon = seq[pos : pos + 3]
        if codon == "ATG":
            end_pos = _find_stop(seq, pos + 3, genome_len)
            if end_pos is not None:
                orf_len = end_pos - pos
                if orf_len >= min_length:
                    protein = _translate(seq[pos:end_pos])
                    orfs.append(ORF(
                        start=pos, end=end_pos,
                        frame=frame, protein=protein,
                    ))
        pos += 3

    return orfs


def _scan_frame_reverse(
    rc_seq: str, offset: int, frame: int, genome_len: int, min_length: int
) -> list[ORF]:
    """逆鎖の1つの読み枠をスキャンしてORFを検出する."""
    orfs: list[ORF] = []
    pos = offset

    while pos + 3 <= genome_len:
        codon = rc_seq[pos : pos + 3]
        if codon == "ATG":
            end_pos = _find_stop(rc_seq, pos + 3, genome_len)
            if end_pos is not None:
                orf_len = end_pos - pos
                if orf_len >= min_length:
                    protein = _translate(rc_seq[pos:end_pos])
                    # 逆鎖の座標を元の配列上に変換
                    orig_start = genome_len - end_pos
                    orig_end = genome_len - pos
                    orfs.append(ORF(
                        start=orig_start, end=orig_end,
                        frame=frame, protein=protein,
                    ))
        pos += 3

    return orfs


def _find_stop(seq: str, start: int, seq_len: int) -> int | None:
    """指定位置から次の終止コドンを探す（同一読み枠内）."""
    pos = start
    while pos + 3 <= seq_len:
        if seq[pos : pos + 3] in STOP_CODONS:
            return pos + 3  # 終止コドンの末端
        pos += 3
    return None
