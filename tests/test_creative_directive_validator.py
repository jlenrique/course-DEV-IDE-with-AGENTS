"""Tests for creative directive validator utility."""

from __future__ import annotations

from typing import Any

from scripts.utilities.creative_directive_validator import validate_creative_directive


def _base_directive() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "experience_profile": "visual-led",
        "slide_mode_proportions": {
            "literal-text": 0.15,
            "literal-visual": 0.25,
            "creative": 0.60,
        },
        "narration_profile_controls": {
            "narrator_source_authority": "source-grounded",
            "slide_content_density": "adaptive",
            "elaboration_budget": "medium",
        },
        "creative_rationale": "Favor rich visual storytelling for this profile.",
    }


def test_validate_creative_directive_passes_on_profile_aligned_payload() -> None:
    errors = validate_creative_directive(_base_directive())
    assert errors == []


def test_validate_creative_directive_fails_unknown_top_level_field() -> None:
    payload = _base_directive()
    payload["unexpected"] = "nope"
    errors = validate_creative_directive(payload)
    assert any("unknown top-level fields" in err for err in errors)


def test_validate_creative_directive_fails_enum_violation() -> None:
    payload = _base_directive()
    payload["narration_profile_controls"]["elaboration_budget"] = "extreme"
    errors = validate_creative_directive(payload)
    assert any("narration_profile_controls.elaboration_budget" in err for err in errors)


def test_validate_creative_directive_fails_unknown_nested_control_key() -> None:
    payload = _base_directive()
    payload["narration_profile_controls"]["extra_style"] = "experimental"
    errors = validate_creative_directive(payload)
    assert any("contains unknown keys" in err for err in errors)


def test_validate_creative_directive_fails_sum_rule() -> None:
    payload = _base_directive()
    payload["slide_mode_proportions"] = {
        "literal-text": 0.2,
        "literal-visual": 0.2,
        "creative": 0.2,
    }
    errors = validate_creative_directive(payload)
    assert any("must sum to 1.0" in err for err in errors)


def test_validate_creative_directive_fails_profile_mapping_mismatch() -> None:
    payload = _base_directive()
    payload["slide_mode_proportions"]["creative"] = 0.55
    payload["slide_mode_proportions"]["literal-text"] = 0.20
    errors = validate_creative_directive(payload)
    assert any("must match profile target values" in err for err in errors)


def test_validate_creative_directive_fails_profile_control_mismatch() -> None:
    payload = _base_directive()
    payload["narration_profile_controls"]["slide_content_density"] = "dense"
    errors = validate_creative_directive(payload)
    assert any("narration_profile_controls must match profile target values" in err for err in errors)
