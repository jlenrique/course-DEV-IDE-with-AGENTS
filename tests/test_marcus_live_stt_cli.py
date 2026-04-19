"""Tests for Marcus live STT CLI mode prompt helpers."""

from __future__ import annotations

from scripts.utilities import marcus_live_stt


def test_should_enable_live_talk_positive_values() -> None:
    assert marcus_live_stt.should_enable_live_talk("y") is True
    assert marcus_live_stt.should_enable_live_talk("YES") is True
    assert marcus_live_stt.should_enable_live_talk("talk live") is True


def test_should_enable_live_talk_defaults_to_no() -> None:
    assert marcus_live_stt.should_enable_live_talk("") is False
    assert marcus_live_stt.should_enable_live_talk("n") is False
    assert marcus_live_stt.should_enable_live_talk("nope") is False


def test_parser_accepts_openai_provider() -> None:
    parser = marcus_live_stt._build_parser()
    args = parser.parse_args(
        [
            "--lesson-plan-json",
            "state/runtime/marcus-live-stt/sample-plan.json",
            "--stt-provider",
            "openai",
        ]
    )
    assert args.stt_provider == "openai"


def test_parser_accepts_mic_input_and_tts_flag() -> None:
    parser = marcus_live_stt._build_parser()
    args = parser.parse_args(
        [
            "--lesson-plan-json",
            "state/runtime/marcus-live-stt/sample-plan.json",
            "--input-mode",
            "mic",
            "--tts-enabled",
            "--mic-seconds",
            "4",
            "--mic-backend",
            "dshow",
            "--silence-timeout-seconds",
            "10",
            "--followup-2-delay-seconds",
            "5",
            "--followup-response-timeout-seconds",
            "3",
            "--voice-shutdown-grace-seconds",
            "2",
        ]
    )
    assert args.input_mode == "mic"
    assert args.tts_enabled is True
    assert args.mic_seconds == 4
    assert args.mic_backend == "dshow"
    assert args.silence_timeout_seconds == 10
    assert args.followup_2_delay_seconds == 5
    assert args.followup_response_timeout_seconds == 3
    assert args.voice_shutdown_grace_seconds == 2


def test_parser_accepts_list_mic_devices_flag() -> None:
    parser = marcus_live_stt._build_parser()
    args = parser.parse_args(
        [
            "--lesson-plan-json",
            "state/runtime/marcus-live-stt/sample-plan.json",
            "--list-mic-devices",
        ]
    )
    assert args.list_mic_devices is True


def test_parser_accepts_chat_mode_without_lesson_plan() -> None:
    parser = marcus_live_stt._build_parser()
    args = parser.parse_args(
        [
            "--session-mode",
            "chat",
            "--input-mode",
            "path",
        ]
    )
    assert args.session_mode == "chat"
    assert args.lesson_plan_json is None


def test_parser_accepts_dry_run_flag() -> None:
    parser = marcus_live_stt._build_parser()
    args = parser.parse_args(
        [
            "--session-mode",
            "chat",
            "--dry-run",
        ]
    )
    assert args.dry_run is True


def test_attempts_for_window_rounds_up() -> None:
    assert marcus_live_stt._attempts_for_window(10.0, 4.0) == 3
    assert marcus_live_stt._attempts_for_window(3.0, 4.0) == 1

