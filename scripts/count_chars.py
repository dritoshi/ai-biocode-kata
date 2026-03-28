#!/usr/bin/env python3
"""各章・付録の文字数と推定読了時間を集計するスクリプト.

4種類のカウントを出力:
- 文字数: len(text) によるraw文字数
- 本文文字数: Markdown記法・コードブロックを除去した本文のみ
- コード文字数: コードブロック内の文字数
- 全角換算: 本文の全角換算文字数（全角=1, 半角=0.5, 端数切り上げ）

読了時間の推定:
- 日本語技術書の読書速度を3段階で推定
- コードブロックは本文より読書速度が遅い前提で別計算
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


class CodeExtractRenderer(mistune.HTMLRenderer):
    """コードブロックのみを抽出するカスタムレンダラー."""

    def text(self, text: str) -> str:
        return ""

    def emphasis(self, text: str) -> str:
        return ""

    def strong(self, text: str) -> str:
        return ""

    def link(self, text: str, url: str, title: str | None = None) -> str:
        return ""

    def image(self, text: str, url: str, title: str | None = None) -> str:
        return ""

    def codespan(self, text: str) -> str:
        return ""

    def linebreak(self) -> str:
        return ""

    def softbreak(self) -> str:
        return ""

    def inline_html(self, html: str) -> str:
        return ""

    def paragraph(self, text: str) -> str:
        return ""

    def heading(self, text: str, level: int, **attrs: object) -> str:
        return ""

    def thematic_break(self) -> str:
        return ""

    def block_text(self, text: str) -> str:
        return ""

    def block_code(self, code: str, info: str | None = None) -> str:
        return code + "\n"

    def block_quote(self, text: str) -> str:
        return ""

    def block_html(self, html: str) -> str:
        return ""

    def block_error(self, text: str) -> str:
        return ""

    def list(self, text: str, ordered: bool, **attrs: object) -> str:
        return ""

    def list_item(self, text: str) -> str:
        return ""


def _render_table(renderer: object, text: str) -> str:
    return text


def _render_table_head(renderer: object, text: str) -> str:
    return text


def _render_table_body(renderer: object, text: str) -> str:
    return text


def _render_table_row(renderer: object, text: str) -> str:
    return text


def _render_table_cell(
    renderer: object, text: str, align: str | None = None, head: bool = False
) -> str:
    return text + " "


def _render_table_empty(renderer: object, text: str) -> str:
    return ""


def _render_table_cell_empty(
    renderer: object, text: str, align: str | None = None, head: bool = False
) -> str:
    return ""


def _create_markdown(renderer: mistune.HTMLRenderer, for_code: bool = False) -> mistune.Markdown:
    """Markdownパーサーを生成する."""
    md = mistune.create_markdown(renderer=renderer, plugins=["table"])
    if for_code:
        renderer.register("table", _render_table_empty)
        renderer.register("table_head", _render_table_empty)
        renderer.register("table_body", _render_table_empty)
        renderer.register("table_row", _render_table_empty)
        renderer.register("table_cell", _render_table_cell_empty)
    else:
        renderer.register("table", _render_table)
        renderer.register("table_head", _render_table_head)
        renderer.register("table_body", _render_table_body)
        renderer.register("table_row", _render_table_row)
        renderer.register("table_cell", _render_table_cell)
    return md


_md_body = _create_markdown(PlainTextRenderer(escape=False))
_md_code = _create_markdown(CodeExtractRenderer(escape=False), for_code=True)


def extract_body_text(markdown_text: str) -> str:
    """Markdown記法を除去して本文テキストのみを抽出する."""
    return _md_body(markdown_text)


def extract_code_text(markdown_text: str) -> str:
    """コードブロックのテキストのみを抽出する."""
    return _md_code(markdown_text)


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


# 読書速度（全角換算文字/分）
READING_SPEEDS = {
    "初心者": {"body": 200, "code": 80},
    "中級者": {"body": 350, "code": 150},
    "上級者": {"body": 500, "code": 250},
}


def estimate_reading_time(body_zenkaku: int, code_zenkaku: int, speed: dict[str, int]) -> float:
    """読了時間を分で返す."""
    body_min = body_zenkaku / speed["body"]
    code_min = code_zenkaku / speed["code"]
    return body_min + code_min


def format_time(minutes: float) -> str:
    """分を「Xh Ym」形式にフォーマットする."""
    if minutes < 60:
        return f"{minutes:.0f}m"
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours}h {mins:02d}m"


def count_chars(
    chapters_dir: Path,
) -> list[tuple[str, int, int, int, int, int]]:
    """chapters/ 内の全 Markdown ファイルの文字数を返す.

    Returns:
        (ラベル, raw文字数, 本文文字数, コード文字数, 本文全角換算, コード全角換算) のリスト
    """
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
        "10_deliverables.md": "§10 成果物の設計",
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
        "appendix_d_agent_vocabulary.md": "付録D 頻出用語・フレーズ集",
        "glossary.md": "用語集",
        "author.md": "著者紹介",
        "roadmap.md": "ロードマップ",
    }

    order = list(labels.keys())

    results: list[tuple[str, int, int, int, int, int]] = []
    for filename in order:
        filepath = chapters_dir / filename
        if filepath.exists():
            text = filepath.read_text(encoding="utf-8")
            raw_count = len(text)
            body_text = extract_body_text(text)
            code_text = extract_code_text(text)
            body_count = len(body_text)
            code_count = len(code_text)
            body_zenkaku = count_zenkaku(body_text)
            code_zenkaku = count_zenkaku(code_text)
            label = labels[filename]
            results.append((label, raw_count, body_count, code_count, body_zenkaku, code_zenkaku))

    return results


def main() -> None:
    chapters_dir = Path(__file__).resolve().parent.parent / "chapters"
    results = count_chars(chapters_dir)

    # --- 文字数テーブル ---
    print("## 文字数")
    print()
    print("| 章 | 文字数 | 本文文字数 | コード文字数 | 本文全角換算 | コード全角換算 |")
    print("|-----|--------|-----------|------------|-----------|------------|")

    total_raw = total_body = total_code = total_body_z = total_code_z = 0
    honbun_body_z = honbun_code_z = 0
    excluded = {"ロードマップ", "用語集", "著者紹介"}

    for label, raw, body, code, body_z, code_z in results:
        print(f"| {label} | {raw:,} | {body:,} | {code:,} | {body_z:,} | {code_z:,} |")
        total_raw += raw
        total_body += body
        total_code += code
        total_body_z += body_z
        total_code_z += code_z
        if label not in excluded:
            honbun_body_z += body_z
            honbun_code_z += code_z

    print(f"| **合計** | **{total_raw:,}** | **{total_body:,}** | **{total_code:,}** | **{total_body_z:,}** | **{total_code_z:,}** |")
    print()

    # --- 読了時間テーブル ---
    print("## 推定読了時間")
    print()
    print("読書速度の前提（全角換算文字/分）:")
    print()
    print("| レベル | 本文 | コード | 想定読者 |")
    print("|-------|------|--------|---------|")
    print("| 初心者 | 200 | 80 | プログラミング未経験の実験系研究者 |")
    print("| 中級者 | 350 | 150 | ある程度のプログラミング経験がある研究者 |")
    print("| 上級者 | 500 | 250 | ソフトウェアエンジニア |")
    print()

    header = "| 章 |"
    separator = "|-----|"
    for level in READING_SPEEDS:
        header += f" {level} |"
        separator += "------|"
    print(header)
    print(separator)

    total_times: dict[str, float] = {level: 0 for level in READING_SPEEDS}
    honbun_times: dict[str, float] = {level: 0 for level in READING_SPEEDS}

    for label, _raw, _body, _code, body_z, code_z in results:
        row = f"| {label} |"
        for level, speed in READING_SPEEDS.items():
            t = estimate_reading_time(body_z, code_z, speed)
            row += f" {format_time(t)} |"
            total_times[level] += t
            if label not in excluded:
                honbun_times[level] += t
        print(row)

    row = "| **合計** |"
    for level in READING_SPEEDS:
        row += f" **{format_time(total_times[level])}** |"
    print(row)

    print()
    print("本文＋付録（ロードマップ・用語集・著者紹介を除く）:")
    row = "| |"
    for level in READING_SPEEDS:
        row += f" **{format_time(honbun_times[level])}** |"
    print(row)


if __name__ == "__main__":
    main()
