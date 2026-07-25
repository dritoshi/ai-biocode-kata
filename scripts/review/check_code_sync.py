#!/usr/bin/env python3
"""本文と scripts/ の同期チェックスクリプト

CLAUDE.md「本文と `scripts/` の同期」の規約に基づき、章の本文にある
コードブロックが `scripts/chNN/` `tests/chNN/` の実体とどれだけ一致するかを測る。

本書は本文から執筆・レビューするため、放置すると本文だけが修正され
`scripts/` が取り残される。その乖離を定量化し、棚卸しの対象を洗い出す。

照合先には非Pythonファイル（Snakefile, config.yaml 等）とサブディレクトリ
（scripts/ch05/mylib/ 等）、および tests/ を含める。これらを漏らすと
乖離を過大に評価する。

照合する言語は python だけではない。CLAUDE.md の表は「設定・ワークフロー
定義」も `scripts/` への配置を求めるため、Dockerfile・YAML・Makefile も
対象とする。これらは `ast.parse` に失敗するが、それを除外の理由にしない。

CLAUDE.md の「`scripts/` に置くコード・置かないコード」の表のうち、
機械的に判定できるもの（呼び出し例・悪例・演習・REPL）は自動で除外する。
「ライブラリの使い方紹介」は自動判定できないため、一致率が低いものを
「要棚卸し」として提示し、人間の判断に委ねる。

要棚卸しは2種に分けて報告する。取るべき対応が異なるため。

- 乖離: 章に同種のファイルがあるのに食い違う → `scripts/` を先に直す
- 新規候補: 章に同種のファイルが無い → `scripts/` に起こすか判断する

既知の制約:

- 一致率は行の集合の包含率であり、順序や文脈は見ない。「完全一致」は
  コードが同一である保証ではなく、全行がそのファイルのどこかに存在する
  ことを意味する。判定は乖離を見落とす方向（偽陰性）に働く
- 照合は章内に閉じる。他章の実体を参照する例（§15 に出てくる Snakemake の
  rule は `scripts/ch14/Snakefile` が対応する）は「乖離」と報告される。
  章をまたいで照合すると無関係な一致が増えるため、あえて広げていない

判断済みのブロックは、コードブロックの直前に次のコメントを置くことで
除外できる。棚卸しの結果をここに記録する。

    <!-- code-sync: skip ライブラリ紹介のため scripts/ には置かない -->

結果を JSON に保存する。既定の出力先は docs/review/code_sync_check.json。
"""

import argparse
import ast
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CHAPTERS_DIR = PROJECT_ROOT / "chapters"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
TESTS_DIR = PROJECT_ROOT / "tests"
DEFAULT_OUTPUT = PROJECT_ROOT / "docs" / "review" / "code_sync_check.json"

# 同期の検証対象とする言語タグ。
# CLAUDE.md の表は「設定・ワークフロー定義」も scripts/ への配置を求めるため、
# python だけでなく Dockerfile・YAML・Makefile も照合する。
# Snakefile は Python 拡張構文のため python タグが付く。
TARGET_LANGS = {"python", "dockerfile", "yaml", "makefile"}

# 行コメントの開始文字。python / yaml / dockerfile / makefile はいずれも "#"
COMMENT_CHAR = "#"

# 言語タグごとの「対応しうるファイル」の見分け方。
# 一致率0%のとき、章に同種のファイルが存在しないのか（新規作成の候補）、
# 存在するのに食い違うのか（乖離）を区別するために使う。対応が必要な作業が
# 異なるため、まとめて報告すると棚卸しの判断を誤る。
LANG_FILE_HINTS: dict[str, tuple[str, ...]] = {
    "python": (".py", "Snakefile"),
    "yaml": (".yml", ".yaml"),
    "dockerfile": ("Dockerfile", ".def"),
    "makefile": ("Makefile",),
}

# これ未満の行数のブロックは断片として扱い、検証対象外とする
MIN_SIGNIFICANT_LINES = 3

# 一致率のしきい値
THRESHOLD_EXACT = 0.999
THRESHOLD_NEAR = 0.8
THRESHOLD_PARTIAL = 0.5

# 棚卸しの判断を本文に記録するためのマーカー
SKIP_MARKER_RE = re.compile(r"<!--\s*code-sync:\s*skip\s*(?P<reason>.*?)\s*-->")

# 章ファイル名から章ディレクトリ名を得る（04_data_formats.md -> ch04）
CHAPTER_RE = re.compile(r"^(\d\d)_")

# コードフェンス。コラム内は "> ```python" のように引用接頭辞が付く
FENCE_RE = re.compile(r"^\s*```(\w*)")
QUOTE_PREFIX_RE = re.compile(r"^\s*>\s?")
HEADING_RE = re.compile(r"^#{2,4} ")

