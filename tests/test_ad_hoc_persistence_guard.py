from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch


def _load_guard_module():
    root = Path(__file__).resolve().parents[1]
    module_path = root / "scripts" / "utilities" / "ad_hoc_persistence_guard.py"
    spec = importlib.util.spec_from_file_location("ad_hoc_persistence_guard_local", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


guard = _load_guard_module()


def test_lenient_missing_mode_state_defaults_to_default() -> None:
    missing = Path("Z:/path/that/does/not/exist/mode_state.json")
    with patch.dict("os.environ", {"RUN_MODE_AMBIGUOUS": "lenient"}, clear=False):
        with patch.object(guard, "mode_state_path", return_value=missing):
            assert guard.resolve_run_mode(None) == "default"


def test_strict_missing_mode_state_fails_closed_to_ad_hoc() -> None:
    missing = Path("Z:/path/that/does/not/exist/mode_state.json")
    with patch.dict("os.environ", {"RUN_MODE_AMBIGUOUS": "strict"}, clear=False):
        with patch.object(guard, "mode_state_path", return_value=missing):
            assert guard.resolve_run_mode(None) == "ad-hoc"


def test_strict_invalid_mode_state_blocks_durable_writes(tmp_path: Path) -> None:
    mode_state = tmp_path / "mode_state.json"
    mode_state.write_text("{invalid-json", encoding="utf-8")

    with patch.dict("os.environ", {"RUN_MODE_AMBIGUOUS": "strict"}, clear=False):
        with patch.object(guard, "mode_state_path", return_value=mode_state):
            result = guard.enforce_ad_hoc_boundary("production_run_db", None)

    assert result["allowed"] is False
    assert result["run_mode"] == "ad-hoc"
    assert result["code"] == "NOOP_AD_HOC_AMBIGUOUS_MODE"


def test_tracked_alias_resolves_to_default() -> None:
    result = guard.enforce_ad_hoc_boundary("production_run_db", "tracked")
    assert result["allowed"] is True
    assert result["run_mode"] == "default"
