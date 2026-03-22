"""review_helper モジュールのテスト.

サンプルdiff文字列を使って、diffパース・型ヒント検査・
docstring検査・チェックリスト生成を検証する。
"""

from scripts.ch20.review_helper import (
    check_type_hints,
    generate_review_checklist,
    parse_diff,
)

# --- テスト用データ ---

SAMPLE_DIFF = """\
diff --git a/scripts/analysis.py b/scripts/analysis.py
index 1234567..abcdefg 100644
--- a/scripts/analysis.py
+++ b/scripts/analysis.py
@@ -1,3 +1,10 @@
+import numpy as np
+
+def calculate_gc(sequence):
+    gc_count = sequence.count("G") + sequence.count("C")
+    return gc_count / len(sequence)
+
+def parse_fasta(filepath: str) -> list[str]:
+    \"\"\"FASTAファイルをパースする.\"\"\"
+    pass
"""

SAMPLE_DIFF_MULTI_FILE = """\
diff --git a/src/utils.py b/src/utils.py
--- a/src/utils.py
+++ b/src/utils.py
@@ -1,2 +1,5 @@
+def helper():
+    return True
+
diff --git a/src/main.py b/src/main.py
--- a/src/main.py
+++ b/src/main.py
@@ -1,2 +1,5 @@
+def run() -> None:
+    \"\"\"メイン処理.\"\"\"
+    pass
"""


# --- parse_diff ---


class TestParseDiff:
    """diffパースのテスト."""

    def test_parse_diff(self) -> None:
        """ファイルパスと追加行が正しく抽出されること."""
        files = parse_diff(SAMPLE_DIFF)
        assert len(files) == 1
        assert files[0].path == "scripts/analysis.py"
        # 追加行に "import numpy" が含まれること
        assert any("import numpy" in line for line in files[0].added_lines)
        # "def calculate_gc" が含まれること
        assert any("def calculate_gc" in line for line in files[0].added_lines)

    def test_parse_diff_multi_file(self) -> None:
        """複数ファイルのdiffが正しくパースされること."""
        files = parse_diff(SAMPLE_DIFF_MULTI_FILE)
        assert len(files) == 2
        paths = [f.path for f in files]
        assert "src/utils.py" in paths
        assert "src/main.py" in paths

    def test_parse_diff_empty(self) -> None:
        """空のdiffで空リストが返ること."""
        files = parse_diff("")
        assert files == []


# --- check_type_hints ---


class TestCheckTypeHints:
    """型ヒント検査のテスト."""

    def test_check_type_hints_missing(self) -> None:
        """型ヒントなし関数が検出されること."""
        lines = [
            "def calculate_gc(sequence):",
            "    gc_count = sequence.count('G')",
        ]
        issues = check_type_hints(lines)
        assert len(issues) == 1
        assert "calculate_gc" in issues[0]
        assert "型ヒント" in issues[0]

    def test_check_type_hints_present(self) -> None:
        """型ヒントあり関数は指摘されないこと."""
        lines = [
            "def parse_fasta(filepath: str) -> list[str]:",
            '    """FASTAファイルをパースする."""',
        ]
        issues = check_type_hints(lines)
        assert len(issues) == 0

    def test_check_type_hints_indented(self) -> None:
        """インデントされた関数定義も検査されること."""
        lines = [
            "    def inner_func(x):",
            "        return x",
        ]
        issues = check_type_hints(lines)
        assert len(issues) == 1
        assert "inner_func" in issues[0]

    def test_check_type_hints_mixed(self) -> None:
        """型ヒントあり・なしが混在する場合."""
        lines = [
            "def good_func(x: int) -> int:",
            "    return x",
            "def bad_func(y):",
            "    return y",
        ]
        issues = check_type_hints(lines)
        assert len(issues) == 1
        assert "bad_func" in issues[0]


# --- generate_review_checklist ---


class TestGenerateReviewChecklist:
    """チェックリスト生成のテスト."""

    def test_generate_review_checklist(self) -> None:
        """Markdownチェックリストが生成されること."""
        result = generate_review_checklist(SAMPLE_DIFF)
        # チェックリスト形式であること
        assert "- [" in result
        # 変更ファイルが含まれること
        assert "scripts/analysis.py" in result
        # 型ヒント欠落の指摘が含まれること
        assert "calculate_gc" in result

    def test_generate_review_checklist_clean(self) -> None:
        """問題のないdiffでは全項目にチェックが入ること."""
        clean_diff = """\
diff --git a/src/clean.py b/src/clean.py
--- a/src/clean.py
+++ b/src/clean.py
@@ -1,2 +1,4 @@
+def greet(name: str) -> str:
+    \"\"\"挨拶文を返す.\"\"\"
+    return f"Hello, {name}"
"""
        result = generate_review_checklist(clean_diff)
        assert "- [x]" in result
