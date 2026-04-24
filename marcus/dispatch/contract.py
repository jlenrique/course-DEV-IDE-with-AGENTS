"""Standard Marcus dispatch envelope, receipt, and error contracts.

PR-R contract scope (v1):
- Irene Pass 2 dispatch
- Kira motion dispatch
- Texas retrieval dispatch

Sprint 2 extension (additive):
- Wanda podcast capability dispatches (episode, dialogue, summary, music-bed,
  chapter markers, audio-assembly handoff) — leaf specialist, no orchestrator
  surface touched.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DispatchKind(StrEnum):
    """Closed dispatch-kind enum (triple-layer reject on unknown values)."""

    IRENE_PASS2 = "irene_pass2"
    KIRA_MOTION = "kira_motion"
    TEXAS_RETRIEVAL = "texas_retrieval"
    # Sprint 2 — Wanda podcast capability edges (leaf specialist; additive).
    WANDA_PODCAST_EPISODE = "wanda_podcast_episode"
    WANDA_PODCAST_DIALOGUE = "wanda_podcast_dialogue"
    WANDA_AUDIO_SUMMARY = "wanda_audio_summary"
    WANDA_MUSIC_BED_APPLY = "wanda_music_bed_apply"
    WANDA_CHAPTER_MARKERS_EMIT = "wanda_chapter_markers_emit"
    WANDA_AUDIO_ASSEMBLY_HANDOFF = "wanda_audio_assembly_handoff"


class SpecialistId(StrEnum):
    """Closed specialist IDs."""

    IRENE = "irene"
    KIRA = "kira"
    TEXAS = "texas"
    # Sprint 2.
    WANDA = "wanda"


DISPATCH_KIND_TO_SPECIALIST: Mapping[DispatchKind, SpecialistId] = {
    DispatchKind.IRENE_PASS2: SpecialistId.IRENE,
    DispatchKind.KIRA_MOTION: SpecialistId.KIRA,
    DispatchKind.TEXAS_RETRIEVAL: SpecialistId.TEXAS,
    DispatchKind.WANDA_PODCAST_EPISODE: SpecialistId.WANDA,
    DispatchKind.WANDA_PODCAST_DIALOGUE: SpecialistId.WANDA,
    DispatchKind.WANDA_AUDIO_SUMMARY: SpecialistId.WANDA,
    DispatchKind.WANDA_MUSIC_BED_APPLY: SpecialistId.WANDA,
    DispatchKind.WANDA_CHAPTER_MARKERS_EMIT: SpecialistId.WANDA,
    DispatchKind.WANDA_AUDIO_ASSEMBLY_HANDOFF: SpecialistId.WANDA,
}


class DispatchOutcome(StrEnum):
    """Dispatch completion posture."""

    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"


class DispatchErrorKind(StrEnum):
    """Pinned dispatch error taxonomy (AC-B.3)."""

    VALIDATION_FAILED = "validation_failed"
    SPECIALIST_UNAVAILABLE = "specialist_unavailable"
    TIMEOUT = "timeout"
    CONTRACT_VIOLATION = "contract_violation"
    INTERNAL_ERROR = "internal_error"


class DispatchError(BaseModel):
    """Structured error contract for dispatch surfaces."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    error_kind: DispatchErrorKind
    message: str = Field(min_length=1)
    error_detail: dict[str, Any] = Field(default_factory=dict)


