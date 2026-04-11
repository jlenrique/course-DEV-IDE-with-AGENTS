"""Tests for init_desmond_sanctum.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_init_creates_sanctum(tmp_path: Path) -> None:
    (tmp_path / ".git").write_text("fake", encoding="utf-8")
    script = Path(__file__).resolve().parents[1] / "init_desmond_sanctum.py"
    r = subprocess.run(
        [sys.executable, str(script), "--repo-root", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    sanctum = tmp_path / "_bmad" / "memory" / "bmad-agent-desmond"
    assert (sanctum / "INDEX.md").exists()
    assert (sanctum / "CREED.md").exists()
    assert (sanctum / "sessions").is_dir()
