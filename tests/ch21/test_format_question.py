"""format_question モジュールのテスト.

実行環境の自動収集と質問テンプレート生成を検証する。
"""

from scripts.ch21.format_question import (
    collect_environment,
    format_biostars_question,
    format_github_issue,
)


# --- collect_environment ---


class TestCollectEnvironment:
    """環境情報収集のテスト."""

    def test_collect_environment(self) -> None:
        """返り値に python_version, os_info キーが含まれること."""
        env = collect_environment()
        assert "python_version" in env
        assert "os_info" in env

    def test_collect_environment_has_package_info(self) -> None:
        """主要パッケージの情報が含まれること."""
        env = collect_environment()
        # numpy はインストールされているはず
        assert "numpy" in env
        assert "pandas" in env
        assert "biopython" in env


# --- format_biostars_question ---


class TestFormatBiostarsQuestion:
    """Biostars質問テンプレート生成のテスト."""

    def test_format_biostars_question(self) -> None:
        """生成テンプレートにtitle, body, error_trace, 環境情報が含まれること."""
        env = {"python_version": "3.10.0", "os_info": "Linux 5.15"}
        result = format_biostars_question(
            title="BLAST結果のパースエラー",
            body="Bio.Blast.NCBIXMLで結果をパースすると例外が発生します。",
            error_trace="Traceback: ValueError: invalid literal",
            env=env,
        )

        assert "BLAST結果のパースエラー" in result
        assert "Bio.Blast.NCBIXMLで結果をパースすると例外が発生します。" in result
        assert "Traceback: ValueError: invalid literal" in result
        assert "python_version" in result
        assert "3.10.0" in result
        assert "os_info" in result


# --- format_github_issue ---


class TestFormatGithubIssue:
    """GitHub Issue テンプレート生成のテスト."""

    def test_format_github_issue(self) -> None:
        """生成テンプレートに再現手順、期待、実際が含まれること."""
        env = {"python_version": "3.10.0", "os_info": "Darwin 23.0"}
        result = format_github_issue(
            title="SeqIO.parseがgzipファイルで失敗する",
            description="gzip圧縮されたFASTQファイルを読み込めない。",
            steps_to_reproduce=[
                "gzip圧縮されたFASTQファイルを用意する",
                "SeqIO.parse('reads.fq.gz', 'fastq') を実行する",
                "エラーが発生する",
            ],
            expected="FASTQレコードが正しく読み込まれる",
            actual="UnicodeDecodeErrorが発生する",
            env=env,
        )

        # 再現手順が含まれること
        assert "gzip圧縮されたFASTQファイルを用意する" in result
        assert "SeqIO.parse" in result
        # 期待・実際が含まれること
        assert "FASTQレコードが正しく読み込まれる" in result
        assert "UnicodeDecodeErrorが発生する" in result
        # 環境情報が含まれること
        assert "python_version" in result
        assert "Darwin" in result

    def test_format_github_issue_steps_numbered(self) -> None:
        """再現手順が番号付きリストになること."""
        env = {"python_version": "3.10.0"}
        result = format_github_issue(
            title="テスト",
            description="テスト",
            steps_to_reproduce=["手順1", "手順2"],
            expected="期待",
            actual="実際",
            env=env,
        )
        assert "1. 手順1" in result
        assert "2. 手順2" in result
