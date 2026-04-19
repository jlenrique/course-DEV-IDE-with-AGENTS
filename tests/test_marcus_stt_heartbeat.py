"""Tests for STT heartbeat utility script."""

from __future__ import annotations

from pathlib import Path

from marcus.orchestrator.voice_interface import TranscriptResult
from scripts.utilities import marcus_stt_heartbeat


class _StubHeartbeatTranscriber:
    def transcribe_chunk(self, _chunk_path: Path) -> TranscriptResult:
        return TranscriptResult(
            transcript_text="in scope because heartbeat succeeded",
            confidence="HIGH",
            confidence_rationale="stubbed",
        )


def test_heartbeat_main_succeeds_with_transcript(monkeypatch, tmp_path, capsys) -> None:
    audio_path = tmp_path / "heartbeat.wav"
    audio_path.write_bytes(b"RIFF")

    monkeypatch.setattr(
        "marcus.orchestrator.voice_interface.build_chunk_transcriber",
        lambda *_args, **_kwargs: _StubHeartbeatTranscriber(),
    )

    rc = marcus_stt_heartbeat.main(
        [
            "--audio-path",
            str(audio_path),
            "--provider",
            "openai",
        ]
    )
    out = capsys.readouterr().out
    assert rc == 0
    assert "heartbeat succeeded" in out

