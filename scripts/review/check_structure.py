#!/usr/bin/env python3
"""構造規約チェックスクリプト

CLAUDE.md の執筆規約に基づき、各章ファイルを対象に:
- 必須セクション存在確認
- セクション順序確認
- **太字** 内のカッコ・カギ括弧チェック
- $...$ 直前/直後の全角カッコチェック
- 演習問題の形式チェック

結果を JSON に保存する。既定の出力先は docs/review/structure_check.json。
"""

import argparse
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CHAPTERS_DIR = PROJECT_ROOT / "chapters"
DEFAULT_OUTPUT = PROJECT_ROOT / "docs" / "review" / "structure_check.json"

# 通常の章ファイル（必須セクションチェック対象）
# hajimeni.md、付録、glossary.md、roadmap.md は除外
EXCLUDED_FILES = {
    "hajimeni.md",
    "roadmap.md",
    "glossary.md",
    "appendix_a_learning_patterns.md",
    "appendix_b_cli_reference.md",
    "appendix_c_checklist.md",
    "appendix_d_agent_vocabulary.md",
}

# 必須セクション（出現すべき順序）
REQUIRED_SECTIONS = ["## まとめ", "## 演習問題", "## さらに学びたい読者へ", "## 参考文献"]

# 演習問題の類型ラベル
VALID_EXERCISE_TYPES = {"レビュー", "指示設計", "設計判断", "実践", "概念"}


def read_file_lines(filepath: Path) -> list[str]:
    """ファイルを読み込み行のリストを返す。"""
    try:
        return filepath.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []


def check_required_sections(filepath: Path, lines: list[str]) -> list[dict]:
    """必須セクションの存在と順序を確認する。"""
    issues = []
    rel_path = str(filepath.relative_to(PROJECT_ROOT))

    # 各必須セクションの行番号を検出
    section_positions: dict[str, int | None] = {s: None for s in REQUIRED_SECTIONS}
    in_code_block = False

    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        for section in REQUIRED_SECTIONS:
            if line.startswith(section):
                section_positions[section] = line_no
                break

    # 存在確認
    for section, pos in section_positions.items():
        if pos is None:
            issues.append({
                "file": rel_path,
                "line": 0,
                "severity": "MAJOR",
                "type": "missing_section",
                "message": f"必須セクションが見つからない: {section}",
            })

    # 順序確認（存在するセクションのみ）
    found_sections = [(s, p) for s, p in section_positions.items() if p is not None]
    for i in range(len(found_sections) - 1):
        curr_section, curr_pos = found_sections[i]
        next_section, next_pos = found_sections[i + 1]
        # REQUIRED_SECTIONSリストでの順序と実際の出現順序を比較
        curr_idx = REQUIRED_SECTIONS.index(curr_section)
        next_idx = REQUIRED_SECTIONS.index(next_section)
        if curr_idx > next_idx:
            issues.append({
                "file": rel_path,
                "line": next_pos,
                "severity": "MAJOR",
                "type": "section_order",
                "message": f"セクション順序違反: '{next_section}' が '{curr_section}' の前にある（期待: まとめ → 演習問題 → さらに学びたい読者へ → 参考文献）",
            })
        elif curr_pos is not None and next_pos is not None and curr_pos > next_pos:
            issues.append({
                "file": rel_path,
                "line": next_pos,
                "severity": "MAJOR",
                "type": "section_order",
                "message": f"セクション順序違反: '{next_section}' (L{next_pos}) が '{curr_section}' (L{curr_pos}) より前にある",
            })

    return issues


