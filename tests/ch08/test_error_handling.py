"""error_handling モジュールのテスト."""

from pathlib import Path

import pytest

from scripts.ch08.error_handling import (
    BiofilterError,
    InvalidSequenceError,
    QualityThresholdError,
    validate_fasta,
)


class TestCustomExceptions:
    """カスタム例外のテスト."""

    def test_invalid_sequence_error_message(self) -> None:
        """InvalidSequenceErrorのエラーメッセージを検証する."""
        err = InvalidSequenceError("ATXGC", 2, "X")
        assert "X" in str(err)
        assert "位置 2" in str(err)
        assert err.position == 2
        assert err.char == "X"

    def test_quality_threshold_error_message(self) -> None:
        """QualityThresholdErrorのエラーメッセージを検証する."""
        err = QualityThresholdError(15.0, 20.0)
        assert "15.0" in str(err)
        assert "20.0" in str(err)

    def test_custom_exceptions_inherit_base(self) -> None:
        """カスタム例外がBiofilterErrorを継承している."""
        assert issubclass(InvalidSequenceError, BiofilterError)
        assert issubclass(QualityThresholdError, BiofilterError)

    def test_biofilter_error_catches_subclasses(self) -> None:
        """BiofilterErrorで派生例外を捕捉できる."""
        with pytest.raises(BiofilterError):
            raise InvalidSequenceError("ATX", 2, "X")

        with pytest.raises(BiofilterError):
            raise QualityThresholdError(10.0, 20.0)


class TestValidateFasta:
    """validate_fasta関数のテスト."""

    def test_file_not_found(self, tmp_path: Path) -> None:
        """存在しないファイルでFileNotFoundErrorが発生する."""
        with pytest.raises(FileNotFoundError, match="見つかりません"):
            validate_fasta(tmp_path / "nonexistent.fasta")

    def test_empty_file(self, tmp_path: Path) -> None:
        """空ファイルでValueErrorが発生する."""
        empty_file = tmp_path / "empty.fasta"
        empty_file.write_text("")
        with pytest.raises(ValueError, match="空です"):
            validate_fasta(empty_file)

    def test_no_sequences(self, tmp_path: Path) -> None:
        """FASTA配列が含まれていないファイルでValueErrorが発生する."""
        bad_file = tmp_path / "bad.fasta"
        bad_file.write_text("this is not a fasta file\n")
        with pytest.raises(ValueError, match="配列が含まれていません"):
            validate_fasta(bad_file)

    def test_valid_fasta(self, tmp_path: Path) -> None:
        """正しいFASTAファイルから配列IDを取得できる."""
        fasta_file = tmp_path / "test.fasta"
        fasta_file.write_text(
            ">seq1 description\nATGCATGC\n"
            ">seq2 another\nGCATGCAT\n"
        )
        ids = validate_fasta(fasta_file)
        assert ids == ["seq1", "seq2"]

    def test_single_sequence(self, tmp_path: Path) -> None:
        """単一配列のFASTAファイルを正しく処理できる."""
        fasta_file = tmp_path / "single.fasta"
        fasta_file.write_text(">only_one\nATGC\n")
        ids = validate_fasta(fasta_file)
        assert ids == ["only_one"]