class DispatchEnvelope(BaseModel):
    """Marcus -> specialist dispatch envelope."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    run_id: str = Field(min_length=1)
    specialist_id: SpecialistId
    dispatch_kind: DispatchKind
    input_packet: dict[str, Any]
    context_refs: tuple[str, ...] = ()
    correlation_id: str = Field(min_length=1)
    timestamp_utc: datetime

    @field_validator("context_refs", mode="before")
    @classmethod
    def _coerce_context_refs(cls, value: Any) -> Any:
        if value is None:
            return ()
        if isinstance(value, list):
            return tuple(value)
        return value

    @field_validator("context_refs")
    @classmethod
    def _validate_context_refs(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        cleaned: list[str] = []
        for raw in value:
            text = str(raw).strip()
            if not text:
                raise ValueError("context_refs entries must be non-empty strings")
            cleaned.append(text)
        return tuple(cleaned)

    @field_validator("timestamp_utc")
    @classmethod
    def _validate_timestamp_tz(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp_utc must be timezone-aware")
        return value.astimezone(UTC)


class DispatchReceipt(BaseModel):
    """Specialist -> Marcus dispatch receipt."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    correlation_id: str = Field(min_length=1)
    specialist_id: SpecialistId
    outcome: DispatchOutcome
    output_artifacts: tuple[str, ...] = ()
    diagnostics: dict[str, Any] = Field(default_factory=dict)
    duration_ms: int = Field(default=0, ge=0)
    timestamp_utc: datetime

    @field_validator("output_artifacts", mode="before")
    @classmethod
    def _coerce_output_artifacts(cls, value: Any) -> Any:
        if value is None:
            return ()
        if isinstance(value, list):
            return tuple(value)
        return value

    @field_validator("output_artifacts")
    @classmethod
    def _validate_output_artifacts(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        cleaned: list[str] = []
        for raw in value:
            text = str(raw).strip()
            if not text:
                raise ValueError("output_artifacts entries must be non-empty strings")
            cleaned.append(text)
        return tuple(cleaned)

    @field_validator("timestamp_utc")
    @classmethod
    def _validate_receipt_timestamp_tz(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp_utc must be timezone-aware")
        return value.astimezone(UTC)


class DispatchContractError(Exception):
    """Base exception class for dispatch contract violations."""

    error_kind = DispatchErrorKind.INTERNAL_ERROR

    def __init__(self, message: str, *, error_detail: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.dispatch_error = DispatchError(
            error_kind=self.error_kind,
            message=message,
            error_detail=error_detail or {},
        )


class DispatchValidationFailedError(DispatchContractError):
    error_kind = DispatchErrorKind.VALIDATION_FAILED


class DispatchSpecialistUnavailableError(DispatchContractError):
    error_kind = DispatchErrorKind.SPECIALIST_UNAVAILABLE


class DispatchTimeoutError(DispatchContractError):
    error_kind = DispatchErrorKind.TIMEOUT


class DispatchContractViolationError(DispatchContractError):
    error_kind = DispatchErrorKind.CONTRACT_VIOLATION


class DispatchInternalError(DispatchContractError):
    error_kind = DispatchErrorKind.INTERNAL_ERROR


_KIND_ALIASES: Mapping[str, DispatchKind] = {
    "irene-pass2": DispatchKind.IRENE_PASS2,
    "irene_pass2": DispatchKind.IRENE_PASS2,
    "irene-pass-2": DispatchKind.IRENE_PASS2,
    "kira-motion": DispatchKind.KIRA_MOTION,
    "kira_motion": DispatchKind.KIRA_MOTION,
    "texas-retrieval": DispatchKind.TEXAS_RETRIEVAL,
    "texas_retrieval": DispatchKind.TEXAS_RETRIEVAL,
    # Sprint 2: Wanda capability aliases. Hyphen and underscore variants both
    # accepted so operator directives don't need to care about delimiter style.
    "wanda-podcast-episode": DispatchKind.WANDA_PODCAST_EPISODE,
    "wanda-podcast-dialogue": DispatchKind.WANDA_PODCAST_DIALOGUE,
    "wanda-audio-summary": DispatchKind.WANDA_AUDIO_SUMMARY,
    "wanda-music-bed-apply": DispatchKind.WANDA_MUSIC_BED_APPLY,
    "wanda-chapter-markers-emit": DispatchKind.WANDA_CHAPTER_MARKERS_EMIT,
    "wanda-audio-assembly-handoff": DispatchKind.WANDA_AUDIO_ASSEMBLY_HANDOFF,
}


def _classify_dispatch_kind(raw_kind: str | DispatchKind) -> DispatchKind:
    """Classify a raw dispatch-kind string into the closed enum.

    Mirrors the retrieval-shape classifier posture from Story 27-2:
    normalize first, then fail closed with a specific validation error.
    """
    if isinstance(raw_kind, DispatchKind):
        return raw_kind

    candidate = str(raw_kind).strip().lower().replace(" ", "_").replace("/", "_")
    candidate = candidate.replace("-", "_")

    try:
        return DispatchKind(candidate)
    except ValueError:
        pass

    aliased = _KIND_ALIASES.get(str(raw_kind).strip().lower())
    if aliased is not None:
        return aliased

    raise DispatchValidationFailedError(
        f"Unknown dispatch_kind {raw_kind!r}. Expected one of "
        f"{sorted(kind.value for kind in DispatchKind)}.",
        error_detail={"dispatch_kind": str(raw_kind)},
    )


def build_dispatch_envelope(
    *,
    run_id: str,
    dispatch_kind: str | DispatchKind,
    input_packet: Mapping[str, Any],
    context_refs: list[str] | tuple[str, ...] | None = None,
    specialist_id: SpecialistId | str | None = None,
    correlation_id: str | None = None,
    timestamp_utc: datetime | None = None,
) -> DispatchEnvelope:
    """Build and validate a standard dispatch envelope."""
    kind = _classify_dispatch_kind(dispatch_kind)
    if specialist_id is None:
        specialist = DISPATCH_KIND_TO_SPECIALIST[kind]
    elif isinstance(specialist_id, SpecialistId):
        specialist = specialist_id
    else:
        specialist = SpecialistId(str(specialist_id).strip().lower())

    return DispatchEnvelope.model_validate(
        {
            "run_id": run_id,
            "specialist_id": specialist,
            "dispatch_kind": kind,
            "input_packet": dict(input_packet),
            "context_refs": tuple(context_refs or ()),
            "correlation_id": correlation_id or f"{kind.value}-{uuid4().hex[:12]}",
            "timestamp_utc": timestamp_utc or datetime.now(tz=UTC),
        }
    )


def build_dispatch_receipt(
    *,
    correlation_id: str,
    specialist_id: SpecialistId | str,
    outcome: DispatchOutcome | str,
    output_artifacts: list[str] | tuple[str, ...] | None = None,
    diagnostics: Mapping[str, Any] | None = None,
    duration_ms: int = 0,
    timestamp_utc: datetime | None = None,
) -> DispatchReceipt:
    """Build and validate a standard dispatch receipt."""
    if isinstance(specialist_id, SpecialistId):
        specialist = specialist_id
    else:
        specialist = SpecialistId(str(specialist_id).strip().lower())

    if isinstance(outcome, DispatchOutcome):
        parsed_outcome = outcome
    else:
        parsed_outcome = DispatchOutcome(str(outcome).strip().lower())

    return DispatchReceipt.model_validate(
        {
            "correlation_id": correlation_id,
            "specialist_id": specialist,
            "outcome": parsed_outcome,
            "output_artifacts": tuple(output_artifacts or ()),
            "diagnostics": dict(diagnostics or {}),
            "duration_ms": duration_ms,
            "timestamp_utc": timestamp_utc or datetime.now(tz=UTC),
        }
    )


def dispatch_start_log_fields(envelope: DispatchEnvelope) -> dict[str, Any]:
    """Structured logger fields for dispatch.start."""
    return {
        "event": "dispatch.start",
        "run_id": envelope.run_id,
        "specialist_id": envelope.specialist_id.value,
        "dispatch_kind": envelope.dispatch_kind.value,
        "correlation_id": envelope.correlation_id,
        "context_refs": list(envelope.context_refs),
    }


def dispatch_end_log_fields(
    receipt: DispatchReceipt,
    *,
    run_id: str,
    dispatch_kind: DispatchKind,
) -> dict[str, Any]:
    """Structured logger fields for dispatch.end."""
    return {
        "event": "dispatch.end",
        "run_id": run_id,
        "specialist_id": receipt.specialist_id.value,
        "dispatch_kind": dispatch_kind.value,
        "correlation_id": receipt.correlation_id,
        "outcome": receipt.outcome.value,
        "duration_ms": receipt.duration_ms,
        "output_artifacts_count": len(receipt.output_artifacts),
    }


def dump_contract_schemas() -> dict[str, Any]:
    """Return machine-usable JSON schema payload for file pinning."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "MarcusDispatchContracts",
        "$defs": {
            "DispatchEnvelope": DispatchEnvelope.model_json_schema(),
            "DispatchReceipt": DispatchReceipt.model_json_schema(),
            "DispatchError": DispatchError.model_json_schema(),
            "DispatchKind": {
                "type": "string",
                "enum": [kind.value for kind in DispatchKind],
            },
            "DispatchOutcome": {
                "type": "string",
                "enum": [outcome.value for outcome in DispatchOutcome],
            },
            "DispatchErrorKind": {
                "type": "string",
                "enum": [kind.value for kind in DispatchErrorKind],
            },
        },
    }


__all__ = [
    "DISPATCH_KIND_TO_SPECIALIST",
    "DispatchContractError",
    "DispatchContractViolationError",
    "DispatchEnvelope",
    "DispatchError",
    "DispatchErrorKind",
    "DispatchInternalError",
    "DispatchKind",
    "DispatchOutcome",
    "DispatchReceipt",
    "DispatchSpecialistUnavailableError",
    "DispatchTimeoutError",
    "DispatchValidationFailedError",
    "SpecialistId",
    "_classify_dispatch_kind",
    "build_dispatch_envelope",
    "build_dispatch_receipt",
    "dispatch_end_log_fields",
    "dispatch_start_log_fields",
    "dump_contract_schemas",
]
