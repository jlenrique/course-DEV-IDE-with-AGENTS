"""Contract checks to keep 33-4 trigger paths manifest-driven."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = ROOT / "skills" / "bmad-agent-cora" / "scripts" / "preclosure_hook.py"


def test_preclosure_hook_reads_triggers_from_manifest() -> None:
    source = HOOK_PATH.read_text(encoding="utf-8")
    assert "block_mode_trigger_paths" in source

    forbidden_literals = [
        "scripts/utilities/run_hud.py",
        "scripts/utilities/progress_map.py",
        "tests/test_run_hud.py",
        "tests/test_progress_map.py",
        "state/config/learning-event-schema.yaml",
    ]
    for literal in forbidden_literals:
        assert literal not in source
