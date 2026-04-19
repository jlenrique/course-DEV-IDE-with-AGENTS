"""Tests for Marcus live STT session cost estimation helpers."""

from __future__ import annotations

from scripts.utilities.marcus_live_stt import SessionCostTracker


def test_cost_estimate_increases_with_usage() -> None:
    tracker = SessionCostTracker()
    baseline = tracker.estimate_total_usd()
    tracker.stt_audio_seconds = 30.0
    tracker.tts_output_chars = 500
    tracker.openai_prompt_tokens = 1000
    tracker.openai_completion_tokens = 500
    assert tracker.estimate_total_usd() > baseline


def test_cost_summary_lines_include_total() -> None:
    tracker = SessionCostTracker(
        stt_audio_seconds=10.0,
        tts_output_chars=120,
        openai_prompt_tokens=50,
        openai_completion_tokens=25,
        turns=2,
    )
    summary = tracker.render_summary_lines()
    assert any("estimated_total_usd=$" in line for line in summary)

