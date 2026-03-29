"""Live integration tests for Wondercraft API client.

These tests make real API calls and are skipped unless WONDERCRAFT_API_KEY is set.
"""

from __future__ import annotations

import pytest

from tests.conftest import requires_wondercraft


@pytest.mark.live_api
@pytest.mark.timeout(60)
@requires_wondercraft
class TestWondercraftLive:
    def test_client_instantiates(self) -> None:
        from scripts.api_clients import WondercraftClient

        client = WondercraftClient()
        assert client.base_url.endswith("/v1")

    def test_connectivity_check(self) -> None:
        from scripts.api_clients import WondercraftClient

        client = WondercraftClient()
        result = client.check_connectivity()
        assert result["reachable"] is True
        assert isinstance(result["status_code"], int)
