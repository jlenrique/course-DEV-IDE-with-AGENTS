"""Live integration tests for Gamma API client.

These tests make REAL API calls. They are skipped when GAMMA_API_KEY is not set.
They use read-only endpoints (themes) to avoid consuming generation credits.
"""

from __future__ import annotations

from tests.conftest import requires_gamma


@requires_gamma
class TestGammaLive:
    def test_client_instantiates(self):
        from scripts.api_clients import GammaClient

        client = GammaClient()
        assert client.base_url

    def test_list_themes(self):
        from scripts.api_clients import GammaClient

        client = GammaClient()
        themes = client.list_themes(limit=3)
        assert isinstance(themes, list)
        assert len(themes) > 0

    def test_list_themes_has_ids(self):
        from scripts.api_clients import GammaClient

        client = GammaClient()
        themes = client.list_themes(limit=1)
        first = themes[0]
        assert "id" in first or "name" in first
