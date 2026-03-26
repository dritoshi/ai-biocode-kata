"""mylib.utils モジュールの個別テスト."""

from scripts.ch05.mylib.utils import validate_sequence


def test_validate_sequence_accepts_valid_sequence() -> None:
    """妥当な配列は有効と判定される."""
    ok, invalid = validate_sequence("ATGCATGC")
    assert ok is True
    assert invalid == []


def test_validate_sequence_reports_invalid_bases() -> None:
    """不正文字を初出順で返す."""
    ok, invalid = validate_sequence("ATXGCY")
    assert ok is False
    assert invalid == ["X", "Y"]


def test_validate_sequence_deduplicates_invalid_bases() -> None:
    """同じ不正文字は一度だけ報告する."""
    ok, invalid = validate_sequence("AXTXGX")
    assert ok is False
    assert invalid == ["X"]


def test_validate_sequence_preserves_first_seen_order() -> None:
    """不正文字の順序は初出順である."""
    ok, invalid = validate_sequence("ATXGYZGX")
    assert ok is False
    assert invalid == ["X", "Y", "Z"]


def test_validate_sequence_accepts_empty_sequence() -> None:
    """空文字列は有効とみなす."""
    ok, invalid = validate_sequence("")
    assert ok is True
    assert invalid == []


def test_validate_sequence_accepts_lowercase_sequence() -> None:
    """小文字配列も受け付ける."""
    ok, invalid = validate_sequence("atgc")
    assert ok is True
    assert invalid == []
