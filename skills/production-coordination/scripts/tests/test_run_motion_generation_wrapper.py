from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "run_motion_generation.py"
)
SPEC = importlib.util.spec_from_file_location("production_run_motion_generation", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_wrapper_delegates_to_target_module(monkeypatch) -> None:
    monkeypatch.setattr(MODULE.TARGET_MODULE, "main", lambda argv=None: 7)
    assert MODULE.main(["--example"]) == 7
