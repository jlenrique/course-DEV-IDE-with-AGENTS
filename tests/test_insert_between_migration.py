"""Regression pin for insert_between migration."""

from __future__ import annotations

from pathlib import Path


def test_no_legacy_insert_4a_references_remain() -> None:
    root = Path(__file__).resolve().parents[1]
    hits: list[str] = []
    needle = "insert_4a" + "_between_step_04_and_05"
    for path in root.rglob("*.py"):
        if path.name == "test_insert_between_migration.py":
            continue
        text = path.read_text(encoding="utf-8")
        if needle in text:
            hits.append(str(path.relative_to(root)))

    assert not hits, f"legacy insertion helper still referenced in: {hits}"

