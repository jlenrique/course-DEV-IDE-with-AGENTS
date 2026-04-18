"""Event-type registry + open-string validator (Story 31-1 AC-B.8).

Two registered sets:

- :data:`KNOWN_PLAN_UNIT_EVENT_TYPES` — the nine Gagne-9 event labels. These
  are the valid ``event_type`` values on ``PlanUnit``.
- :data:`RESERVED_LOG_EVENT_TYPES` — the mandatory log event-types pre-registered
  for 31-2 emission. Reserved, not emitted by 31-1 (single-writer rule per
  R1 ruling amendment 13).

:func:`validate_event_type` WARNS (does not reject) on event_types outside
either set so that future learning-model / event-stream extensions emerge
visibly in observability, not silently. Invalid-regex strings are REJECTED.
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Known plan_unit event_type labels (Gagne-9)
# ---------------------------------------------------------------------------

KNOWN_PLAN_UNIT_EVENT_TYPES: frozenset[str] = frozenset(
    {f"gagne-event-{n}" for n in range(1, 10)}
)
"""The nine Gagne Events of Instruction as open-string labels."""


# ---------------------------------------------------------------------------
# Reserved log event_types (R1 ruling amendment 8 / R2 rider W-1)
# ---------------------------------------------------------------------------

RESERVED_LOG_EVENT_TYPES: frozenset[str] = frozenset(
    {
        # Reserved for 31-2 pre_packet_snapshot emission per R1 ruling amendment 13
        # (single-writer rule).
        "pre_packet_snapshot",
        "plan_unit.created",
        "scope_decision.set",
        "scope_decision_transition",
        "plan.locked",
        "fanout.envelope.emitted",
    }
)


REGISTERED_EVENT_TYPES: frozenset[str] = (
    KNOWN_PLAN_UNIT_EVENT_TYPES | RESERVED_LOG_EVENT_TYPES
)
"""Union of known + reserved event_types; the "registered" set."""


_OPEN_ID_REGEX = re.compile(r"^[a-z0-9._-]+$")

# SF-4: dedup warnings — warn only on FIRST encounter of an unknown event_type
# per process lifetime. Without this, a hot path emitting the same unknown
# event_type on every call floods the logs (Edge Case Hunter #8 / Blind #7).
_WARNED_UNKNOWN_TYPES: set[str] = set()


def _reset_warning_state() -> None:
    """Clear the warn-once memo. For test isolation only."""
    _WARNED_UNKNOWN_TYPES.clear()


def validate_event_type(value: str) -> str:
    """Validate an event_type string; WARN once per unknown value (AC-B.8 / AC-T.6).

    Rules:
        - Must be a non-empty string matching ``^[a-z0-9._-]+$``.
        - If the value is in :data:`REGISTERED_EVENT_TYPES`, return silently.
        - Otherwise log a warning at WARNING level **only on first encounter
          per process lifetime** and return the value unchanged. Unknown
          values are PERMITTED for Gagne-seam extensibility (future learning
          models ship a second-tier story). Dedup implemented via
          ``_WARNED_UNKNOWN_TYPES`` module-level set (SF-4).
    """
    if not isinstance(value, str) or not value:
        raise ValueError("event_type must be a non-empty string")
    if not _OPEN_ID_REGEX.match(value):
        raise ValueError(
            f"event_type {value!r} fails open-id regex ^[a-z0-9._-]+$"
        )
    if value not in REGISTERED_EVENT_TYPES and value not in _WARNED_UNKNOWN_TYPES:
        logger.warning(
            "event_type %r not in known registry; "
            "permitted for Gagné-seam extensibility",
            value,
        )
        _WARNED_UNKNOWN_TYPES.add(value)
    return value


__all__ = [
    "KNOWN_PLAN_UNIT_EVENT_TYPES",
    "REGISTERED_EVENT_TYPES",
    "RESERVED_LOG_EVENT_TYPES",
    "validate_event_type",
]
