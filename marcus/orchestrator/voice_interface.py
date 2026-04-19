"""Voice intake adapter for Marcus 4A scope-decision sessions.

This module keeps the Marcus loop contract unchanged by translating
speech transcripts into the existing ``IntakeCallable`` shape used by
``Facade.run_4a``.
"""

from __future__ import annotations

import importlib
import os
import sys
import types
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from re import IGNORECASE, search
from typing import TYPE_CHECKING, Literal, Protocol

import requests
from dotenv import load_dotenv

from marcus.lesson_plan.schema import ScopeDecision
from scripts.utilities.skill_module_loader import load_module_from_path

if TYPE_CHECKING:
    from marcus.orchestrator.loop import FourAState

ConfidenceLevel = Literal["LOW", "MEDIUM", "HIGH"]
ChunkProvider = Callable[[str, int], str | Path | None]
TypedFallbackProvider = Callable[[str], tuple[ScopeDecision, str] | None]
ConfirmationProvider = Callable[[str, ScopeDecision, str, str], bool]
LiveTalkCommand = Literal["enable_live_talk", "disable_live_talk"]
TypedTextProvider = Callable[[], str | None]


@dataclass(frozen=True)
class TranscriptResult:
    """Normalized transcript result for one captured audio chunk."""

    transcript_text: str
    confidence: ConfidenceLevel
    confidence_rationale: str


@dataclass(frozen=True)
class ParsedVoiceDecision:
    """Parsed decision payload extracted from transcript text."""

    decision: ScopeDecision
    rationale: str


@dataclass(frozen=True)
class LiveTurnResult:
    """Represents one conversation turn result in live chat mode."""

    kind: Literal["utterance", "command", "silence"]
    utterance: str | None = None


class LiveTalkModeController:
    """Tracks and toggles live-talk mode using command phrases."""

    _ENABLE_PATTERNS: tuple[str, ...] = (
        r"\blet'?s\s+talk\s+live\b",
        r"\btalk\s+live\b",
        r"\benable\s+(?:live\s+talk|stt)\b",
        r"\bstt\s+on\b",
    )
    _DISABLE_PATTERNS: tuple[str, ...] = (
        r"\bshut\s+down\s+live\s+talk\b",
        r"\bdisable\s+(?:live\s+talk|stt)\b",
        r"\bstt\s+off\b",
        r"\btext(?:-only|\s+only)\b",
    )

    def __init__(self, *, live_enabled: bool = True) -> None:
        self._live_enabled = live_enabled

    @property
    def live_enabled(self) -> bool:
        return self._live_enabled

    def process_command(self, text: str) -> LiveTalkCommand | None:
        """Switch mode when text matches command phrases."""
        normalized = text.strip()
        if not normalized:
            return None
        if any(search(pattern, normalized, IGNORECASE) for pattern in self._ENABLE_PATTERNS):
            self._live_enabled = True
            return "enable_live_talk"
        if any(search(pattern, normalized, IGNORECASE) for pattern in self._DISABLE_PATTERNS):
            self._live_enabled = False
            return "disable_live_talk"
        return None


class ChunkTranscriber(Protocol):
    """Speech-to-text adapter protocol for chunked audio."""

    def transcribe_chunk(self, chunk_path: Path) -> TranscriptResult:
        """Return transcript details for one audio chunk."""


