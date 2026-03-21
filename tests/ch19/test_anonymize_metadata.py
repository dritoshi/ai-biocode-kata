"""anonymize_metadata モジュールのテスト.

年齢の一般化、地域の一般化、k-匿名性判定ロジックを検証する。
"""

import pytest

from scripts.ch19.anonymize_metadata import (
    KAnonymityResult,
    anonymize_csv,
    anonymize_record,
    check_k_anonymity,
    generalize_age,
    generalize_region,
)

# --- テスト用データ ---

SAMPLE_CSV = """\
sample_id,name,age,region,diagnosis
S001,田中太郎,35,東京都,TypeA
S002,鈴木花子,38,神奈川県,TypeA
S003,佐藤一郎,42,東京都,TypeB
S004,高橋美咲,45,千葉県,TypeA
S005,伊藤健太,33,東京都,TypeB
S006,渡辺由美,37,埼玉県,TypeA
S007,山本大輔,41,神奈川県,TypeB
S008,中村悠子,36,東京都,TypeA
S009,小林正樹,44,千葉県,TypeB
S010,加藤裕子,39,埼玉県,TypeA
"""

REGION_MAPPING = {
    "東京都": "関東",
    "神奈川県": "関東",
    "千葉県": "関東",
    "埼玉県": "関東",
    "大阪府": "関西",
    "京都府": "関西",
}


# --- generalize_age ---

class TestGeneralizeAge:
    """年齢の一般化テスト."""

    def test_age_30s(self) -> None:
        """30代は '30-39'."""
        assert generalize_age(35) == "30-39"

    def test_age_boundary_lower(self) -> None:
        """ビン下限ちょうど."""
        assert generalize_age(30) == "30-39"

    def test_age_boundary_upper(self) -> None:
        """ビン上限ちょうど."""
        assert generalize_age(39) == "30-39"

    def test_age_0(self) -> None:
        """0歳は '0-9'."""
        assert generalize_age(0) == "0-9"

    def test_age_100(self) -> None:
        """100歳は '100-109'."""
        assert generalize_age(100) == "100-109"

    def test_custom_bin_size(self) -> None:
        """カスタムビンサイズ."""
        assert generalize_age(35, bin_size=5) == "35-39"
        assert generalize_age(33, bin_size=5) == "30-34"

    def test_negative_age_raises(self) -> None:
        """負の年齢で ValueError."""
        with pytest.raises(ValueError, match="0以上"):
            generalize_age(-1)

    def test_zero_bin_size_raises(self) -> None:
        """ビンサイズ0で ValueError."""
        with pytest.raises(ValueError, match="正の整数"):
            generalize_age(30, bin_size=0)


# --- generalize_region ---

class TestGeneralizeRegion:
    """地域の一般化テスト."""

    def test_known_region(self) -> None:
        """マッピングにある地域は一般化される."""
        assert generalize_region("東京都", REGION_MAPPING) == "関東"

    def test_unknown_region(self) -> None:
        """マッピングにない地域は 'その他'."""
        assert generalize_region("北海道", REGION_MAPPING) == "その他"


# --- anonymize_record ---

class TestAnonymizeRecord:
    """レコード匿名化のテスト."""

    def test_anonymize_with_all_options(self) -> None:
        """全オプション適用."""
        record = {
            "sample_id": "S001",
            "name": "田中太郎",
            "age": "35",
            "region": "東京都",
            "diagnosis": "TypeA",
        }
        result = anonymize_record(
            record,
            drop_columns=["name"],
            region_mapping=REGION_MAPPING,
        )
        assert "name" not in result
        assert result["age"] == "30-39"
        assert result["region"] == "関東"
        assert result["sample_id"] == "S001"
        assert result["diagnosis"] == "TypeA"

    def test_drop_columns(self) -> None:
        """直接識別子の削除."""
        record = {"name": "田中太郎", "age": "35"}
        result = anonymize_record(record, drop_columns=["name"])
        assert "name" not in result

    def test_no_modification_without_options(self) -> None:
        """オプションなしの場合、年齢のみ一般化."""
        record = {"sample_id": "S001", "age": "25"}
        result = anonymize_record(record)
        assert result["age"] == "20-29"
        assert result["sample_id"] == "S001"

    def test_invalid_age_keeps_original(self) -> None:
        """不正な年齢値は変更しない."""
        record = {"age": "unknown"}
        result = anonymize_record(record)
        assert result["age"] == "unknown"


