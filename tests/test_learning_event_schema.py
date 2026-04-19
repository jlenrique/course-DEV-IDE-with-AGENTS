"""Tests for learning-event schema and model loading."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from scripts.utilities.learning_event_capture import LearningEvent, validate_event


def test_schema_loads_and_validates_happy_path() -> None:
    event = LearningEvent(
        run_id=uuid4(),
        gate="G2C",
        event_type="approval",
        timestamp=datetime.now(tz=UTC),
    )
    assert validate_event(event) is True
