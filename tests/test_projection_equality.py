"""Projection equality checks against pipeline manifest."""

from __future__ import annotations

from scripts.utilities.pipeline_manifest import hud_steps, load_manifest
from scripts.utilities.run_hud import PIPELINE_STEPS as HUD_PIPELINE_STEPS


def test_run_hud_projection_matches_manifest() -> None:
    manifest_steps = hud_steps(load_manifest())
    assert manifest_steps == HUD_PIPELINE_STEPS

