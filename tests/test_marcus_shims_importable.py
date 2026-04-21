"""Smoke test: Marcus dispatch shims under scripts/marcus_shims/ are importable.

These are one-shot runner scripts authored during trial runs (e.g.,
C1-M1-PRES-20260419B §12 narration synthesis, §13 Quinn-R pre-composition)
pending CLI canonicalization (follow-on filed in deferred-inventory.md).

This test guards against syntax and import regressions only. Runtime
behavior is exercised via the trial runs themselves, not via unit tests,
because these shims invoke live external APIs (ElevenLabs synthesis,
ffprobe) and touch bundle paths that only exist during a trial.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SHIM_DIR = Path(__file__).resolve().parent.parent / "scripts" / "marcus_shims"


def _shim_paths() -> list[Path]:
    if not SHIM_DIR.is_dir():
        return []
    return sorted(p for p in SHIM_DIR.glob("*.py") if p.name != "__init__.py")


@pytest.mark.parametrize("shim_path", _shim_paths(), ids=lambda p: p.name)
def test_shim_module_loads_without_syntax_or_import_error(shim_path: Path) -> None:
    spec = importlib.util.spec_from_file_location(shim_path.stem, shim_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert hasattr(module, "__file__")
