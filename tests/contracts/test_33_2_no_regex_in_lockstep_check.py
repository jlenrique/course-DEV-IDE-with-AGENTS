"""Contract pin: lockstep checker must avoid regex parsing."""

from __future__ import annotations

import ast
from pathlib import Path


def test_no_re_import_in_check_script() -> None:
    script = (
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "utilities"
        / "check_pipeline_manifest_lockstep.py"
    )
    tree = ast.parse(script.read_text(encoding="utf-8"))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(alias.name != "re" for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            assert node.module != "re"

