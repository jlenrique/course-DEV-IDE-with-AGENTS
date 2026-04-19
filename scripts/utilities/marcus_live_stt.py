#!/usr/bin/env python3
"""Run a live chunked STT session against Marcus 4A orchestration."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
import uuid
import wave
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

if TYPE_CHECKING:
    from marcus.lesson_plan.schema import LessonPlan


@dataclass
class SessionCostTracker:
    """Tracks session usage and returns a rough USD estimate."""

    stt_audio_seconds: float = 0.0
    tts_output_chars: int = 0
    openai_prompt_tokens: int = 0
    openai_completion_tokens: int = 0
    turns: int = 0

    # Heuristic defaults; tune to account-specific pricing if needed.
    elevenlabs_stt_usd_per_minute: float = 0.03
    elevenlabs_tts_usd_per_1k_chars: float = 0.30
    openai_input_usd_per_1m_tokens: float = 0.15
    openai_output_usd_per_1m_tokens: float = 0.60

    def record_stt_chunk(self, chunk_path: Path) -> None:
        self.stt_audio_seconds += _audio_duration_seconds(chunk_path)

    def record_tts_text(self, text: str) -> None:
        self.tts_output_chars += len(text.strip())

    def record_openai_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.openai_prompt_tokens += max(prompt_tokens, 0)
        self.openai_completion_tokens += max(completion_tokens, 0)

    def estimate_total_usd(self) -> float:
        stt_cost = (self.stt_audio_seconds / 60.0) * self.elevenlabs_stt_usd_per_minute
        tts_cost = (self.tts_output_chars / 1000.0) * self.elevenlabs_tts_usd_per_1k_chars
        openai_input_cost = (
            self.openai_prompt_tokens / 1_000_000.0
        ) * self.openai_input_usd_per_1m_tokens
        openai_output_cost = (
            self.openai_completion_tokens / 1_000_000.0
        ) * self.openai_output_usd_per_1m_tokens
        return stt_cost + tts_cost + openai_input_cost + openai_output_cost

    def render_summary_lines(self) -> list[str]:
        return [
            "[cost] session usage estimate (heuristic):",
            f"[cost] turns={self.turns}",
            f"[cost] stt_audio_seconds={self.stt_audio_seconds:.2f}",
            f"[cost] tts_output_chars={self.tts_output_chars}",
            (
                "[cost] openai_tokens="
                f"{self.openai_prompt_tokens} prompt / {self.openai_completion_tokens} completion"
            ),
            f"[cost] estimated_total_usd=${self.estimate_total_usd():.4f}",
        ]


def _audio_duration_seconds(path: Path) -> float:
    """Return WAV duration seconds when available; fallback to zero."""
    try:
        with wave.open(str(path), "rb") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            if rate <= 0:
                return 0.0
            return frames / float(rate)
    except (wave.Error, FileNotFoundError, OSError):
        return 0.0


class MeteredChunkTranscriber:
    """Wraps a chunk transcriber and records consumed audio duration."""

    def __init__(self, *, delegate, tracker: SessionCostTracker) -> None:
        self._delegate = delegate
        self._tracker = tracker

    def transcribe_chunk(self, chunk_path: Path):
        self._tracker.record_stt_chunk(chunk_path)
        return self._delegate.transcribe_chunk(chunk_path)


class ElevenLabsLiveVoice:
    """Lightweight ElevenLabs TTS player for local headphone playback."""

    def __init__(
        self,
        *,
        output_dir: Path,
        voice_id: str | None = None,
        tracker: SessionCostTracker | None = None,
    ) -> None:
        from scripts.api_clients.elevenlabs_client import ElevenLabsClient
        from scripts.utilities.ffmpeg import resolve_ffmpeg_binary

        load_dotenv(REPO_ROOT / ".env", override=True)
        self._client = ElevenLabsClient()
        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._voice_id = voice_id or self._resolve_default_voice_id()
        self._ffmpeg_binary = resolve_ffmpeg_binary()
        self._tracker = tracker

    def speak(self, text: str) -> None:
        """Synthesize and play one short Marcus utterance."""
        try:
            import winsound
        except ImportError as exc:
            raise RuntimeError("winsound is unavailable on this platform.") from exc

        cleaned = text.strip()
        if not cleaned:
            return
        if self._tracker is not None:
            self._tracker.record_tts_text(cleaned)
        output_stem = self._output_dir / f"marcus-tts-{uuid.uuid4().hex}"
        mp3_path = output_stem.with_suffix(".mp3")
        wav_path = output_stem.with_suffix(".wav")
        audio_mp3 = self._client.text_to_speech(
            cleaned,
            self._voice_id,
            output_format="mp3_44100_128",
        )
        mp3_path.write_bytes(audio_mp3)
        conversion = subprocess.run(
            [
                self._ffmpeg_binary,
                "-y",
                "-i",
                str(mp3_path),
                str(wav_path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if conversion.returncode != 0:
            tail = (
                conversion.stderr.strip().splitlines()[-1]
                if conversion.stderr
                else "ffmpeg conversion failed"
            )
            raise RuntimeError(f"TTS playback conversion failed: {tail}")
        with wave.open(str(wav_path), "rb"):
            pass
        winsound.PlaySound(str(wav_path), winsound.SND_FILENAME)

    def _resolve_default_voice_id(self) -> str:
        voices = self._client.list_voices()
        if not voices:
            raise RuntimeError("No ElevenLabs voices available for TTS playback.")
        first_voice = voices[0]
        voice_id = str(first_voice.get("voice_id", "")).strip()
        if not voice_id:
            raise RuntimeError("ElevenLabs voice catalog response missing voice_id.")
        return voice_id


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run Marcus 4A using chunked speech-to-text input. "
            "Each unit prompts for an audio chunk path."
        )
    )
    parser.add_argument(
        "--session-mode",
        choices=("4a", "chat"),
        default="4a",
        help="4a locks a plan; chat keeps a natural ongoing conversation.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use scope-neutral conversational policy (no execution routing).",
    )
    parser.add_argument(
        "--lesson-plan-json",
        required=False,
        type=Path,
        help="Path to a lesson plan JSON file to pass into Facade.run_4a.",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=None,
        help="Optional path for LessonPlanLog JSONL output.",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=3,
        help="Max STT attempts per unit before typed fallback.",
    )
    parser.add_argument(
        "--min-confidence",
        choices=("LOW", "MEDIUM", "HIGH"),
        default="MEDIUM",
        help="Lowest accepted STT confidence level.",
    )
    parser.add_argument(
        "--input-mode",
        choices=("path", "mic"),
        default="path",
        help="Audio chunk source: path prompt or live microphone capture.",
    )
    parser.add_argument(
        "--list-mic-devices",
        action="store_true",
        help="List discoverable ffmpeg dshow microphone devices and exit.",
    )
    parser.add_argument(
        "--mic-seconds",
        type=float,
        default=6.0,
        help="Capture duration in seconds per live mic chunk.",
    )
    parser.add_argument(
        "--silence-timeout-seconds",
        type=float,
        default=10.0,
        help="In chat+mic mode, end session after this much continuous silence.",
    )
    parser.add_argument(
        "--followup-2-delay-seconds",
        type=float,
        default=5.0,
        help="Delay after 'are you there 01' before issuing 'are you there 02'.",
    )
    parser.add_argument(
        "--followup-response-timeout-seconds",
        type=float,
        default=3.0,
        help="How long to wait for response after each follow-up prompt.",
    )
    parser.add_argument(
        "--voice-shutdown-grace-seconds",
        type=float,
        default=2.0,
        help="Delay after shutdown warning before voice mode is actually disabled.",
    )
    parser.add_argument(
        "--mic-device",
        default="default",
        help="Microphone device identifier (default uses OS default input).",
    )
    parser.add_argument(
        "--mic-backend",
        choices=("dshow", "wasapi"),
        default="dshow",
        help="ffmpeg input backend for microphone capture on Windows.",
    )
    parser.add_argument(
        "--mic-sample-rate",
        type=int,
        default=16000,
        help="Mic capture sample rate for chunk transcription.",
    )
    parser.add_argument(
        "--runtime-audio-dir",
        type=Path,
        default=Path("state/runtime/marcus-live-stt/live-chunks"),
        help="Directory for temporary live mic chunks and TTS files.",
    )
    parser.add_argument(
        "--tts-enabled",
        action="store_true",
        help="Speak Marcus prompts/results through local audio playback.",
    )
    parser.add_argument(
        "--tts-voice-id",
        type=str,
        default=None,
        help="Optional ElevenLabs voice id for Marcus live playback.",
    )
    parser.add_argument(
        "--stt-provider",
        choices=("auto", "elevenlabs", "openai"),
        default="auto",
        help="STT provider strategy: auto uses ElevenLabs with OpenAI fallback.",
    )
    parser.add_argument(
        "--keyterm",
        action="append",
        default=[],
        help="Optional keyterm bias term for ElevenLabs STT (repeatable).",
    )
    return parser


def _read_lesson_plan(path: Path) -> LessonPlan:
    from marcus.lesson_plan.schema import LessonPlan

    if not path.exists():
        raise FileNotFoundError(f"lesson plan file does not exist: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return LessonPlan.model_validate(payload)


def _interactive_chunk_provider(unit_id: str, attempt_index: int) -> Path | None:
    response = input(
        f"[voice] unit={unit_id} attempt={attempt_index} audio chunk path "
        "(empty to trigger typed fallback): "
    ).strip()
    if not response:
        return None
    return Path(response)


def _capture_mic_chunk(
    *,
    output_path: Path,
    seconds: float,
    device: str,
    sample_rate: int,
    backend: str,
) -> None:
    from scripts.utilities.ffmpeg import resolve_ffmpeg_binary

    ffmpeg = resolve_ffmpeg_binary()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    input_device = device
    if backend == "dshow":
        if device == "default":
            input_device = "audio=default"
        elif not device.startswith("audio="):
            input_device = f"audio={device}"
    command = [
        ffmpeg,
        "-y",
        "-f",
        backend,
        "-i",
        input_device,
        "-t",
        f"{seconds:.2f}",
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        str(output_path),
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        tail = result.stderr.strip().splitlines()[-1] if result.stderr else "unknown ffmpeg error"
        raise RuntimeError(f"mic capture failed: {tail}")


def _list_dshow_audio_devices() -> list[str]:
    from scripts.utilities.ffmpeg import resolve_ffmpeg_binary

    ffmpeg = resolve_ffmpeg_binary()
    result = subprocess.run(
        [ffmpeg, "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
        check=False,
        capture_output=True,
        text=True,
    )
    output = f"{result.stdout}\n{result.stderr}"
    devices: list[str] = []
    for match in re.finditer(r'"([^"]+)"\s+\(audio\)', output):
        normalized = " ".join(match.group(1).split())
        devices.append(normalized)
    return devices


def _build_live_mic_chunk_provider(
    *,
    runtime_audio_dir: Path,
    mic_seconds: float,
    mic_device: str,
    mic_sample_rate: int,
    mic_backend: str,
    tts_voice: ElevenLabsLiveVoice | None,
) -> Callable[[str, int], Path | None]:
    def _provider(unit_id: str, attempt_index: int) -> Path | None:
        print(
            f"[voice] live mic capture unit={unit_id} attempt={attempt_index} "
            f"for {mic_seconds:.1f}s (device={mic_device})."
        )
        chunk_path = runtime_audio_dir / f"{unit_id}-attempt-{attempt_index}.wav"
        try:
            _capture_mic_chunk(
                output_path=chunk_path,
                seconds=mic_seconds,
                device=mic_device,
                sample_rate=mic_sample_rate,
                backend=mic_backend,
            )
        except RuntimeError as exc:
            print(f"[voice] mic capture error: {exc}")
            return None
        return chunk_path

    return _provider


def _safe_speak(tts_voice: ElevenLabsLiveVoice, text: str) -> None:
    """Best-effort Marcus playback without breaking the session on TTS errors."""
    try:
        tts_voice.speak(text)
    except Exception as exc:  # pragma: no cover - runtime environment variability
        print(f"[voice] TTS playback unavailable: {exc}")


def should_enable_live_talk(response: str) -> bool:
    """Return True if the session should start in live STT mode."""
    normalized = response.strip().lower()
    return normalized in {"y", "yes", "stt", "talk live", "live"}


def _prompt_for_live_talk_mode() -> bool:
    response = input("Start session in live talk (STT) mode? [y/N]: ")
    return should_enable_live_talk(response)


def _print_locked_plan(locked: LessonPlan) -> None:
    print("\nMarcus plan locked.")
    print(f"revision={locked.revision} digest={locked.digest}")
    print("ratified decisions:")
    for unit in locked.plan_units:
        scope = unit.scope_decision.scope if unit.scope_decision is not None else "<none>"
        print(f"- {unit.unit_id}: {scope} rationale={unit.rationale!r}")


def _interactive_text_provider() -> str | None:
    """Prompt for typed conversation input in chat mode."""
    return input("[chat] you: ")


def _no_typed_input_provider() -> str | None:
    """Disable typed fallback (used for mic-only silence timeout flow)."""
    return None


def _compose_chat_reply(user_text: str, *, dry_run: bool = False) -> str:
    """Produce a deterministic fallback reply for live chat mode."""
    lowered = user_text.strip().lower()
    if lowered in {"exit", "quit", "goodbye", "stop conversation"}:
        return "I hear you. I am closing live conversation now. Want to start another session?"
    if dry_run:
        return (
            "Under dry-run, I keep this conversational and avoid executing actions. "
            "What do you want to explore next?"
        )
    if "scope" in lowered or "in-scope" in lowered or "out-of-scope" in lowered:
        return (
            "Got it. We can discuss scope naturally and decide on execution separately. "
            "What direction do you want to take?"
        )
    if "execute" in lowered or "run this" in lowered:
        return (
            "I can queue this as an execution step while keeping the conversation open. "
            "Should I proceed?"
        )
    return "Understood. Tell me what outcome you want, and I will help you shape the next step."


def _attempts_for_window(window_seconds: float, mic_seconds: float) -> int:
    """Convert a wall-clock wait window into mic-chunk attempts."""
    safe_chunk = max(mic_seconds, 0.1)
    safe_window = max(window_seconds, 0.1)
    return max(1, math.ceil(safe_window / safe_chunk))


class OpenAIChatResponder:
    """OpenAI-backed conversational responder with short rolling history."""

    def __init__(
        self,
        *,
        dry_run: bool,
        model: str = "gpt-4o-mini",
        max_history_messages: int = 10,
        tracker: SessionCostTracker | None = None,
    ) -> None:
        load_dotenv(REPO_ROOT / ".env", override=True)
        self._api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not self._api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self._model = model
        self._max_history = max_history_messages
        self._tracker = tracker
        policy = (
            "You are Marcus in live conversation mode. "
            "Keep responses natural, concise, and helpful. "
            "Do not parrot the user's words unless clarification is necessary. "
            "Do not end the session unless user asks to exit."
        )
        if dry_run:
            policy += (
                " This session is dry-run: do not commit/execute actions, "
                "but continue natural conversation."
            )
        self._messages: list[dict[str, str]] = [{"role": "system", "content": policy}]

    def reply(self, user_text: str) -> str:
        self._messages.append({"role": "user", "content": user_text})
        self._messages = [self._messages[0], *self._messages[-self._max_history :]]
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self._model,
                "messages": self._messages,
                "temperature": 0.6,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        usage = payload.get("usage", {})
        if self._tracker is not None:
            self._tracker.record_openai_usage(
                int(usage.get("prompt_tokens", 0) or 0),
                int(usage.get("completion_tokens", 0) or 0),
            )
        content = (
            payload.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        if not content:
            content = "I am here with you. What should we tackle next?"
        self._messages.append({"role": "assistant", "content": content})
        self._messages = [self._messages[0], *self._messages[-self._max_history :]]
        return content


def _run_chat_session(
    *,
    transcriber,
    chunk_provider,
    typed_text_provider,
    mode_controller,
    tts_voice: ElevenLabsLiveVoice | None,
    max_attempts: int,
    dry_run: bool,
    silence_timeout_seconds: float,
    followup_2_delay_seconds: float,
    followup_response_timeout_seconds: float,
    voice_shutdown_grace_seconds: float,
    mic_seconds: float | None,
    typed_fallback_when_live: bool,
    tracker: SessionCostTracker,
) -> int:
    from marcus.orchestrator.voice_interface import LiveConversationSession

    chat_session = LiveConversationSession(
        transcriber=transcriber,
        chunk_provider=chunk_provider,
        typed_text_provider=typed_text_provider,
        mode_controller=mode_controller,
        max_attempts_per_turn=max_attempts,
        typed_fallback_when_live=typed_fallback_when_live,
    )
    print("[chat] live conversation mode active. Say or type 'exit' to stop.")
    if dry_run:
        print("[chat] dry-run policy enabled: scope-neutral conversation responses.")
    chat_responder = None
    try:
        chat_responder = OpenAIChatResponder(dry_run=dry_run, tracker=tracker)
        print("[chat] using OpenAI conversational responder.")
    except Exception:
        print("[chat] OpenAI responder unavailable; using local fallback replies.")
    if tts_voice is not None:
        _safe_speak(tts_voice, "Live conversation mode is active. I am listening.")

    turn_index = 1
    while True:
        turn = chat_session.next_turn(f"turn-{turn_index}")
        if turn.kind == "command":
            continue
        if turn.kind == "silence":
            if not mode_controller.live_enabled or mic_seconds is None:
                continue

            followup_attempts = _attempts_for_window(
                followup_response_timeout_seconds,
                mic_seconds,
            )
            followup_gap_attempts = _attempts_for_window(
                followup_2_delay_seconds,
                mic_seconds,
            )

            followup_1 = "are you there 01"
            print(f"[marcus] {followup_1}")
            if tts_voice is not None:
                _safe_speak(tts_voice, followup_1)
            turn = chat_session.next_turn(
                f"turn-{turn_index}-followup-1",
                max_attempts_override=followup_attempts,
            )
            if turn.kind == "utterance":
                print("[chat] response received after follow-up 01; resetting silence timer.")
                # Continue with normal reply generation below.
            elif turn.kind == "command":
                continue
            else:
                gap_turn = chat_session.next_turn(
                    f"turn-{turn_index}-followup-gap",
                    max_attempts_override=followup_gap_attempts,
                )
                if gap_turn.kind == "utterance":
                    print("[chat] response received during follow-up gap; resetting silence timer.")
                    turn = gap_turn
                elif gap_turn.kind == "command":
                    continue
                else:
                    followup_2 = "are you there 02"
                    print(f"[marcus] {followup_2}")
                    if tts_voice is not None:
                        _safe_speak(tts_voice, followup_2)
                    turn = chat_session.next_turn(
                        f"turn-{turn_index}-followup-2",
                        max_attempts_override=followup_attempts,
                    )
                    if turn.kind == "utterance":
                        print(
                            "[chat] response received after follow-up 02; "
                            "resetting silence timer."
                        )
                    elif turn.kind == "command":
                        continue
                    else:
                        warning = (
                            "I am about to switch off voice mode due to continued silence."
                        )
                        print(f"[marcus] {warning}")
                        if tts_voice is not None:
                            _safe_speak(tts_voice, warning)
                        time.sleep(max(voice_shutdown_grace_seconds, 0.0))
                        mode_controller.process_command("shut down live talk")
                        shutdown = (
                            "I am switching off voice mode due to continued silence. "
                            "We can continue in text."
                        )
                        print(f"[marcus] {shutdown}")
                        if tts_voice is not None:
                            _safe_speak(tts_voice, shutdown)
                        continue
        utterance = turn.utterance or ""
        tracker.turns += 1
        print(f"[chat] transcript: {utterance}")
        if chat_responder is not None:
            try:
                reply = chat_responder.reply(utterance)
            except Exception as exc:
                print(f"[chat] OpenAI responder error: {exc}. Falling back to local policy.")
                chat_responder = None
                reply = _compose_chat_reply(utterance, dry_run=dry_run)
        else:
            reply = _compose_chat_reply(utterance, dry_run=dry_run)
        print(f"[marcus] {reply}")
        if tts_voice is not None:
            _safe_speak(tts_voice, reply)
        if utterance.strip().lower() in {"exit", "quit", "goodbye", "stop conversation"}:
            return 0
        turn_index += 1


def main(argv: Sequence[str] | None = None) -> int:
    from marcus.facade import get_facade
    from marcus.lesson_plan.log import LessonPlanLog
    from marcus.orchestrator.voice_interface import (
        LiveTalkModeController,
        VoiceIntakeSession,
        build_chunk_transcriber,
    )

    args = _build_parser().parse_args(argv)
    tracker = SessionCostTracker()

    if args.list_mic_devices:
        devices = _list_dshow_audio_devices()
        if not devices:
            print("No dshow microphone devices discovered.")
        else:
            print("Discovered microphone devices:")
            for device in devices:
                print(f"- {device}")
        return 0

    if args.session_mode == "4a":
        if args.lesson_plan_json is None:
            print("--lesson-plan-json is required for --session-mode 4a", file=sys.stderr)
            return 2
        try:
            plan = _read_lesson_plan(args.lesson_plan_json)
        except Exception as exc:
            print(f"failed to load lesson plan: {exc}", file=sys.stderr)
            return 2

    log = (
        LessonPlanLog(path=args.log_path)
        if args.log_path is not None and args.session_mode == "4a"
        else None
    )
    transcriber = build_chunk_transcriber(
        args.stt_provider,
        keyterms=list(args.keyterm),
    )
    transcriber = MeteredChunkTranscriber(delegate=transcriber, tracker=tracker)
    tts_voice: ElevenLabsLiveVoice | None = None
    if args.tts_enabled:
        try:
            tts_voice = ElevenLabsLiveVoice(
                output_dir=args.runtime_audio_dir,
                voice_id=args.tts_voice_id,
                tracker=tracker,
            )
        except RuntimeError as exc:
            print(f"[voice] failed to initialize TTS playback: {exc}", file=sys.stderr)
            return 2

    if args.input_mode == "mic":
        chunk_provider = _build_live_mic_chunk_provider(
            runtime_audio_dir=args.runtime_audio_dir,
            mic_seconds=args.mic_seconds,
            mic_device=args.mic_device,
            mic_sample_rate=args.mic_sample_rate,
            mic_backend=args.mic_backend,
            tts_voice=tts_voice,
        )
        chat_typed_provider = _no_typed_input_provider
        chat_attempts = max(1, math.ceil(args.silence_timeout_seconds / max(args.mic_seconds, 0.1)))
        chat_typed_fallback_when_live = False
        chat_mic_seconds = args.mic_seconds
    else:
        chunk_provider = _interactive_chunk_provider
        chat_typed_provider = _interactive_text_provider
        chat_attempts = args.max_attempts
        chat_typed_fallback_when_live = True
        chat_mic_seconds = None

    start_live_talk = _prompt_for_live_talk_mode()
    mode_controller = LiveTalkModeController(live_enabled=start_live_talk)
    if start_live_talk:
        print("[voice] live talk mode enabled.")
        if tts_voice is not None:
            _safe_speak(tts_voice, "Live talk mode is enabled.")
    else:
        print("[voice] live talk mode disabled (text-only default).")
        if tts_voice is not None:
            _safe_speak(tts_voice, "Live talk mode is disabled. Text mode is active.")
    if args.session_mode == "chat":
        exit_code = _run_chat_session(
            transcriber=transcriber,
            chunk_provider=chunk_provider,
            typed_text_provider=chat_typed_provider,
            mode_controller=mode_controller,
            tts_voice=tts_voice,
            max_attempts=chat_attempts,
            dry_run=bool(args.dry_run),
            silence_timeout_seconds=args.silence_timeout_seconds,
            followup_2_delay_seconds=args.followup_2_delay_seconds,
            followup_response_timeout_seconds=args.followup_response_timeout_seconds,
            voice_shutdown_grace_seconds=args.voice_shutdown_grace_seconds,
            mic_seconds=chat_mic_seconds,
            typed_fallback_when_live=chat_typed_fallback_when_live,
            tracker=tracker,
        )
        for line in tracker.render_summary_lines():
            print(line)
        return exit_code

    session = VoiceIntakeSession.with_terminal_fallback(
        transcriber=transcriber,
        chunk_provider=chunk_provider,
        mode_controller=mode_controller,
        max_attempts_per_unit=args.max_attempts,
        min_confidence=args.min_confidence,
    )
    locked = get_facade().run_4a(
        plan,
        intake_callable=session.intake_callable,
        log=log,
    )
    _print_locked_plan(locked)
    if tts_voice is not None:
        _safe_speak(tts_voice, "Plan locked. Marcus has completed this cycle.")
    for line in tracker.render_summary_lines():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

