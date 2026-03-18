"""データ構造の検索性能デモのテスト."""

from scripts.ch03.data_structure_bench import (
    benchmark_search,
    build_gene_ids,
    search_in_dict,
    search_in_list,
    search_in_set,
)


class TestBuildGeneIds:
    """build_gene_ids() のテスト."""

    def test_generates_correct_count(self) -> None:
        ids = build_gene_ids(100)
        assert len(ids) == 100

    def test_format(self) -> None:
        ids = build_gene_ids(3)
        assert ids == ["GENE_000000", "GENE_000001", "GENE_000002"]

    def test_empty(self) -> None:
        ids = build_gene_ids(0)
        assert ids == []


class TestSearchInList:
    """search_in_list() のテスト."""

    def test_found(self) -> None:
        gene_list = build_gene_ids(100)
        assert search_in_list(gene_list, "GENE_000050") is True

    def test_not_found(self) -> None:
        gene_list = build_gene_ids(100)
        assert search_in_list(gene_list, "GENE_999999") is False


class TestSearchInSet:
    """search_in_set() のテスト."""

    def test_found(self) -> None:
        gene_set = set(build_gene_ids(100))
        assert search_in_set(gene_set, "GENE_000050") is True

    def test_not_found(self) -> None:
        gene_set = set(build_gene_ids(100))
        assert search_in_set(gene_set, "GENE_999999") is False


class TestSearchInDict:
    """search_in_dict() のテスト."""

    def test_found(self) -> None:
        gene_list = build_gene_ids(100)
        gene_dict = {g: i for i, g in enumerate(gene_list)}
        assert search_in_dict(gene_dict, "GENE_000050") is True

    def test_not_found(self) -> None:
        gene_list = build_gene_ids(100)
        gene_dict = {g: i for i, g in enumerate(gene_list)}
        assert search_in_dict(gene_dict, "GENE_999999") is False


class TestBenchmarkSearch:
    """benchmark_search() のテスト."""

    def test_returns_all_structures(self) -> None:
        results = benchmark_search(n=1000, n_queries=10)
        assert set(results.keys()) == {"list", "set", "dict"}

    def test_times_are_positive(self) -> None:
        results = benchmark_search(n=1000, n_queries=10)
        for time_val in results.values():
            assert time_val > 0.0
