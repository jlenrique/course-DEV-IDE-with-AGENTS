"""Audio sensory bridge — speech-to-text transcription via ElevenLabs Scribe v2.

Produces timestamped transcripts with WPM measurement and pronunciation flags.
ElevenLabs Scribe v2 provides word-level timestamps, keyterm prompting for
medical terminology, and ≤5% WER for English.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from skills.sensory_bridges.scripts.bridge_utils import build_response

logger = logging.getLogger(__name__)

STT_ENDPOINT = "https://api.elevenlabs.io/v1/speech-to-text"
DEFAULT_MODEL = "scribe_v2"


def _get_api_key() -> str:
    """Load ElevenLabs API key from environment."""
    load_dotenv()
    key = os.getenv("ELEVENLABS_API_KEY", "")
    if not key:
        raise RuntimeError("ELEVENLABS_API_KEY not set in environment")
    return key


def _call_stt(
    file_path: Path,
    api_key: str,
    model: str = DEFAULT_MODEL,
    keyterms: list[str] | None = None,
) -> dict[str, Any]:
    """Call ElevenLabs Speech-to-Text API."""
    headers = {"xi-api-key": api_key}

    data: dict[str, Any] = {"model_id": model}
    if keyterms:
        data["keyterms"] = keyterms

    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f)}
        response = requests.post(
            STT_ENDPOINT,
            headers=headers,
            data=data,
            files=files,
            timeout=300,
        )

    response.raise_for_status()
    return response.json()


def _compute_wpm(words: list[dict[str, Any]], total_duration_s: float) -> float:
    """Compute words per minute from timestamped word list."""
    word_count = sum(1 for w in words if w.get("type") == "word")
    if total_duration_s <= 0:
        return 0.0
    return round(word_count / (total_duration_s / 60), 1)


def transcribe_audio(
    artifact_path: str | Path,
    gate: str = "G5",
    keyterms: list[str] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Transcribe an audio file using ElevenLabs Scribe v2.

    Args:
        artifact_path: Path to the audio file (.mp3, .wav, etc.).
        gate: Production gate identifier.
        keyterms: Optional list of medical terms to bias recognition.

    Returns:
        Canonical perception response with transcript, timestamps, WPM.
    """
    path = Path(artifact_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    try:
        api_key = _get_api_key()
    except RuntimeError as e:
        return build_response(
            modality="audio",
            artifact_path=path,
            confidence="LOW",
            confidence_rationale=str(e),
            transcript_text="",
            timestamped_words=[],
            total_duration_ms=0,
            wpm=0.0,
            pronunciation_flags=[],
        )

    try:
        result = _call_stt(path, api_key, keyterms=keyterms)
    except requests.HTTPError as e:
        return build_response(
            modality="audio",
            artifact_path=path,
            confidence="LOW",
            confidence_rationale=f"STT API error: {e}",
            transcript_text="",
            timestamped_words=[],
            total_duration_ms=0,
            wpm=0.0,
            pronunciation_flags=[],
        )

    transcript_text = result.get("text", "")
    raw_words = result.get("words", [])

    timestamped_words = [
        {
            "text": w["text"],
            "start_ms": int(w.get("start", 0) * 1000),
            "end_ms": int(w.get("end", 0) * 1000),
            "type": w.get("type", "word"),
            "speaker_id": w.get("speaker_id", ""),
        }
        for w in raw_words
    ]

    last_end = max((w["end_ms"] for w in timestamped_words), default=0)
    total_duration_ms = last_end
    wpm = _compute_wpm(raw_words, total_duration_ms / 1000)

    if not transcript_text:
        confidence = "LOW"
        rationale = "STT returned empty transcript"
    elif wpm < 50:
        confidence = "MEDIUM"
        rationale = f"Transcript produced but WPM unusually low ({wpm}) — may indicate poor audio quality"
    else:
        confidence = "HIGH"
        rationale = f"Transcript produced: {len(transcript_text)} chars, {wpm} WPM, {len(timestamped_words)} word tokens"

    return build_response(
        modality="audio",
        artifact_path=path,
        confidence=confidence,
        confidence_rationale=rationale,
        transcript_text=transcript_text,
        timestamped_words=timestamped_words,
        total_duration_ms=total_duration_ms,
        wpm=wpm,
        pronunciation_flags=[],
        language_code=result.get("language_code", "en"),
    )