# --- anonymize_csv ---

class TestAnonymizeCsv:
    """CSV全体の匿名化テスト."""

    def test_anonymize_removes_names(self) -> None:
        """氏名カラムが削除される."""
        result = anonymize_csv(
            SAMPLE_CSV,
            drop_columns=["name"],
            region_mapping=REGION_MAPPING,
        )
        assert "田中太郎" not in result
        assert "鈴木花子" not in result
        assert "name" not in result.split("\n")[0]

    def test_anonymize_generalizes_age(self) -> None:
        """年齢が年代に一般化される."""
        result = anonymize_csv(
            SAMPLE_CSV,
            drop_columns=["name"],
            region_mapping=REGION_MAPPING,
        )
        assert "30-39" in result
        assert "40-49" in result
        # 元の具体的な年齢は含まれない
        assert ",35," not in result
        assert ",38," not in result

    def test_anonymize_generalizes_region(self) -> None:
        """地域が上位区分に一般化される."""
        result = anonymize_csv(
            SAMPLE_CSV,
            drop_columns=["name"],
            region_mapping=REGION_MAPPING,
        )
        assert "関東" in result
        assert "東京都" not in result

    def test_empty_csv(self) -> None:
        """空のCSV."""
        result = anonymize_csv("")
        assert result == ""

    def test_output_row_count(self) -> None:
        """出力行数が入力と一致する."""
        result = anonymize_csv(
            SAMPLE_CSV,
            drop_columns=["name"],
            region_mapping=REGION_MAPPING,
        )
        # ヘッダー行 + 10データ行 + 末尾改行
        lines = result.strip().split("\n")
        assert len(lines) == 11  # 1ヘッダー + 10データ


# --- check_k_anonymity ---

class TestCheckKAnonymity:
    """k-匿名性検証のテスト."""

    def test_satisfies_k2(self) -> None:
        """匿名化後のデータが k=2 を満たす."""
        anonymized = anonymize_csv(
            SAMPLE_CSV,
            drop_columns=["name"],
            region_mapping=REGION_MAPPING,
        )
        result = check_k_anonymity(
            anonymized,
            quasi_identifiers=["age", "region"],
            target_k=2,
        )
        assert isinstance(result, KAnonymityResult)
        assert result.satisfies is True
        assert result.k >= 2

    def test_high_k_fails(self) -> None:
        """高い k 値では不満足になる."""
        anonymized = anonymize_csv(
            SAMPLE_CSV,
            drop_columns=["name"],
            region_mapping=REGION_MAPPING,
        )
        result = check_k_anonymity(
            anonymized,
            quasi_identifiers=["age", "region"],
            target_k=100,
        )
        assert result.satisfies is False

    def test_single_group_high_k(self) -> None:
        """全レコードが同一グループなら高い k 値を達成."""
        csv_text = "age,region\n30-39,関東\n30-39,関東\n30-39,関東\n"
        result = check_k_anonymity(
            csv_text,
            quasi_identifiers=["age", "region"],
            target_k=3,
        )
        assert result.satisfies is True
        assert result.k == 3
        assert result.total_groups == 1

    def test_empty_csv(self) -> None:
        """空のCSVでは k=0."""
        csv_text = "age,region\n"
        result = check_k_anonymity(
            csv_text,
            quasi_identifiers=["age", "region"],
            target_k=5,
        )
        assert result.satisfies is False
        assert result.k == 0

    def test_missing_quasi_identifier_raises(self) -> None:
        """存在しない準識別子で ValueError."""
        csv_text = "age,region\n30-39,関東\n"
        with pytest.raises(ValueError, match="準識別子がCSVに存在しません"):
            check_k_anonymity(
                csv_text,
                quasi_identifiers=["age", "nonexistent"],
                target_k=5,
            )

    def test_result_fields(self) -> None:
        """結果フィールドが正しく設定されている."""
        csv_text = "age,region\n30-39,関東\n30-39,関東\n40-49,関東\n"
        result = check_k_anonymity(
            csv_text,
            quasi_identifiers=["age", "region"],
            target_k=2,
        )
        assert result.total_records == 3
        assert result.total_groups == 2
        assert result.smallest_group_size == 1
        assert result.k == 1
        assert result.satisfies is False
