"""本文と BibTeX の対応判定ヘルパ."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote


ENTRY_START_RE = re.compile(r"^\s*@(?P<entry_type>\w+)\{(?P<key>[^,]+),\s*$")
FIELD_RE = re.compile(r"^\s*(?P<field>[A-Za-z]+)\s*=\s*(?P<value>.+?)\s*,?\s*$")
URL_COMMAND_RE = re.compile(r"\\url\{(https?://[^}]+)\}")
RAW_URL_RE = re.compile(r"https?://[^\s}]+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")
ANGLE_URL_RE = re.compile(r"<(https?://[^>]+)>")
SECTION_TITLES = ("さらに学びたい読者へ", "参考文献")


@dataclass(frozen=True)
class BibEntry:
    entry_type: str
    key: str
    fields: dict[str, str]
    field_lines: dict[str, int]
    start_line: int
    end_line: int


@dataclass(frozen=True)
class ChapterUsageContext:
    raw_text: str
    normalized_text: str
    normalized_title_text: str


@dataclass(frozen=True)
class ChapterReferenceItem:
    section_title: str
    line_number: int
    raw_text: str
    urls: tuple[str, ...]
    normalized_text: str
    normalized_title_text: str


def reference_file_to_chapter_path(reference_path: Path, repo_root: Path) -> Path | None:
    """`references/*.bib` に対応する章ファイルを返す."""
    try:
        relative = reference_path.resolve().relative_to((repo_root / "references").resolve())
    except ValueError:
        return None

    stem = relative.stem
    chapter_dir = repo_root / "chapters"

    if stem == "appendix_a":
        candidate = chapter_dir / "appendix_a_learning_patterns.md"
        return candidate if candidate.exists() else None
    if stem == "hajimeni":
        candidate = chapter_dir / "hajimeni.md"
        return candidate if candidate.exists() else None
    if not stem.startswith("ch"):
        return None

    matches = sorted(chapter_dir.glob(f"{stem[2:]}_*.md"))
    return matches[0] if matches else None


def parse_bib_entries(path: Path) -> list[BibEntry]:
    """BibTeX ファイルを行単位で単純にパースする."""
    entries: list[BibEntry] = []
    current_type: str | None = None
    current_key: str | None = None
    current_fields: dict[str, str] = {}
    current_field_lines: dict[str, int] = {}
    current_start_line: int | None = None

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        start_match = ENTRY_START_RE.match(line)
        if start_match:
            if current_type is not None and current_key is not None and current_start_line is not None:
                entries.append(
                    BibEntry(
                        entry_type=current_type,
                        key=current_key,
                        fields=current_fields,
                        field_lines=current_field_lines,
                        start_line=current_start_line,
                        end_line=line_number - 1,
                    )
                )
            current_type = start_match.group("entry_type")
            current_key = start_match.group("key")
            current_fields = {}
            current_field_lines = {}
            current_start_line = line_number
            continue

        if current_type is None or current_key is None or current_start_line is None:
            continue

        if line.strip() == "}":
            entries.append(
                BibEntry(
                    entry_type=current_type,
                    key=current_key,
                    fields=current_fields,
                    field_lines=current_field_lines,
                    start_line=current_start_line,
                    end_line=line_number,
                )
            )
            current_type = None
            current_key = None
            current_fields = {}
            current_field_lines = {}
            current_start_line = None
            continue

        field_match = FIELD_RE.match(line)
        if not field_match:
            continue

        field_name = field_match.group("field").lower()
        current_fields[field_name] = field_match.group("value").strip()
        current_field_lines[field_name] = line_number

    if current_type is not None and current_key is not None and current_start_line is not None:
        entries.append(
            BibEntry(
                entry_type=current_type,
                key=current_key,
                fields=current_fields,
                field_lines=current_field_lines,
                start_line=current_start_line,
                end_line=current_start_line,
            )
        )

    return entries


def extract_explicit_url(entry: BibEntry) -> tuple[str, int] | None:
    """`url` / `howpublished` から閲覧用 URL を取り出す."""
    for field_name in ("url", "howpublished"):
        value = entry.fields.get(field_name)
        if not value:
            continue

        command_match = URL_COMMAND_RE.search(value)
        if command_match:
            return command_match.group(1), entry.field_lines[field_name]

        raw_match = RAW_URL_RE.search(value)
        if raw_match:
            return raw_match.group(0), entry.field_lines[field_name]

    return None


def extract_doi(entry: BibEntry) -> tuple[str, int] | None:
    """DOI フィールドとその行番号を返す."""
    doi = entry.fields.get("doi")
    if not doi:
        return None
    return doi.strip("{}"), entry.field_lines["doi"]


def build_chapter_usage_context(chapter_text: str) -> ChapterUsageContext:
    """本文照合用に正規化した文字列を用意する."""
    return ChapterUsageContext(
        raw_text=chapter_text,
        normalized_text=_normalize_text(chapter_text),
        normalized_title_text=_normalize_title_text(chapter_text),
    )


def bib_entry_is_used(entry: BibEntry, context: ChapterUsageContext) -> bool:
    """BibTeX 項目が対応章に現れるかを判定する."""
    explicit_url = extract_explicit_url(entry)
    if explicit_url is not None:
        url = _normalize_text(explicit_url[0].rstrip("/"))
        if url and (url in context.normalized_text or f"{url}/" in context.normalized_text):
            return True

    doi = extract_doi(entry)
    if doi is not None and doi[0].lower() in context.normalized_text:
        return True

    title = entry.fields.get("title", "")
    normalized_title = _normalize_title_text(title)
    if normalized_title and normalized_title in context.normalized_title_text:
        return True

    return False


def iter_used_bib_entries(reference_path: Path, repo_root: Path) -> list[BibEntry]:
    """本文で使われている BibTeX 項目だけを返す."""
    entries = parse_bib_entries(reference_path)
    chapter_path = reference_file_to_chapter_path(reference_path, repo_root)
    if chapter_path is None or not chapter_path.exists():
        return entries

    context = build_chapter_usage_context(chapter_path.read_text(encoding="utf-8"))
    return [entry for entry in entries if bib_entry_is_used(entry, context)]


def find_unused_bib_entries(reference_path: Path, repo_root: Path) -> list[BibEntry]:
    """本文で使われていない BibTeX 項目を返す."""
    entries = parse_bib_entries(reference_path)
    chapter_path = reference_file_to_chapter_path(reference_path, repo_root)
    if chapter_path is None or not chapter_path.exists():
        return []

    context = build_chapter_usage_context(chapter_path.read_text(encoding="utf-8"))
    return [entry for entry in entries if not bib_entry_is_used(entry, context)]


def extract_chapter_reference_items(
    chapter_path: Path, section_titles: tuple[str, ...] = SECTION_TITLES
) -> list[ChapterReferenceItem]:
    """指定セクション内の参考文献項目を抽出する."""
    items: list[ChapterReferenceItem] = []
    active_section: str | None = None
    active_level: int | None = None
    in_code_fence = False

    for line_number, line in enumerate(chapter_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            if title in section_titles:
                active_section = title
                active_level = level
                continue
            if active_section is not None and active_level is not None and level <= active_level:
                active_section = None
                active_level = None

        if active_section is None:
            continue

        urls = extract_external_urls_from_line(line)
        if not urls:
            continue

        items.append(
            ChapterReferenceItem(
                section_title=active_section,
                line_number=line_number,
                raw_text=line.strip(),
                urls=tuple(urls),
                normalized_text=_normalize_text(line),
                normalized_title_text=_normalize_title_text(line),
            )
        )

    return items


def chapter_reference_item_matches_bib_entry(item: ChapterReferenceItem, entry: BibEntry) -> bool:
    """章内の参考文献項目が BibTeX 項目と一致するか判定する."""
    item_urls = {_normalize_url_for_match(url) for url in item.urls}

    explicit_url = extract_explicit_url(entry)
    if explicit_url is not None and _normalize_url_for_match(explicit_url[0]) in item_urls:
        return True

    doi = extract_doi(entry)
    if doi is not None:
        doi_url = doi[0] if doi[0].startswith("http") else f"https://doi.org/{doi[0]}"
        if _normalize_url_for_match(doi_url) in item_urls:
            return True
        if doi[0].lower() in item.normalized_text:
            return True

    title = entry.fields.get("title", "")
    normalized_title = _normalize_title_text(title)
    if normalized_title and normalized_title in item.normalized_title_text:
        return True

    return False


def find_missing_chapter_reference_items(reference_path: Path, repo_root: Path) -> list[ChapterReferenceItem]:
    """章内の参考文献項目で `.bib` に対応がないものを返す."""
    chapter_path = reference_file_to_chapter_path(reference_path, repo_root)
    if chapter_path is None or not chapter_path.exists():
        return []

    items = extract_chapter_reference_items(chapter_path)
    entries = parse_bib_entries(reference_path)
    return [item for item in items if not any(chapter_reference_item_matches_bib_entry(item, entry) for entry in entries)]


def extract_external_urls_from_line(line: str) -> list[str]:
    """1 行の Markdown から外部 URL を重複なく抽出する."""
    urls: list[str] = []
    inline_code_spans = find_inline_code_spans(line)
    consumed_spans: list[tuple[int, int]] = []

    for pattern in (MARKDOWN_LINK_RE, ANGLE_URL_RE):
        for match in pattern.finditer(line):
            if is_inside_spans(match.start(), inline_code_spans):
                continue
            urls.append(_clean_line_url(match.group(1)))
            consumed_spans.append((match.start(), match.end()))

    for match in RAW_URL_RE.finditer(line):
        if is_inside_spans(match.start(), inline_code_spans):
            continue
        if any(start <= match.start() < end for start, end in consumed_spans):
            continue
        urls.append(_clean_line_url(match.group(0)))

    deduped: list[str] = []
    seen: set[str] = set()
    for url in urls:
        if url in seen:
            continue
        deduped.append(url)
        seen.add(url)

    return deduped


def find_inline_code_spans(line: str) -> list[tuple[int, int]]:
    """インラインコードの span を返す."""
    spans: list[tuple[int, int]] = []
    stack: tuple[str, int] | None = None
    index = 0

    while index < len(line):
        if line[index] != "`":
            index += 1
            continue

        end = index
        while end < len(line) and line[end] == "`":
            end += 1

        fence = line[index:end]
        if stack is None:
            stack = (fence, index)
        elif stack[0] == fence:
            spans.append((stack[1], end))
            stack = None
        index = end

    return spans


def is_inside_spans(index: int, spans: list[tuple[int, int]]) -> bool:
    return any(start <= index < end for start, end in spans)


def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"\\[A-Za-z]+\{([^}]*)\}", r"\1", text)
    text = text.replace("---", " ").replace("--", " ")
    text = text.replace("{", "").replace("}", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _normalize_title_text(text: str) -> str:
    text = _normalize_text(text)
    text = re.sub(r"[^\w\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _clean_line_url(url: str) -> str:
    return url.rstrip('`"\'.:,;)')


def _normalize_url_for_match(url: str) -> str:
    return _normalize_text(unquote(_clean_line_url(url))).rstrip("/")