# CLAUDE.md の表のうち機械的に判定できるカテゴリ
EXCLUSION_RULES: list[tuple[str, str]] = [
    ("scripts_call", r"^(from|import)\s+scripts\."),
    ("bad_example", r"❌|悪い例|アンチパターン|危険:|誤り:"),
    ("repl", r"^\s*>>>"),
]

# Snakefile は Python 拡張構文のため ast.parse に失敗するが、
# CLAUDE.md の表では「設定・ワークフロー定義」として scripts/ への配置が必要。
# Python として解釈できないことを理由に検証対象から外してはならない。
SNAKEMAKE_RE = re.compile(
    r"^\s*(rule\s+\w+:|configfile:|include:|workdir:)", re.MULTILINE
)


@dataclass
class Block:
    """本文から抽出したコードブロック1件."""

    file: str
    line: int
    lang: str
    heading: str
    signature: list[str] = field(default_factory=list)
    category: str = "checked"
    reason: str = ""
    ratio: float = 0.0
    best_match: str = ""
    counterpart: bool = True


def strip_inline_comment(line: str) -> str:
    """行末コメントを落とす。文字列リテラル内の "#" は残す.

    本書は「コードブロック内のコメントは日本語」を規約とし、本文には解説
    コメントを付けて `scripts/` には付けない（あるいは別の文言にする）ことが
    多い。これを残したまま比較すると、同一のコードが不一致と判定される。

    判定は1行内で完結し、複数行にまたがる文字列は追跡しない。本文と
    `scripts/` の双方に同じ処理を適用するため、多少崩れても比較の一貫性は
    保たれる。
    """
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
        elif char == COMMENT_CHAR:
            return line[:index]
        index += 1
    return line


def significant_lines(code: str) -> list[str]:
    """比較用に意味のある行だけを残す.

    空行・コメント行・行末コメントを落とし、連続する空白を1つに畳む。
    本文にだけ付いた説明コメントや字下げの差で不一致にならないようにするため。
    """
    result: list[str] = []
    for raw in code.split("\n"):
        stripped = strip_inline_comment(raw).strip()
        if stripped:
            result.append(re.sub(r"\s+", " ", stripped))
    return result


def chapter_dir_name(md_name: str) -> str | None:
    """章ファイル名から scripts/tests のディレクトリ名を得る."""
    match = CHAPTER_RE.match(md_name)
    return f"ch{match.group(1)}" if match else None


def build_corpus(chapter: str) -> dict[str, set[str]]:
    """章に対応する scripts/ tests/ の全ファイルを読み込む.

    非Pythonファイル（Snakefile, config.yaml 等）とサブディレクトリも含める。
    """
    corpus: dict[str, set[str]] = {}
    for base in (SCRIPTS_DIR / chapter, TESTS_DIR / chapter):
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            if path.name == "__init__.py":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            corpus[str(path.relative_to(PROJECT_ROOT))] = set(significant_lines(text))
    return corpus


def classify(
    code: str, heading: str, skip_reason: str | None, lang: str = "python"
) -> tuple[str, str]:
    """ブロックを CLAUDE.md の分類表に照らして仕分ける.

    Python として解釈できるかの判定は `python` タグのブロックにのみ適用する。
    Dockerfile・YAML・Makefile は当然 `ast.parse` に失敗するため、これを
    検証対象から外す理由にしてはならない。CLAUDE.md の表では設定・
    ワークフロー定義も `scripts/` への配置が必要である。

    Returns
    -------
    tuple[str, str]
        カテゴリ名と、その判定理由
    """
    if skip_reason is not None:
        return "marked_skip", skip_reason or "本文のマーカーによる除外"
    if "演習 " in heading:
        return "exercise", "演習問題のコードは問題文中にインライン配置する規約"
    for name, pattern in EXCLUSION_RULES:
        if re.search(pattern, code, re.MULTILINE):
            return name, f"パターン一致: {pattern}"
    if lang != "python":
        return "checked", f"設定・ワークフロー定義（{lang}）として検証対象"
    if SNAKEMAKE_RE.search(code):
        return "checked", "Snakefile（設定・ワークフロー定義として検証対象）"
    try:
        ast.parse(code)
    except SyntaxError:
        return "not_python", "Python として解釈できない（図解・出力例・抜粋の可能性）"
    return "checked", ""


def best_ratio(signature: list[str], corpus: dict[str, set[str]]) -> tuple[float, str]:
    """ブロックの行が最もよく含まれるファイルとその一致率を返す."""
    unique = set(signature)
    if not unique:
        return 0.0, ""
    best, where = 0.0, ""
    for path, body in corpus.items():
        ratio = len(unique & body) / len(unique)
        if ratio > best:
            best, where = ratio, path
    return best, where


