# /// script
# requires-python = ">=3.10"
# ///
"""Tests for generate-production-plan.py."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "generate-production-plan.py"

CANONICAL_CONTENT_TYPES = [
    "lecture-slides",
    "case-study",
    "assessment",
    "discussion-prompt",
    "video-script",
    "animated-explainer",
    "bespoke-medical-illustration",
    "voiceover",
    "interactive-module",
    "coursearc-deployment",
    "narrated-slides",
    "narrated-lesson",
]


def run_plan(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def run_plan_json(*args: str) -> dict[str, object]:
    result = run_plan(*args, "--json")
    assert result.returncode == 0, f"stderr: {result.stderr}"
    return json.loads(result.stdout)


def test_markdown_output() -> None:
    """Script produces markdown for a known content type."""
    result = run_plan("lecture-slides")
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert "# Production Plan: Lecture Slides" in result.stdout
    assert "gamma-specialist" in result.stdout
    assert "Style bible consulted" in result.stdout
    assert "**Workflow Template:** lecture-slides" in result.stdout


def test_json_output() -> None:
    """Script produces valid JSON with canonical content type output."""
    data = run_plan_json("assessment")
    assert data["content_type"] == "assessment"
    assert data["requested_content_type"] == "assessment"
    assert data["label"] == "Assessment / Quiz"
    assert len(data["stages"]) > 0


def test_all_content_types() -> None:
    """All canonical workflow templates produce valid output."""
    for content_type in CANONICAL_CONTENT_TYPES:
        data = run_plan_json(content_type)
        assert data["content_type"] == content_type
        assert len(data["stages"]) > 0, f"No stages for {content_type}"


def test_module_and_lesson_args() -> None:
    """Module and lesson arguments are included in output."""
    data = run_plan_json("lecture-slides", "--module", "M2", "--lesson", "L3")
    assert data["module"] == "M2"
    assert data["lesson"] == "L3"


def test_markdown_includes_module() -> None:
    """Markdown output includes module when specified."""
    result = run_plan("case-study", "--module", "M1")
    assert result.returncode == 0
    assert "**Module:** M1" in result.stdout


def test_human_checkpoint_present() -> None:
    """All workflow templates include at least one human checkpoint."""
    for content_type in CANONICAL_CONTENT_TYPES:
        result = run_plan(content_type)
        assert result.returncode == 0
        assert "USER REVIEW" in result.stdout, f"No user checkpoint for {content_type}"


def test_alias_resolution_for_narrated_presentation() -> None:
    """Narrated presentation alias resolves to the narrated slides template."""
    data = run_plan_json("narrated-presentation")
    assert data["content_type"] == "narrated-slides"
    assert data["requested_content_type"] == "narrated-presentation"
    assert "narrated-presentation" in data["aliases"]


def test_alias_resolution_for_video_variant() -> None:
    """Video workflow alias resolves to the narrated lesson template."""
    data = run_plan_json("narrated-presentation-with-video")
    assert data["content_type"] == "narrated-lesson"
    assert data["requested_content_type"] == "narrated-presentation-with-video"
    assert "narrated-presentation-with-video" in data["aliases"]


def test_narrated_lesson_stage_order() -> None:
    """Narrated lesson workflow preserves the happy-path dependency order."""
    data = run_plan_json("narrated-lesson")
    stages = [stage["stage"] for stage in data["stages"]]
    assert stages == [
        "source-wrangling",
        "lesson-plan-and-slide-brief",
        "fidelity-g1",
        "fidelity-g2",
        "quality-g2",
        "gate-1",
        "imagine-handoff",
        "slide-generation",
        "storyboard",
        "fidelity-g3",
        "quality-g3",
        "gate-2",
        "narration-and-manifest",
        "fidelity-g4",
        "quality-g4",
        "gate-3",
        "audio-generation",
        "fidelity-g5",
        "motion-generation",
        "pre-composition-validation",
        "composition-guide",
        "post-composition-validation",
        "gate-4",
    ]


def test_help_flag_lists_new_workflows() -> None:
    """Help output includes the new narrated workflow ids and aliases."""
    result = run_plan("--help")
    assert result.returncode == 0
    stdout = result.stdout.lower()
    assert "narrated-lesson" in stdout
    assert "narrated-presentation" in stdout
    assert "narrated-presentation-with-video" in stdout


if __name__ == "__main__":
    tests = [
        test_markdown_output,
        test_json_output,
        test_all_content_types,
        test_module_and_lesson_args,
        test_markdown_includes_module,
        test_human_checkpoint_present,
        test_alias_resolution_for_narrated_presentation,
        test_alias_resolution_for_video_variant,
        test_narrated_lesson_stage_order,
        test_help_flag_lists_new_workflows,
    ]
    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
        except AssertionError as e:
            print(f"  FAIL: {test.__name__}: {e}")
