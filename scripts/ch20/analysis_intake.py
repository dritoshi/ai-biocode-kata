"""解析タイプに応じた情報収集チェックリストを生成するモジュール.

バイオインフォマティクス解析を依頼する際に必要な情報を
チェックリストとして整理し、メタデータの検証も行う。
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# 解析タイプごとのチェックリスト定義
_INTAKE_CHECKLISTS: dict[str, dict[str, list[str]]] = {
    "rna-seq": {
        "サンプル情報": [
            "生物種（学名）",
            "組織・細胞種",
            "実験条件（コントロール vs 処理）",
            "バイオロジカルリプリケート数",
        ],
        "シーケンス情報": [
            "シーケンサ機種",
            "リード長（例: 150bp PE）",
            "ライブラリ調製法（例: polyA選択, rRNA除去）",
            "想定リード数/サンプル",
        ],
        "リファレンス情報": [
            "リファレンスゲノムのバージョン（例: GRCh38）",
            "アノテーションファイル（GTF/GFF）のバージョン",
        ],
        "解析要件": [
            "発現変動遺伝子（DEG）解析の有無",
            "パスウェイ解析の有無",
            "有意水準（FDR閾値）",
            "fold change閾値",
        ],
    },
    "chip-seq": {
        "サンプル情報": [
            "生物種（学名）",
            "細胞種",
            "ターゲットタンパク質/修飾",
            "抗体情報（カタログ番号）",
            "Input/IgGコントロールの有無",
        ],
        "シーケンス情報": [
            "シーケンサ機種",
            "リード長",
            "シングルエンド/ペアエンド",
        ],
        "リファレンス情報": [
            "リファレンスゲノムのバージョン",
        ],
        "解析要件": [
            "ピークコーラー（例: MACS2）",
            "ピーク種類（narrow/broad）",
            "差分解析の有無",
        ],
    },
    "wgs": {
        "サンプル情報": [
            "生物種（学名）",
            "サンプル数",
            "家系情報（トリオ解析の場合）",
            "疾患/表現型情報",
        ],
        "シーケンス情報": [
            "シーケンサ機種",
            "リード長",
            "想定カバレッジ",
        ],
        "リファレンス情報": [
            "リファレンスゲノムのバージョン（例: GRCh38）",
        ],
        "解析要件": [
            "バリアントコーラー（例: GATK HaplotypeCaller）",
            "対象バリアント種類（SNV/InDel/SV）",
            "アノテーションツール（例: VEP, ANNOVAR）",
            "フィルタリング基準",
        ],
    },
    "metagenome": {
        "サンプル情報": [
            "サンプル種類（土壌、腸内、海水等）",
            "採取条件・時期",
            "サンプル数とグループ分け",
            "バイオロジカルリプリケート数",
        ],
        "シーケンス情報": [
            "解析手法（16S/ITS/ショットガン）",
            "シーケンサ機種",
            "リード長",
            "ターゲット領域（16Sの場合: V3-V4等）",
        ],
        "リファレンス情報": [
            "データベース（例: Silva, Greengenes2, GTDB）",
        ],
        "解析要件": [
            "多様性解析（α/β多様性）の有無",
            "組成差分解析の有無",
            "機能予測の有無",
        ],
    },
    "general": {
        "プロジェクト情報": [
            "解析の目的",
            "期待するアウトプット",
            "納期・スケジュール",
        ],
        "サンプル情報": [
            "生物種",
            "サンプル数",
            "実験デザイン",
        ],
        "データ情報": [
            "データ形式（FASTQ, BAM, VCF等）",
            "データサイズ",
            "データの受け渡し方法",
        ],
        "解析要件": [
            "使用ツール・パイプラインの指定",
            "統計的有意水準",
            "既知の問題点・注意事項",
        ],
    },
}


def get_intake_checklist(analysis_type: str) -> str:
    """解析タイプに応じたチェックリストをMarkdown形式で返す.

    Parameters
    ----------
    analysis_type : str
        解析タイプ。``"rna-seq"``, ``"chip-seq"``, ``"wgs"``,
        ``"metagenome"``, ``"general"`` のいずれか。
        未知の解析タイプの場合は ``"general"`` にフォールバックする。

    Returns
    -------
    str
        Markdown形式のチェックリスト。
    """
    if analysis_type not in _INTAKE_CHECKLISTS:
        logger.warning(
            "未知の解析タイプ '%s' が指定されました。'general' を使用します。",
            analysis_type,
        )
        analysis_type = "general"

    checklist = _INTAKE_CHECKLISTS[analysis_type]

    sections: list[str] = []
    for section_name, items in checklist.items():
        item_lines = "\n".join(f"- [ ] {item}" for item in items)
        sections.append(f"### {section_name}\n\n{item_lines}")

    sections_text = "\n\n".join(sections)

    return f"""\
# {analysis_type} 解析インテークチェックリスト

{sections_text}
"""


def validate_metadata(
    metadata_rows: list[dict[str, str]],
    required_columns: list[str],
) -> list[str]:
    """メタデータの必須カラムと空値を検証する.

    Parameters
    ----------
    metadata_rows : list[dict[str, str]]
        メタデータ辞書のリスト。各辞書は1行分のメタデータ。
    required_columns : list[str]
        必須カラム名のリスト。

    Returns
    -------
    list[str]
        問題があればメッセージのリスト。問題がなければ空リスト。
    """
    issues: list[str] = []

    if not metadata_rows:
        issues.append("メタデータが空です")
        return issues

    # 最初の行のカラムを基準に必須カラムの存在を確認
    available_columns = set(metadata_rows[0].keys())
    for col in required_columns:
        if col not in available_columns:
            issues.append(f"必須カラム '{col}' がありません")

    # 各行の空値チェック
    for i, row in enumerate(metadata_rows, start=1):
        for col in required_columns:
            if col in row and row[col].strip() == "":
                issues.append(f"行 {i}: カラム '{col}' が空です")

    if issues:
        logger.warning("メタデータ検証で %d 件の問題を検出", len(issues))

    return issues
