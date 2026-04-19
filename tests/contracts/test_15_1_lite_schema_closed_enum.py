"""Closed-enum contract checks for 15-1-lite learning events."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from scripts.utilities.learning_event_capture import (
    LearningEvent,
    LearningEventValidationError,
    create_event,
    validate_event,
)


def test_event_type_enum_rejects_drift_at_three_surfaces() -> None:
    with pytest.raises(ValidationError):
        LearningEvent(
            run_id=uuid4(),
            gate="G2C",
            event_type="circuit_break",  # type: ignore[arg-type]
            timestamp=datetime.now(tz=UTC),
        )

    with pytest.raises(LearningEventValidationError):
        validate_event(
            {
                "run_id": str(uuid4()),
                "gate": "G2C",
                "event_type": "circuit_break",
                "timestamp": datetime.now(tz=UTC).isoformat(),
            }
        )

    with pytest.raises(LearningEventValidationError):
        create_event(run_id=uuid4(), gate="G2C", event_type="circuit_break")