def check_bold_brackets(filepath: Path, lines: list[str]) -> list[dict]:
    """**太字** 内にカッコやカギ括弧が含まれていないかチェックする。

    パターン: **...（...** or **...(...** or **...「...** or **...」...**
    """
    issues = []
    rel_path = str(filepath.relative_to(PROJECT_ROOT))
    in_code_block = False

    # **...** 内に全角カッコ、半角カッコ、カギ括弧が含まれるパターン
    bold_pattern = re.compile(r'\*\*([^*]+)\*\*')
    bracket_chars = re.compile(r'[（）()「」]')

    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # テーブル行はスキップ（ツール対照表など例外的にカッコが入る）
        if stripped.startswith("|"):
            continue

        for match in bold_pattern.finditer(line):
            bold_content = match.group(1)
            bracket_match = bracket_chars.search(bold_content)
            if bracket_match:
                issues.append({
                    "file": rel_path,
                    "line": line_no,
                    "severity": "MINOR",
                    "type": "bold_bracket",
                    "message": f"太字内にカッコ/カギ括弧を含む: **{bold_content}**",
                    "found_char": bracket_match.group(),
                })

    return issues


def check_math_fullwidth_brackets(filepath: Path, lines: list[str]) -> list[dict]:
    """$...$ 直前/直後に全角カッコが隣接していないかチェックする。"""
    issues = []
    rel_path = str(filepath.relative_to(PROJECT_ROOT))
    in_code_block = False

    # パターン: 全角カッコの直後に $ or $ の直後に全角カッコ
    # （$...$ or $...$）
    pattern_before = re.compile(r'（\$')
    pattern_after = re.compile(r'\$）')

    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        for match in pattern_before.finditer(line):
            issues.append({
                "file": rel_path,
                "line": line_no,
                "severity": "MINOR",
                "type": "math_fullwidth_bracket",
                "message": f"$数式の直前に全角カッコ '（' がある（GitHub MathJaxで数式が壊れる可能性）",
                "context": line.strip()[:120],
            })

        for match in pattern_after.finditer(line):
            issues.append({
                "file": rel_path,
                "line": line_no,
                "severity": "MINOR",
                "type": "math_fullwidth_bracket",
                "message": f"$数式の直後に全角カッコ '）' がある（GitHub MathJaxで数式が壊れる可能性）",
                "context": line.strip()[:120],
            })

    return issues


