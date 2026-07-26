"""本文コードと実体資産の精密対応表を生成する共通実装."""

from __future__ import annotations

import ast
import hashlib
import json
import platform
import re
import subprocess
import time
from collections import Counter, defaultdict
from collections.abc import Iterable
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

FENCE_RE = re.compile(r"^\s*(?:>\s*)*(`{3,}|~{3,})\s*([^\s`]*)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
SKIP_MARKER_RE = re.compile(
    r"<!--\s*code-sync:\s*skip\s*(?P<reason>.*?)\s*-->"
)
CHAPTER_FILE_RE = re.compile(r"^(?P<number>\d\d)_")
CHAPTER_DIR_RE = re.compile(r"^ch\d\d$")
DEF_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
RANK = {"E0": 0, "E1": 1, "E2": 2, "E3": 3, "E4": 4, "E5": 5, "EN": 6}
VALID_PLACEMENTS = {"required_scripts", "required_tests", "not_required"}
VALID_EQUIVALENCE = set(RANK)


@dataclass
class Entity:
    """Pythonの定義単位."""

    id: str
    origin: str
    path: str
    chapter: str
    name: str
    kind: str
    line_start: int
    line_end: int
    ast_exact: str
    ast_nodoc: str
    ast_noname: str
    body_statements: list[str]


@dataclass
class SourceBlock:
    """本文から抽出したfenced code block."""

    id: str
    chapter: str
    path: str
    line_start: int
    line_end: int
    lang: str
    heading: str
    heading_markdown: str
    heading_path: list[str]
    context_before: str
    code: str
    sha256: str
    nonempty_lines: int
    parseable: bool | None
    syntax_error: str | None
    category: str
    placement: str
    category_reason: str
    review_required: bool
    skip_reason: str | None = None
    entity_ids: list[str] = field(default_factory=list)
    candidates: list[dict[str, Any]] = field(default_factory=list)


def sha256_text(text: str) -> str:
    """UTF-8文字列のSHA-256を返す."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    """バイト列のSHA-256を返す."""

    return hashlib.sha256(data).hexdigest()


def strip_quote(line: str) -> str:
    """Markdown引用の接頭辞を1段除く."""

    return re.sub(r"^\s*>\s?", "", line)


def strip_inline_comment(line: str) -> str:
    """文字列リテラル外の行末コメントを除く."""

    quote: str | None = None
    index = 0
    while index < len(line):
        char = line[index]
        if quote:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char == "#":
            return line[:index]
        index += 1
    return line


def significant_lines(code: str) -> list[str]:
    """空行・コメント・空白差を除いた比較用行列を返す."""

    result: list[str] = []
    for raw in code.splitlines():
        stripped = strip_inline_comment(raw).strip()
        if stripped:
            result.append(re.sub(r"\s+", " ", stripped))
    return result


def _is_docstring(node: ast.stmt) -> bool:
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    )


class _RemoveDocstrings(ast.NodeTransformer):
    """モジュール・定義の先頭docstringを除く."""

    def _clean(self, node: ast.AST) -> ast.AST:
        body = getattr(node, "body", None)
        if isinstance(body, list) and body and _is_docstring(body[0]):
            node.body = body[1:]  # type: ignore[attr-defined]
        return node

    def visit_Module(self, node: ast.Module) -> ast.AST:
        self.generic_visit(node)
        return self._clean(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        self.generic_visit(node)
        return self._clean(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        self.generic_visit(node)
        return self._clean(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        self.generic_visit(node)
        return self._clean(node)


class _HideDefinitionNames(ast.NodeTransformer):
    """定義名だけを比較対象外にする."""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        self.generic_visit(node)
        node.name = "__DEF__"
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        self.generic_visit(node)
        node.name = "__DEF__"
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        self.generic_visit(node)
        node.name = "__DEF__"
        return node


def _clone_ast(node: ast.AST) -> ast.AST:
    return ast.parse(ast.unparse(node))


def _dump_ast(node: ast.AST) -> str:
    return ast.dump(node, annotate_fields=True, include_attributes=False)


def normalized_ast(
    node: ast.AST,
    *,
    remove_docstrings: bool = False,
    hide_definition_names: bool = False,
) -> str:
    """指定した説明上の差を除いたAST文字列を返す."""

    copied = _clone_ast(node)
    if remove_docstrings:
        copied = _RemoveDocstrings().visit(copied)
    if hide_definition_names:
        copied = _HideDefinitionNames().visit(copied)
    ast.fix_missing_locations(copied)
    return _dump_ast(copied)


def _body_statements(node: ast.AST) -> list[str]:
    copied = _RemoveDocstrings().visit(_clone_ast(node))
    return [_dump_ast(item) for item in getattr(copied, "body", [])]


def _qualified_definitions(tree: ast.AST) -> list[tuple[str, ast.AST]]:
    found: list[tuple[str, ast.AST]] = []

    def walk(body: list[ast.stmt], prefix: str = "") -> None:
        for node in body:
            if isinstance(node, DEF_TYPES):
                name = f"{prefix}.{node.name}" if prefix else node.name
                found.append((name, node))
                walk(getattr(node, "body", []), name)

    walk(getattr(tree, "body", []))
    return found


def _make_entity(
    entity_id: str,
    origin: str,
    path: str,
    chapter: str,
    name: str,
    node: ast.AST,
    *,
    line_offset: int = 0,
) -> Entity:
    line_start = line_offset + int(getattr(node, "lineno", 1))
    line_end = line_offset + int(
        getattr(node, "end_lineno", getattr(node, "lineno", 1))
    )
    return Entity(
        id=entity_id,
        origin=origin,
        path=path,
        chapter=chapter,
        name=name,
        kind=type(node).__name__,
        line_start=line_start,
        line_end=line_end,
        ast_exact=normalized_ast(node),
        ast_nodoc=normalized_ast(node, remove_docstrings=True),
        ast_noname=normalized_ast(
            node,
            remove_docstrings=True,
            hide_definition_names=True,
        ),
        body_statements=_body_statements(node),
    )


def classify_block(
    lang: str,
    code: str,
    headings: list[str],
    context: str,
    parseable: bool | None,
) -> tuple[str, str, str, bool]:
    """規約から機械的に確定できる種別と配置を返す."""

    joined = " / ".join(headings)
    nearby = f"{joined}\n{context}\n{code}"
    if any("演習 " in heading or heading.startswith("演習") for heading in headings):
        return "exercise", "not_required", "演習問題のコード", False
    if "from scripts.ch" in code or "import scripts.ch" in code:
        return "scripts_call", "not_required", "`scripts/` を呼び出す例", False
    bad_markers = (
        "❌",
        "悪い例",
        "悪例",
        "反面教師",
        "バグのある",
        "問題のあるコード",
    )
    if any(marker in nearby for marker in bad_markers):
        return "bad_example", "not_required", "悪例・反面教師を示す文脈", True
    config_languages = {
        "dockerfile",
        "yaml",
        "yml",
        "toml",
        "ini",
        "groovy",
        "makefile",
        "gitignore",
    }
    if lang in config_languages:
        return (
            "config_workflow",
            "required_scripts",
            f"{lang} の設定・ワークフロー",
            True,
        )
    if lang == "python":
        if re.search(
            r"^\s*(?:rule|checkpoint)\s+\w+\s*:",
            code,
            re.MULTILINE,
        ):
            return (
                "config_workflow",
                "required_scripts",
                "Snakefileの規則",
                True,
            )
        if re.search(
            r"^\s*(?:def\s+test_|class\s+Test|@pytest\.fixture|@fixture)",
            code,
            re.MULTILINE,
        ):
            return "test_code", "required_tests", "pytest形式のテストコード", True
        if parseable is False:
            if code.lstrip().startswith(">>>"):
                return "output_data_diagram", "not_required", "REPLセッション", False
            return "pending", "pending", "Pythonタグだが構文解析不能", True
        if re.search(
            r"^\s*(?:async\s+def|def|class)\s+",
            code,
            re.MULTILINE,
        ):
            return (
                "implementation",
                "required_scripts",
                "名前付き実装定義",
                True,
            )
        return "pending", "pending", "トップレベルPython断片", True
    if lang == "bash":
        if (
            "#SBATCH" in code
            or code.startswith("#!")
            or re.search(r"^\s*(?:for|while|if)\b", code, re.MULTILINE)
        ):
            return (
                "config_workflow",
                "required_scripts",
                "実行可能なシェル／ジョブ定義",
                True,
            )
        return "command", "not_required", "コマンド実行例", True
    if lang in {"text", "none", "markdown", "mermaid", "diff"}:
        return (
            "output_data_diagram",
            "not_required",
            f"{lang} の出力・データ・図解候補",
            True,
        )
    if lang in {"json", "sql", "sparql"}:
        return "pending", "pending", f"{lang} 断片は文脈確認が必要", True
    return "pending", "pending", f"未分類の言語タグ: {lang}", True


def extract_source_blocks(
    md_path: Path,
    *,
    root: Path,
) -> tuple[list[SourceBlock], list[Entity]]:
    """1章の全fenced code blockを短さや言語で除外せず抽出する."""

    chapter_match = CHAPTER_FILE_RE.match(md_path.name)
    if chapter_match is None:
        return [], []
    chapter_number = chapter_match.group("number")
    chapter = f"ch{chapter_number}"
    try:
        relative = str(md_path.relative_to(root))
    except ValueError:
        relative = md_path.name
    lines = md_path.read_text(encoding="utf-8").splitlines()
    headings: dict[int, str] = {}
    blocks: list[SourceBlock] = []
    entities: list[Entity] = []
    open_char: str | None = None
    start = 0
    lang = "none"
    buffer: list[str] = []
    heading_snapshot: list[str] = []
    context = ""
    pending_skip: str | None = None
    block_skip: str | None = None

    for line_number, raw in enumerate(lines, 1):
        clean = strip_quote(raw)
        heading_match = HEADING_RE.match(clean)
        if heading_match and open_char is None:
            level = len(heading_match.group(1))
            headings = {key: value for key, value in headings.items() if key < level}
            headings[level] = heading_match.group(2)

        marker = SKIP_MARKER_RE.search(raw)
        if marker and open_char is None:
            pending_skip = marker.group("reason")
            continue

        fence_match = FENCE_RE.match(raw)
        if open_char is None:
            if fence_match is None:
                if clean.strip():
                    pending_skip = None
                continue
            open_char = fence_match.group(1)[0]
            start = line_number
            lang = (fence_match.group(2) or "none").lower()
            buffer = []
            heading_snapshot = [headings[key] for key in sorted(headings)]
            context_start = max(0, start - 9)
            context = "\n".join(
                strip_quote(item) for item in lines[context_start : start - 1]
            )
            block_skip = pending_skip
            pending_skip = None
            continue

        if fence_match and fence_match.group(1)[0] == open_char:
            code = "\n".join(buffer)
            block_id = f"B-{chapter_number}-{len(blocks) + 1:03d}"
            parseable: bool | None = None
            syntax_error: str | None = None
            tree: ast.Module | None = None
            if lang == "python":
                try:
                    tree = ast.parse(code)
                    parseable = True
                except SyntaxError as exc:
                    parseable = False
                    syntax_error = f"{exc.msg} (line {exc.lineno})"
            category, placement, reason, review_required = classify_block(
                lang,
                code,
                heading_snapshot,
                context,
                parseable,
            )
            if block_skip is not None:
                category = "marked_skip"
                placement = "not_required"
                reason = block_skip or "本文のマーカーによる除外"
                review_required = False
            block = SourceBlock(
                id=block_id,
                chapter=chapter,
                path=relative,
                line_start=start,
                line_end=line_number,
                lang=lang,
                heading=heading_snapshot[-1] if heading_snapshot else "",
                heading_markdown=(
                    f"{'#' * max(headings)} {heading_snapshot[-1]}"
                    if heading_snapshot
                    else ""
                ),
                heading_path=heading_snapshot,
                context_before=context,
                code=code,
                sha256=sha256_text(code),
                nonempty_lines=sum(bool(item.strip()) for item in buffer),
                parseable=parseable,
                syntax_error=syntax_error,
                category=category,
                placement=placement,
                category_reason=reason,
                review_required=review_required,
                skip_reason=block_skip,
            )
            if tree is not None:
                for index, (name, node) in enumerate(
                    _qualified_definitions(tree),
                    1,
                ):
                    entity_id = f"{block_id}-E{index:02d}"
                    entities.append(
                        _make_entity(
                            entity_id,
                            "book",
                            relative,
                            chapter,
                            name,
                            node,
                            line_offset=start,
                        )
                    )
                    block.entity_ids.append(entity_id)
            blocks.append(block)
            open_char = None
            block_skip = None
            continue
        buffer.append(clean)

    if open_char is not None:
        raise ValueError(f"閉じていないコードフェンス: {md_path}:{start}")
    return blocks, entities


def extract_all_blocks(root: Path) -> tuple[list[SourceBlock], list[Entity]]:
    """番号付き全章からコードブロックとPython定義を抽出する."""

    blocks: list[SourceBlock] = []
    entities: list[Entity] = []
    for chapter_path in sorted((root / "chapters").glob("[0-9][0-9]_*.md")):
        chapter_blocks, chapter_entities = extract_source_blocks(
            chapter_path,
            root=root,
        )
        blocks.extend(chapter_blocks)
        entities.extend(chapter_entities)
    return blocks, entities


def asset_paths(root: Path, base_name: str) -> list[Path]:
    """`scripts/chNN` または `tests/chNN` の全実ファイルを返す."""

    return sorted(
        path
        for path in (root / base_name).glob("ch[0-9][0-9]/**/*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    )


def extract_assets(
    root: Path,
) -> tuple[list[dict[str, Any]], list[Entity]]:
    """章別スクリプト・テスト資産とPython定義を抽出する."""

    files: list[dict[str, Any]] = []
    entities: list[Entity] = []
    for origin in ("scripts", "tests"):
        for index, path in enumerate(asset_paths(root, origin), 1):
            relative = str(path.relative_to(root))
            chapter = next(
                part for part in path.parts if CHAPTER_DIR_RE.fullmatch(part)
            )
            text = path.read_text(encoding="utf-8", errors="replace")
            file_id = f"{'S' if origin == 'scripts' else 'T'}-{chapter[2:]}-{index:03d}"
            record: dict[str, Any] = {
                "id": file_id,
                "origin": origin,
                "chapter": chapter,
                "path": relative,
                "name": path.name,
                "suffix": path.suffix,
                "sha256": sha256_text(text),
                "line_count": len(text.splitlines()),
                "entity_ids": [],
                "parseable": None,
                "syntax_error": None,
            }
            if path.suffix == ".py":
                try:
                    tree = ast.parse(text)
                    record["parseable"] = True
                    record["module_ast_exact"] = normalized_ast(tree)
                    record["module_ast_nodoc"] = normalized_ast(
                        tree,
                        remove_docstrings=True,
                    )
                    record["module_statements"] = _body_statements(tree)
                    for entity_index, (name, node) in enumerate(
                        _qualified_definitions(tree),
                        1,
                    ):
                        entity_id = f"{file_id}-E{entity_index:03d}"
                        entities.append(
                            _make_entity(
                                entity_id,
                                origin,
                                relative,
                                chapter,
                                name,
                                node,
                            )
                        )
                        record["entity_ids"].append(entity_id)
                except SyntaxError as exc:
                    record["parseable"] = False
                    record["syntax_error"] = f"{exc.msg} (line {exc.lineno})"
            files.append(record)
    return files, entities


def is_subsequence(short: list[str], long: list[str]) -> bool:
    """短い列が長い列の真の順序保存部分列なら真を返す."""

    if not short or len(short) >= len(long):
        return False
    iterator = iter(long)
    return all(any(item == candidate for candidate in iterator) for item in short)


def normalize_nonpython_lines(text: str, lang: str) -> list[str]:
    """非Python資産を順序を保つ行列へ正規化する."""

    result: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if lang not in {"dockerfile", "gitignore"} and stripped.startswith("#"):
            continue
        result.append(re.sub(r"\s+", " ", stripped))
    return result


def add_python_candidates(
    blocks: list[SourceBlock],
    book_entities: list[Entity],
    files: list[dict[str, Any]],
    target_entities: list[Entity],
) -> None:
    """ASTと定義名からPythonブロックの対応候補を追加する."""

    entity_by_id = {
        entity.id: entity for entity in [*book_entities, *target_entities]
    }
    targets_by_exact: dict[str, list[Entity]] = defaultdict(list)
    targets_by_nodoc: dict[str, list[Entity]] = defaultdict(list)
    targets_by_noname: dict[str, list[Entity]] = defaultdict(list)
    targets_by_leaf: dict[str, list[Entity]] = defaultdict(list)
    for entity in target_entities:
        targets_by_exact[entity.ast_exact].append(entity)
        targets_by_nodoc[entity.ast_nodoc].append(entity)
        targets_by_noname[entity.ast_noname].append(entity)
        targets_by_leaf[entity.name.split(".")[-1]].append(entity)

    files_by_chapter: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in files:
        files_by_chapter[item["chapter"]].append(item)

    for block in blocks:
        if block.lang != "python" or block.parseable is not True:
            continue
        expected_origin = "tests" if block.category == "test_code" else "scripts"
        seen: set[tuple[str, str, str | None]] = set()

        def add(
            target: Entity,
            relation: str,
            evidence: str,
            source_entity: str,
        ) -> None:
            key = (target.id, relation, source_entity)
            if key in seen:
                return
            seen.add(key)
            block.candidates.append(
                {
                    "target_id": target.id,
                    "target_file": target.path,
                    "target_entity": target.name,
                    "target_origin": target.origin,
                    "relation_candidate": relation,
                    "evidence": evidence,
                    "source_entity_id": source_entity,
                    "same_chapter": target.chapter == block.chapter,
                }
            )

        for source_id in block.entity_ids:
            source = entity_by_id[source_id]
            pools = (
                ("E0", targets_by_exact[source.ast_exact], "AST完全一致"),
                ("E1", targets_by_nodoc[source.ast_nodoc], "docstring除去AST一致"),
                (
                    "E1",
                    targets_by_noname[source.ast_noname],
                    "定義名を伏せたAST一致",
                ),
            )
            for candidate_stage, pool, evidence in pools:
                for target in pool:
                    if target.origin == expected_origin or block.category == "pending":
                        add(target, candidate_stage, evidence, source_id)
            leaf_name = source.name.split(".")[-1]
            for target in targets_by_leaf[leaf_name]:
                if (
                    target.origin != expected_origin
                    and block.category != "pending"
                ):
                    continue
                if is_subsequence(
                    source.body_statements,
                    target.body_statements,
                ):
                    add(
                        target,
                        "E2",
                        "本文本体が実体本体の順序保存部分列",
                        source_id,
                    )
                elif target.chapter == block.chapter:
                    add(target, "E3", "同章・同名だがAST差", source_id)
                elif source.name == target.name:
                    add(target, "E4", "章をまたぐ同名候補", source_id)

        code_tree = ast.parse(block.code)
        block_exact = normalized_ast(code_tree)
        block_nodoc = normalized_ast(code_tree, remove_docstrings=True)
        block_statements = _body_statements(code_tree)
        for file in files_by_chapter[block.chapter]:
            if (
                file["origin"] != expected_origin
                and block.category != "pending"
            ):
                continue
            relation: str | None = None
            evidence = ""
            if block_exact == file.get("module_ast_exact"):
                relation, evidence = "E0", "ブロックとモジュールのAST完全一致"
            elif block_nodoc == file.get("module_ast_nodoc"):
                relation, evidence = (
                    "E1",
                    "docstring除去後にモジュールAST一致",
                )
            elif is_subsequence(
                block_statements,
                file.get("module_statements", []),
            ):
                relation, evidence = (
                    "E2",
                    "ブロック文がモジュール文の順序保存部分列",
                )
            if relation:
                key = (file["id"], relation, None)
                if key in seen:
                    continue
                seen.add(key)
                block.candidates.append(
                    {
                        "target_id": file["id"],
                        "target_file": file["path"],
                        "target_entity": None,
                        "target_origin": file["origin"],
                        "relation_candidate": relation,
                        "evidence": evidence,
                        "source_entity_id": None,
                        "same_chapter": True,
                    }
                )


def add_nonpython_candidates(
    root: Path,
    blocks: list[SourceBlock],
    files: list[dict[str, Any]],
) -> None:
    """順序を保つ正規化行から非Pythonブロックの候補を追加する."""

    script_files = [item for item in files if item["origin"] == "scripts"]
    text_by_file = {
        item["id"]: (root / item["path"]).read_text(
            encoding="utf-8",
            errors="replace",
        )
        for item in script_files
    }
    lang_hints = {
        "bash": {".sh"},
        "yaml": {".yaml", ".yml"},
        "yml": {".yaml", ".yml"},
        "dockerfile": {"Dockerfile", ".multistage"},
        "makefile": {"Makefile"},
        "gitignore": {".template"},
        "toml": {".toml"},
        "ini": {".ini"},
        "groovy": {".groovy"},
        "markdown": {".md"},
    }
    for block in blocks:
        if block.lang == "python":
            continue
        short = normalize_nonpython_lines(block.code, block.lang)
        if not short:
            continue
        for item in script_files:
            if item["chapter"] != block.chapter:
                continue
            hints = lang_hints.get(block.lang)
            if hints:
                suffix_or_name = item["suffix"] or item["name"]
                if item["name"] not in hints and suffix_or_name not in hints:
                    continue
            long = normalize_nonpython_lines(
                text_by_file[item["id"]],
                block.lang,
            )
            relation: str | None = None
            evidence = ""
            if short == long:
                relation, evidence = "E0", "正規化行列が完全一致"
            elif is_subsequence(short, long):
                relation, evidence = "E2", "正規化行が順序保存部分列"
            else:
                overlap = len(set(short) & set(long)) / len(set(short))
                if overlap >= 0.5:
                    relation = "E4"
                    evidence = f"同章・同種ファイルで行重複 {overlap:.0%}"
            if relation:
                block.candidates.append(
                    {
                        "target_id": item["id"],
                        "target_file": item["path"],
                        "target_entity": None,
                        "target_origin": "scripts",
                        "relation_candidate": relation,
                        "evidence": evidence,
                        "source_entity_id": None,
                        "same_chapter": True,
                    }
                )


def load_overrides(path: Path) -> dict[str, Any]:
    """人手判断台帳を読み、トップレベルのスキーマを検証する."""

    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("override schema_versionは1でなければならない")
    required = {
        "category_overrides",
        "relation_overrides",
        "goldset",
        "substitution_tests",
        "substitution_environment",
    }
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"overrideに必須キーがない: {', '.join(missing)}")
    if not isinstance(data["category_overrides"], dict):
        raise ValueError("category_overridesはobjectでなければならない")
    if not isinstance(data["relation_overrides"], dict):
        raise ValueError("relation_overridesはobjectでなければならない")
    if not isinstance(data["goldset"], list):
        raise ValueError("goldsetはarrayでなければならない")
    if not isinstance(data["substitution_tests"], dict):
        raise ValueError("substitution_testsはobjectでなければならない")
    return data


def _validate_override_hash(
    block_by_id: dict[str, SourceBlock],
    block_id: str,
    entry: dict[str, Any],
    kind: str,
) -> SourceBlock:
    if block_id not in block_by_id:
        raise ValueError(f"{kind}が存在しないブロックを参照: {block_id}")
    block = block_by_id[block_id]
    expected = entry.get("block_sha256")
    if expected != block.sha256:
        raise ValueError(
            f"{kind}のブロックハッシュが古い: {block_id} "
            f"expected={expected} actual={block.sha256}"
        )
    return block


def apply_category_overrides(
    blocks: list[SourceBlock],
    overrides: dict[str, Any],
) -> None:
    """分類overrideを適用し、残る保留を利用紹介へ確定する."""

    block_by_id = {block.id: block for block in blocks}
    for block_id, entry in overrides["category_overrides"].items():
        block = _validate_override_hash(
            block_by_id,
            block_id,
            entry,
            "category override",
        )
        placement = entry.get("placement")
        if placement not in VALID_PLACEMENTS:
            raise ValueError(f"不正なplacement: {block_id}: {placement}")
        block.category = str(entry["category"])
        block.placement = str(placement)
        block.category_reason = str(entry["reason"])
    for block in blocks:
        if block.placement == "pending":
            block.category = "library_usage"
            block.placement = "not_required"
            block.category_reason = (
                "前後を目視し、ライブラリ/API/言語機能の使い方紹介と判定"
            )


def _module_to_path(root: Path, module: str) -> str | None:
    if not module.startswith("scripts."):
        return None
    candidate = root / (module.replace(".", "/") + ".py")
    if candidate.exists():
        return str(candidate.relative_to(root))
    package = root / module.replace(".", "/") / "__init__.py"
    if package.exists():
        return str(package.relative_to(root))
    return None


def imported_script_paths(root: Path, code: str) -> list[str]:
    """コード中の`scripts.*` importを実ファイルへ解決する."""

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    paths: set[str] = set()
    for node in ast.walk(tree):
        module: str | None = None
        if isinstance(node, ast.ImportFrom):
            module = node.module
        elif isinstance(node, ast.Import):
            for alias in node.names:
                path = _module_to_path(root, alias.name)
                if path:
                    paths.add(path)
        if module:
            path = _module_to_path(root, module)
            if path:
                paths.add(path)
    return sorted(paths)


def _relation_from_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "target_file": candidate["target_file"],
        "target_entity": candidate["target_entity"],
        "equivalence": candidate["relation_candidate"],
        "kind": "excerpt",
        "evidence": candidate["evidence"],
        "verification": "AST/順序比較後に章・対象名を目視",
        "cross_chapter": not candidate["same_chapter"],
    }


def _automatic_relations(block: SourceBlock) -> list[dict[str, Any]]:
    expected = "tests" if block.placement == "required_tests" else "scripts"
    candidates = [
        item
        for item in block.candidates
        if item["target_origin"] == expected and item["same_chapter"]
    ]
    if not candidates:
        return []
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in candidates:
        grouped[item["target_file"]].append(item)
    file_best = {
        path: min(items, key=lambda item: RANK[item["relation_candidate"]])
        for path, items in grouped.items()
    }
    best_rank = min(
        RANK[item["relation_candidate"]] for item in file_best.values()
    )
    return sorted(
        (
            _relation_from_candidate(item)
            for item in file_best.values()
            if RANK[item["relation_candidate"]] == best_rank
        ),
        key=lambda item: item["target_file"],
    )


def add_relations(
    root: Path,
    blocks: list[SourceBlock],
    overrides: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    """人手確定関係を優先し、それ以外は安全な自動候補から確定する."""

    block_by_id = {block.id: block for block in blocks}
    relation_overrides = overrides["relation_overrides"]
    for block_id, entry in relation_overrides.items():
        _validate_override_hash(
            block_by_id,
            block_id,
            entry,
            "relation override",
        )

    result: dict[str, list[dict[str, Any]]] = {}
    for block in blocks:
        if block.id in relation_overrides:
            relations = deepcopy(relation_overrides[block.id]["relations"])
        elif block.placement in {"required_scripts", "required_tests"}:
            relations = _automatic_relations(block)
        else:
            relations = []
        if block.category == "scripts_call":
            for path in imported_script_paths(root, block.code):
                relations.append(
                    {
                        "target_file": path,
                        "target_entity": None,
                        "equivalence": "EN",
                        "kind": "reference",
                        "evidence": "本文コードが対象モジュールをimportして呼び出す",
                        "verification": "AST import解析",
                        "cross_chapter": not path.startswith(
                            f"scripts/{block.chapter}/"
                        ),
                    }
                )
        unique: dict[tuple[str, str | None, str], dict[str, Any]] = {}
        for relation in relations:
            equivalence = relation.get("equivalence")
            if equivalence not in VALID_EQUIVALENCE:
                raise ValueError(
                    f"不正なequivalence: {block.id}: {equivalence}"
                )
            relation.setdefault("target_entity", None)
            relation.setdefault(
                "cross_chapter",
                not relation["target_file"].startswith(
                    (
                        f"scripts/{block.chapter}/",
                        f"tests/{block.chapter}/",
                    )
                ),
            )
            key = (
                relation["target_file"],
                relation["target_entity"],
                relation["kind"],
            )
            unique[key] = relation
        result[block.id] = list(unique.values())
    return result


def correspondence_of(
    placement: str,
    relations: list[dict[str, Any]],
) -> str:
    """配置要否と関係からE判定を返す."""

    if placement == "not_required":
        return "EN"
    if not relations:
        return "E5"
    stages = [
        relation["equivalence"]
        for relation in relations
        if relation["equivalence"] != "EN"
    ]
    return max(stages, key=lambda stage: RANK[stage]) if stages else "E5"


def _parse_pytest_count(output: str, word: str) -> int:
    match = re.search(rf"(\d+)\s+{re.escape(word)}\b", output)
    return int(match.group(1)) if match else 0


def collect_test_results(
    root: Path,
    *,
    timeout_seconds: int = 60,
) -> dict[str, dict[str, Any]]:
    """章別とレビュー用の各pytestファイルを個別実行する."""

    pytest_path = root / ".venv" / "bin" / "pytest"
    if not pytest_path.is_file():
        raise FileNotFoundError(f"pytestが見つからない: {pytest_path}")
    paths = [
        *sorted((root / "tests").glob("ch[0-9][0-9]/test_*.py")),
        *sorted((root / "tests" / "review").glob("test_*.py")),
    ]
    results: dict[str, dict[str, Any]] = {}
    for path in paths:
        relative = str(path.relative_to(root))
        started = time.monotonic()
        completed = subprocess.run(
            [
                str(pytest_path),
                relative,
                "-q",
                "-p",
                "no:cacheprovider",
            ],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        output = "\n".join(
            part.strip()
            for part in (completed.stdout, completed.stderr)
            if part.strip()
        )
        results[relative] = {
            "returncode": completed.returncode,
            "passed": _parse_pytest_count(output, "passed"),
            "failed": _parse_pytest_count(output, "failed"),
            "skipped": _parse_pytest_count(output, "skipped"),
            "errors": _parse_pytest_count(output, "error")
            + _parse_pytest_count(output, "errors"),
            "duration_seconds": round(time.monotonic() - started, 3),
            "summary": output.splitlines()[-1] if output else "",
        }
    return results


def validate_test_results(
    root: Path,
    test_results: dict[str, dict[str, Any]],
) -> None:
    """対象テストの漏れと失敗があれば生成前に停止する."""

    expected = {
        str(path.relative_to(root))
        for path in [
            *sorted((root / "tests").glob("ch[0-9][0-9]/test_*.py")),
            *sorted((root / "tests/review").glob("test_*.py")),
        ]
    }
    actual = set(test_results)
    if expected != actual:
        missing = ", ".join(sorted(expected - actual)) or "なし"
        extra = ", ".join(sorted(actual - expected)) or "なし"
        raise ValueError(
            f"個別テスト結果の対象が一致しない: missing={missing}; extra={extra}"
        )
    failed = [
        path
        for path, result in test_results.items()
        if int(result.get("returncode", 1)) != 0
        or int(result.get("failed", 0)) != 0
        or int(result.get("errors", 0)) != 0
    ]
    if failed:
        raise ValueError(
            "失敗した個別テストがある: " + ", ".join(sorted(failed))
        )


def _module_path_from_import(root: Path, module: str) -> str | None:
    return _module_to_path(root, module)


def build_test_mapping(
    root: Path,
    files: list[dict[str, Any]],
    test_results: dict[str, dict[str, Any]],
) -> dict[str, list[dict[str, str]]]:
    """import、命名、直接パス参照から資産とテストを対応付ける."""

    script_files = [item for item in files if item["origin"] == "scripts"]
    test_paths = [
        root / path
        for path in test_results
        if re.match(r"tests/ch\d\d/test_", path)
    ]
    imports: dict[str, set[str]] = defaultdict(set)
    test_text: dict[str, str] = {}
    for path in test_paths:
        relative = str(path.relative_to(root))
        text = path.read_text(encoding="utf-8")
        test_text[relative] = text
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
            elif isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            for module in modules:
                target = _module_path_from_import(root, module)
                if target:
                    imports[target].add(relative)

    mapping: dict[str, list[dict[str, str]]] = {}
    for item in script_files:
        path = item["path"]
        evidence: dict[str, str] = {
            test_path: "direct_import"
            for test_path in imports.get(path, set())
        }
        stem = Path(path).stem
        conventional = f"tests/{item['chapter']}/test_{stem}.py"
        if conventional in test_results:
            evidence.setdefault(conventional, "naming")
        for test_path, text in test_text.items():
            constructed_path = (
                '"scripts"' in text
                and f'"{item["chapter"]}"' in text
                and f'"{item["name"]}"' in text
            )
            if path in text or constructed_path:
                evidence[test_path] = "direct_path_reference"
        mapping[path] = [
            {"test_file": test_path, "evidence": reason}
            for test_path, reason in sorted(evidence.items())
        ]
    return mapping


def summarize_test_results(
    paths: list[str],
    results: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """指定テスト群の結果を集計する."""

    selected_paths = [path for path in paths if path in results]
    if not selected_paths:
        return {
            "status": "no_direct_test",
            "files": [],
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
        }
    selected = [results[path] for path in selected_paths]
    failed = sum(int(item["failed"]) for item in selected)
    errors = sum(int(item["errors"]) for item in selected)
    skipped = sum(int(item["skipped"]) for item in selected)
    status = (
        "failed"
        if failed or errors
        else "passed_with_skip"
        if skipped
        else "passed"
    )
    return {
        "status": status,
        "files": selected_paths,
        "passed": sum(int(item["passed"]) for item in selected),
        "failed": failed,
        "skipped": skipped,
        "errors": errors,
    }


def source_snapshot(root: Path, paths: Iterable[Path]) -> str:
    """相対パスと内容を順序付きでハッシュ化する."""

    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _file_role(item: dict[str, Any]) -> str:
    path = Path(item["path"])
    name = path.name
    if name == "__init__.py":
        return "package_support"
    if "data" in path.parts:
        return "data_support"
    if name.startswith(("plot_", "generate_")):
        return "figure_generation"
    if name.endswith((".template", ".example")) or name == "project_readme_template.md":
        return "template_support"
    if name in {"Dockerfile", "Dockerfile.multistage", "Snakefile", "Makefile"}:
        return "config_workflow"
    if path.suffix in {".yaml", ".yml", ".sh", ".def"}:
        return "config_workflow"
    if "validate" in name or "check_" in name:
        return "validator"
    if "demo" in name:
        return "demo"
    return "implementation"


def _test_asset_role(item: dict[str, Any]) -> str:
    path = Path(item["path"])
    if path.name == "__init__.py":
        return "package_support"
    if path.name == "conftest.py":
        return "fixture_support"
    if path.name.startswith("test_") and path.suffix == ".py":
        return "pytest_file"
    if "data" in path.parts or path.suffix in {
        ".fasta",
        ".fastq",
        ".csv",
        ".tsv",
    }:
        return "test_data"
    return "test_support"


def _last_update(
    root: Path,
    path: str,
    start: int | None = None,
    end: int | None = None,
) -> str | None:
    if start is not None and end is not None:
        command = [
            "git",
            "log",
            "-1",
            "--format=%cI",
            "-L",
            f"{start},{end}:{path}",
        ]
    else:
        command = ["git", "log", "-1", "--format=%cI", "--", path]
    completed = subprocess.run(
        command,
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    for line in completed.stdout.splitlines():
        if re.match(r"\d{4}-\d\d-\d\dT", line):
            return line
    return None


def _current_commit(root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.stdout.strip() or "unknown"


def _validate_substitution_results(
    root: Path,
    blocks: list[SourceBlock],
    overrides: dict[str, Any],
    file_by_path: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    block_by_id = {block.id: block for block in blocks}
    expected_environment = overrides.get("substitution_environment", {})
    if expected_environment:
        pytest_binary = root / ".venv/bin/pytest"
        actual_pytest = (
            subprocess.run(
                [str(pytest_binary), "--version"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            ).stdout.strip()
            if pytest_binary.is_file()
            else "not available"
        )
        if expected_environment.get("python") != platform.python_version():
            raise ValueError("substitution testのPython環境が変わっている")
        if expected_environment.get("pytest") != actual_pytest:
            raise ValueError("substitution testのpytest環境が変わっている")
    results: dict[str, dict[str, Any]] = {}
    for key, entry in overrides["substitution_tests"].items():
        block_id = entry.get("block_id")
        target_file = entry.get("target_file")
        if block_id not in block_by_id:
            raise ValueError(f"substitution testのblockが存在しない: {key}")
        if target_file not in file_by_path:
            raise ValueError(f"substitution testのtargetが存在しない: {key}")
        if entry.get("block_sha256") != block_by_id[block_id].sha256:
            raise ValueError(f"substitution testのblockハッシュが古い: {key}")
        actual_target_hash = file_by_path[target_file]["sha256"]
        if entry.get("target_sha256") != actual_target_hash:
            raise ValueError(f"substitution testのtargetハッシュが古い: {key}")
        test_files = entry.get("test_files", [])
        test_file_hashes = entry.get("test_file_sha256", {})
        if set(test_files) != set(test_file_hashes):
            raise ValueError(f"substitution testのテスト証拠が不足: {key}")
        for test_file, expected_hash in test_file_hashes.items():
            if test_file not in file_by_path:
                raise ValueError(
                    f"substitution testのテストファイルが存在しない: {key}"
                )
            if file_by_path[test_file]["sha256"] != expected_hash:
                raise ValueError(
                    f"substitution testのテストハッシュが古い: {key}"
                )
        result = {
            result_key: deepcopy(value)
            for result_key, value in entry.items()
            if result_key
            not in {
                "block_sha256",
                "target_sha256",
                "test_file_sha256",
            }
        }
        results[key] = result
    return results


def build_inventory(
    root: Path,
    overrides: dict[str, Any],
    test_results: dict[str, dict[str, Any]],
    *,
    generated_at: str | None = None,
    include_history: bool = True,
) -> dict[str, Any]:
    """ソース、override、実テスト結果から精密対応表を生成する."""

    validate_test_results(root, test_results)
    blocks, book_entities = extract_all_blocks(root)
    files, target_entities = extract_assets(root)
    apply_category_overrides(blocks, overrides)
    add_python_candidates(blocks, book_entities, files, target_entities)
    add_nonpython_candidates(root, blocks, files)
    relation_by_block = add_relations(root, blocks, overrides)

    file_by_path = {item["path"]: item for item in files}
    file_id_by_path = {path: item["id"] for path, item in file_by_path.items()}
    entity_locations: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(
        list
    )
    for entity in target_entities:
        entity_locations[(entity.path, entity.name)].append(
            {
                "id": entity.id,
                "name": entity.name,
                "kind": entity.kind,
                "line_start": entity.line_start,
                "line_end": entity.line_end,
            }
        )

    block_records: list[dict[str, Any]] = []
    for block in blocks:
        relations = relation_by_block[block.id]
        for relation in relations:
            target_file = relation["target_file"]
            if target_file not in file_id_by_path:
                raise ValueError(
                    f"relationのtarget_fileが存在しない: "
                    f"{block.id}: {target_file}"
                )
            relation["target_file_id"] = file_id_by_path[target_file]
            target_entity = relation.get("target_entity")
            locations = (
                sorted(
                    entity_locations.get((target_file, target_entity), []),
                    key=lambda item: (item["line_start"], item["id"]),
                )
                if target_entity
                else []
            )
            if target_entity and not locations and target_entity.startswith("rule "):
                rule_name = target_entity.removeprefix("rule ")
                target_lines = (root / target_file).read_text(
                    encoding="utf-8"
                ).splitlines()
                locations = [
                    {
                        "id": (
                            f"{relation['target_file_id']}-RULE-{rule_name}"
                        ),
                        "name": target_entity,
                        "kind": "SnakefileRule",
                        "line_start": line_number,
                        "line_end": line_number,
                    }
                    for line_number, line in enumerate(target_lines, 1)
                    if re.match(
                        rf"^\s*rule\s+{re.escape(rule_name)}\s*:",
                        line,
                    )
                ]
            relation["target_entity_locations"] = locations
        record = asdict(block)
        record["relations"] = relations
        record["correspondence"] = correspondence_of(
            block.placement,
            relations,
        )
        for key in (
            "code",
            "context_before",
            "heading_markdown",
            "candidates",
            "entity_ids",
            "review_required",
            "parseable",
            "syntax_error",
            "skip_reason",
        ):
            record.pop(key, None)
        block_records.append(record)

    test_mapping = build_test_mapping(root, files, test_results)
    for block_record in block_records:
        related_tests: set[str] = set()
        if block_record["placement"] == "required_tests":
            related_tests.update(
                relation["target_file"]
                for relation in block_record["relations"]
                if relation["target_file"].startswith("tests/")
            )
        else:
            for relation in block_record["relations"]:
                for item in test_mapping.get(relation["target_file"], []):
                    related_tests.add(item["test_file"])
        block_record["tests"] = summarize_test_results(
            sorted(related_tests),
            test_results,
        )

    body_relations: dict[str, list[str]] = defaultdict(list)
    reference_relations: dict[str, list[str]] = defaultdict(list)
    for block_record in block_records:
        for relation in block_record["relations"]:
            destination = (
                reference_relations
                if relation["kind"] == "reference"
                else body_relations
            )
            destination[relation["target_file"]].append(block_record["id"])

    chapter_text = {
        f"ch{path.name[:2]}": path.read_text(encoding="utf-8")
        for path in sorted((root / "chapters").glob("[0-9][0-9]_*.md"))
    }
    script_views: list[dict[str, Any]] = []
    test_asset_views: list[dict[str, Any]] = []
    for item in files:
        if item["origin"] == "scripts":
            tests = test_mapping.get(item["path"], [])
            mentioned = (
                item["path"] in chapter_text[item["chapter"]]
                or item["name"] in chapter_text[item["chapter"]]
            )
            body_ids = sorted(set(body_relations.get(item["path"], [])))
            reference_ids = sorted(
                set(reference_relations.get(item["path"], []))
            )
            if body_ids:
                book_status = "body_correspondence"
            elif reference_ids or mentioned:
                book_status = "reference_only"
            else:
                book_status = "script_only"
            script_views.append(
                {
                    "id": item["id"],
                    "path": item["path"],
                    "chapter": item["chapter"],
                    "sha256": item["sha256"],
                    "line_count": item["line_count"],
                    "role": _file_role(item),
                    "book_status": book_status,
                    "body_block_ids": body_ids,
                    "reference_block_ids": reference_ids,
                    "mentioned_in_chapter_prose": mentioned,
                    "tests": tests,
                    "test_result": summarize_test_results(
                        [entry["test_file"] for entry in tests],
                        test_results,
                    ),
                }
            )
        else:
            path = item["path"]
            test_asset_views.append(
                {
                    "id": item["id"],
                    "path": path,
                    "chapter": item["chapter"],
                    "sha256": item["sha256"],
                    "line_count": item["line_count"],
                    "role": _test_asset_role(item),
                    "body_block_ids": sorted(
                        set(body_relations.get(path, []))
                    ),
                    "reference_block_ids": sorted(
                        set(reference_relations.get(path, []))
                    ),
                    "test_result": test_results.get(path),
                }
            )

    if include_history:
        history_cache: dict[
            tuple[str, int | None, int | None],
            str | None,
        ] = {}
        for block_record in block_records:
            if block_record["correspondence"] != "E3":
                continue
            book_key = (
                block_record["path"],
                block_record["line_start"] + 1,
                block_record["line_end"] - 1,
            )
            if book_key not in history_cache:
                history_cache[book_key] = _last_update(root, *book_key)
            for relation in block_record["relations"]:
                if relation["equivalence"] != "E3":
                    continue
                target_key = (relation["target_file"], None, None)
                if target_key not in history_cache:
                    history_cache[target_key] = _last_update(
                        root,
                        relation["target_file"],
                    )
                relation["history"] = {
                    "book_last_update": history_cache[book_key],
                    "target_last_update": history_cache[target_key],
                    "target_granularity": "file",
                }

    substitution_results = _validate_substitution_results(
        root,
        blocks,
        overrides,
        file_by_path,
    )
    for block_record in block_records:
        block_record["substitution_tests"] = [
            result
            for result in substitution_results.values()
            if result["block_id"] == block_record["id"]
        ]

    block_by_id = {block["id"]: block for block in block_records}
    goldset: list[dict[str, Any]] = []
    for expected in overrides["goldset"]:
        block_id = expected["block_id"]
        if block_id not in block_by_id:
            raise ValueError(f"goldsetのblockが存在しない: {block_id}")
        actual = block_by_id[block_id]["correspondence"]
        goldset.append(
            {
                "block_id": block_id,
                "expected": expected["expected"],
                "actual": actual,
                "matched": actual == expected["expected"],
                "reason": expected["reason"],
            }
        )

    placements = Counter(block["placement"] for block in block_records)
    categories = Counter(block["category"] for block in block_records)
    correspondence = Counter(
        block["correspondence"] for block in block_records
    )
    required_blocks = [
        block
        for block in block_records
        if block["placement"] in {"required_scripts", "required_tests"}
    ]
    required_correspondence = Counter(
        block["correspondence"] for block in required_blocks
    )
    test_totals = {
        "files": len(test_results),
        "chapter_test_files": sum(
            path.startswith("tests/ch") for path in test_results
        ),
        "review_test_files": sum(
            path.startswith("tests/review") for path in test_results
        ),
        "passed": sum(int(item["passed"]) for item in test_results.values()),
        "failed": sum(int(item["failed"]) for item in test_results.values()),
        "skipped": sum(int(item["skipped"]) for item in test_results.values()),
        "errors": sum(int(item["errors"]) for item in test_results.values()),
    }
    source_paths = [
        *sorted((root / "chapters").glob("[0-9][0-9]_*.md")),
        *asset_paths(root, "scripts"),
        *asset_paths(root, "tests"),
    ]
    pytest_binary = root / ".venv/bin/pytest"
    pytest_version = (
        subprocess.run(
            [str(pytest_binary), "--version"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        ).stdout.strip()
        if pytest_binary.is_file()
        else "not available"
    )
    metadata = overrides.get("review_metadata", {})
    output = {
        "schema_version": 3,
        "generated_at": generated_at
        or datetime.now().astimezone().isoformat(timespec="seconds"),
        "method": (
            "docs/review/2026-07-25_code_correspondence_reaudit_plan.md"
        ),
        "source_commit": _current_commit(root),
        "source_snapshot_sha256": source_snapshot(root, source_paths),
        "environment": {
            "python": platform.python_version(),
            "pytest": pytest_version,
            "test_command": ".venv/bin/pytest tests/ -q -p no:cacheprovider",
        },
        "summary": {
            "chapters": len(
                list((root / "chapters").glob("[0-9][0-9]_*.md"))
            ),
            "book_blocks": len(block_records),
            "script_files": len(script_views),
            "test_files_under_chapters": len(test_asset_views),
            "languages": dict(Counter(block.lang for block in blocks)),
            "categories": dict(categories),
            "placements": dict(placements),
            "correspondence_all": dict(correspondence),
            "correspondence_required": dict(required_correspondence),
            "script_book_status": dict(
                Counter(view["book_status"] for view in script_views)
            ),
            "script_test_status": dict(
                Counter(view["test_result"]["status"] for view in script_views)
            ),
            "test_run": test_totals,
            "substitution_test_status": dict(
                Counter(
                    result["status"]
                    for result in substitution_results.values()
                )
            ),
        },
        "blocks": block_records,
        "scripts": script_views,
        "test_assets": test_asset_views,
        "test_files": test_results,
        "classification_review": {
            "pending_resolved": int(metadata.get("pending_resolved", 0)),
            "manual_category_overrides": len(
                overrides["category_overrides"]
            ),
            "manual_relation_blocks": len(
                overrides["relation_overrides"]
            ),
            "note": str(metadata.get("note", "")),
            "goldset_method": str(metadata.get("goldset_method", "")),
            "goldset": goldset,
        },
        "substitution_tests": substitution_results,
    }
    return output


def _table_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_report(data: dict[str, Any]) -> str:
    """精密対応表JSONから人向けMarkdownレポートを生成する."""

    summary = data["summary"]
    blocks = data["blocks"]
    correspondence = summary["correspondence_all"]
    placements = summary["placements"]
    required_total = int(placements.get("required_scripts", 0)) + int(
        placements.get("required_tests", 0)
    )
    generated_date = str(data["generated_at"]).split("T", maxsplit=1)[0]
    lines = [
        "# 本文コード ↔ `scripts/ch*` 対応関係の再監査",
        "",
        f"- 生成日: {generated_date}",
        f"- 対象コミット: `{data['source_commit']}`",
        "- 調査計画: "
        "[`2026-07-25_code_correspondence_reaudit_plan.md`]"
        "(./2026-07-25_code_correspondence_reaudit_plan.md)",
        "- E5解消計画: "
        "[`2026-07-25_e5_remediation_plan.md`]"
        "(./2026-07-25_e5_remediation_plan.md)",
        "- 全件表: [`code_correspondence.json`](./code_correspondence.json)",
        "",
        "本書の配置規約を先に適用し、その後に対応と本質的一致を判定した。",
        "演習、悪例、ライブラリ紹介、コマンド、出力例など、規約上実体を",
        "必要としないブロックは「欠落」に数えずENとして全件表に残した。",
        "",
        "## 1. 結論",
        "",
        "| 判定 | 件数 | 意味 |",
        "|---|---:|---|",
    ]
    meanings = {
        "E0": "コメント・空白を除いて同一",
        "E1": "docstringや説明上の差を除けば同じ処理",
        "E2": "実体と矛盾しない抜粋",
        "E3": "対応はあるが構造または振る舞いに差がある",
        "E4": "対応候補はあるが確定していない",
        "E5": "配置が必要だが対応実体がない",
        "EN": "規約上、対応実体は不要",
    }
    for stage in ("E0", "E1", "E2", "E3", "E4", "E5", "EN"):
        count = int(correspondence.get(stage, 0))
        if count or stage != "E4":
            lines.append(f"| {stage} | {count} | {meanings[stage]} |")
    lines.extend(
        [
            f"| **合計** | **{summary['book_blocks']}** | 全本文ブロック |",
            "",
            f"配置が必要なブロックは{required_total}件である。"
            f"E5は{correspondence.get('E5', 0)}件であり、"
            "具体的な解消順序はE5解消計画に記録した。",
            "",
            f"`scripts/ch*` 側は全{summary['script_files']}ファイルで、"
            f"本文コードと直接対応"
            f"{summary['script_book_status'].get('body_correspondence', 0)}件、"
            f"本文から参照のみ"
            f"{summary['script_book_status'].get('reference_only', 0)}件、"
            f"本文コードとの対応なし"
            f"{summary['script_book_status'].get('script_only', 0)}件である。",
            "",
            "## 2. 章別集計",
            "",
            "| 章 | 全ブロック | 配置必須 | E0 | E1 | E2 | E3 | E4 | E5 | EN |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    chapters = sorted({block["chapter"] for block in blocks})
    totals: Counter[str] = Counter()
    for chapter in chapters:
        chapter_blocks = [
            block for block in blocks if block["chapter"] == chapter
        ]
        chapter_corr = Counter(
            block["correspondence"] for block in chapter_blocks
        )
        required = sum(
            block["placement"] in {"required_scripts", "required_tests"}
            for block in chapter_blocks
        )
        values = {
            "all": len(chapter_blocks),
            "required": required,
            **{stage: chapter_corr.get(stage, 0) for stage in RANK},
        }
        totals.update(values)
        lines.append(
            f"| {chapter} | {values['all']} | {values['required']} | "
            f"{values['E0']} | {values['E1']} | {values['E2']} | "
            f"{values['E3']} | {values['E4']} | {values['E5']} | "
            f"{values['EN']} |"
        )
    lines.extend(
        [
            f"| **合計** | **{totals['all']}** | **{totals['required']}** | "
            f"**{totals['E0']}** | **{totals['E1']}** | "
            f"**{totals['E2']}** | **{totals['E3']}** | "
            f"**{totals['E4']}** | **{totals['E5']}** | "
            f"**{totals['EN']}** |",
            "",
            "## 3. 対応実体がないブロック",
            "",
            "| ID | 章・開始行 | 種別 | 見出し |",
            "|---|---|---|---|",
        ]
    )
    e5_blocks = [
        block for block in blocks if block["correspondence"] == "E5"
    ]
    if e5_blocks:
        for block in e5_blocks:
            lines.append(
                f"| `{block['id']}` | `{block['chapter']}` "
                f"L{block['line_start']} | "
                f"{_table_escape(block['category'])} | "
                f"{_table_escape(block['heading'])} |"
            )
    else:
        lines.append("| — | — | — | E5は0件 |")

    lines.extend(
        [
            "",
            "## 4. 対応はあるが差があるブロック",
            "",
            "| ブロック | 対応先 | 差し替え結果 | 差の根拠 |",
            "|---|---|---|---|",
        ]
    )
    e3_blocks = [
        block for block in blocks if block["correspondence"] == "E3"
    ]
    for block in e3_blocks:
        substitutions = {
            item["target_file"]: item for item in block["substitution_tests"]
        }
        for relation in block["relations"]:
            if relation["equivalence"] != "E3":
                continue
            substitution = substitutions.get(relation["target_file"])
            if substitution is None:
                result = "対象外"
            elif substitution["status"] == "not_run":
                result = f"未実行: {substitution['reason']}"
            else:
                result = str(substitution.get("summary", substitution["status"]))
            lines.append(
                f"| `{block['id']}` | `{relation['target_file']}` | "
                f"{_table_escape(result)} | "
                f"{_table_escape(relation['evidence'])} |"
            )
    if not e3_blocks:
        lines.append("| — | — | — | E3は0件 |")

    test_run = summary["test_run"]
    lines.extend(
        [
            "",
            "## 5. テスト状況",
            "",
            "全対象テストファイルを個別実行し、その結果を対応表へ保存した。",
            "",
            "| 項目 | 結果 |",
            "|---|---:|",
            f"| テストファイル | {test_run['files']} |",
            f"| 章別テストファイル | {test_run['chapter_test_files']} |",
            f"| レビュー用テストファイル | {test_run['review_test_files']} |",
            f"| passed | {test_run['passed']} |",
            f"| skipped | {test_run['skipped']} |",
            f"| failed | {test_run['failed']} |",
            f"| errors | {test_run['errors']} |",
            "",
            "## 6. 多対多対応",
            "",
        ]
    )
    multi_target = [
        block for block in blocks if len(block["relations"]) > 1
    ]
    lines.extend(
        [
            f"1ブロックから複数ファイルへの対応は{len(multi_target)}件ある。",
            "",
            "| 本文ブロック | 対応先 |",
            "|---|---|",
        ]
    )
    for block in multi_target:
        targets = "、".join(
            f"`{relation['target_file']}`"
            for relation in block["relations"]
        )
        lines.append(f"| `{block['id']}` | {targets} |")
    if not multi_target:
        lines.append("| — | なし |")

    script_only = [
        item
        for item in data["scripts"]
        if item["book_status"] == "script_only"
    ]
    lines.extend(
        [
            "",
            "## 7. 実体側だけにあるファイル",
            "",
            f"本文コードとの対応がない資産は{len(script_only)}件である。",
            "個別の役割とテスト結果は全件表の`scripts`に記録した。",
            "",
            "| 役割 | ファイル数 |",
            "|---|---:|",
        ]
    )
    for role, count in sorted(
        Counter(item["role"] for item in script_only).items()
    ):
        lines.append(f"| {role} | {count} |")

    review = data["classification_review"]
    lines.extend(
        [
            "",
            "## 8. 手法と検証",
            "",
            "1. 文字数や言語で除外せず、番号付き章の全コードブロックを抽出した",
            "2. `scripts/ch*` と `tests/ch*` の全実ファイルを別母集団で抽出した",
            "3. 機械分類後、ハッシュ付きoverride台帳の人手判断を適用した",
            "4. Python AST、定義名、順序保存部分列、非Python正規化行を候補生成に使った",
            "5. import、命名、直接パス参照から実体とテストを対応付けた",
            "6. 独立監査でソースハッシュ、ID、参照先、集計、Markdownを再計算する",
            "",
            f"分類overrideは{review['manual_category_overrides']}件、"
            f"関係overrideは{review['manual_relation_blocks']}件である。"
            "override対象の本文ハッシュが変わった場合、生成処理は停止する。",
            "",
            "## 9. 全件表の読み方",
            "",
            "`blocks`は本文ブロック、`scripts`はスクリプト資産、"
            "`test_assets`は章別テスト資産、`test_files`は個別実行結果を保持する。",
            "各関係の`target_file_id`は`scripts`または`test_assets`のIDへ"
            "解決され、定義単位の対応には`target_entity_locations`を記録する。",
            "",
            "## 10. 限界",
            "",
            "1. テスト成功は現行テスト範囲の観測であり、完全な意味論的等価の証明ではない",
            "2. 非Python資産は統一構文木を持たないため、正規化行と人手確認を併用する",
            "3. Git履歴は本文が行範囲、対応先がファイル単位であり偽陽性がありうる",
            "4. 実体配置の要否は現行の執筆規約に基づく",
            "",
        ]
    )
    return "\n".join(lines)


def normalized_for_determinism(data: dict[str, Any]) -> dict[str, Any]:
    """日時・所要時間などを除いた再現性比較用のコピーを返す."""

    copied = deepcopy(data)
    copied.pop("generated_at", None)
    copied.pop("source_commit", None)
    for result in copied.get("test_files", {}).values():
        result.pop("duration_seconds", None)
        if "summary" in result:
            result["summary"] = re.sub(
                r" in \d+(?:\.\d+)?s$",
                "",
                result["summary"],
            )
    for result in copied.get("substitution_tests", {}).values():
        if "summary" in result:
            result["summary"] = re.sub(
                r" in \d+(?:\.\d+)?s$",
                "",
                result["summary"],
            )
    for block in copied.get("blocks", []):
        for substitution in block.get("substitution_tests", []):
            if "summary" in substitution:
                substitution["summary"] = re.sub(
                    r" in \d+(?:\.\d+)?s$",
                    "",
                    substitution["summary"],
                )
    return copied
