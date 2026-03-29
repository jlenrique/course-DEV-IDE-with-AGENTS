"""Live integration tests for Canvas LMS API client.

These tests make REAL API calls. Skipped when CANVAS_ACCESS_TOKEN is not set.
Uses read-only endpoints only.
"""

from __future__ import annotations

import pytest

from tests.conftest import requires_canvas


@pytest.mark.live_api
@pytest.mark.timeout(60)
@requires_canvas
class TestCanvasLive:
    def test_client_instantiates(self):
        from scripts.api_clients import CanvasClient

        client = CanvasClient()
        assert client.base_url

    def test_get_self(self):
        from scripts.api_clients import CanvasClient

        client = CanvasClient()
        user = client.get_self()
        assert isinstance(user, dict)
        assert "id" in user
        assert "name" in user

    def test_list_courses(self):
        from scripts.api_clients import CanvasClient

        client = CanvasClient()
        courses = list(client.list_courses())
        assert isinstance(courses, list)
        # User should have at least one course
        if courses:
            assert "id" in courses[0]
            assert "name" in courses[0]

    def test_list_courses_pagination(self):
        """Verify pagination works by requesting small pages."""
        from scripts.api_clients import CanvasClient

        client = CanvasClient()
        courses = list(client.list_courses(per_page=2))
        assert isinstance(courses, list)
