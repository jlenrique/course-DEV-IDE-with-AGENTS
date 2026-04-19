"""Tests for manifest learning-event extension declarations."""

from __future__ import annotations

from scripts.utilities.pipeline_manifest import load_manifest


def test_manifest_carries_schema_ref_and_gate_emissions() -> None:
    manifest = load_manifest()
    assert manifest.learning_events.schema_ref == "state/config/learning-event-schema.yaml"

    by_gate = {
        step.gate_code: step
        for step in manifest.steps
        if step.gate_code in {"G2C", "G3", "G4"}
    }
    assert by_gate["G2C"].learning_events.emits is True
    assert by_gate["G3"].learning_events.emits is True
    assert by_gate["G4"].learning_events.emits is True
    assert tuple(by_gate["G2C"].learning_events.event_types) == (
        "approval",
        "revision",
        "waiver",
    )
