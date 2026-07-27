"""第16章のProxyJump設定を検証する."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SSH_CONFIG = PROJECT_ROOT / "scripts" / "ch16" / "ssh_config.example"
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
def test_bastion_alias_expands() -> None:
    """踏み台別名から接続先と利用者が展開される."""
    settings = _expanded_settings("bastion")

    assert settings["hostname"] == "gateway.example.ac.jp"
    assert settings["user"] == "your_username"


@pytest.mark.skipif(SSH is None, reason="sshがインストールされていない")
def test_hpc_alias_uses_bastion() -> None:
    """hpc別名が踏み台、接続先、キープアライブを展開する."""
    settings = _expanded_settings("hpc")

    assert settings["hostname"] == "login.hpc.internal"
    assert settings["user"] == "your_username"
    assert settings["proxyjump"] == "bastion"
    assert settings["serveraliveinterval"] == "60"
