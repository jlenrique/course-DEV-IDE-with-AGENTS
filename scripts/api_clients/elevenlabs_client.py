"""ElevenLabs API client for voice synthesis and audio generation.

API Docs: https://elevenlabs.io/docs/api-reference
Auth: xi-api-key header
Models: Eleven v3, Multilingual v2, Flash v2.5, Turbo v2.5
Output: MP3, WAV, PCM, Opus
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from scripts.api_clients.base_client import BaseAPIClient

logger = logging.getLogger(__name__)

ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"


class ElevenLabsClient(BaseAPIClient):
    """Client for ElevenLabs voice synthesis API.

    Args:
        api_key: ElevenLabs API key. Defaults to ``ELEVENLABS_API_KEY`` env var.
    """

    def __init__(self, api_key: str | None = None) -> None:
        api_key = api_key or os.environ.get("ELEVENLABS_API_KEY", "")
        super().__init__(
            base_url=ELEVENLABS_BASE_URL,
            auth_header="xi-api-key",
            auth_prefix="",
            api_key=api_key,
        )

    def list_voices(self) -> list[dict[str, Any]]:
        """List all available voices."""
        data = self.get("/voices")
        return data.get("voices", [])

    def get_voice(self, voice_id: str) -> dict[str, Any]:
        """Get details for a specific voice."""
        return self.get(f"/voices/{voice_id}")

    def list_models(self) -> list[dict[str, Any]]:
        """List available TTS models."""
        data = self.get("/models")
        return data if isinstance(data, list) else []

    def get_user(self) -> dict[str, Any]:
        """Get current user info including subscription details."""
        return self.get("/user")

    def text_to_speech(
        self,
        text: str,
        voice_id: str,
        *,
        model_id: str = "eleven_multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        output_format: str = "mp3_44100_128",
    ) -> bytes:
        """Generate speech audio from text.

        Args:
            text: Text to convert to speech.
            voice_id: Voice ID from ``list_voices()``.
            model_id: TTS model to use.
            stability: Voice stability (0.0-1.0).
            similarity_boost: Voice clarity/similarity (0.0-1.0).
            style: Style exaggeration (0.0-1.0).
            output_format: Audio format string.

        Returns:
            Raw audio bytes in the requested format.
        """
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
            },
        }
        response = self.post_raw(
            f"/text-to-speech/{voice_id}",
            json=payload,
            params={"output_format": output_format},
        )
        return response.content

    def text_to_speech_file(
        self,
        text: str,
        voice_id: str,
        output_path: str | Path,
        **kwargs: Any,
    ) -> Path:
        """Generate speech and save to a file.

        Args:
            text: Text to convert.
            voice_id: Voice ID.
            output_path: File path to write audio.
            **kwargs: Additional args passed to ``text_to_speech()``.

        Returns:
            Path to the written audio file.
        """
        audio = self.text_to_speech(text, voice_id, **kwargs)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(audio)
        logger.info(
            "Audio saved: %s (%d bytes)", output_path, len(audio)
        )
        return output_path