class VoiceDecisionParser:
    """Parse transcript text into one ratified ``ScopeDecision`` + rationale."""

    _PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("out-of-scope", (r"\bout[\s-]?of[\s-]?scope\b", r"\bexclude\b")),
        ("in-scope", (r"\bin[\s-]?scope\b", r"\binclude\b")),
        ("delegated", (r"\bdelegat(?:e|ed|ing)\b", r"\bhand(?:\s+it)?\s+off\b")),
        ("blueprint", (r"\bblueprint\b",)),
    )

    def parse(self, transcript_text: str) -> ParsedVoiceDecision:
        """Parse a transcript string into a ratified decision and rationale."""
        normalized = transcript_text.strip()
        if not normalized:
            raise ValueError("voice transcript is empty")

        matches: list[str] = []
        for scope, patterns in self._PATTERNS:
            if any(search(pattern, normalized, IGNORECASE) for pattern in patterns):
                matches.append(scope)

        if len(matches) != 1:
            raise ValueError(
                "voice transcript must contain exactly one scope decision phrase"
            )

        rationale = self._extract_rationale(normalized)
        decision = ScopeDecision(
            state="ratified",
            scope=matches[0],  # type: ignore[arg-type]
            proposed_by="operator",
            ratified_by="maya",
        )
        return ParsedVoiceDecision(decision=decision, rationale=rationale)

    @staticmethod
    def _extract_rationale(transcript_text: str) -> str:
        because_match = search(r"\bbecause\b(?P<tail>.+)$", transcript_text, IGNORECASE)
        if because_match:
            extracted = because_match.group("tail").strip()
            if extracted:
                return extracted
        return transcript_text


class ElevenLabsChunkTranscriber:
    """Chunk transcriber backed by sensory-bridges ElevenLabs STT utility."""

    def __init__(
        self,
        *,
        repo_root: Path | None = None,
        keyterms: list[str] | None = None,
        transcribe_fn: Callable[..., dict] | None = None,
    ) -> None:
        self._repo_root = repo_root or Path(__file__).resolve().parents[2]
        self._keyterms = tuple(keyterms or ())
        self._transcribe_fn = transcribe_fn or self._resolve_transcribe_fn()

    def transcribe_chunk(self, chunk_path: Path) -> TranscriptResult:
        """Transcribe one chunk path via ElevenLabs STT helper."""
        payload = self._transcribe_fn(str(chunk_path), keyterms=list(self._keyterms))
        transcript = str(payload.get("transcript_text", "")).strip()
        confidence = str(payload.get("confidence", "LOW")).upper()
        if confidence not in {"LOW", "MEDIUM", "HIGH"}:
            confidence = "LOW"
        rationale = str(payload.get("confidence_rationale", ""))
        return TranscriptResult(
            transcript_text=transcript,
            confidence=confidence,  # type: ignore[arg-type]
            confidence_rationale=rationale,
        )

    def _resolve_transcribe_fn(self) -> Callable[..., dict]:
        try:
            module = importlib.import_module("skills.sensory_bridges.scripts.audio_to_agent")
            return module.transcribe_audio  # type: ignore[attr-defined]
        except ModuleNotFoundError as err:
            scripts_dir = self._repo_root / "skills" / "sensory-bridges" / "scripts"
            if not scripts_dir.exists():
                raise RuntimeError(
                    "Cannot locate sensory-bridges scripts directory for audio transcription."
                ) from err

            self._ensure_module_stub("skills")
            self._ensure_module_stub("skills.sensory_bridges")
            self._ensure_module_stub("skills.sensory_bridges.scripts")

            bridge_utils = load_module_from_path(
                "skills.sensory_bridges.scripts.bridge_utils",
                scripts_dir / "bridge_utils.py",
            )
            sys.modules.setdefault("skills.sensory_bridges.scripts.bridge_utils", bridge_utils)
            module = load_module_from_path(
                "skills.sensory_bridges.scripts.audio_to_agent",
                scripts_dir / "audio_to_agent.py",
            )
            return module.transcribe_audio  # type: ignore[attr-defined]

    @staticmethod
    def _ensure_module_stub(name: str) -> None:
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)


