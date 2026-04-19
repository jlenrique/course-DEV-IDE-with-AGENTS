"""Tests for Marcus chunked speech-to-text intake adapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from marcus.lesson_plan.schema import ScopeDecision
from marcus.orchestrator.voice_interface import (
    ElevenLabsChunkTranscriber,
    FallbackChunkTranscriber,
    LiveConversationSession,
    LiveTalkModeController,
    OpenAIWhisperChunkTranscriber,
    TranscriptResult,
    VoiceDecisionParser,
    VoiceIntakeSession,
    build_chunk_transcriber,
)


class _StubTranscriber:
    def __init__(self, results: list[TranscriptResult]) -> None:
        self._results = results
        self.calls = 0

    def transcribe_chunk(self, chunk_path: Path) -> TranscriptResult:
        _ = chunk_path
        index = min(self.calls, len(self._results) - 1)
        self.calls += 1
        return self._results[index]


def _fallback(unit_id: str) -> tuple[ScopeDecision, str]:
    return (
        ScopeDecision(
            state="ratified",
            scope="out-of-scope",
            proposed_by="operator",
            ratified_by="maya",
        ),
        f"typed fallback for {unit_id}",
    )


def test_mode_controller_toggles_on_commands() -> None:
    mode = LiveTalkModeController(live_enabled=False)
    assert mode.process_command("let's talk live") == "enable_live_talk"
    assert mode.live_enabled is True
    assert mode.process_command("shut down live talk") == "disable_live_talk"
    assert mode.live_enabled is False


def test_parser_extracts_in_scope_decision_with_because_clause() -> None:
    parser = VoiceDecisionParser()
    parsed = parser.parse("in scope because this is core learning objective")
    assert parsed.decision.scope == "in-scope"
    assert parsed.rationale == "this is core learning objective"


def test_parser_rejects_ambiguous_multi_scope_transcript() -> None:
    parser = VoiceDecisionParser()
    with pytest.raises(ValueError, match="exactly one scope decision phrase"):
        parser.parse("in scope and delegated for research support")


def test_session_accepts_first_valid_transcript() -> None:
    transcriber = _StubTranscriber(
        [
            TranscriptResult(
                transcript_text="delegated because need SME support",
                confidence="HIGH",
                confidence_rationale="clear speech",
            )
        ]
    )
    session = VoiceIntakeSession(
        transcriber=transcriber,
        chunk_provider=lambda _unit, _attempt: Path("chunk-1.wav"),
        typed_fallback_provider=_fallback,
        max_attempts_per_unit=2,
        min_confidence="MEDIUM",
    )
    decision, rationale = session.intake_callable(None, "unit-1")  # type: ignore[arg-type]
    assert decision.scope == "delegated"
    assert rationale == "need SME support"
    assert transcriber.calls == 1


def test_session_retries_after_low_confidence_and_succeeds() -> None:
    transcriber = _StubTranscriber(
        [
            TranscriptResult(
                transcript_text="in scope because this should be included",
                confidence="LOW",
                confidence_rationale="too noisy",
            ),
            TranscriptResult(
                transcript_text="in scope because this should be included",
                confidence="HIGH",
                confidence_rationale="clear speech",
            ),
        ]
    )
    session = VoiceIntakeSession(
        transcriber=transcriber,
        chunk_provider=lambda _unit, _attempt: Path("chunk.wav"),
        typed_fallback_provider=_fallback,
        max_attempts_per_unit=3,
        min_confidence="MEDIUM",
    )
    decision, rationale = session.intake_callable(None, "unit-2")  # type: ignore[arg-type]
    assert decision.scope == "in-scope"
    assert rationale == "this should be included"
    assert transcriber.calls == 2


def test_session_falls_back_after_exhausting_attempts() -> None:
    transcriber = _StubTranscriber(
        [
            TranscriptResult(
                transcript_text="",
                confidence="LOW",
                confidence_rationale="silence",
            )
        ]
    )
    session = VoiceIntakeSession(
        transcriber=transcriber,
        chunk_provider=lambda _unit, _attempt: Path("silence.wav"),
        typed_fallback_provider=_fallback,
        max_attempts_per_unit=2,
        min_confidence="MEDIUM",
    )
    decision, rationale = session.intake_callable(None, "unit-3")  # type: ignore[arg-type]
    assert decision.scope == "out-of-scope"
    assert rationale == "typed fallback for unit-3"
    assert transcriber.calls == 2


def test_elevenlabs_transcriber_normalizes_payload() -> None:
    def _fake_transcribe(_path: str, **_kwargs: object) -> dict:
        return {
            "transcript_text": "out of scope because duplicate topic",
            "confidence": "medium",
            "confidence_rationale": "good enough",
        }

    transcriber = ElevenLabsChunkTranscriber(transcribe_fn=_fake_transcribe)
    result = transcriber.transcribe_chunk(Path("chunk.wav"))
    assert result.confidence == "MEDIUM"
    assert "duplicate topic" in result.transcript_text


def test_openai_transcriber_normalizes_payload() -> None:
    def _fake_transcribe(_path: Path) -> dict:
        return {"text": "in scope because openai fallback transcript"}

    transcriber = OpenAIWhisperChunkTranscriber(transcribe_fn=_fake_transcribe)
    result = transcriber.transcribe_chunk(Path("chunk.wav"))
    assert result.confidence == "HIGH"
    assert "openai fallback" in result.transcript_text


def test_fallback_transcriber_uses_secondary_when_primary_empty() -> None:
    primary = _StubTranscriber(
        [
            TranscriptResult(
                transcript_text="",
                confidence="LOW",
                confidence_rationale="primary api unavailable",
            )
        ]
    )
    secondary = _StubTranscriber(
        [
            TranscriptResult(
                transcript_text="blueprint because fallback provider succeeded",
                confidence="HIGH",
                confidence_rationale="fallback success",
            )
        ]
    )
    transcriber = FallbackChunkTranscriber(primary=primary, secondary=secondary)
    result = transcriber.transcribe_chunk(Path("chunk.wav"))
    assert result.confidence == "HIGH"
    assert "fallback provider succeeded" in result.transcript_text
    assert primary.calls == 1
    assert secondary.calls == 1


def test_build_chunk_transcriber_auto_returns_fallback_chain() -> None:
    transcriber = build_chunk_transcriber("auto")
    assert isinstance(transcriber, FallbackChunkTranscriber)


def test_live_conversation_session_accepts_non_scope_transcript() -> None:
    transcriber = _StubTranscriber(
        [
            TranscriptResult(
                transcript_text="hey marcus can you hear me",
                confidence="HIGH",
                confidence_rationale="clear speech",
            )
        ]
    )
    session = LiveConversationSession(
        transcriber=transcriber,
        chunk_provider=lambda _unit, _attempt: Path("chunk.wav"),
        typed_text_provider=lambda: None,
        mode_controller=LiveTalkModeController(live_enabled=True),
    )
    turn = session.next_turn("turn-1")
    assert turn.kind == "utterance"
    assert turn.utterance == "hey marcus can you hear me"


def test_live_conversation_session_returns_none_for_toggle_command() -> None:
    transcriber = _StubTranscriber(
        [
            TranscriptResult(
                transcript_text="shut down live talk",
                confidence="HIGH",
                confidence_rationale="clear speech",
            )
        ]
    )
    mode = LiveTalkModeController(live_enabled=True)
    session = LiveConversationSession(
        transcriber=transcriber,
        chunk_provider=lambda _unit, _attempt: Path("chunk.wav"),
        typed_text_provider=lambda: None,
        mode_controller=mode,
    )
    turn = session.next_turn("turn-1")
    assert turn.kind == "command"
    assert turn.utterance is None
    assert mode.live_enabled is False


def test_live_conversation_session_reports_silence() -> None:
    transcriber = _StubTranscriber(
        [
            TranscriptResult(
                transcript_text="",
                confidence="LOW",
                confidence_rationale="silence",
            )
        ]
    )
    session = LiveConversationSession(
        transcriber=transcriber,
        chunk_provider=lambda _unit, _attempt: Path("chunk.wav"),
        typed_text_provider=lambda: None,
        mode_controller=LiveTalkModeController(live_enabled=True),
    )
    turn = session.next_turn("turn-1")
    assert turn.kind == "silence"


def test_live_conversation_session_skips_typed_fallback_when_live_disabled() -> None:
    transcriber = _StubTranscriber(
        [
            TranscriptResult(
                transcript_text="",
                confidence="LOW",
                confidence_rationale="silence",
            )
        ]
    )
    session = LiveConversationSession(
        transcriber=transcriber,
        chunk_provider=lambda _unit, _attempt: Path("chunk.wav"),
        typed_text_provider=lambda: "typed response",
        mode_controller=LiveTalkModeController(live_enabled=True),
        typed_fallback_when_live=False,
    )
    turn = session.next_turn("turn-1")
    assert turn.kind == "silence"


def test_session_starts_text_only_when_mode_disabled() -> None:
    mode = LiveTalkModeController(live_enabled=False)
    transcriber = _StubTranscriber(
        [
            TranscriptResult(
                transcript_text="in scope because should not be used",
                confidence="HIGH",
                confidence_rationale="clear speech",
            )
        ]
    )
    session = VoiceIntakeSession(
        transcriber=transcriber,
        chunk_provider=lambda _unit, _attempt: Path("unused.wav"),
        typed_fallback_provider=_fallback,
        mode_controller=mode,
    )
    decision, rationale = session.intake_callable(None, "unit-text-only")  # type: ignore[arg-type]
    assert decision.scope == "out-of-scope"
    assert rationale == "typed fallback for unit-text-only"
    assert transcriber.calls == 0


def test_session_enables_live_mode_from_typed_command() -> None:
    mode = LiveTalkModeController(live_enabled=False)
    transcriber = _StubTranscriber(
        [
            TranscriptResult(
                transcript_text="in scope because this belongs in the lesson",
                confidence="HIGH",
                confidence_rationale="clear speech",
            )
        ]
    )

    fallback_calls = {"count": 0}

    def _typed_provider(_unit_id: str) -> tuple[ScopeDecision, str] | None:
        fallback_calls["count"] += 1
        if fallback_calls["count"] == 1:
            mode.process_command("let's talk live")
            return None
        return _fallback(_unit_id)

    session = VoiceIntakeSession(
        transcriber=transcriber,
        chunk_provider=lambda _unit, _attempt: Path("chunk.wav"),
        typed_fallback_provider=_typed_provider,
        mode_controller=mode,
    )
    decision, rationale = session.intake_callable(None, "unit-live-toggle")  # type: ignore[arg-type]
    assert decision.scope == "in-scope"
    assert "belongs in the lesson" in rationale
    assert transcriber.calls == 1
    assert fallback_calls["count"] == 1


def test_session_disables_live_mode_from_spoken_command() -> None:
    mode = LiveTalkModeController(live_enabled=True)
    transcriber = _StubTranscriber(
        [
            TranscriptResult(
                transcript_text="shut down live talk",
                confidence="HIGH",
                confidence_rationale="clear speech",
            )
        ]
    )
    session = VoiceIntakeSession(
        transcriber=transcriber,
        chunk_provider=lambda _unit, _attempt: Path("chunk.wav"),
        typed_fallback_provider=_fallback,
        mode_controller=mode,
    )
    decision, rationale = session.intake_callable(None, "unit-disable-live")  # type: ignore[arg-type]
    assert decision.scope == "out-of-scope"
    assert rationale == "typed fallback for unit-disable-live"
    assert mode.live_enabled is False
    assert transcriber.calls == 1

