"""analysis_intake モジュールのテスト.

解析タイプ別チェックリスト生成とメタデータ検証を検証する。
"""

from scripts.ch20.analysis_intake import (
    get_intake_checklist,
    validate_metadata,
)


# --- get_intake_checklist ---


class TestGetIntakeChecklist:
    """チェックリスト生成のテスト."""

    def test_get_intake_checklist_rna_seq(self) -> None:
        """RNA-seq用チェックリストにリファレンスゲノム、リプリケートなどが含まれること."""
        result = get_intake_checklist("rna-seq")
        assert "rna-seq" in result
        assert "リファレンスゲノム" in result
        assert "リプリケート" in result
        assert "- [ ]" in result

    def test_get_intake_checklist_chip_seq(self) -> None:
        """ChIP-seq用チェックリストにターゲットタンパク質が含まれること."""
        result = get_intake_checklist("chip-seq")
        assert "chip-seq" in result
        assert "ターゲットタンパク質" in result

    def test_get_intake_checklist_wgs(self) -> None:
        """WGS用チェックリストにバリアントコーラーが含まれること."""
        result = get_intake_checklist("wgs")
        assert "wgs" in result
        assert "バリアントコーラー" in result

    def test_get_intake_checklist_metagenome(self) -> None:
        """メタゲノム用チェックリストに多様性解析が含まれること."""
        result = get_intake_checklist("metagenome")
        assert "metagenome" in result
        assert "多様性解析" in result

    def test_get_intake_checklist_unknown(self) -> None:
        """未知の解析タイプで 'general' にフォールバックすること."""
        result = get_intake_checklist("unknown-analysis")
        assert "general" in result
        assert "解析の目的" in result

    def test_get_intake_checklist_general(self) -> None:
        """general用チェックリストが正しく生成されること."""
        result = get_intake_checklist("general")
        assert "general" in result
        assert "データ形式" in result


# --- validate_metadata ---


class TestValidateMetadata:
    """メタデータ検証のテスト."""

    def test_validate_metadata_valid(self) -> None:
        """正常なメタデータで空リストが返ること."""
        metadata = [
            {"sample_id": "S001", "condition": "control", "replicate": "1"},
            {"sample_id": "S002", "condition": "treated", "replicate": "2"},
        ]
        required = ["sample_id", "condition", "replicate"]
        issues = validate_metadata(metadata, required)
        assert issues == []

    def test_validate_metadata_missing_column(self) -> None:
        """必須カラム不足で指摘が返ること."""
        metadata = [
            {"sample_id": "S001", "condition": "control"},
        ]
        required = ["sample_id", "condition", "replicate"]
        issues = validate_metadata(metadata, required)
        assert len(issues) >= 1
        assert any("replicate" in issue for issue in issues)

    def test_validate_metadata_empty_value(self) -> None:
        """空値で指摘が返ること."""
        metadata = [
            {"sample_id": "S001", "condition": "", "replicate": "1"},
        ]
        required = ["sample_id", "condition", "replicate"]
        issues = validate_metadata(metadata, required)
        assert len(issues) >= 1
        assert any("condition" in issue and "空" in issue for issue in issues)

    def test_validate_metadata_empty_rows(self) -> None:
        """空のメタデータで指摘が返ること."""
        issues = validate_metadata([], ["sample_id"])
        assert len(issues) >= 1
        assert any("空" in issue for issue in issues)

    def test_validate_metadata_multiple_issues(self) -> None:
        """複数行に空値がある場合、すべて検出されること."""
        metadata = [
            {"sample_id": "", "condition": "control"},
            {"sample_id": "S002", "condition": ""},
        ]
        required = ["sample_id", "condition"]
        issues = validate_metadata(metadata, required)
        assert len(issues) == 2