class OpenAIWhisperChunkTranscriber:
    """Chunk transcriber backed by OpenAI audio transcription."""

    def __init__(
        self,
        *,
        model_id: str = "whisper-1",
        api_key: str | None = None,
        endpoint: str = "https://api.openai.com/v1/audio/transcriptions",
        transcribe_fn: Callable[[Path], dict] | None = None,
    ) -> None:
        self._model_id = model_id
        self._endpoint = endpoint
        self._api_key = api_key
        self._transcribe_fn = transcribe_fn

    def transcribe_chunk(self, chunk_path: Path) -> TranscriptResult:
        """Transcribe one chunk path via OpenAI Whisper."""
        if self._transcribe_fn is not None:
            payload = self._transcribe_fn(chunk_path)
            transcript_text = str(payload.get("text", "")).strip()
            confidence = "HIGH" if transcript_text else "LOW"
            rationale = str(payload.get("confidence_rationale", "OpenAI transcription response"))
            return TranscriptResult(
                transcript_text=transcript_text,
                confidence=confidence,
                confidence_rationale=rationale,
            )

        if not chunk_path.exists():
            raise FileNotFoundError(f"Audio file not found: {chunk_path}")

        load_dotenv()
        api_key = self._api_key or os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return TranscriptResult(
                transcript_text="",
                confidence="LOW",
                confidence_rationale="OPENAI_API_KEY not set in environment",
            )

        headers = {"Authorization": f"Bearer {api_key}"}
        data = {"model": self._model_id}
        with open(chunk_path, "rb") as handle:
            files = {"file": (chunk_path.name, handle)}
            response = requests.post(
                self._endpoint,
                headers=headers,
                data=data,
                files=files,
                timeout=300,
            )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            return TranscriptResult(
                transcript_text="",
                confidence="LOW",
                confidence_rationale=f"OpenAI STT API error: {exc}",
            )

        payload = response.json()
        transcript_text = str(payload.get("text", "")).strip()
        if not transcript_text:
            return TranscriptResult(
                transcript_text="",
                confidence="LOW",
                confidence_rationale="OpenAI STT returned empty transcript",
            )
        return TranscriptResult(
            transcript_text=transcript_text,
            confidence="HIGH",
            confidence_rationale=f"OpenAI STT transcript produced ({len(transcript_text)} chars)",
        )


class FallbackChunkTranscriber:
    """Use a secondary STT transcriber when the primary yields no transcript."""

    def __init__(
        self,
        *,
        primary: ChunkTranscriber,
        secondary: ChunkTranscriber,
    ) -> None:
        self._primary = primary
        self._secondary = secondary

    def transcribe_chunk(self, chunk_path: Path) -> TranscriptResult:
        """Transcribe with primary provider; fallback when transcript is empty."""
        primary_result = self._primary.transcribe_chunk(chunk_path)
        if primary_result.transcript_text.strip():
            return primary_result

        secondary_result = self._secondary.transcribe_chunk(chunk_path)
        if secondary_result.transcript_text.strip():
            return secondary_result

        return TranscriptResult(
            transcript_text="",
            confidence="LOW",
            confidence_rationale=(
                "Primary STT yielded no transcript "
                f"({primary_result.confidence_rationale}); "
                "fallback STT yielded no transcript "
                f"({secondary_result.confidence_rationale})"
            ),
        )


def build_chunk_transcriber(
    provider: Literal["elevenlabs", "openai", "auto"] = "auto",
    *,
    keyterms: list[str] | None = None,
) -> ChunkTranscriber:
    """Build an STT transcriber provider with optional automatic fallback."""
    if provider == "elevenlabs":
        return ElevenLabsChunkTranscriber(keyterms=keyterms)
    if provider == "openai":
        return OpenAIWhisperChunkTranscriber()
    return FallbackChunkTranscriber(
        primary=ElevenLabsChunkTranscriber(keyterms=keyterms),
        secondary=OpenAIWhisperChunkTranscriber(),
    )


