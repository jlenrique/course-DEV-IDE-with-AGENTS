"""Read-only Tracy smoke fixture catalog for Lesson Planner trial support."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
TRACY_SMOKE_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "retrieval" / "tracy_smoke"
TRACY_SMOKE_FIXTURE_CATALOG = (
    "embellish_examples",
    "corroborate_supporting",
    "corroborate_contrasting",
    "gap_fill_background",
)

__all__ = [
    "TRACY_SMOKE_FIXTURE_CATALOG",
    "TRACY_SMOKE_FIXTURE_DIR",
    "list_tracy_smoke_fixtures",
    "load_tracy_smoke_fixture",
]


def list_tracy_smoke_fixtures() -> tuple[str, ...]:
    """Return the canonical Tracy smoke fixture identifiers in stable order."""

    return TRACY_SMOKE_FIXTURE_CATALOG


def load_tracy_smoke_fixture(name: str) -> dict[str, Any]:
    """Load one committed Tracy smoke fixture by catalog name."""

    if name not in TRACY_SMOKE_FIXTURE_CATALOG:
        raise KeyError(f"Unknown Tracy smoke fixture: {name}")
    fixture_path = TRACY_SMOKE_FIXTURE_DIR / f"{name}.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))
