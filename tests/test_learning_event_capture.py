"""Unit tests for learning-event capture and ledger behavior."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from scripts.utilities.learning_event_capture import (
    LearningEventValidationError,
    append_to_ledger,
    create_event,
    validate_event,
)


def test_create_event_happy_path() -> None:
    event = create_event(run_id=uuid4(), gate="G2C", event_type="approval")
    assert event.gate == "G2C"
    assert event.event_type == "approval"
    assert event.timestamp.tzinfo is not None


def test_validate_event_rejects_unknown_event_type() -> None:
    with pytest.raises(LearningEventValidationError):
        validate_event(
            {
                "run_id": str(uuid4()),
                "gate": "G2C",
                "event_type": "circuit_break",
                "timestamp": datetime.now(tz=UTC).isoformat(),
            }
        )


def test_append_to_ledger_creates_file_if_missing(tmp_path: Path) -> None:
    event = create_event(run_id=uuid4(), gate="G2C", event_type="approval")
    append_to_ledger(event, tmp_path)
    ledger = tmp_path / "learning-events.yaml"
    assert ledger.exists()
    text = ledger.read_text(encoding="utf-8")
    assert "event_type: approval" in text


def test_append_to_ledger_preserves_prior_entries_byte_identical(tmp_path: Path) -> None:
    first = create_event(run_id=uuid4(), gate="G2C", event_type="approval")
    second = create_event(run_id=uuid4(), gate="G3", event_type="revision")

    append_to_ledger(first, tmp_path)
    ledger = tmp_path / "learning-events.yaml"
    first_bytes = ledger.read_bytes()
    append_to_ledger(second, tmp_path)
    second_bytes = ledger.read_bytes()

    assert second_bytes.startswith(first_bytes)
