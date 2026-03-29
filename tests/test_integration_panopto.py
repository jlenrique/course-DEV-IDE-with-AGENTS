"""Live integration tests for Panopto API client.

These tests make REAL API calls. Skipped when PANOPTO_BASE_URL is not set.
Uses read-only endpoints only.
"""

from __future__ import annotations

import pytest

from tests.conftest import requires_panopto


@pytest.mark.live_api
@pytest.mark.timeout(60)
@requires_panopto
class TestPanoptoLive:
    def test_client_instantiates(self):
        from scripts.api_clients import PanoptoClient

        client = PanoptoClient()
        assert client._panopto_base

    def test_authenticate(self):
        from scripts.api_clients import PanoptoClient

        client = PanoptoClient()
        token = client.authenticate()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_list_folders(self):
        from scripts.api_clients import PanoptoClient

        client = PanoptoClient()
        folders = client.list_folders()
        assert isinstance(folders, list)