class VoiceIntakeSession:
    """Stateful adapter that turns chunked STT into ``IntakeCallable`` output."""

    _CONFIDENCE_ORDER: tuple[ConfidenceLevel, ...] = ("LOW", "MEDIUM", "HIGH")

    def __init__(
        self,
        *,
        transcriber: ChunkTranscriber,
        chunk_provider: ChunkProvider,
        parser: VoiceDecisionParser | None = None,
        typed_fallback_provider: TypedFallbackProvider | None = None,
        confirmation_provider: ConfirmationProvider | None = None,
        mode_controller: LiveTalkModeController | None = None,
        max_attempts_per_unit: int = 3,
        min_confidence: ConfidenceLevel = "MEDIUM",
    ) -> None:
        if max_attempts_per_unit < 1:
            raise ValueError("max_attempts_per_unit must be >= 1")
        self._transcriber = transcriber
        self._chunk_provider = chunk_provider
        self._parser = parser or VoiceDecisionParser()
        self._typed_fallback_provider = typed_fallback_provider
        self._confirmation_provider = confirmation_provider
        self._mode_controller = mode_controller or LiveTalkModeController(live_enabled=True)
        self._max_attempts = max_attempts_per_unit
        self._min_confidence = min_confidence

    def intake_callable(
        self,
        _state: FourAState,
        unit_id: str,
    ) -> tuple[ScopeDecision, str]:
        """Provide one unit decision by retrying chunk transcription then fallback."""
        fallback_cycles = 0
        while True:
            if self._mode_controller.live_enabled:
                for attempt in range(1, self._max_attempts + 1):
                    chunk = self._chunk_provider(unit_id, attempt)
                    if chunk is None:
                        break

                    transcript = self._transcriber.transcribe_chunk(Path(chunk))
                    command = self._mode_controller.process_command(transcript.transcript_text)
                    if command == "disable_live_talk":
                        break
                    if command == "enable_live_talk":
                        continue

                    if not self._meets_confidence_threshold(transcript.confidence):
                        continue

                    try:
                        parsed = self._parser.parse(transcript.transcript_text)
                    except ValueError:
                        continue

                    if self._confirmation_provider is not None:
                        accepted = self._confirmation_provider(
                            unit_id,
                            parsed.decision,
                            transcript.transcript_text,
                            parsed.rationale,
                        )
                        if not accepted:
                            continue

                    return parsed.decision, parsed.rationale

            if self._typed_fallback_provider is None:
                break
            fallback = self._typed_fallback_provider(unit_id)
            if fallback is not None:
                return fallback

            fallback_cycles += 1
            if fallback_cycles >= self._max_attempts:
                break

        raise RuntimeError(
            f"voice intake could not produce a valid decision for unit_id={unit_id!r}"
        )

    @classmethod
    def with_terminal_fallback(
        cls,
        *,
        transcriber: ChunkTranscriber,
        chunk_provider: ChunkProvider,
        parser: VoiceDecisionParser | None = None,
        mode_controller: LiveTalkModeController | None = None,
        max_attempts_per_unit: int = 3,
        min_confidence: ConfidenceLevel = "MEDIUM",
    ) -> VoiceIntakeSession:
        """Build a session that falls back to terminal typed input."""
        resolved_mode_controller = mode_controller or LiveTalkModeController(live_enabled=True)
        return cls(
            transcriber=transcriber,
            chunk_provider=chunk_provider,
            parser=parser,
            typed_fallback_provider=_build_terminal_typed_fallback(resolved_mode_controller),
            confirmation_provider=_terminal_confirmation,
            mode_controller=resolved_mode_controller,
            max_attempts_per_unit=max_attempts_per_unit,
            min_confidence=min_confidence,
        )

    def _meets_confidence_threshold(self, observed: ConfidenceLevel) -> bool:
        return self._CONFIDENCE_ORDER.index(observed) >= self._CONFIDENCE_ORDER.index(
            self._min_confidence
        )


