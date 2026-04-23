from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from marcus.dispatch.contract import (
    DispatchEnvelope,
    DispatchKind,
    DispatchOutcome,
    DispatchReceipt,
    DispatchValidationFailedError,
    _classify_dispatch_kind,
    build_dispatch_envelope,
    build_dispatch_receipt,
    dump_contract_schemas,
)


def test_classify_dispatch_kind_accepts_normalized_aliases() -> None:
    assert _classify_dispatch_kind("irene_pass2") == DispatchKind.IRENE_PASS2
    assert _classify_dispatch_kind("kira-motion") == DispatchKind.KIRA_MOTION
    assert _classify_dispatch_kind("texas retrieval") == DispatchKind.TEXAS_RETRIEVAL


def test_classify_dispatch_kind_rejects_unknown_kind() -> None:
    with pytest.raises(DispatchValidationFailedError, match="Unknown dispatch_kind"):
        _classify_dispatch_kind("vera_fidelity")


def test_dispatch_envelope_round_trip_json() -> None:
    envelope = build_dispatch_envelope(
        run_id="RUN-PRR-001",
        dispatch_kind="irene_pass2",
        input_packet={"handoff_status": "prepared-pending-irene-pass2"},
        context_refs=["bundle/pass2-envelope.json"],
        correlation_id="corr-prr-001",
        timestamp_utc=datetime(2026, 4, 22, 12, 0, tzinfo=UTC),
    )
    payload = envelope.model_dump(mode="json")
    hydrated = DispatchEnvelope.model_validate(payload)

    assert hydrated.dispatch_kind == DispatchKind.IRENE_PASS2
    assert hydrated.correlation_id == "corr-prr-001"


def test_dispatch_receipt_round_trip_json() -> None:
    receipt = build_dispatch_receipt(
        correlation_id="corr-prr-001",
        specialist_id="irene",
        outcome=DispatchOutcome.COMPLETE,
        output_artifacts=["bundle/narration-script.md", "bundle/segment-manifest.yaml"],
        diagnostics={"warnings": 0},
        duration_ms=120,
        timestamp_utc=datetime(2026, 4, 22, 12, 1, tzinfo=UTC),
    )
    payload = receipt.model_dump(mode="json")
    hydrated = DispatchReceipt.model_validate(payload)

    assert hydrated.outcome == DispatchOutcome.COMPLETE
    assert len(hydrated.output_artifacts) == 2


def test_timestamp_must_be_timezone_aware() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        build_dispatch_envelope(
            run_id="RUN-PRR-002",
            dispatch_kind="kira_motion",
            input_packet={"slide_id": "slide-01"},
            timestamp_utc=datetime(2026, 4, 22, 12, 0),
        )


def test_error_classes_reside_in_dispatch_module() -> None:
    try:
        _classify_dispatch_kind("unknown-kind")
    except DispatchValidationFailedError as exc:
        assert type(exc).__module__.startswith("marcus.dispatch.")
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected DispatchValidationFailedError")


def test_schema_file_has_required_defs() -> None:
    schema_path = (
        Path(__file__).resolve().parents[2]
        / "state"
        / "config"
        / "schemas"
        / "marcus-dispatch-envelope.schema.json"
    )
    payload = json.loads(schema_path.read_text(encoding="utf-8"))

    assert "$defs" in payload
    assert "DispatchEnvelope" in payload["$defs"]
    assert "DispatchReceipt" in payload["$defs"]
    assert "DispatchError" in payload["$defs"]


def test_generated_schema_contains_closed_dispatch_kind_enum() -> None:
    generated = dump_contract_schemas()
    enum_values = generated["$defs"]["DispatchKind"]["enum"]
    assert enum_values == ["irene_pass2", "kira_motion", "texas_retrieval"]