def check_exercises(filepath: Path, lines: list[str]) -> list[dict]:
    """演習問題の形式チェック。

    - ### 演習 X-Y: タイトル **[類型]** の形式
    - 類型ラベルが5種のいずれかであること
    - 章番号Xがファイル名と一致すること
    """
    issues = []
    rel_path = str(filepath.relative_to(PROJECT_ROOT))
    filename = filepath.name

    # ファイル名から章番号を取得
    chapter_match = re.match(r'(\d+)_', filename)
    if chapter_match:
        expected_chapter = int(chapter_match.group(1))
    else:
        return issues  # 章番号のないファイル（hajimeni等）はスキップ

    in_code_block = False
    in_exercises = False
    exercise_count = 0
    expected_y = 1

    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        if line.startswith("## 演習問題"):
            in_exercises = True
            continue

        if in_exercises and line.startswith("## ") and not line.startswith("## 演習問題"):
            in_exercises = False
            continue

        if not in_exercises:
            continue

        # 演習見出しの検出
        exercise_match = re.match(r'^### 演習\s+(\d+)-(\d+)[：:]\s*(.+)$', stripped)
        if exercise_match:
            exercise_count += 1
            x = int(exercise_match.group(1))
            y = int(exercise_match.group(2))
            title_part = exercise_match.group(3)

            # 章番号の一致確認
            if x != expected_chapter:
                issues.append({
                    "file": rel_path,
                    "line": line_no,
                    "severity": "MAJOR",
                    "type": "exercise_chapter_mismatch",
                    "message": f"演習の章番号が不一致: 演習 {x}-{y} (期待: {expected_chapter}-{y})",
                })

            # 連番確認
            if y != expected_y:
                issues.append({
                    "file": rel_path,
                    "line": line_no,
                    "severity": "MINOR",
                    "type": "exercise_number_gap",
                    "message": f"演習番号が連番でない: 演習 {x}-{y} (期待: {x}-{expected_y})",
                })
            expected_y = y + 1

            # 類型ラベルの確認
            type_match = re.search(r'\*\*\[([^\]]+)\]\*\*', title_part)
            if type_match:
                exercise_type = type_match.group(1)
                if exercise_type not in VALID_EXERCISE_TYPES:
                    issues.append({
                        "file": rel_path,
                        "line": line_no,
                        "severity": "MAJOR",
                        "type": "invalid_exercise_type",
                        "message": f"無効な演習類型ラベル: [{exercise_type}] (有効: {', '.join(sorted(VALID_EXERCISE_TYPES))})",
                    })
            else:
                issues.append({
                    "file": rel_path,
                    "line": line_no,
                    "severity": "MAJOR",
                    "type": "missing_exercise_type",
                    "message": f"演習に類型ラベルがない: {stripped}",
                })

        elif stripped.startswith("### 演習"):
            # パターンに一致しない演習見出し
            issues.append({
                "file": rel_path,
                "line": line_no,
                "severity": "MAJOR",
                "type": "malformed_exercise",
                "message": f"演習見出しの形式が不正: {stripped} (期待形式: ### 演習 X-Y: タイトル **[類型]**)",
            })

    # 演習問題セクションがあるのに問題が0個の場合
    if in_exercises and exercise_count == 0:
        issues.append({
            "file": rel_path,
            "line": 0,
            "severity": "MINOR",
            "type": "empty_exercises",
            "message": "演習問題セクションはあるが問題が0個",
        })

    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="JSON 出力先。既定は docs/review/structure_check.json",
    )
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    md_files = sorted(CHAPTERS_DIR.glob("*.md"))
    all_issues: list[dict] = []
    stats = {
        "total_files_checked": 0,
        "chapter_files_checked": 0,
        "missing_sections": 0,
        "section_order_violations": 0,
        "bold_bracket_violations": 0,
        "math_bracket_violations": 0,
        "exercise_issues": 0,
    }

    for md_file in md_files:
        stats["total_files_checked"] += 1
        lines = read_file_lines(md_file)

        if not lines:
            continue

        filename = md_file.name
        is_chapter = filename not in EXCLUDED_FILES

        # 全ファイル共通チェック
        bold_issues = check_bold_brackets(md_file, lines)
        all_issues.extend(bold_issues)
        stats["bold_bracket_violations"] += len(bold_issues)

        math_issues = check_math_fullwidth_brackets(md_file, lines)
        all_issues.extend(math_issues)
        stats["math_bracket_violations"] += len(math_issues)

        # 章ファイルのみのチェック
        if is_chapter:
            stats["chapter_files_checked"] += 1

            section_issues = check_required_sections(md_file, lines)
            all_issues.extend(section_issues)
            for issue in section_issues:
                if issue["type"] == "missing_section":
                    stats["missing_sections"] += 1
                elif issue["type"] == "section_order":
                    stats["section_order_violations"] += 1

            exercise_issues = check_exercises(md_file, lines)
            all_issues.extend(exercise_issues)
            stats["exercise_issues"] += len(exercise_issues)

    # 重大度でソート
    severity_order = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2}
    all_issues.sort(key=lambda x: (severity_order.get(x["severity"], 99), x["file"], x["line"]))

    result = {
        "check": "structure_check",
        "stats": stats,
        "total_issues": len(all_issues),
        "issues": all_issues,
    }

    output_path = args.output
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # コンソール出力
    print("=== 構造規約チェック結果 ===")
    print(f"チェック対象ファイル数: {stats['total_files_checked']} (うち章ファイル: {stats['chapter_files_checked']})")
    print()
    print(f"問題件数: {len(all_issues)}")
    print(f"  必須セクション不在:           {stats['missing_sections']}")
    print(f"  セクション順序違反:           {stats['section_order_violations']}")
    print(f"  太字内カッコ/カギ括弧:       {stats['bold_bracket_violations']}")
    print(f"  数式隣接全角カッコ:           {stats['math_bracket_violations']}")
    print(f"  演習問題形式:                 {stats['exercise_issues']}")
    print()

    for issue in all_issues:
        severity = issue["severity"]
        line_info = f":{issue['line']}" if issue["line"] > 0 else ""
        print(f"[{severity}] {issue['file']}{line_info} — {issue['message']}")

    print(f"\n結果を {output_path.relative_to(PROJECT_ROOT)} に保存しました。")


if __name__ == "__main__":
    main()
