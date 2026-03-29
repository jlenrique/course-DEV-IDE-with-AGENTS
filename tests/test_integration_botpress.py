"""Live integration tests for Botpress API client.

These tests make real API calls and are skipped unless BOTPRESS_API_KEY is set.
"""

from __future__ import annotations

import pytest

from tests.conftest import requires_botpress


@pytest.mark.live_api
@pytest.mark.timeout(60)
@requires_botpress
class TestBotpressLive:
    def test_client_instantiates(self) -> None:
        from scripts.api_clients import BotpressClient

        client = BotpressClient()
        assert client.base_url.endswith("/v1")

    def test_connectivity_check(self) -> None:
        from scripts.api_clients import BotpressClient

        client = BotpressClient()
        result = client.check_connectivity()
        assert result["reachable"] is True
        assert isinstance(result["status_code"], int)
