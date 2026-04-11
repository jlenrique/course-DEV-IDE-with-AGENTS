"""Tests for refresh_descript_reference.py."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch


def _load_refresh_module():
    refresh_path = Path(__file__).resolve().parents[1] / "refresh_descript_reference.py"
    spec = importlib.util.spec_from_file_location("refresh_descript_reference", refresh_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_dry_run_lists_enabled(tmp_path: Path) -> None:
    skill = tmp_path / "bmad-agent-desmond"
    (skill / "references" / "cache").mkdir(parents=True)
    reg = {"sources": [{"id": "t1", "url": "https://example.com/help", "enabled": True}]}
    (skill / "references" / "descript-doc-registry.json").write_text(
        json.dumps(reg), encoding="utf-8"
    )
    rdr = _load_refresh_module()
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = rdr.main(["--dry-run", "--skill-root", str(skill)])
    assert code == 0
    out = buf.getvalue()
    assert "DRY-RUN" in out and "t1" in out


def test_fetch_writes_snapshot(tmp_path: Path) -> None:
    skill = tmp_path / "bmad-agent-desmond"
    (skill / "references" / "cache").mkdir(parents=True)
    reg = {"sources": [{"id": "t2", "url": "https://example.com/page", "enabled": True}]}
    (skill / "references" / "descript-doc-registry.json").write_text(
        json.dumps(reg), encoding="utf-8"
    )

    def fake_fetch(url: str, timeout: float = 30.0) -> tuple[int, bytes]:
        return 200, b"<html>ok</html>"

    rdr = _load_refresh_module()
    with patch.object(rdr, "fetch_url", fake_fetch):
        code = rdr.main(["--skill-root", str(skill)])
    assert code == 0

    out = skill / "references" / "cache" / "t2.snapshot.txt"
    assert out.exists()
    body = out.read_text(encoding="utf-8")
    assert "t2" in body and "<html>ok</html>" in body


def test_cli_invocation_smoke() -> None:
    script = Path(__file__).resolve().parents[1] / "refresh_descript_reference.py"
    r = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0
    assert "dry-run" in r.stdout.lower()
