"""HMM遺伝子予測のテスト."""

from itertools import product

from scripts.ch00.find_orfs import find_all_orfs
from scripts.ch00.hmm_gene_predict import (
    LOG_INIT,
    LOG_TRANS,
    STATES,
    _log_emit,
    predict_genes,
    viterbi,
)


def _path_score(path: tuple[str, ...], codons: list[str]) -> float:
    """状態列の対数尤度を計算する."""
    score = LOG_INIT[path[0]] + _log_emit(path[0], codons[0])
    for index in range(1, len(path)):
        score += LOG_TRANS[(path[index - 1], path[index])]
        score += _log_emit(path[index], codons[index])
    return score


class TestViterbi:
    """viterbi() のテスト."""

    def test_empty_sequence(self) -> None:
        """空配列では空リストを返す."""
        assert viterbi("") == []

    def test_short_sequence(self) -> None:
        """短い配列でも動作する."""
        # ATGのみ（1コドン）
        path = viterbi("ATG")
        assert len(path) == 1
        assert path[0] in ("C", "N")

    def test_coding_sequence(self) -> None:
        """E. coliのコーディング配列はCが多いはず."""
        # E. coli頻出コドンで構成された配列
        coding_seq = "ATGGCTGAAGATGCGCTGGCGATCAACACCCCG" * 3
        path = viterbi(coding_seq)
        coding_count = sum(1 for s in path if s == "C")
        assert coding_count / len(path) > 0.5

    def test_returns_valid_states(self) -> None:
        """返される状態はCまたはNのみ."""
        path = viterbi("ATGGCTATGCGT")
        assert all(s in ("C", "N") for s in path)

    def test_restores_optimal_path(self) -> None:
        """バックトレースが全経路中の最尤状態列を復元する."""
        codons = ["ATG", "GCT", "TTT", "CCC"]
        predicted = tuple(viterbi("".join(codons)))
        candidates = list(product(STATES, repeat=len(codons)))

        assert _path_score(predicted, codons) == max(
            _path_score(candidate, codons) for candidate in candidates
        )


class TestPredictGenes:
    """predict_genes() のテスト."""

    def test_empty_orfs(self, genome_sequence: str) -> None:
        """ORFリストが空なら空リストを返す."""
        assert predict_genes(genome_sequence, []) == []

    def test_reduces_orf_count(self, genome_sequence: str) -> None:
        """HMM予測でORF数が大幅に削減される."""
        orfs = find_all_orfs(genome_sequence, min_length=100)
        predicted = predict_genes(genome_sequence, orfs)
        assert len(predicted) < len(orfs)
        # 279個 → 19個程度（半分以下にはなるはず）
        assert len(predicted) < len(orfs) * 0.5

    def test_predicted_count_range(self, genome_sequence: str) -> None:
        """予測遺伝子数が妥当な範囲にある."""
        orfs = find_all_orfs(genome_sequence, min_length=100)
        predicted = predict_genes(genome_sequence, orfs)
        # 20 kbp のE. coliゲノムで10〜25個が妥当
        assert 10 <= len(predicted) <= 25

    def test_known_gene_detected(self, genome_sequence: str) -> None:
        """既知のthrA遺伝子が予測結果に含まれる."""
        orfs = find_all_orfs(genome_sequence, min_length=100)
        predicted = predict_genes(genome_sequence, orfs)
        # thrA: frame +1, start ~336, end ~2799
        thra = [
            o for o in predicted
            if o.frame == 1 and o.start <= 340 and o.end >= 2795
        ]
        assert len(thra) >= 1

    def test_sorted_by_start(self, genome_sequence: str) -> None:
        """結果が開始位置でソートされている."""
        orfs = find_all_orfs(genome_sequence, min_length=100)
        predicted = predict_genes(genome_sequence, orfs)
        starts = [o.start for o in predicted]
        assert starts == sorted(starts)