class LiveConversationSession:
    """Persistent live conversation adapter with no scope-decision filtering."""

    def __init__(
        self,
        *,
        transcriber: ChunkTranscriber,
        chunk_provider: ChunkProvider,
        typed_text_provider: TypedTextProvider,
        mode_controller: LiveTalkModeController | None = None,
        max_attempts_per_turn: int = 3,
        typed_fallback_when_live: bool = True,
    ) -> None:
        if max_attempts_per_turn < 1:
            raise ValueError("max_attempts_per_turn must be >= 1")
        self._transcriber = transcriber
        self._chunk_provider = chunk_provider
        self._typed_text_provider = typed_text_provider
        self._mode_controller = mode_controller or LiveTalkModeController(live_enabled=True)
        self._max_attempts = max_attempts_per_turn
        self._typed_fallback_when_live = typed_fallback_when_live

    def next_user_utterance(self, turn_id: str) -> str | None:
        """Backward-compatible wrapper returning only utterance text."""
        result = self.next_turn(turn_id)
        return result.utterance

    def next_turn(
        self,
        turn_id: str,
        *,
        max_attempts_override: int | None = None,
    ) -> LiveTurnResult:
        """Return structured next-turn result (utterance/command/silence)."""
        saw_command = False
        max_attempts = max_attempts_override or self._max_attempts
        if max_attempts < 1:
            max_attempts = 1
        if self._mode_controller.live_enabled:
            for attempt in range(1, max_attempts + 1):
                chunk = self._chunk_provider(turn_id, attempt)
                if chunk is None:
                    break
                transcript = self._transcriber.transcribe_chunk(Path(chunk))
                if not transcript.transcript_text.strip():
                    continue

                command = self._mode_controller.process_command(transcript.transcript_text)
                if command is not None:
                    saw_command = True
                    continue
                return LiveTurnResult(kind="utterance", utterance=transcript.transcript_text)
            if not self._typed_fallback_when_live:
                if saw_command:
                    return LiveTurnResult(kind="command")
                return LiveTurnResult(kind="silence")

        typed_text = self._typed_text_provider()
        if typed_text is None:
            if saw_command:
                return LiveTurnResult(kind="command")
            return LiveTurnResult(kind="silence")
        stripped = typed_text.strip()
        if not stripped:
            if saw_command:
                return LiveTurnResult(kind="command")
            return LiveTurnResult(kind="silence")
        command = self._mode_controller.process_command(stripped)
        if command is not None:
            return LiveTurnResult(kind="command")
        return LiveTurnResult(kind="utterance", utterance=stripped)


def _build_terminal_typed_fallback(
    mode_controller: LiveTalkModeController,
) -> TypedFallbackProvider:
    def _typed_fallback(unit_id: str) -> tuple[ScopeDecision, str] | None:
        print(f"[voice] fallback to typed input for unit={unit_id}")
        while True:
            scope_or_command = input(
                "Type scope decision (in-scope/out-of-scope/delegated/blueprint) "
                "or command ('let's talk live' / 'shut down live talk'): "
            ).strip()
            command = mode_controller.process_command(scope_or_command)
            if command == "enable_live_talk":
                print("[voice] live talk enabled.")
                return None
            if command == "disable_live_talk":
                print("[voice] live talk disabled. Staying text-only.")
                return None

            rationale = input("Type rationale: ")
            parser = VoiceDecisionParser()
            try:
                parsed = parser.parse(f"{scope_or_command} because {rationale}")
            except ValueError:
                print("[voice] invalid decision text. Try again.")
                continue
            return parsed.decision, rationale

    return _typed_fallback


def _terminal_confirmation(
    unit_id: str,
    decision: ScopeDecision,
    transcript_text: str,
    rationale: str,
) -> bool:
    print(
        f"[voice] unit={unit_id} transcript={transcript_text!r} "
        f"decision={decision.scope!r} rationale={rationale!r}"
    )
    response = input("[voice] accept this transcript? [y/N]: ").strip().lower()
    return response in {"y", "yes"}


def _terminal_typed_fallback(unit_id: str) -> tuple[ScopeDecision, str] | None:
    print(f"[voice] fallback to typed input for unit={unit_id}")
    scope_input = input("Type scope decision (in-scope/out-of-scope/delegated/blueprint): ")
    rationale = input("Type rationale: ")
    parser = VoiceDecisionParser()
    try:
        parsed = parser.parse(f"{scope_input} because {rationale}")
    except ValueError:
        return None
    return parsed.decision, rationale