def has_counterpart(lang: str, corpus: dict[str, set[str]]) -> bool:
    """章の scripts/ tests/ に、その言語に対応しうるファイルがあるか."""
    for hint in LANG_FILE_HINTS.get(lang, ()):
        for path in corpus:
            name = Path(path).name
            if hint.startswith(".") and name.endswith(hint):
                return True
            if not hint.startswith(".") and name.startswith(hint):
                return True
    return False


def bucket_of(ratio: float) -> str:
    """一致率を報告用の区分に変換する."""
    if ratio >= THRESHOLD_EXACT:
        return "exact"
    if ratio >= THRESHOLD_NEAR:
        return "near"
    if ratio >= THRESHOLD_PARTIAL:
        return "partial"
    if ratio > 0:
        return "slight"
    return "none"


def extract_blocks(md_path: Path) -> list[Block]:
    """章ファイルからコードブロックを抽出する.

    コラム内のブロックは行頭に "> " が付くため、これを除いてから解釈する。
    """
    blocks: list[Block] = []
    lines = md_path.read_text(encoding="utf-8").split("\n")
    in_block = False
    lang = ""
    buffer: list[str] = []
    start = 0
    heading = ""
    skip_reason: str | None = None
    pending_skip: str | None = None

    for number, raw in enumerate(lines, start=1):
        if HEADING_RE.match(raw):
            heading = raw.strip()
        marker = SKIP_MARKER_RE.search(raw)
        if marker and not in_block:
            pending_skip = marker.group("reason")
            continue

        body = QUOTE_PREFIX_RE.sub("", raw)
        fence = FENCE_RE.match(body)

        if fence and not in_block:
            in_block = True
            lang = fence.group(1) or "none"
            buffer = []
            start = number
            skip_reason = pending_skip
            pending_skip = None
        elif fence and in_block:
            in_block = False
            code = "\n".join(buffer)
            signature = significant_lines(code)
            if len(signature) >= MIN_SIGNIFICANT_LINES:
                if lang in TARGET_LANGS:
                    category, reason = classify(code, heading, skip_reason, lang)
                else:
                    # 検証対象外の言語も記録する。黙って飛ばすと
                    # 「網羅した」と誤読されるため（no silent skips）
                    category, reason = "other_lang", f"検証対象外の言語タグ: {lang}"
                blocks.append(
                    Block(
                        file=md_path.name,
                        line=start,
                        lang=lang,
                        heading=heading,
                        signature=signature,
                        category=category,
                        reason=reason,
                    )
                )
            skip_reason = None
        elif in_block:
            buffer.append(body)
        elif raw.strip():
            pending_skip = None  # 直前の行がマーカーでなければ無効化

    return blocks


def analyze() -> tuple[list[Block], dict[str, int], dict[str, dict[str, int]]]:
    """全章を走査して分類と一致率を求める."""
    all_blocks: list[Block] = []
    corpus_cache: dict[str, dict[str, set[str]]] = {}

    for md_path in sorted(CHAPTERS_DIR.glob("*.md")):
        chapter = chapter_dir_name(md_path.name)
        if chapter is None:
            continue
        if chapter not in corpus_cache:
            corpus_cache[chapter] = build_corpus(chapter)
        corpus = corpus_cache[chapter]

        for block in extract_blocks(md_path):
            if block.category == "checked":
                block.ratio, block.best_match = best_ratio(block.signature, corpus)
                block.counterpart = has_counterpart(block.lang, corpus)
            all_blocks.append(block)

    categories: dict[str, int] = {}
    per_file: dict[str, dict[str, int]] = {}
    for block in all_blocks:
        categories[block.category] = categories.get(block.category, 0) + 1
        if block.category == "checked":
            name = bucket_of(block.ratio)
            per_file.setdefault(block.file, {})
            per_file[block.file][name] = per_file[block.file].get(name, 0) + 1
    return all_blocks, categories, per_file


