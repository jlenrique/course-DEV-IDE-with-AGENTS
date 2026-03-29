"""Wondercraft API client for podcast and audio episode generation.

API: https://api.wondercraft.ai/v1
Auth: X-API-KEY
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

from scripts.api_clients.base_client import APIError, BaseAPIClient

logger = logging.getLogger(__name__)

POLL_INTERVAL = 5
MAX_POLL_ATTEMPTS = 120


class WondercraftClient(BaseAPIClient):
    """Client for Wondercraft REST API.

    Args:
        api_key: Wondercraft API key. Defaults to ``WONDERCRAFT_API_KEY``.
        base_url: API base URL. Defaults to
            ``WONDERCRAFT_BASE_URL`` or ``https://api.wondercraft.ai/v1``.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        api_key = api_key or os.environ.get("WONDERCRAFT_API_KEY", "")
        normalized_base = (base_url or os.environ.get(
            "WONDERCRAFT_BASE_URL",
            "https://api.wondercraft.ai/v1",
        )).rstrip("/")

        super().__init__(
            base_url=normalized_base,
            auth_header="X-API-KEY",
            auth_prefix="",
            api_key=api_key,
        )

    def check_connectivity(self) -> dict[str, Any]:
        """Check basic Wondercraft API reachability without mutating data."""
        try:
            response = self._request_raw("GET", "/podcast", params={"page": 1, "pageSize": 1})
            status_code = response.status_code
            url = response.url
        except APIError as exc:
            status_code = exc.status_code or 0
            url = f"{self.base_url}/podcast"

        return {
            "reachable": bool(status_code) and status_code < 500,
            "status_code": status_code,
            "url": url,
        }

    def list_episodes(self, page: int = 1, page_size: int = 20) -> list[dict[str, Any]]:
        """List generated podcast episodes."""
        data = self.get("/podcast", params={"page": page, "pageSize": page_size})
        if isinstance(data, dict):
            if "items" in data and isinstance(data["items"], list):
                return data["items"]
            if "episodes" in data and isinstance(data["episodes"], list):
                return data["episodes"]
        return data if isinstance(data, list) else []

    def create_podcast(
        self,
        title: str,
        prompt: str,
        *,
        voice_id: str | None = None,
    ) -> dict[str, Any]:
        """Create an AI-scripted podcast from a prompt."""
        payload: dict[str, Any] = {
            "title": title,
            "prompt": prompt,
        }
        if voice_id:
            payload["voiceId"] = voice_id
        return self.post("/podcast", json=payload)

    def create_scripted_podcast(
        self,
        title: str,
        script: str,
        *,
        voice_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a podcast episode from a user-provided script."""
        payload: dict[str, Any] = {
            "title": title,
            "script": script,
        }
        if voice_id:
            payload["voiceId"] = voice_id
        return self.post("/podcast/scripted", json=payload)

    def create_conversation_podcast(
        self,
        title: str,
        script: str,
    ) -> dict[str, Any]:
        """Create a conversation-mode podcast from structured script text."""
        return self.post(
            "/podcast/convo-mode/user-scripted",
            json={"title": title, "script": script},
        )

    def get_job_status(self, job_id: str) -> dict[str, Any]:
        """Fetch async generation job status."""
        return self.get(f"/jobs/{job_id}")

    def wait_for_job(
        self,
        job_id: str,
        poll_interval: int = POLL_INTERVAL,
        max_attempts: int = MAX_POLL_ATTEMPTS,
    ) -> dict[str, Any]:
        """Poll Wondercraft async job until completion or failure."""
        for attempt in range(max_attempts):
            data = self.get_job_status(job_id)
            status = (
                data.get("status")
                or data.get("state")
                or data.get("job_status")
                or ""
            )
            status_normalized = str(status).lower()

            if status_normalized in ("completed", "complete", "done", "success", "succeed"):
                logger.info("Job %s completed after %d polls", job_id, attempt + 1)
                return data
            if status_normalized in ("failed", "error"):
                error_msg = data.get("error") or data.get("message") or "unknown error"
                raise RuntimeError(f"Wondercraft job {job_id} failed: {error_msg}")

            time.sleep(poll_interval)

        raise TimeoutError(
            f"Wondercraft job {job_id} did not complete within {max_attempts * poll_interval}s"
        )
