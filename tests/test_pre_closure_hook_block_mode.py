"""Pre-flight smoke checks for 33-4 block-mode behavior."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = ROOT / "skills" / "bmad-agent-cora" / "scripts" / "preclosure_hook.py"


def _load_hook_module():
    spec = importlib.util.spec_from_file_location("preclosure_hook_block_mode", HOOK_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_learning_event_schema_edit_fires_block_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_hook_module()
    assert module.classify_change_window(["state/config/learning-event-schema.yaml"]) == "block"

    class FakeResult:
        returncode = 1
        stdout = (
            "lockstep-check exit=1 "
            "trace=reports/dev-coherence/test/check-pipeline-manifest-lockstep.FAIL.yaml"
        )
        stderr = ""

    monkeypatch.setattr(module.subprocess, "run", lambda *args, **kwargs: FakeResult())
    result = module.run_preclosure_check(
        story_id="33-4",
        diff_paths=["state/config/learning-event-schema.yaml"],
    )
    assert result.classification == "block"
    assert result.permit_closure is False


def test_prose_edit_stays_warn_mode() -> None:
    module = _load_hook_module()
    result = module.run_preclosure_check(
        story_id="33-4",
        diff_paths=["docs/project-context.md", "SESSION-HANDOFF.md"],
    )
    assert result.classification == "warn"
    assert result.permit_closure is True
