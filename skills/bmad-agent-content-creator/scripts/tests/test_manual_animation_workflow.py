# /// script
# requires-python = ">=3.10"
# ///
"""Tests for Epic 14 manual animation guidance and import."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manual_animation_workflow import (
    ManualAnimationError,
    generate_animation_guidance,
    import_manual_motion_asset,
)


def _assignment() -> dict:
    return {
        "slide_id": "slide-03",
        "motion_type": "animation",
        "motion_brief": "Pulse the callouts in sequence",
        "guidance_notes": "Keep the labels readable throughout",
        "narration_intent": "Guide attention across the labels one by one",
        "motion_duration_seconds": 7.0,
    }


def test_generate_animation_guidance_defaults_to_tool_agnostic() -> None:
    result = generate_animation_guidance(_assignment())
    assert result["tool_mode"] == "generic"
    assert "tool-agnostic guidance" in result["content"]
    assert "Pulse the callouts in sequence" in result["content"]


def test_generate_animation_guidance_supports_vyond_mode() -> None:
    result = generate_animation_guidance(_assignment(), tool="vyond")
    assert result["tool_mode"] == "vyond"
    assert "Vyond-specific" in result["content"]


def test_import_manual_motion_asset_records_valid_file(tmp_path: Path) -> None:
    asset = tmp_path / "slide-03_motion.mp4"
    asset.write_bytes(b"video-bytes")

    result = import_manual_motion_asset(_assignment(), asset, duration_seconds=7.0)

    assert result["motion_source"] == "manual"
    assert result["motion_status"] == "imported"
    assert result["motion_asset_path"].endswith("slide-03_motion.mp4")


def test_import_manual_motion_asset_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ManualAnimationError, match="does not exist"):
        import_manual_motion_asset(_assignment(), tmp_path / "missing.mp4", duration_seconds=7.0)


def test_import_manual_motion_asset_rejects_invalid_format(tmp_path: Path) -> None:
    asset = tmp_path / "slide-03_motion.gif"
    asset.write_bytes(b"gif-bytes")

    with pytest.raises(ManualAnimationError, match="Unsupported"):
        import_manual_motion_asset(_assignment(), asset, duration_seconds=7.0)


def test_import_manual_motion_asset_rejects_duration_out_of_range(tmp_path: Path) -> None:
    asset = tmp_path / "slide-03_motion.mp4"
    asset.write_bytes(b"video-bytes")

    with pytest.raises(ManualAnimationError, match="expected range"):
        import_manual_motion_asset(_assignment(), asset, duration_seconds=30.0)
