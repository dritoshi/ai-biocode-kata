"""my-toolの最小CLI実装."""

from pathlib import Path

import click


@click.group()
@click.version_option("0.1.0")
def main() -> None:
    """配列解析用のCLI例."""


@main.command()
@click.option(
    "--input",
    "input_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="入力ファイル",
)
def align(input_path: Path) -> None:
    """入力ファイルを使うアラインメント処理の入口を示す."""
    click.echo(f"入力を確認: {input_path.name}")