def render_summary(
    blocks: list[Block], categories: dict[str, int], unsynced: list[Block]
) -> str:
    """人が読む要約を組み立てる."""
    checked = [b for b in blocks if b.category == "checked"]
    totals: dict[str, int] = {}
    for block in checked:
        name = bucket_of(block.ratio)
        totals[name] = totals.get(name, 0) + 1

    labels = {
        "exact": "完全一致",
        "near": f"ほぼ一致（{int(THRESHOLD_NEAR * 100)}-99%）",
        "partial": f"部分一致（{int(THRESHOLD_PARTIAL * 100)}-79%）",
        "slight": "わずか（1-49%）",
        "none": "該当なし（0%）",
    }
    cat_labels = {
        "marked_skip": "本文マーカーで除外",
        "exercise": "演習問題",
        "bad_example": "悪例・反面教師",
        "scripts_call": "scripts の呼び出し例",
        "repl": "REPL セッション",
        "not_python": "Python でない（図解・出力例・抜粋）",
    }

    out = ["=== 本文↔scripts 同期チェック ===", ""]
    out.append(f"全コードブロック（{MIN_SIGNIFICANT_LINES}行以上）: {len(blocks)}")
    out.append(f"照合する言語タグ: {', '.join(sorted(TARGET_LANGS))}")
    out.append("")
    out.append("規約により検証対象外:")
    for key, label in cat_labels.items():
        if categories.get(key):
            out.append(f"  {label:34} {categories[key]:4}")
    other = [b for b in blocks if b.category == "other_lang"]
    if other:
        by_lang: dict[str, int] = {}
        for block in other:
            by_lang[block.lang] = by_lang.get(block.lang, 0) + 1
        detail = " ".join(f"{k}:{v}" for k, v in sorted(by_lang.items()))
        out.append(f"  {'照合対象外の言語':34} {len(other):4}  ({detail})")
    out.append("")
    out.append(f"検証対象: {len(checked)}")
    for key in ("exact", "near", "partial", "slight", "none"):
        count = totals.get(key, 0)
        share = count / len(checked) * 100 if checked else 0.0
        bar = "#" * round(share / 100 * 32)
        out.append(f"  {labels[key]:22} {count:4}  {bar} {share:.0f}%")
    out.append("")
    out.append(
        f"要棚卸し（一致率 {int(THRESHOLD_PARTIAL * 100)}% 未満）: {len(unsynced)}"
    )
    no_counterpart = [b for b in unsynced if not b.counterpart]
    out.append(
        f"  ├ 実体があるのに食い違う（乖離）      {len(unsynced) - len(no_counterpart):4}"
    )
    out.append(f"  └ 章に同種のファイルが無い（新規候補）{len(no_counterpart):4}")
    out.append(
        "  ※ 一致率は行の集合の包含率であり、順序や文脈は見ない。"
        "「完全一致」はコードが同一である保証ではなく、"
        "全行がそのファイルのどこかに存在することを意味する"
    )
    out.append(
        "  ※ 要棚卸しには「ライブラリの使い方紹介」など "
        "scripts/ に置く必要のないものが含まれる。件数がそのまま作業量ではない"
    )
    return "\n".join(out)


def read_previous_unsynced(path: Path) -> int | None:
    """前回の出力から要棚卸し件数を読む.

    コミット済みの JSON がベースラインになるため、上書きする前に読んで
    増減を示す。壊れていたり形式が違えば None を返し、報告を省く。
    """
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    value = data.get("unsynced_count")
    return value if isinstance(value, int) else None


def main() -> None:
    """コマンドラインから実行する."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="JSON 出力先。既定は docs/review/code_sync_check.json",
    )
    parser.add_argument(
        "--max-unsynced",
        type=int,
        default=None,
        help="要棚卸しがこの件数を超えたら終了コード1で終わる（CI 用。既定は判定しない）",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="要棚卸しのブロックを一覧表示する",
    )
    args = parser.parse_args()

    blocks, categories, per_file = analyze()
    unsynced = sorted(
        (b for b in blocks if b.category == "checked" and b.ratio < THRESHOLD_PARTIAL),
        key=lambda b: (b.file, b.line),
    )

    print(render_summary(blocks, categories, unsynced))
    if args.list:
        print("\n=== 要棚卸し一覧 ===")
        for block in unsynced:
            where = block.best_match or "-"
            kind = "乖離" if block.counterpart else "新規候補"
            print(
                f"  {block.file}:{block.line:<5} {block.ratio * 100:3.0f}% "
                f"[{kind:4}] {block.lang:10} → {where:34} {block.heading[:30]}"
            )

    # 既存の出力（コミット済みのベースライン）と比べて増減を示す。
    # 上書き前に読むこと。
    previous = read_previous_unsynced(args.output)
    if previous is not None:
        delta = len(unsynced) - previous
        sign = "+" if delta > 0 else ""
        state = "変化なし" if delta == 0 else f"{sign}{delta}"
        print(f"\n前回の記録 {previous} 件からの増減: {state}")

    payload = {
        "check": "code_sync_check",
        "thresholds": {
            "exact": THRESHOLD_EXACT,
            "near": THRESHOLD_NEAR,
            "partial": THRESHOLD_PARTIAL,
            "min_significant_lines": MIN_SIGNIFICANT_LINES,
        },
        "categories": categories,
        "per_file": per_file,
        "unsynced_count": len(unsynced),
        "blocks": [
            {k: v for k, v in asdict(b).items() if k != "signature"} for b in blocks
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\n結果を {args.output.relative_to(PROJECT_ROOT)} に保存しました。")

    if args.max_unsynced is not None and len(unsynced) > args.max_unsynced:
        raise SystemExit(
            f"要棚卸しが {len(unsynced)} 件で上限 {args.max_unsynced} 件を超えている。"
        )


if __name__ == "__main__":
    main()
