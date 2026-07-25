"""check_code_sync のテスト.

分類ロジックは棚卸しの対象を決めるため、誤ると本来直すべきブロックを
見逃す。特に「Snakefile を Python でないという理由で除外しない」ことと
「コラム内のブロックを取りこぼさない」ことを重点的に確認する。
"""

from pathlib import Path

from scripts.review.check_code_sync import (
    best_ratio,
    bucket_of,
    chapter_dir_name,
    classify,
    extract_blocks,
    significant_lines,
)


class TestSignificantLines:
    """significant_lines のテスト."""

    def test_drops_blank_and_comment_lines(self) -> None:
        """空行とコメント行を落とす."""
        code = "# 説明コメント\n\nx = 1\n   \n# もう1つ\ny = 2\n"
        assert significant_lines(code) == ["x = 1", "y = 2"]

    def test_normalizes_whitespace(self) -> None:
        """連続する空白を1つに畳み、字下げの差を無視する."""
        assert significant_lines("    a  =   1") == ["a = 1"]

    def test_book_only_comment_does_not_affect_match(self) -> None:
        """本文にだけ付いた説明コメントは一致判定に影響しない."""
        book = "# 本文だけの解説\nresult = compute(x)"
        script = "result = compute(x)"
        assert significant_lines(book) == significant_lines(script)


class TestClassify:
    """classify のテスト."""

    def test_snakefile_is_checked_not_excluded(self) -> None:
        """Snakefile は ast.parse に失敗するが検証対象から外さない."""
        code = (
            "rule fastqc:\n"
            '    input: "data/{sample}.fastq"\n'
            '    output: "qc/{sample}.html"'
        )
        category, reason = classify(code, "#### ruleの基本構造", None)
        assert category == "checked"
        assert "Snakefile" in reason

    def test_configfile_is_checked(self) -> None:
        """configfile 行だけでも Snakefile と判定する."""
        code = 'configfile: "config.yaml"\nSAMPLES = config["samples"]\nprint(SAMPLES)'
        assert classify(code, "#### 設定", None)[0] == "checked"

    def test_exercise_is_excluded(self) -> None:
        """演習問題のコードは規約により scripts/ に置かない."""
        code = "def process(x):\n    return x\n\nprocess(1)"
        assert (
            classify(code, "### 演習 3-1: データ構造の選択ミス", None)[0] == "exercise"
        )

    def test_bad_example_is_excluded(self) -> None:
        """悪例は scripts/ に置かない."""
        code = "# ❌ ハードコーディング\npath = '/home/user/data.csv'\nopen(path)"
        assert classify(code, "### ハードコーディングの問題", None)[0] == "bad_example"

    def test_scripts_call_is_excluded(self) -> None:
        """scripts/ を呼び出す例は scripts/ 本体と一致しなくてよい."""
        code = (
            "from scripts.ch14.validate_workflow import validate\n\n"
            "validate('Snakefile')"
        )
        assert classify(code, "### 自動チェック", None)[0] == "scripts_call"

    def test_repl_is_excluded(self) -> None:
        """REPL セッションは実行可能なコードではない."""
        code = ">>> 0.1 + 0.2\n0.30000000000000004\n>>> round(0.1 + 0.2, 2)"
        assert classify(code, "### IEEE 754", None)[0] == "repl"

    def test_non_python_is_excluded(self) -> None:
        """図解などPythonとして解釈できないものは対象外にする."""
        code = (
            "パッケージA: requires numpy>=1.24\nパッケージB: requires numpy<1.20\n衝突"
        )
        assert classify(code, "### 依存関係地獄", None)[0] == "not_python"

    def test_marker_takes_precedence(self) -> None:
        """本文のマーカーは他のどの判定よりも優先する."""
        code = "import polars as pl\nlf = pl.scan_csv('a.csv')\nprint(lf.collect())"
        category, reason = classify(code, "### 通常の見出し", "ライブラリ紹介のため")
        assert category == "marked_skip"
        assert reason == "ライブラリ紹介のため"

    def test_plain_python_is_checked(self) -> None:
        """通常の実装コードは検証対象になる."""
        code = (
            "def gc(seq: str) -> float:\n"
            "    return (seq.count('G') + seq.count('C')) / len(seq)"
        )
        assert classify(code, "### GC含量", None)[0] == "checked"


