"""Validation tests for experience profile definitions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


PROFILES_PATH = Path("state/config/experience-profiles.yaml")
EXPECTED_MODE_KEYS = {"literal-text", "literal-visual", "creative"}


def _load_profiles() -> dict[str, Any]:
    data = yaml.safe_load(PROFILES_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_profiles_file_has_required_top_level_shape() -> None:
    data = _load_profiles()
    assert data["schema_version"] == "1.0"
    assert isinstance(data.get("profiles"), dict)
    assert {"visual-led", "text-led"}.issubset(data["profiles"].keys())


def test_profile_mode_proportions_are_canonical_and_normalized() -> None:
    profiles = _load_profiles()["profiles"]
    for profile_name, profile_data in profiles.items():
        assert isinstance(profile_data, dict)
        modes = profile_data.get("slide_mode_proportions")
        assert isinstance(modes, dict), f"{profile_name} missing slide_mode_proportions"
        assert set(modes.keys()) == EXPECTED_MODE_KEYS
        total = 0.0
        for key, value in modes.items():
            assert isinstance(value, (int, float)) and not isinstance(value, bool)
            numeric = float(value)
            assert 0.0 <= numeric <= 1.0
            total += numeric
        assert abs(total - 1.0) <= 0.001


def test_profile_narration_controls_have_required_keys() -> None:
    profiles = _load_profiles()["profiles"]
    required_controls = {
        "narrator_source_authority",
        "slide_content_density",
        "elaboration_budget",
    }
    for profile_name, profile_data in profiles.items():
        controls = profile_data.get("narration_profile_controls")
        assert isinstance(controls, dict), f"{profile_name} missing narration_profile_controls"
        assert required_controls.issubset(controls.keys())
