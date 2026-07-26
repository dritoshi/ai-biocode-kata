"""第21章のBiocondaレシピテンプレートを検証する."""

import re
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parents[2]
RECIPE_PATH = (
    PROJECT_ROOT / "scripts" / "ch21" / "bioconda_recipe" / "meta.yaml.template"
)


def test_recipe_is_explicit_unresolved_template() -> None:
    """必須sectionを持ち、URLとハッシュを実在値として装わない."""
    data = yaml.safe_load(RECIPE_PATH.read_text(encoding="utf-8"))

    assert set(data) == {
        "package",
        "source",
        "build",
        "requirements",
        "test",
    }
    assert data["package"] == {
        "name": "REPLACE_WITH_PACKAGE_NAME",
        "version": "REPLACE_WITH_VERSION",
    }
    assert data["source"]["url"] == "REPLACE_WITH_RELEASE_ARCHIVE_URL"
    assert data["source"]["sha256"] == "REPLACE_WITH_64_CHARACTER_SHA256"
    assert re.fullmatch(r"[0-9a-f]{64}", data["source"]["sha256"]) is None
    assert data["requirements"]["host"] == ["python >=3.10", "pip"]
    assert data["requirements"]["run"] == [
        "python >=3.10",
        "biopython >=1.80",
    ]
    assert data["test"]["commands"] == ["REPLACE_WITH_COMMAND --help"]
