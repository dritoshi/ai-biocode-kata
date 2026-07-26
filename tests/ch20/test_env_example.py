"""第20章の環境変数テンプレートを検証する."""

from pathlib import Path

from scripts.ch20.secret_scanner import scan_file

PROJECT_ROOT = Path(__file__).parents[2]
ENV_PATH = PROJECT_ROOT / "scripts" / "ch20" / ".env.example"


def test_env_example_has_required_placeholders() -> None:
    """必要なキーは実シークレットでなくプレースホルダを持つ."""
    values = dict(
        line.split("=", 1)
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    )

    assert values == {
        "NCBI_API_KEY": "your_key_here",
        "DATABASE_URL": "postgresql://localhost:5432/mydb",
        "DATA_DIR": "/path/to/data",
    }
    assert scan_file(ENV_PATH) == []
