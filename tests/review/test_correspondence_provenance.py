"""E1生成物コミットとPR provenanceの検証."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.review.check_correspondence_provenance import (
    artifact_changes,
    validate_pr_json,
)
from scripts.review.create_e1_pr import provenance_marker


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def _repository(tmp_path: Path) -> tuple[Path, str, str]:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    review = root / "docs/review"
    review.mkdir(parents=True)
    (review / "code_correspondence.json").write_text("{}\n", encoding="utf-8")
    (review / "code_correspondence.md").write_text("# old\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "source")
    source = _git(root, "rev-parse", "HEAD")
    (review / "code_correspondence.json").write_text(
        '{"schema_version": 4}\n',
        encoding="utf-8",
    )
    (review / "code_correspondence.md").write_text("# new\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "artifacts")
    artifact = _git(root, "rev-parse", "HEAD")
    return root, source, artifact


def test_accepts_direct_artifact_commit(tmp_path: Path) -> None:
    root, source, artifact = _repository(tmp_path)

    changed = artifact_changes(root, source, artifact)

    assert changed == {
        "docs/review/code_correspondence.json",
        "docs/review/code_correspondence.md",
    }


def test_rejects_non_artifact_change(tmp_path: Path) -> None:
    root, source, _ = _repository(tmp_path)
    (root / "chapters").mkdir()
    (root / "chapters/01.md").write_text("# changed\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "unexpected")
    artifact = _git(root, "rev-parse", "HEAD")

    with pytest.raises(ValueError, match="直接の親"):
        artifact_changes(root, source, artifact)


def test_validates_pr_marker(tmp_path: Path) -> None:
    root, source, artifact = _repository(tmp_path)
    marker = provenance_marker(42, source, artifact)
    data = {
        "number": 42,
        "state": "OPEN",
        "body": f"説明\n\n{marker}\n",
        "headRefOid": artifact,
        "mergeCommit": None,
    }

    validate_pr_json(root, data, source, artifact, "OPEN", None)


def test_rejects_duplicate_pr_marker(tmp_path: Path) -> None:
    root, source, artifact = _repository(tmp_path)
    marker = provenance_marker(42, source, artifact)
    data = {
        "number": 42,
        "state": "OPEN",
        "body": f"{marker}\n{marker}\n",
        "headRefOid": artifact,
    }

    with pytest.raises(ValueError, match="ちょうど1件"):
        validate_pr_json(root, data, source, artifact, "OPEN", None)


def test_marker_payload_is_canonical_json() -> None:
    marker = provenance_marker(3, "source", "artifact")
    payload = marker.removeprefix("<!-- e1-provenance: ").removesuffix(" -->")

    assert json.loads(payload) == {
        "pr_number": 3,
        "source_commit": "source",
        "artifact_commit": "artifact",
    }
