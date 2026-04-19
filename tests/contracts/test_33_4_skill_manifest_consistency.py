"""Contract checks for 33-4 SKILL and manifest consistency."""

from __future__ import annotations

from pathlib import Path

from scripts.utilities.pipeline_manifest import load_manifest

ROOT = Path(__file__).resolve().parents[2]
CORA_SKILL = ROOT / "skills" / "bmad-agent-cora" / "SKILL.md"
MANIFEST = ROOT / "state" / "config" / "pipeline-manifest.yaml"


def test_cora_skill_hud_scope_union_matches_manifest_trigger_paths() -> None:
    manifest = load_manifest(MANIFEST)
    trigger_paths = set(manifest.block_mode_trigger_paths)
    skill_text = CORA_SKILL.read_text(encoding="utf-8")

    expected_paths = {
        "scripts/utilities/run_hud.py",
        "scripts/utilities/progress_map.py",
        "tests/test_run_hud.py",
        "tests/test_progress_map.py",
        "state/config/learning-event-schema.yaml",
        "scripts/utilities/learning_event_capture.py",
    }
    for path in expected_paths:
        assert path in skill_text
        assert path in trigger_paths
