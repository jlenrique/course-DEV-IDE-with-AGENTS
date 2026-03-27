"""Tests for compositor_operations.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "compositor_operations.py"
SPEC = importlib.util.spec_from_file_location("compositor_operations", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def sample_manifest() -> dict:
    return {
        "lesson_id": "C1-M1-L1",
        "title": "Compositor Smoke",
        "segments": [
            {
                "id": "seg-01",
                "narration_duration": 3.2,
                "narration_file": "course-content/staging/C1-M1-L1/audio/seg-01.mp3",
                "narration_vtt": "course-content/staging/C1-M1-L1/captions/seg-01.vtt",
                "visual_file": "course-content/staging/C1-M1-L1/visuals/seg-01.jpg",
                "visual_duration": 3.2,
                "transition_in": "fade",
                "transition_out": "cross-dissolve",
                "behavioral_intent": "credible",
                "music": "duck",
                "sfx_file": None,
                "visual_mode": "static-hold",
            }
        ],
    }


class TestTimelineRows:
    def test_build_timeline_rows(self) -> None:
        rows = MODULE.build_timeline_rows(sample_manifest())
        assert len(rows) == 1
        assert rows[0]["start"] == 0.0
        assert rows[0]["behavioral_intent"] == "credible"


class TestGuideGeneration:
    def test_generate_assembly_guide_contains_behavioral_intent(self) -> None:
        guide = MODULE.generate_assembly_guide(
            sample_manifest(),
            "course-content/staging/C1-M1-L1/manifest.yaml",
        )
        assert "Behavioral Intent" in guide
        assert "`credible`" in guide
        assert "Intent note:" in guide
        assert "Track plan" in guide

    def test_generate_assembly_guide_file(self, tmp_path: Path) -> None:
        manifest_path = tmp_path / "manifest.yaml"
        manifest_path.write_text(
            """
lesson_id: C1-M1-L1
title: Compositor Smoke
segments:
  - id: seg-01
    narration_duration: 3.2
    narration_file: course-content/staging/C1-M1-L1/audio/seg-01.mp3
    narration_vtt: course-content/staging/C1-M1-L1/captions/seg-01.vtt
    visual_file: course-content/staging/C1-M1-L1/visuals/seg-01.jpg
    visual_duration: 3.2
    transition_in: fade
    transition_out: cross-dissolve
    behavioral_intent: credible
    music: duck
    sfx_file: null
    visual_mode: static-hold
""".strip()
            + "\n",
            encoding="utf-8",
        )
        output = MODULE.generate_assembly_guide_file(
            manifest_path, tmp_path / "descript-assembly-guide.md"
        )
        content = output.read_text(encoding="utf-8")
        assert "Descript Assembly Guide" in content
        assert "course-content/staging/C1-M1-L1/audio/seg-01.mp3" in content


class TestValidation:
    def test_validate_manifest_raises_for_missing_fields(self) -> None:
        manifest = {"segments": [{"id": "seg-01"}]}
        try:
            MODULE.validate_manifest(manifest)
        except ValueError as exc:
            assert "missing required fields" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("Expected validation failure")
