"""Canvas LMS API client for course content management.

API Docs: https://canvas.instructure.com/doc/api/
Auth: Authorization: Bearer {token}
Pagination: Link header with rel="next"
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from typing import Any

from scripts.api_clients.base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class CanvasClient(BaseAPIClient):
    """Client for Canvas LMS REST API.

    Args:
        api_url: Canvas instance URL (e.g. ``https://school.instructure.com``).
            Defaults to ``CANVAS_API_URL`` env var.
        access_token: Canvas API access token.
            Defaults to ``CANVAS_ACCESS_TOKEN`` env var.
    """

    def __init__(
        self,
        api_url: str | None = None,
        access_token: str | None = None,
    ) -> None:
        api_url = api_url or os.environ.get("CANVAS_API_URL", "")
        base_url = f"{api_url.rstrip('/')}/api/v1"
        access_token = access_token or os.environ.get(
            "CANVAS_ACCESS_TOKEN", ""
        )
        super().__init__(
            base_url=base_url,
            auth_header="Authorization",
            auth_prefix="Bearer",
            api_key=access_token,
        )

    # -- User --

    def get_self(self) -> dict[str, Any]:
        """Get the current authenticated user."""
        return self.get("/users/self")

    # -- Courses --

    def list_courses(self, **params: Any) -> Iterator[dict[str, Any]]:
        """List courses for the current user (paginated)."""
        params.setdefault("per_page", 50)
        yield from self.get_paginated("/courses", params=params)

    def get_course(self, course_id: int | str) -> dict[str, Any]:
        """Get a single course by ID."""
        return self.get(f"/courses/{course_id}")

    # -- Modules --

    def list_modules(
        self, course_id: int | str, **params: Any
    ) -> Iterator[dict[str, Any]]:
        """List modules in a course (paginated)."""
        params.setdefault("per_page", 50)
        yield from self.get_paginated(
            f"/courses/{course_id}/modules", params=params
        )

    def create_module(
        self,
        course_id: int | str,
        name: str,
        *,
        position: int | None = None,
        unlock_at: str | None = None,
        require_sequential_progress: bool = False,
    ) -> dict[str, Any]:
        """Create a new module in a course."""
        payload: dict[str, Any] = {
            "module[name]": name,
            "module[require_sequential_progress]": require_sequential_progress,
        }
        if position is not None:
            payload["module[position]"] = position
        if unlock_at:
            payload["module[unlock_at]"] = unlock_at
        return self.post(
            f"/courses/{course_id}/modules", data=payload
        )

    # -- Pages --

    def list_pages(
        self, course_id: int | str, **params: Any
    ) -> Iterator[dict[str, Any]]:
        """List pages in a course (paginated)."""
        params.setdefault("per_page", 50)
        yield from self.get_paginated(
            f"/courses/{course_id}/pages", params=params
        )

    def create_page(
        self,
        course_id: int | str,
        title: str,
        body: str,
        *,
        published: bool = False,
        editing_roles: str = "teachers",
    ) -> dict[str, Any]:
        """Create a new page in a course."""
        payload = {
            "wiki_page[title]": title,
            "wiki_page[body]": body,
            "wiki_page[published]": published,
            "wiki_page[editing_roles]": editing_roles,
        }
        return self.post(
            f"/courses/{course_id}/pages", data=payload
        )

    def get_page(
        self, course_id: int | str, url_or_id: str
    ) -> dict[str, Any]:
        """Get a page by URL slug or ID."""
        return self.get(f"/courses/{course_id}/pages/{url_or_id}")

    # -- Assignments --

    def list_assignments(
        self, course_id: int | str, **params: Any
    ) -> Iterator[dict[str, Any]]:
        """List assignments in a course (paginated)."""
        params.setdefault("per_page", 50)
        yield from self.get_paginated(
            f"/courses/{course_id}/assignments", params=params
        )

    def create_assignment(
        self,
        course_id: int | str,
        name: str,
        *,
        submission_types: list[str] | None = None,
        points_possible: float | None = None,
        description: str = "",
        published: bool = False,
    ) -> dict[str, Any]:
        """Create an assignment in a course."""
        payload: dict[str, Any] = {
            "assignment[name]": name,
            "assignment[description]": description,
            "assignment[published]": published,
        }
        if submission_types:
            payload["assignment[submission_types][]"] = submission_types
        if points_possible is not None:
            payload["assignment[points_possible]"] = points_possible
        return self.post(
            f"/courses/{course_id}/assignments", data=payload
        )

    # -- Quizzes (New Quizzes via Assignments) --

    def list_quizzes(
        self, course_id: int | str, **params: Any
    ) -> Iterator[dict[str, Any]]:
        """List quizzes in a course (paginated)."""
        params.setdefault("per_page", 50)
        yield from self.get_paginated(
            f"/courses/{course_id}/quizzes", params=params
        )

    # -- Enrollments --

    def list_enrollments(
        self, course_id: int | str, **params: Any
    ) -> Iterator[dict[str, Any]]:
        """List enrollments in a course (paginated)."""
        params.setdefault("per_page", 50)
        yield from self.get_paginated(
            f"/courses/{course_id}/enrollments", params=params
        )
