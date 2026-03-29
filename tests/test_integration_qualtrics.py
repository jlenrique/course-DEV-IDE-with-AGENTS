"""Live integration tests for Qualtrics API client.

These tests make REAL API calls. Skipped when QUALTRICS_API_TOKEN is not set.
Uses read-only endpoints only.
"""

from __future__ import annotations

import pytest

from tests.conftest import requires_qualtrics


@pytest.mark.live_api
@pytest.mark.timeout(60)
@requires_qualtrics
class TestQualtricsLive:
    def test_client_instantiates(self):
        from scripts.api_clients import QualtricsClient

        client = QualtricsClient()
        assert client.base_url

    def test_whoami(self):
        from scripts.api_clients import QualtricsClient

        client = QualtricsClient()
        user = client.whoami()
        assert isinstance(user, dict)
        assert "userName" in user or "userId" in user

    def test_list_surveys(self):
        from scripts.api_clients import QualtricsClient

        client = QualtricsClient()
        surveys = client.list_surveys(page_size=5)
        assert isinstance(surveys, list)
        if surveys:
            first = surveys[0]
            assert "id" in first or "SurveyID" in first or "name" in first
