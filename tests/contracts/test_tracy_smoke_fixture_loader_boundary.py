"""Boundary tests for the Story 28-4 Tracy smoke fixture loader."""

from __future__ import annotations

import ast
from pathlib import Path


def test_tracy_smoke_fixture_loader_keeps_read_only_boundary() -> None:
    module_path = (
        Path(__file__).resolve().parents[2]
        / "skills"
        / "bmad_agent_tracy"
        / "scripts"
        / "smoke_fixtures.py"
    )
    tree = ast.parse(module_path.read_text(encoding="utf-8"))

    forbidden_roots = {
        "posture_dispatcher",
        "irene_bridge",
        "requests",
        "httpx",
        "aiohttp",
        "urllib",
        "socket",
    }
    imported_roots: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert forbidden_roots.isdisjoint(imported_roots)
