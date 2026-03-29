"""Tests for Marcus platform allocation intelligence (Story G.1)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "platform_allocation.py"
SPEC = importlib.util.spec_from_file_location("platform_allocation", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _matrix() -> dict[str, object]:
    return {
        "version": "test",
        "rules": {
            "required_canvas_flags": [
                "graded",
                "peer_discussion",
                "instructor_facilitation",
            ],
            "preferred_coursearc_content_types": ["interactive-module", "case-study"],
            "preferred_panopto_content_types": ["recorded-lecture"],
            "preferred_direct_embed_content_types": ["quick-reference"],
            "high_interactivity_levels": ["high", "very-high"],
            "default_platform": "canvas",
        },
    }


def test_recommend_canvas_when_graded() -> None:
    result = MODULE.recommend_platform(
        {
            "content_type": "interactive-module",
            "graded": True,
            "interactivity_level": "high",
        },
        matrix=_matrix(),
        course_code="C1",
    )
    assert result["recommended_platform"] == "canvas"
    assert any("graded" in line for line in result["rationale"])


def test_recommend_coursearc_for_high_interactivity() -> None:
    result = MODULE.recommend_platform(
        {
            "content_type": "interactive-module",
            "interactivity_level": "high",
            "graded": False,
            "peer_discussion": False,
            "instructor_facilitation": False,
        },
        matrix=_matrix(),
        course_code="C1",
    )
    assert result["recommended_platform"] == "coursearc"


def test_recommend_panopto_for_recorded_lecture() -> None:
    result = MODULE.recommend_platform(
        {
            "content_type": "recorded-lecture",
            "interactivity_level": "low",
            "graded": False,
            "peer_discussion": False,
            "instructor_facilitation": False,
        },
        matrix=_matrix(),
        course_code="C1",
    )
    assert result["recommended_platform"] == "panopto"


def test_recommend_direct_embed_for_quick_reference() -> None:
    result = MODULE.recommend_platform(
        {
            "content_type": "quick-reference",
            "interactivity_level": "low",
            "graded": False,
            "peer_discussion": False,
            "instructor_facilitation": False,
        },
        matrix=_matrix(),
        course_code="C1",
    )
    assert result["recommended_platform"] == "direct-embed"


def test_result_contains_accept_modify_override_options() -> None:
    result = MODULE.recommend_platform(
        {
            "content_type": "unknown-content",
            "interactivity_level": "low",
            "graded": False,
            "peer_discussion": False,
            "instructor_facilitation": False,
        },
        matrix=_matrix(),
        course_code="C1",
    )
    assert set(result["options"].keys()) == {"accept", "modify", "override"}
    assert result["recommended_platform"] == "canvas"


def test_recommend_coursearc_for_narrative_control() -> None:
    result = MODULE.recommend_platform(
        {
            "content_type": "generic-lesson",
            "interactivity_level": "low",
            "graded": False,
            "peer_discussion": False,
            "instructor_facilitation": False,
            "narrative_control": True,
        },
        matrix=_matrix(),
        course_code="C1",
    )
    assert result["recommended_platform"] == "coursearc"
    assert any("Narrative control" in line for line in result["rationale"])


def test_recommend_coursearc_for_accessibility_critical() -> None:
    result = MODULE.recommend_platform(
        {
            "content_type": "generic-lesson",
            "interactivity_level": "low",
            "graded": False,
            "peer_discussion": False,
            "instructor_facilitation": False,
            "accessibility_critical": True,
        },
        matrix=_matrix(),
        course_code="C1",
    )
    assert result["recommended_platform"] == "coursearc"
    assert any("Accessibility-critical" in line for line in result["rationale"])


def test_raises_for_unknown_required_flag_reference() -> None:
    matrix = _matrix()
    matrix["rules"]["required_canvas_flags"] = ["graded", "unknown_flag"]
    with pytest.raises(KeyError, match="unknown_flag"):
        MODULE.recommend_platform(
            {
                "content_type": "interactive-module",
                "interactivity_level": "high",
            },
            matrix=matrix,
            course_code="C1",
        )


def test_raises_for_invalid_interactivity_level() -> None:
    with pytest.raises(ValueError, match="Invalid interactivity_level"):
        MODULE.recommend_platform(
            {
                "content_type": "interactive-module",
                "interactivity_level": "extreme",
            },
            matrix=_matrix(),
            course_code="C1",
        )


def test_save_allocation_decision_appends_to_patterns(tmp_path: Path) -> None:
    patterns = tmp_path / "patterns.md"
    patterns.write_text("# Patterns\n", encoding="utf-8")

    decision = MODULE.recommend_platform(
        {
            "content_type": "interactive-module",
            "interactivity_level": "high",
        },
        matrix=_matrix(),
        course_code="C1",
    )

    out_path = MODULE.save_allocation_decision(decision, patterns_path=patterns)
    content = out_path.read_text(encoding="utf-8")

    assert "allocation decision" in content
    assert "interactive-module" in content
    assert "coursearc" in content
