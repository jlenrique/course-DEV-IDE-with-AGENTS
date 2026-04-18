"""Shared parametrized envelope-shape contract test (AC-T.5 from story 26-6).

Asserts that every capability (full + stub) emits a ReturnEnvelope conforming
to the pinned 7-field shape. Tests envelope STRUCTURE only, not capability
logic — that's each capability's own test file's job.

Marked ``trial_critical`` — envelope drift across capabilities would silently
break Marcus's routing.
"""

from __future__ import annotations

import importlib

import pytest

from scripts.marcus_capabilities import CAPABILITY_REGISTRY
from scripts.marcus_capabilities._shared import (
    RETURN_FIELDS,
    Invocation,
    InvocationContext,
    ReturnEnvelope,
)

pytestmark = pytest.mark.trial_critical

ALL_CODES = sorted(CAPABILITY_REGISTRY.keys())


@pytest.fixture
def summarize_invocation_factory():
    """Build a minimal valid summarize-mode invocation for a given code."""

    def _make(code: str) -> Invocation:
        return Invocation(
            capability_code=code,
            mode="summarize",
            args={},
            context=InvocationContext(run_id="test-run-id", invoked_by="marcus"),
            idempotency_key=None,
        )

    return _make


def _import_capability_module(code: str):
    """Load the script module declared in the registry entry."""
    entry = CAPABILITY_REGISTRY[code]
    return importlib.import_module(entry.script_module)


@pytest.mark.parametrize("code", ALL_CODES)
def test_summarize_returns_conforming_envelope(code, summarize_invocation_factory) -> None:
    """Every capability's summarize handler returns a ReturnEnvelope with the canonical 7 fields."""
    module = _import_capability_module(code)
    invocation = summarize_invocation_factory(code)

    assert hasattr(module, "summarize"), f"{code}: missing summarize function"
    envelope = module.summarize(invocation)

    assert isinstance(envelope, ReturnEnvelope), f"{code}: summarize must return ReturnEnvelope"
    assert envelope.capability_code == code, f"{code}: envelope.capability_code mismatch"

    envelope_dict = envelope.to_dict()
    allowed_fields = RETURN_FIELDS
    unexpected = set(envelope_dict) - allowed_fields
    assert not unexpected, f"{code}: envelope has unexpected fields {unexpected}"


@pytest.mark.parametrize("code", ALL_CODES)
def test_envelope_status_is_valid(code, summarize_invocation_factory) -> None:
    """Status must be one of the canonical Literal values."""
    module = _import_capability_module(code)
    envelope = module.summarize(summarize_invocation_factory(code))
    assert envelope.status in {"ok", "error", "partial"}, envelope.status


@pytest.mark.parametrize("code", ALL_CODES)
def test_envelope_echoes_run_id_from_context(code, summarize_invocation_factory) -> None:
    """Return envelope should echo the run_id Marcus passed in."""
    module = _import_capability_module(code)
    envelope = module.summarize(summarize_invocation_factory(code))
    assert envelope.run_id == "test-run-id", f"{code}: run_id not echoed"


@pytest.mark.parametrize("code", ALL_CODES)
def test_telemetry_present(code, summarize_invocation_factory) -> None:
    """Every envelope carries a telemetry dict (may be empty initially; CLI fills duration_ms)."""
    module = _import_capability_module(code)
    envelope = module.summarize(summarize_invocation_factory(code))
    assert isinstance(envelope.telemetry, dict), f"{code}: telemetry must be a dict"
