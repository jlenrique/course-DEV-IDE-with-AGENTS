"""Contract guard: learning-event lockstep check must stay AST-driven."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECK_PATH = ROOT / "scripts" / "utilities" / "check_learning_event_lockstep.py"


def test_check_learning_event_lockstep_no_re_import() -> None:
    source = CHECK_PATH.read_text(encoding="utf-8")
    assert "import re" not in source
    assert "import regex" not in source
    assert ".match(" not in source
    assert ".search(" not in source
    assert ".findall(" not in source
