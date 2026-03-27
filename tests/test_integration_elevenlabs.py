"""Live integration tests for ElevenLabs API client.

These tests make REAL API calls. Skipped when ELEVENLABS_API_KEY is not set.
Uses read-only endpoints to avoid consuming credits.
"""

from __future__ import annotations

import os

from tests.conftest import requires_elevenlabs


@requires_elevenlabs
class TestElevenLabsLive:
    def test_client_instantiates(self):
        from scripts.api_clients import ElevenLabsClient

        client = ElevenLabsClient()
        assert client.base_url

    def test_list_voices(self):
        from scripts.api_clients import ElevenLabsClient

        client = ElevenLabsClient()
        voices = client.list_voices()
        assert isinstance(voices, list)
        assert len(voices) > 0

    def test_voices_have_ids_and_names(self):
        from scripts.api_clients import ElevenLabsClient

        client = ElevenLabsClient()
        voices = client.list_voices()
        first = voices[0]
        assert "voice_id" in first
        assert "name" in first

    def test_list_models(self):
        from scripts.api_clients import ElevenLabsClient

        client = ElevenLabsClient()
        models = client.list_models()
        assert isinstance(models, list)
        assert len(models) > 0

    def test_voice_details(self):
        """Fetch details for a specific voice to verify single-resource access."""
        from scripts.api_clients import ElevenLabsClient

        client = ElevenLabsClient()
        voices = client.list_voices()
        assert len(voices) > 0
        detail = client.get_voice(voices[0]["voice_id"])
        assert "voice_id" in detail
        assert "name" in detail

    def test_list_pronunciation_dictionaries(self):
        """Pronunciation dictionary listing should return structured metadata."""
        from scripts.api_clients import ElevenLabsClient

        client = ElevenLabsClient()
        payload = client.list_pronunciation_dictionaries(page_size=10)
        assert "pronunciation_dictionaries" in payload
        assert "has_more" in payload

    def test_timestamps_smoke_when_enabled(self):
        """Optional credit-consuming smoke test for narration + timestamps."""
        if os.environ.get("ELEVENLABS_ENABLE_GENERATION_TESTS") != "1":
            return

        from scripts.api_clients import ElevenLabsClient

        client = ElevenLabsClient()
        voices = client.list_voices()
        assert voices, "Expected at least one available voice"
        result = client.text_to_speech_with_timestamps(
            "Testing timestamped narration for medical education.",
            voices[0]["voice_id"],
        )
        assert result["audio_bytes"]
        assert "alignment" in result or "normalized_alignment" in result
