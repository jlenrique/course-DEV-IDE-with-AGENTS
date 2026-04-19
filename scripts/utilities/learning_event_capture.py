"""Learning-event capture utilities for Marcus gate decisions."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Literal
from uuid import UUID

import yaml
from pydantic import UUID4, BaseModel, ConfigDict, ValidationError, field_validator

from scripts.utilities.pipeline_manifest import load_manifest


class LearningEventValidationError(ValueError):
    """Raised when a learning event does not satisfy schema constraints."""


class LedgerWriteError(RuntimeError):
    """Raised when append-only ledger writes fail."""


def _emitter_gate_ids() -> set[str]:
    manifest = load_manifest()
    return {
        step.gate_code
        for step in manifest.steps
        if step.learning_events.emits and step.gate_code
    }


class LearningEvent(BaseModel):
    """Validated learning event payload."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    run_id: UUID4
    gate: str
    event_type: Literal["approval", "revision", "waiver"]
    timestamp: datetime

    @field_validator("gate")
    @classmethod
    def _validate_gate(cls, value: str) -> str:
        valid = _emitter_gate_ids()
        if value not in valid:
            raise ValueError(f"gate {value!r} is not declared as a learning-event emitter")
        return value

    @field_validator("timestamp")
    @classmethod
    def _validate_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return value.astimezone(UTC)


def create_event(
    run_id: UUID,
    gate: str,
    event_type: str,
    *,
    timestamp: datetime | None = None,
) -> LearningEvent:
    """Create a validated learning event."""
    event_ts = timestamp or datetime.now(tz=UTC)
    try:
        return LearningEvent(
            run_id=run_id,
            gate=gate,
            event_type=event_type,  # type: ignore[arg-type]
            timestamp=event_ts,
        )
    except ValidationError as exc:
        raise LearningEventValidationError(
            "Learning event is invalid. Verify gate, event_type, and timestamp contract values."
        ) from exc


def validate_event(
    event: LearningEvent | dict,
    schema_path: Path | None = None,
) -> bool:
    """Validate event against model + schema enum."""
    try:
        parsed = event if isinstance(event, LearningEvent) else LearningEvent.model_validate(event)
    except ValidationError as exc:
        raise LearningEventValidationError(
            "Learning event validation failed. Provide run_id, gate, event_type, "
            "and tz-aware timestamp."
        ) from exc

    schema = schema_path or (
        Path(__file__).resolve().parents[2]
        / "state"
        / "config"
        / "learning-event-schema.yaml"
    )
    schema_data = yaml.safe_load(schema.read_text(encoding="utf-8")) or {}
    enum_values = set(schema_data.get("event_type_enum", []))
    if enum_values and parsed.event_type not in enum_values:
        raise LearningEventValidationError(
            f"Learning event type {parsed.event_type!r} is not declared in "
            "learning-event-schema.yaml."
        )
    return True


def append_to_ledger(event: LearningEvent, run_dir: Path) -> None:
    """Append a learning event to run-scoped YAML ledger atomically."""
    validate_event(event)
    run_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = run_dir / "learning-events.yaml"

    existing = ledger_path.read_bytes() if ledger_path.exists() else b""
    chunk = yaml.safe_dump(
        [event.model_dump(mode="json")],
        sort_keys=False,
        allow_unicode=False,
    ).encode("utf-8")

    new_bytes = bytearray(existing)
    if new_bytes and not new_bytes.endswith(b"\n"):
        new_bytes.extend(b"\n")
    new_bytes.extend(chunk)
    if not new_bytes.endswith(b"\n"):
        new_bytes.extend(b"\n")

    try:
        with NamedTemporaryFile("wb", delete=False, dir=run_dir) as tmp:
            tmp.write(new_bytes)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_file = Path(tmp.name)
        tmp_file.replace(ledger_path)
    except OSError as exc:
        raise LedgerWriteError(
            f"Unable to append learning event ledger at {ledger_path}. "
            "Verify run directory permissions."
        ) from exc


__all__ = (
    "create_event",
    "validate_event",
    "append_to_ledger",
    "LearningEvent",
    "LearningEventValidationError",
    "LedgerWriteError",
)
