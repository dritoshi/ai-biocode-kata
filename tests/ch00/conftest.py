"""§0 テスト用共有fixture."""

from pathlib import Path

import pytest

FASTA_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ch00" / "data" / "ecoli_k12_fragment.fasta"


@pytest.fixture()
def genome_sequence() -> str:
    """E. coli K-12 断片のDNA配列を返す."""
    with open(FASTA_PATH) as f:
        lines = f.readlines()
    return "".join(line.strip() for line in lines if not line.startswith(">"))


# E. coli K-12 MG1655 1-20,000 bp 領域の期待値
# アノテーション済み遺伝子: thrA, thrB, thrC, yaaX, yaaA, yaaJ 等
EXPECTED_GENE_COUNT_MIN = 10
EXPECTED_GENE_COUNT_MAX = 25
