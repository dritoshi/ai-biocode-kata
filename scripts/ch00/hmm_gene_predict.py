"""HMM遺伝子予測 — Viterbiアルゴリズムによるコーディング領域の同定."""

import math

from scripts.ch00.find_orfs import ORF, reverse_complement

# E. coli K-12のコドン使用頻度（コーディング領域）
# 出典: Kazusa Codon Usage Database (https://www.kazusa.or.jp/codon/)
CODING_CODON_FREQ: dict[str, float] = {
    "TTT": 0.0218, "TTC": 0.0169, "TTA": 0.0133, "TTG": 0.0133,
    "CTT": 0.0108, "CTC": 0.0110, "CTA": 0.0038, "CTG": 0.0530,
    "ATT": 0.0299, "ATC": 0.0254, "ATA": 0.0044, "ATG": 0.0274,
    "GTT": 0.0183, "GTC": 0.0153, "GTA": 0.0108, "GTG": 0.0261,
    "TCT": 0.0084, "TCC": 0.0087, "TCA": 0.0069, "TCG": 0.0089,
    "CCT": 0.0069, "CCC": 0.0054, "CCA": 0.0083, "CCG": 0.0232,
    "ACT": 0.0088, "ACC": 0.0230, "ACA": 0.0069, "ACG": 0.0141,
    "GCT": 0.0150, "GCC": 0.0256, "GCA": 0.0198, "GCG": 0.0335,
    "TAT": 0.0160, "TAC": 0.0124, "TAA": 0.0020, "TAG": 0.0003,
    "CAT": 0.0128, "CAC": 0.0098, "CAA": 0.0150, "CAG": 0.0291,
    "AAT": 0.0174, "AAC": 0.0218, "AAA": 0.0334, "AAG": 0.0101,
    "GAT": 0.0318, "GAC": 0.0192, "GAA": 0.0396, "GAG": 0.0177,
    "TGT": 0.0050, "TGC": 0.0065, "TGA": 0.0010, "TGG": 0.0152,
    "CGT": 0.0209, "CGC": 0.0223, "CGA": 0.0035, "CGG": 0.0054,
    "AGT": 0.0087, "AGC": 0.0161, "AGA": 0.0020, "AGG": 0.0012,
    "GGT": 0.0248, "GGC": 0.0293, "GGA": 0.0079, "GGG": 0.0109,
}

# 非コーディング領域のコドン出力確率（ほぼ均一）
NON_CODING_CODON_FREQ: dict[str, float] = {
    codon: 1.0 / 64.0 for codon in CODING_CODON_FREQ
}

# HMMの遷移確率（対数）
LOG_TRANS: dict[tuple[str, str], float] = {
    ("C", "C"): math.log(0.997),  # コーディング→コーディング
    ("C", "N"): math.log(0.003),  # コーディング→非コーディング
    ("N", "N"): math.log(0.98),   # 非コーディング→非コーディング
    ("N", "C"): math.log(0.02),   # 非コーディング→コーディング
}

# 初期状態確率（対数）
LOG_INIT: dict[str, float] = {
    "C": math.log(0.5),
    "N": math.log(0.5),
}

STATES: list[str] = ["C", "N"]


def _log_emit(state: str, codon: str) -> float:
    """状態とコドンから出力確率の対数を返す."""
    if state == "C":
        freq = CODING_CODON_FREQ.get(codon, 1e-6)
    else:
        freq = NON_CODING_CODON_FREQ.get(codon, 1e-6)
    return math.log(max(freq, 1e-10))


def viterbi(sequence: str) -> list[str]:
    """2状態HMMのViterbiアルゴリズムでコーディング領域を予測する.

    Parameters
    ----------
    sequence : str
        DNA配列

    Returns
    -------
    list[str]
        各コドン位置の状態ラベル（'C': コーディング、'N': 非コーディング）
    """
    seq = sequence.upper()
    n_codons = len(seq) // 3
    if n_codons == 0:
        return []

    codons = [seq[i * 3 : (i + 1) * 3] for i in range(n_codons)]

    # Viterbiテーブル
    v: list[dict[str, float]] = []
    backpointer: list[dict[str, str]] = []

    # 初期化
    first_emit = {s: _log_emit(s, codons[0]) for s in STATES}
    v.append({s: LOG_INIT[s] + first_emit[s] for s in STATES})
    backpointer.append({s: "" for s in STATES})

    # 再帰
    for t in range(1, n_codons):
        vt: dict[str, float] = {}
        bpt: dict[str, str] = {}
        for s in STATES:
            emit = _log_emit(s, codons[t])
            best_score = -math.inf
            best_prev = STATES[0]
            for prev_s in STATES:
                score = v[t - 1][prev_s] + LOG_TRANS[(prev_s, s)] + emit
                if score > best_score:
                    best_score = score
                    best_prev = prev_s
            vt[s] = best_score
            bpt[s] = best_prev
        v.append(vt)
        backpointer.append(bpt)

    # バックトレース
    path: list[str] = [""] * n_codons
    last_state = max(STATES, key=lambda s: v[-1][s])
    path[-1] = last_state
    for t in range(n_codons - 2, -1, -1):
        path[t] = backpointer[t + 1][path[t + 1]]

    return path


def predict_genes(sequence: str, orfs: list[ORF]) -> list[ORF]:
    """ORFをHMMでスコアリングし、遺伝子候補を返す.

    Parameters
    ----------
    sequence : str
        ゲノム全体のDNA配列
    orfs : list[ORF]
        find_all_orfs()で検出されたORFリスト

    Returns
    -------
    list[ORF]
        HMMによってコーディング領域と予測されたORF
    """
    if not orfs:
        return []

    seq = sequence.upper()
    scored: list[ORF] = []

    for orf in orfs:
        # ORFのDNA配列を取り出す
        orf_seq = seq[orf.start : orf.end]
        if orf.frame < 0:
            orf_seq = reverse_complement(orf_seq)

        # Viterbiでコーディング領域を予測
        path = viterbi(orf_seq)
        if not path:
            continue

        # コーディング状態の割合を計算
        coding_ratio = sum(1 for s in path if s == "C") / len(path)

        # 80%以上がコーディングと予測されたら遺伝子候補
        if coding_ratio >= 0.8:
            scored.append(orf)

    # 重複ORFを除去（各領域で最長のものだけを残す）
    return _remove_overlapping(scored)


def _remove_overlapping(orfs: list[ORF]) -> list[ORF]:
    """重複するORFを除去し、各領域で最長のものだけを残す."""
    if not orfs:
        return []

    # 長さの降順にソート（長いORFを優先的に残す）
    sorted_orfs = sorted(orfs, key=lambda o: o.length_nt, reverse=True)
    kept: list[ORF] = []

    for orf in sorted_orfs:
        overlapping = False
        for kept_orf in kept:
            # 座標が重複しているか判定
            overlap_start = max(orf.start, kept_orf.start)
            overlap_end = min(orf.end, kept_orf.end)
            overlap = max(0, overlap_end - overlap_start)
            # 短い方の50%以上が重複していたら除外
            if overlap > 0.5 * orf.length_nt:
                overlapping = True
                break
        if not overlapping:
            kept.append(orf)

    return sorted(kept, key=lambda o: o.start)
