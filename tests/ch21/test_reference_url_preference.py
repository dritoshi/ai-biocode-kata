"""参考文献 URL 抽出の優先順位テスト."""

import scripts.build_review_artifacts as build_review_artifacts
import scripts.review.check_urls_all as check_urls_all
from scripts.review.check_urls_all import extract_urls_from_bib, extract_urls_from_md
from scripts.reference_usage import (
    extract_chapter_reference_items,
    find_missing_chapter_reference_items,
)


def test_extract_urls_from_bib_prefers_explicit_url(tmp_path) -> None:
    bib_file = tmp_path / "sample.bib"
    bib_file.write_text(
        """@article{example,
  title = {Example},
  doi = {10.1093/bioinformatics/btp163},
  url = {https://pubmed.ncbi.nlm.nih.gov/19304878/}
}
""",
        encoding="utf-8",
    )

    urls = extract_urls_from_bib(bib_file)

    assert urls == [("https://pubmed.ncbi.nlm.nih.gov/19304878/", 4)]


def test_extract_urls_from_bib_uses_doi_when_url_missing(tmp_path) -> None:
    bib_file = tmp_path / "sample.bib"
    bib_file.write_text(
        """@article{example,
  title = {Example},
  doi = {10.1093/bioinformatics/btp163}
}
""",
        encoding="utf-8",
    )

    urls = extract_urls_from_bib(bib_file)

    assert urls == [("https://doi.org/10.1093/bioinformatics/btp163", 3)]


def test_scan_reference_files_prefers_explicit_url(tmp_path, monkeypatch) -> None:
    bib_file = tmp_path / "sample.bib"
    bib_file.write_text(
        """@article{example,
  title = {Example},
  doi = {10.1093/bioinformatics/btp163},
  url = {https://pubmed.ncbi.nlm.nih.gov/19304878/}
}
        """,
        encoding="utf-8",
    )

    monkeypatch.setattr(build_review_artifacts, "REPO_ROOT", tmp_path)
    rows = build_review_artifacts.scan_reference_files([bib_file])

    assert len(rows) == 1
    assert rows[0]["source_kind"] == "bib_url"
    assert rows[0]["normalized_target"] == "https://pubmed.ncbi.nlm.nih.gov/19304878/"


def test_scan_reference_files_uses_doi_when_url_missing(tmp_path, monkeypatch) -> None:
    bib_file = tmp_path / "sample.bib"
    bib_file.write_text(
        """@article{example,
  title = {Example},
  doi = {10.1093/bioinformatics/btp163}
}
        """,
        encoding="utf-8",
    )

    monkeypatch.setattr(build_review_artifacts, "REPO_ROOT", tmp_path)
    rows = build_review_artifacts.scan_reference_files([bib_file])

    assert len(rows) == 1
    assert rows[0]["source_kind"] == "bib_doi"
    assert rows[0]["normalized_target"] == "https://doi.org/10.1093/bioinformatics/btp163"


def test_extract_urls_from_bib_supports_howpublished_url_command(tmp_path) -> None:
    bib_file = tmp_path / "sample.bib"
    bib_file.write_text(
        """@misc{example,
  title = {Example},
  howpublished = {\\url{https://docs.github.com/en}}
}
""",
        encoding="utf-8",
    )

    urls = extract_urls_from_bib(bib_file)

    assert urls == [("https://docs.github.com/en", 3)]


