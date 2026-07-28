#!/usr/bin/env python3
"""固定Git refのスキーマ3対応表からE1バッチ0状態を生成する."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.review.e1_remediation import (  # noqa: E402
    baseline_e1_ids,
    load_fixture,
    pending_comment_record,
)


def _git_bytes(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode(errors="replace").strip()
        raise ValueError(f"git {' '.join(args)} に失敗: {detail}")
    return result.stdout


def build_batch0_state(
    root: Path,
    baseline_ref: str,
    fixture: dict[str, Any],
) -> dict[str, Any]:
    """基準blobを検査し、決定的な遷移状態へ正規化する."""
    relative = "docs/review/code_correspondence.json"
    raw = _git_bytes(root, "show", f"{baseline_ref}:{relative}")
    data = json.loads(raw)
    ids = baseline_e1_ids(fixture)
    blocks = {
        block["id"]: block
        for block in data.get("blocks", [])
        if block.get("id") in set(ids)
    }
    if data.get("schema_version") != 3:
        raise ValueError("バッチ0の基準対応表はschema_version 3が必要")
    if data.get("source_commit") != fixture["baseline_source_commit"]:
        raise ValueError("バッチ0のsource_commitがfixtureと異なる")
    if set(blocks) != set(ids):
        raise ValueError("バッチ0のE1 ID集合がfixtureと異なる")
    if any(block["correspondence"] != "E1" for block in blocks.values()):
        raise ValueError("バッチ0の固定45 IDにE1以外が含まれる")
    if {
        block_id: blocks[block_id]["placement"] for block_id in ids
    } != fixture["placements"]:
        raise ValueError("バッチ0のplacementがfixtureと異なる")
    expected_batch = fixture["batches"]["0"]
    if data["summary"]["correspondence_all"] != expected_batch["correspondence"]:
        raise ValueError("バッチ0のE件数がfixtureと異なる")
    relation_count = sum(len(block["relations"]) for block in blocks.values())
    if relation_count != expected_batch["relation_count"]:
        raise ValueError("バッチ0の関係件数がfixtureと異なる")

    normalized = (
        json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode()
    blob_oid = _git_bytes(
        root,
        "rev-parse",
        f"{baseline_ref}:{relative}",
    ).decode().strip()
    return {
        "schema_version": 1,
        "kind": "e1_batch0_transition_state",
        "baseline_ref": baseline_ref,
        "baseline_blob_oid": blob_oid,
        "baseline_normalized_sha256": hashlib.sha256(normalized).hexdigest(),
        "source_commit": data["source_commit"],
        "remediation_scope": {
            "baseline_commit": baseline_ref,
            "baseline_e1_ids": ids,
            "baseline_e1_sha256": fixture["baseline_e1_sha256"],
            "completed_batch": 0,
        },
        "summary": {
            "correspondence_all": expected_batch["correspondence"],
            "e1_relation_count": relation_count,
        },
        "comment_sync": [
            pending_comment_record(block_id, fixture["comment_expectations"][block_id])
            for block_id in ids
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--baseline-ref", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    fixture = load_fixture(root)
    state = build_batch0_state(root, args.baseline_ref, fixture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"E1バッチ0状態を生成: {args.output}")


if __name__ == "__main__":
    main()
