"""第2章の基本SSH設定を検証する."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SSH_CONFIG = PROJECT_ROOT / "scripts" / "ch02" / "ssh_config.example"
SSH = shutil.which("ssh")


def _expanded_settings(host: str) -> dict[str, str]:
    """ssh -Gで展開した設定を辞書として返す."""
    assert SSH is not None
    result = subprocess.run(
        [SSH, "-G", "-F", str(SSH_CONFIG), host],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    settings: dict[str, str] = {}
    for line in result.stdout.splitlines():
        key, separator, value = line.partition(" ")
        if separator:
            settings.setdefault(key, value)
    return settings


@pytest.mark.skipif(SSH is None, reason="sshがインストールされていない")
def test_basic_hpc_alias_expands() -> None:
    """hpc別名から接続先・利用者・鍵が展開される."""
    settings = _expanded_settings("hpc")

    assert settings["hostname"] == "hpc.university.ac.jp"
    assert settings["user"] == "tanaka"
    assert settings["identityfile"].endswith("/.ssh/id_ed25519")
