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
    has_counterpart,
    read_previous_unsynced,
    significant_lines,
    strip_inline_comment,
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


class TestStripInlineComment:
    """strip_inline_comment のテスト.

    本文には解説コメントを付け scripts/ には付けないことが多く、これを
    残したまま比較すると同一のコードが不一致と判定される（実測で全体の
    12% が偽陽性だった）。
    """

    def test_removes_trailing_comment(self) -> None:
        """行末コメントを落とす."""
        assert (
            strip_inline_comment("x = compute()  # ここで実行").strip()
            == "x = compute()"
        )

    def test_keeps_hash_inside_double_quotes(self) -> None:
        """二重引用符の中の # は残す."""
        assert strip_inline_comment('path = "a#b"') == 'path = "a#b"'

    def test_keeps_hash_inside_single_quotes(self) -> None:
        """単一引用符の中の # は残す."""
        assert (
            strip_inline_comment("p = re.compile('#\\\\d+')")
            == "p = re.compile('#\\\\d+')"
        )

    def test_handles_escaped_quote(self) -> None:
        """エスケープされた引用符で文字列が終わったと誤認しない."""
        assert strip_inline_comment('s = "a\\"b"  # 注釈').strip() == 's = "a\\"b"'

    def test_line_without_comment_is_unchanged(self) -> None:
        """コメントがなければそのまま返す."""
        assert strip_inline_comment("x = 1") == "x = 1"

    def test_book_and_script_match_after_stripping(self) -> None:
        """本文だけに行末コメントがあっても一致する."""
        book = "result = compute(x)  # ここで初めて実行"
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

    def test_dockerfile_is_checked_despite_parse_failure(self) -> None:
        """Dockerfile は ast.parse に失敗するが検証対象から外さない.

        CLAUDE.md の表では設定・ワークフロー定義も scripts/ への配置が必要。
        Python として解釈できないことを除外の理由にしてはならない。
        """
        code = "FROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt ."
        category, reason = classify(code, "### Dockerfile", None, "dockerfile")
        assert category == "checked"
        assert "dockerfile" in reason

    def test_yaml_is_checked_despite_parse_failure(self) -> None:
        """YAML も同様に検証対象とする."""
        code = "samples:\n  - SRR001\n  - SRR002"
        assert classify(code, "### 設定", None, "yaml")[0] == "checked"

    def test_bad_example_rule_still_applies_to_config(self) -> None:
        """設定ファイルでも悪例は除外する."""
        code = "# ❌ 悪い例\nFROM ubuntu:latest\nRUN apt-get install -y python3"
        assert classify(code, "### 注意", None, "dockerfile")[0] == "bad_example"

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


class TestHasCounterpart:
    """has_counterpart のテスト.

    「乖離」と「そもそも実体が無い」では棚卸しで取る対応が異なるため、
    両者を取り違えてはならない。
    """

    def test_python_with_py_file(self) -> None:
        """py ファイルがあれば python の対応先ありとみなす."""
        assert has_counterpart("python", {"scripts/ch01/a.py": set()})

    def test_yaml_without_yaml_file(self) -> None:
        """py しかない章に yaml の対応先は無い."""
        assert not has_counterpart("yaml", {"scripts/ch08/a.py": set()})

    def test_yaml_with_yml_file(self) -> None:
        """.yml も yaml の対応先として数える."""
        assert has_counterpart("yaml", {"scripts/ch15/docker-compose.yml": set()})

    def test_dockerfile_matches_by_prefix(self) -> None:
        """Dockerfile.multistage のような派生名も対応先とみなす."""
        assert has_counterpart(
            "dockerfile", {"scripts/ch15/Dockerfile.multistage": set()}
        )

    def test_snakefile_counts_for_python(self) -> None:
        """Snakefile は python タグで書かれるため python の対応先になる."""
        assert has_counterpart("python", {"scripts/ch14/Snakefile": set()})

    def test_empty_corpus(self) -> None:
        """照合先が空なら対応先なし."""
        assert not has_counterpart("python", {})


class TestReadPreviousUnsynced:
    """read_previous_unsynced のテスト."""

    def test_reads_count(self, tmp_path: Path) -> None:
        """前回の件数を読む."""
        path = tmp_path / "out.json"
        path.write_text('{"unsynced_count": 74}', encoding="utf-8")
        assert read_previous_unsynced(path) == 74

    def test_missing_file(self, tmp_path: Path) -> None:
        """初回実行では None を返す."""
        assert read_previous_unsynced(tmp_path / "none.json") is None

    def test_broken_json(self, tmp_path: Path) -> None:
        """壊れた JSON でも例外を投げない."""
        path = tmp_path / "out.json"
        path.write_text("{壊れている", encoding="utf-8")
        assert read_previous_unsynced(path) is None

    def test_unexpected_shape(self, tmp_path: Path) -> None:
        """想定外の形式なら None を返す."""
        path = tmp_path / "out.json"
        path.write_text('{"unsynced_count": "多い"}', encoding="utf-8")
        assert read_previous_unsynced(path) is None


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

    def test_non_target_language_is_recorded_not_dropped(self, tmp_path: Path) -> None:
        """照合対象外の言語も記録する.

        黙って飛ばすと報告が「網羅した」と誤読される。件数を出せるよう
        other_lang として残す。
        """
        md = tmp_path / "01_x.md"
        md.write_text("```bash\nls -l\ncd /tmp\npwd\n```\n", encoding="utf-8")
        blocks = extract_blocks(md)
        assert len(blocks) == 1
        assert blocks[0].category == "other_lang"
        assert blocks[0].lang == "bash"

    def test_dockerfile_block_is_extracted(self, tmp_path: Path) -> None:
        """設定・ワークフロー定義は照合対象の言語として抽出する."""
        md = tmp_path / "15_x.md"
        md.write_text(
            "```dockerfile\nFROM python:3.12\nWORKDIR /app\nCOPY . .\n```\n",
            encoding="utf-8",
        )
        blocks = extract_blocks(md)
        assert blocks[0].category == "checked"
        assert blocks[0].lang == "dockerfile"

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