class TestBestRatio:
    """best_ratio のテスト."""

    def test_full_containment(self) -> None:
        """全行が含まれれば 1.0 になる."""
        corpus = {"scripts/ch01/a.py": {"x = 1", "y = 2", "z = 3"}}
        ratio, where = best_ratio(["x = 1", "y = 2"], corpus)
        assert ratio == 1.0
        assert where == "scripts/ch01/a.py"

    def test_picks_best_file(self) -> None:
        """最も一致するファイルを選ぶ."""
        corpus = {
            "scripts/ch01/a.py": {"x = 1"},
            "scripts/ch01/b.py": {"x = 1", "y = 2"},
        }
        assert best_ratio(["x = 1", "y = 2"], corpus)[1] == "scripts/ch01/b.py"

    def test_empty_corpus(self) -> None:
        """照合先がなければ 0.0 を返す."""
        assert best_ratio(["x = 1"], {}) == (0.0, "")


class TestBucketOf:
    """bucket_of のテスト."""

    def test_boundaries(self) -> None:
        """しきい値の境界で区分が切り替わる."""
        assert bucket_of(1.0) == "exact"
        assert bucket_of(0.9) == "near"
        assert bucket_of(0.6) == "partial"
        assert bucket_of(0.1) == "slight"
        assert bucket_of(0.0) == "none"


class TestChapterDirName:
    """chapter_dir_name のテスト."""

    def test_chapter_file(self) -> None:
        """章ファイルはディレクトリ名へ変換される."""
        assert chapter_dir_name("04_data_formats.md") == "ch04"

    def test_non_chapter_file(self) -> None:
        """番号のないファイルは対象外."""
        assert chapter_dir_name("hajimeni.md") is None


class TestExtractBlocks:
    """extract_blocks のテスト."""

    def test_extracts_python_block(self, tmp_path: Path) -> None:
        """通常のコードブロックを抽出する."""
        md = tmp_path / "01_x.md"
        md.write_text(
            "## 見出し\n\n```python\nx = 1\ny = 2\nz = 3\n```\n", encoding="utf-8"
        )
        blocks = extract_blocks(md)
        assert len(blocks) == 1
        assert blocks[0].signature == ["x = 1", "y = 2", "z = 3"]

    def test_extracts_block_inside_column(self, tmp_path: Path) -> None:
        """コラム内の引用接頭辞付きブロックも取りこぼさない."""
        md = tmp_path / "01_x.md"
        md.write_text(
            "> **コラム**\n>\n> ```python\n> a = 1\n> b = 2\n> c = 3\n> ```\n",
            encoding="utf-8",
        )
        blocks = extract_blocks(md)
        assert len(blocks) == 1
        assert blocks[0].signature == ["a = 1", "b = 2", "c = 3"]

    def test_skips_short_blocks(self, tmp_path: Path) -> None:
        """3行未満の断片は対象外."""
        md = tmp_path / "01_x.md"
        md.write_text("```python\nx = 1\n```\n", encoding="utf-8")
        assert extract_blocks(md) == []

    def test_ignores_non_target_language(self, tmp_path: Path) -> None:
        """python 以外の言語タグは対象外."""
        md = tmp_path / "01_x.md"
        md.write_text("```bash\nls -l\ncd /tmp\npwd\n```\n", encoding="utf-8")
        assert extract_blocks(md) == []

    def test_skip_marker_applies_to_next_block(self, tmp_path: Path) -> None:
        """マーカーは直後のブロックに適用される."""
        md = tmp_path / "01_x.md"
        md.write_text(
            "<!-- code-sync: skip ライブラリ紹介 -->\n"
            "```python\nimport json\nd = json.loads('{}')\nprint(d)\n```\n",
            encoding="utf-8",
        )
        blocks = extract_blocks(md)
        assert blocks[0].category == "marked_skip"
        assert blocks[0].reason == "ライブラリ紹介"

    def test_skip_marker_does_not_leak_to_later_block(self, tmp_path: Path) -> None:
        """マーカーと無関係な本文を挟んだ次のブロックには適用されない."""
        md = tmp_path / "01_x.md"
        md.write_text(
            "<!-- code-sync: skip 理由 -->\n"
            "```python\nimport json\nd = json.loads('{}')\nprint(d)\n```\n"
            "\n間に入る本文。\n\n"
            "```python\nx = 1\ny = 2\nz = 3\n```\n",
            encoding="utf-8",
        )
        blocks = extract_blocks(md)
        assert blocks[0].category == "marked_skip"
        assert blocks[1].category == "checked"

    def test_records_heading_and_line(self, tmp_path: Path) -> None:
        """直近の見出しと開始行を記録する."""
        md = tmp_path / "01_x.md"
        md.write_text(
            "## A\n\n### B\n\n```python\nx = 1\ny = 2\nz = 3\n```\n", encoding="utf-8"
        )
        block = extract_blocks(md)[0]
        assert block.heading == "### B"
        assert block.line == 5
