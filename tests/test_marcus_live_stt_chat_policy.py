"""Tests for Marcus live chat response policy helpers."""

from __future__ import annotations

from scripts.utilities import marcus_live_stt


def test_compose_chat_reply_dry_run_is_scope_neutral() -> None:
    reply = marcus_live_stt._compose_chat_reply(
        "in-scope because this might execute",
        dry_run=True,
    )
    assert "dry-run" in reply.lower()
    assert "scope intent" not in reply.lower()

