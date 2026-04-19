"""Tests for Cora pre-closure hook block/warn classification behavior."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = ROOT / "skills" / "bmad-agent-cora" / "scripts" / "preclosure_hook.py"


def _load_hook_module():
    spec = importlib.util.spec_from_file_location("preclosure_hook_module", HOOK_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "path",
    [
        "state/config/pipeline-manifest.yaml",
        "scripts/utilities/check_pipeline_manifest_lockstep.py",
        "scripts/utilities/run_hud.py",
        "marcus/orchestrator/workflow_runner.py",
        "docs/workflow/production-prompt-pack-v4.2-foo.md",
    ],
)
def test_classify_workflow_stage_paths_returns_block(path: str) -> None:
    module = _load_hook_module()
    assert module.classify_change_window([path]) == "block"


@pytest.mark.parametrize(
    "path",
    [
        "README.md",
        "docs/project-context.md",
        "tests/test_unrelated.py",
    ],
)
def test_classify_non_trigger_paths_returns_warn(path: str) -> None:
    module = _load_hook_module()
    assert module.classify_change_window([path]) == "warn"


def test_run_preclosure_check_blocks_on_l1_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_hook_module()

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
        diff_paths=["state/config/pipeline-manifest.yaml"],
    )
    assert result.classification == "block"
    assert result.permit_closure is False
    assert result.l1_exit_code == 1
    assert result.l1_trace_path is not None
    assert "Story close-out blocked: lockstep check flagged divergence." in result.operator_message


def test_run_preclosure_check_permits_on_l1_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_hook_module()

    class FakeResult:
        returncode = 0
        stdout = (
            "lockstep-check exit=0 "
            "trace=reports/dev-coherence/test/check-pipeline-manifest-lockstep.PASS.yaml"
        )
        stderr = ""

    monkeypatch.setattr(module.subprocess, "run", lambda *args, **kwargs: FakeResult())
    result = module.run_preclosure_check(
        story_id="33-4",
        diff_paths=["scripts/utilities/run_hud.py"],
    )
    assert result.classification == "block"
    assert result.permit_closure is True
    assert result.l1_exit_code == 0


def test_run_preclosure_check_warn_mode_short_circuits(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_hook_module()
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def _spy(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("subprocess.run should not be called in warn mode")

    monkeypatch.setattr(module.subprocess, "run", _spy)
    result = module.run_preclosure_check(
        story_id="33-4",
        diff_paths=["docs/project-context.md"],
    )
    assert result.classification == "warn"
    assert result.permit_closure is True
    assert result.l1_exit_code is None
    assert calls == []
