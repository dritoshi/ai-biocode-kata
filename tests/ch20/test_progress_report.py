"""progress_report モジュールのテスト.

サンプルgit logテキストを使って、コミットパース・分類・
レポート生成を検証する。
"""

from scripts.ch20.progress_report import (
    Commit,
    categorize_commits,
    generate_report,
    parse_git_log,
)

# --- テスト用データ ---

SAMPLE_GIT_LOG = """\
a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2|feat: RNA-seq解析パイプラインを追加|2024-03-18 10:30:00 +0900
b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3|fix: GC含量計算の丸め誤差を修正|2024-03-17 15:20:00 +0900
c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4|docs: READMEにインストール手順を追加|2024-03-17 09:00:00 +0900
d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5|feat(parser): FASTQパーサを実装|2024-03-16 14:00:00 +0900
e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6|初期コミット|2024-03-15 08:00:00 +0900
"""


# --- parse_git_log ---


class TestParseGitLog:
    """git logパースのテスト."""

    def test_parse_git_log(self) -> None:
        """コミット情報が正しくパースされること."""
        commits = parse_git_log(SAMPLE_GIT_LOG)
        assert len(commits) == 5
        assert commits[0].hash == "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
        assert commits[0].subject == "feat: RNA-seq解析パイプラインを追加"
        assert "2024-03-18" in commits[0].date

    def test_parse_git_log_empty(self) -> None:
        """空テキストで空リストが返ること."""
        commits = parse_git_log("")
        assert commits == []

    def test_parse_git_log_single_line(self) -> None:
        """1行だけのログが正しくパースされること."""
        log = "abc123def456|fix: バグ修正|2024-01-01 00:00:00 +0900"
        commits = parse_git_log(log)
        assert len(commits) == 1
        assert commits[0].subject == "fix: バグ修正"


# --- categorize_commits ---


class TestCategorizeCommits:
    """コミット分類のテスト."""

    def test_categorize_commits(self) -> None:
        """feat/fix/docsに正しく分類されること."""
        commits = parse_git_log(SAMPLE_GIT_LOG)
        categorized = categorize_commits(commits)

        # feat: 2件（feat: と feat(parser):）
        assert "feat" in categorized
        assert len(categorized["feat"]) == 2

        # fix: 1件
        assert "fix" in categorized
        assert len(categorized["fix"]) == 1

        # docs: 1件
        assert "docs" in categorized
        assert len(categorized["docs"]) == 1

        # other: 1件（「初期コミット」はConventional Commits形式でない）
        assert "other" in categorized
        assert len(categorized["other"]) == 1

    def test_categorize_commits_scoped(self) -> None:
        """スコープ付きコミット（feat(parser):）が正しく分類されること."""
        commits = [
            Commit(
                hash="abc123",
                subject="feat(parser): FASTQパーサ",
                date="2024-01-01",
            )
        ]
        categorized = categorize_commits(commits)
        assert "feat" in categorized
        assert len(categorized["feat"]) == 1


# --- generate_report ---


class TestGenerateReport:
    """レポート生成のテスト."""

    def test_generate_report(self) -> None:
        """Markdown報告が生成され、期間とカテゴリが含まれること."""
        commits = parse_git_log(SAMPLE_GIT_LOG)
        period = "2024-03-15 〜 2024-03-18"
        report = generate_report(commits, period)

        # 期間が含まれること
        assert "2024-03-15 〜 2024-03-18" in report

        # カテゴリ別セクションが含まれること
        assert "機能追加" in report
        assert "バグ修正" in report
        assert "ドキュメント" in report

        # コミット数が含まれること
        assert "5" in report

    def test_generate_report_includes_short_hash(self) -> None:
        """レポートに短縮ハッシュが含まれること."""
        commits = parse_git_log(SAMPLE_GIT_LOG)
        report = generate_report(commits, "2024-03")
        # 最初のコミットの短縮ハッシュ
        assert "a1b2c3d" in report

    def test_generate_report_empty_commits(self) -> None:
        """コミットが空の場合でもレポートが生成されること."""
        report = generate_report([], "2024-03")
        assert "0件" in report
