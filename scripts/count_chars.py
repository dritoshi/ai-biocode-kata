#!/usr/bin/env python3
"""各章・付録の文字数を集計するスクリプト.

3種類のカウントを出力:
- 文字数: len(text) によるraw文字数
- 本文文字数: Markdown記法・コードブロックを除去した本文のみ
- 全角換算: 本文の全角換算文字数（全角=1, 半角=0.5, 端数切り上げ）
"""

import unicodedata
from pathlib import Path

import mistune


class PlainTextRenderer(mistune.HTMLRenderer):
    """Markdownからプレーンテキストを抽出するカスタムレンダラー."""

    def text(self, text: str) -> str:
        return text

    def emphasis(self, text: str) -> str:
        return text

    def strong(self, text: str) -> str:
        return text

    def link(self, text: str, url: str, title: str | None = None) -> str:
        return text

    def image(self, text: str, url: str, title: str | None = None) -> str:
        return ""

    def codespan(self, text: str) -> str:
        return text

    def linebreak(self) -> str:
        return "\n"

    def softbreak(self) -> str:
        return "\n"

    def inline_html(self, html: str) -> str:
        return ""

    def paragraph(self, text: str) -> str:
        return text + "\n"

    def heading(self, text: str, level: int, **attrs: object) -> str:
        return text + "\n"

    def thematic_break(self) -> str:
        return ""

    def block_text(self, text: str) -> str:
        return text

    def block_code(self, code: str, info: str | None = None) -> str:
        return ""

    def block_quote(self, text: str) -> str:
        return text

    def block_html(self, html: str) -> str:
        return ""

    def block_error(self, text: str) -> str:
        return ""

    def list(self, text: str, ordered: bool, **attrs: object) -> str:
        return text

    def list_item(self, text: str) -> str:
        return text


def render_table(renderer: object, text: str) -> str:
    return text


def render_table_head(renderer: object, text: str) -> str:
    return text


def render_table_body(renderer: object, text: str) -> str:
    return text


def render_table_row(renderer: object, text: str) -> str:
    return text


def render_table_cell(
    renderer: object, text: str, align: str | None = None, head: bool = False
) -> str:
    return text + " "


def _create_markdown() -> mistune.Markdown:
    """プレーンテキスト抽出用のMarkdownパーサーを生成する."""
    renderer = PlainTextRenderer(escape=False)
    md = mistune.create_markdown(renderer=renderer, plugins=["table"])
    # テーブルプラグインのレンダラーをプレーンテキスト用に上書き
    renderer.register("table", render_table)
    renderer.register("table_head", render_table_head)
    renderer.register("table_body", render_table_body)
    renderer.register("table_row", render_table_row)
    renderer.register("table_cell", render_table_cell)
    return md


_md = _create_markdown()


def extract_body_text(markdown_text: str) -> str:
    """Markdown記法を除去して本文テキストのみを抽出する."""
    return _md(markdown_text)


def count_zenkaku(text: str) -> int:
    """全角換算の文字数（全角=1、半角=0.5、端数切り上げ）."""
    half_widths = 0
    for ch in text:
        eaw = unicodedata.east_asian_width(ch)
        if eaw in ("W", "F"):  # Wide, Fullwidth
            half_widths += 2
        else:  # Narrow, Halfwidth, Neutral, Ambiguous
            half_widths += 1
    return -(-half_widths // 2)


def count_chars(
    chapters_dir: Path,
) -> list[tuple[str, int, int, int]]:
    """chapters/ 内の全 Markdown ファイルの文字数を返す.

    Returns:
        (ラベル, raw文字数, 本文文字数, 全角換算文字数) のリスト
    """
    # 表示用のラベルマッピング
    labels: dict[str, str] = {
        "hajimeni.md": "はじめに",
        "00_ai_agent.md": "§0 AIエージェントにコードを書かせる",
        "01_design.md": "§1 設計原則",
        "02_terminal.md": "§2 ターミナル操作",
        "03_cs_basics.md": "§3 計算機科学の基礎",
        "04_data_formats.md": "§4 データフォーマット",
        "05_software_components.md": "§5 ソフトウェアの構成要素",
        "06_dev_environment.md": "§6 Python環境の構築",
        "07_git.md": "§7 Git入門",
        "08_testing.md": "§8 テスト技法",
        "09_debug.md": "§9 デバッグ",
        "10_deliverables.md": "§10 成果物の形式",
        "11_cli.md": "§11 CLIツールの設計",
        "12_data_processing.md": "§12 データ処理の実践",
        "13_visualization.md": "§13 可視化",
        "14_workflow.md": "§14 パイプライン自動化",
        "15_container.md": "§15 コンテナ",
        "16_hpc.md": "§16 スパコン・HPC",
        "17_performance.md": "§17 パフォーマンス",
        "18_documentation.md": "§18 ドキュメント",
        "19_database_api.md": "§19 データベース・API",
        "20_security_ethics.md": "§20 セキュリティ・倫理",
        "21_collaboration.md": "§21 チーム開発",
        "appendix_a_learning_patterns.md": "付録A 学習パターン集",
        "appendix_b_cli_reference.md": "付録B CLIリファレンス",
        "appendix_c_checklist.md": "付録C チェックリスト",
        "glossary.md": "用語集",
        "roadmap.md": "ロードマップ",
    }

    # 表示順序
    order = list(labels.keys())

    results: list[tuple[str, int, int, int]] = []
    for filename in order:
        filepath = chapters_dir / filename
        if filepath.exists():
            text = filepath.read_text(encoding="utf-8")
            raw_count = len(text)
            body_text = extract_body_text(text)
            body_count = len(body_text)
            zenkaku_count = count_zenkaku(body_text)
            label = labels[filename]
            results.append((label, raw_count, body_count, zenkaku_count))

    return results


def main() -> None:
    chapters_dir = Path(__file__).resolve().parent.parent / "chapters"
    results = count_chars(chapters_dir)

    # Markdown テーブル形式で出力
    print("| 章 | 文字数 | 本文文字数 | 全角換算 |")
    print("|-----|--------|-----------|---------|")

    total_raw = 0
    total_body = 0
    total_zenkaku = 0
    honbun_raw = 0
    honbun_body = 0
    honbun_zenkaku = 0

    for label, raw, body, zenkaku in results:
        print(f"| {label} | {raw:,} | {body:,} | {zenkaku:,} |")
        total_raw += raw
        total_body += body
        total_zenkaku += zenkaku
        if label not in ("ロードマップ", "用語集"):
            honbun_raw += raw
            honbun_body += body
            honbun_zenkaku += zenkaku

    print(f"| **合計** | **{total_raw:,}** | **{total_body:,}** | **{total_zenkaku:,}** |")
    print()
    print(
        f"ロードマップ・用語集を除いた本文＋付録の合計: "
        f"**{honbun_raw:,}文字** / 本文 **{honbun_body:,}文字** / 全角換算 **{honbun_zenkaku:,}文字**"
    )


if __name__ == "__main__":
    main()
