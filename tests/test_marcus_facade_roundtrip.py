"""Facade → orchestrator → log round-trip (AC-T.11).

Real :class:`LessonPlanLog` instance on tmp_path. No mocks of the 31-2
log. Proves 30-1's seams don't subtly break the 31-2 contract.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from marcus.facade import get_facade, reset_facade
from marcus.lesson_plan.events import EventEnvelope
from marcus.lesson_plan.log import LessonPlanLog
from marcus.orchestrator import ORCHESTRATOR_MODULE_IDENTITY
from marcus.orchestrator.write_api import emit_pre_packet_snapshot

_VALID_PAYLOAD: dict = {
    "source_ref": {
        "path": "tests/fixtures/trial_corpus/placeholder.md",
        "sha256": "b" * 64,
    },
    "pre_packet_artifact_path": "tests/fixtures/trial_corpus/placeholder.md",
    "audience_profile_version": 1,
    "sme_refs": ["placeholder"],
}


def test_facade_roundtrip_real_log(tmp_path: Path) -> None:
    """AC-T.11 — facade is callable; write_api round-trips to real 31-2 log."""
    reset_facade()
    try:
        # Facade surfaces (Maya-side smoke).
        facade = get_facade()
        greeting = facade.greet()
        assert "Marcus" in greeting

        # Write-side round-trip.
        log = LessonPlanLog(path=tmp_path / "log.jsonl")
        envelope = EventEnvelope(
            event_id=str(uuid4()),
            timestamp=datetime.now(tz=UTC),
            plan_revision=0,
            event_type="pre_packet_snapshot",
            payload=_VALID_PAYLOAD,
        )
        emit_pre_packet_snapshot(
            envelope, writer=ORCHESTRATOR_MODULE_IDENTITY, log=log
        )

        # Read-side verification — 31-2 log received the envelope.
        events = list(log.read_events())
        assert len(events) == 1
        assert events[0].event_id == envelope.event_id
        assert events[0].event_type == "pre_packet_snapshot"
        assert events[0].payload["pre_packet_artifact_path"] == (
            "tests/fixtures/trial_corpus/placeholder.md"
        )
    finally:
        reset_facade()