def test_extract_urls_from_bib_skips_unused_entry_for_repo_pair(tmp_path, monkeypatch) -> None:
    chapter_dir = tmp_path / "chapters"
    reference_dir = tmp_path / "references"
    chapter_dir.mkdir()
    reference_dir.mkdir()

    (chapter_dir / "21_collaboration.md").write_text(
        """# 共同開発

## 参考文献

[1] GitHub Docs. https://docs.github.com/
""",
        encoding="utf-8",
    )
    bib_file = reference_dir / "ch21.bib"
    bib_file.write_text(
        """@misc{used,
  title = {GitHub Docs},
  url = {https://docs.github.com/}
}

@article{unused,
  title = {Ten Simple Rules for the Open Development of Scientific Software},
  doi = {10.1371/journal.pcbi.1002802}
}
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(check_urls_all, "PROJECT_ROOT", tmp_path)

    urls = extract_urls_from_bib(bib_file)

    assert urls == [("https://docs.github.com/", 3)]


def test_extract_urls_from_md_supports_bare_urls_without_duplicates(tmp_path) -> None:
    md_file = tmp_path / "sample.md"
    md_file.write_text(
        """# Sample

ベタ書きURL: https://quarto.org/docs/get-started/
Markdownリンク: [Quarto](https://quarto.org/docs/get-started/)
句読点付き: https://docs.python.org/3/library/json.html)。本文は続く。
"""
    )

    urls = extract_urls_from_md(md_file)

    assert urls == [
        ("https://quarto.org/docs/get-started/", 3),
        ("https://quarto.org/docs/get-started/", 4),
        ("https://docs.python.org/3/library/json.html", 5),
    ]


def test_extract_urls_from_md_skips_placeholder_without_host(tmp_path) -> None:
    md_file = tmp_path / "sample.md"
    md_file.write_text(
        """# Sample

track 行: bigDataUrl=https://...
"""
    )

    assert extract_urls_from_md(md_file) == []


def test_scan_reference_files_skips_unused_entry_for_repo_pair(tmp_path, monkeypatch) -> None:
    chapter_dir = tmp_path / "chapters"
    reference_dir = tmp_path / "references"
    chapter_dir.mkdir()
    reference_dir.mkdir()

    (chapter_dir / "hajimeni.md").write_text(
        """# はじめに

GitHub Copilotの利用者は 20M+ users に達し[1](https://github.blog/example)。

## 参考文献

[1] GitHub. https://github.blog/example
""",
        encoding="utf-8",
    )
    bib_file = reference_dir / "hajimeni.bib"
    bib_file.write_text(
        """@online{used,
  title = {GitHub blog example},
  url = {https://github.blog/example}
}

@online{unused,
  title = {{GitHub Copilot} crosses 20M all-time users},
  url = {https://techcrunch.com/example}
}
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(build_review_artifacts, "REPO_ROOT", tmp_path)

    rows = build_review_artifacts.scan_reference_files([bib_file])

    assert len(rows) == 1
    assert rows[0]["normalized_target"] == "https://github.blog/example"


def test_extract_chapter_reference_items_limits_to_reference_sections(tmp_path) -> None:
    chapter_file = tmp_path / "sample.md"
    chapter_file.write_text(
        """# Sample

本文中の例示 URL: https://example.org/body

## さらに学びたい読者へ

- **Example Book.** https://books.example.org/example

## 参考文献

[1] Example Docs. https://docs.example.org/
""",
        encoding="utf-8",
    )

    items = extract_chapter_reference_items(chapter_file)

    assert [item.line_number for item in items] == [7, 11]
    assert items[0].urls == ("https://books.example.org/example",)
    assert items[1].urls == ("https://docs.example.org/",)


def test_find_missing_chapter_reference_items_uses_title_match(tmp_path) -> None:
    chapter_dir = tmp_path / "chapters"
    reference_dir = tmp_path / "references"
    chapter_dir.mkdir()
    reference_dir.mkdir()

    (chapter_dir / "18_documentation.md").write_text(
        """# ドキュメント

## さらに学びたい読者へ

- **Quarto Documentation.** https://quarto.org/docs/ — 説明文。
""",
        encoding="utf-8",
    )
    bib_file = reference_dir / "ch18.bib"
    bib_file.write_text(
        """@misc{quarto,
  title = {Quarto Documentation},
  url = {https://quarto.org/}
}
""",
        encoding="utf-8",
    )

    missing = find_missing_chapter_reference_items(bib_file, tmp_path)

    assert missing == []


def test_find_missing_chapter_reference_items_reports_unmatched_line(tmp_path) -> None:
    chapter_dir = tmp_path / "chapters"
    reference_dir = tmp_path / "references"
    chapter_dir.mkdir()
    reference_dir.mkdir()

    (chapter_dir / "21_collaboration.md").write_text(
        """# 共同開発

## 参考文献

[1] GitHub Docs. https://docs.github.com/
[2] Raymond, E. S. \"How To Ask Questions The Smart Way\". http://www.catb.org/esr/faqs/smart-questions.html
""",
        encoding="utf-8",
    )
    bib_file = reference_dir / "ch21.bib"
    bib_file.write_text(
        """@misc{ghdocs,
  title = {GitHub Docs},
  url = {https://docs.github.com/}
}
""",
        encoding="utf-8",
    )

    missing = find_missing_chapter_reference_items(bib_file, tmp_path)

    assert len(missing) == 1
    assert missing[0].line_number == 6
    assert "How To Ask Questions The Smart Way" in missing[0].raw_text
