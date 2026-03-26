"""Live integration tests for ElevenLabs API client.

These tests make REAL API calls. Skipped when ELEVENLABS_API_KEY is not set.
Uses read-only endpoints to avoid consuming credits.
"""

from __future__ import annotations

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
