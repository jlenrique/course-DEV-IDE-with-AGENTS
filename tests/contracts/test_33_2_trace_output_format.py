"""Contract pin for lockstep trace output structure."""

from __future__ import annotations

from scripts.utilities.check_pipeline_manifest_lockstep import (
    DEFAULT_MANIFEST_PATH,
    DEFAULT_PACK_PATH,
    run_check,
)


def test_trace_output_has_required_oia_fields() -> None:
    _, trace = run_check(DEFAULT_MANIFEST_PATH, DEFAULT_PACK_PATH, "v4.2")
    required = {"lane", "scope", "timestamp", "findings", "l1_checks_run", "closure_gate"}
    missing = sorted(required - set(trace.keys()))
    assert not missing, f"trace payload missing required keys: {missing}"
