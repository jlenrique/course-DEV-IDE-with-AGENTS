"""Gamma API client for AI slide generation.

API Docs: https://developers.gamma.app
Auth: X-API-KEY header
Rate Limit: 50 generations/hour (beta)
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

from scripts.api_clients.base_client import BaseAPIClient

logger = logging.getLogger(__name__)

GAMMA_BASE_URL = "https://public-api.gamma.app/v1.0"
POLL_INTERVAL = 3
MAX_POLL_ATTEMPTS = 120


class GammaClient(BaseAPIClient):
    """Client for Gamma slide generation API.

    Args:
        api_key: Gamma API key. Defaults to ``GAMMA_API_KEY`` env var.
    """

    def __init__(self, api_key: str | None = None) -> None:
        api_key = api_key or os.environ.get("GAMMA_API_KEY", "")
        super().__init__(
            base_url=GAMMA_BASE_URL,
            auth_header="X-API-KEY",
            auth_prefix="",
            api_key=api_key,
            default_headers={"Content-Type": "application/json"},
        )

    def list_themes(self, limit: int = 20) -> list[dict[str, Any]]:
        """List available presentation themes."""
        data = self.get("/themes", params={"limit": limit})
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data.get("themes", [data])

    def generate(
        self,
        topic: str,
        *,
        num_cards: int | None = None,
        output_format: str = "cards",
        llm: str | None = None,
        language: str | None = None,
        theme_id: str | None = None,
    ) -> dict[str, Any]:
        """Start an AI content generation.

        Args:
            topic: Topic or detailed prompt for the generation.
            num_cards: Number of slides/cards to generate.
            output_format: "cards" (slides) or "document".
            llm: LLM model to use (e.g. "claude-3", "gpt-4o").
            language: Output language code.
            theme_id: Theme ID from ``list_themes()``.

        Returns:
            Generation response with ``id`` for polling status.
        """
        payload: dict[str, Any] = {
            "topic": topic,
            "outputFormat": output_format,
        }
        if num_cards is not None:
            payload["numCards"] = num_cards
        if llm:
            payload["llm"] = llm
        if language:
            payload["language"] = language
        if theme_id:
            payload["themeId"] = theme_id

        return self.post("/generations", json=payload)

    def get_generation(self, generation_id: str) -> dict[str, Any]:
        """Get the current status of a generation."""
        return self.get(f"/generations/{generation_id}")

    def wait_for_generation(
        self,
        generation_id: str,
        poll_interval: int = POLL_INTERVAL,
        max_attempts: int = MAX_POLL_ATTEMPTS,
    ) -> dict[str, Any]:
        """Poll until a generation completes or fails.

        Returns:
            Final generation data including output URLs.

        Raises:
            TimeoutError: If generation doesn't complete within max_attempts.
        """
        for attempt in range(max_attempts):
            data = self.get_generation(generation_id)
            status = data.get("status", "")

            if status in ("completed", "complete", "done"):
                logger.info(
                    "Generation %s completed after %d polls",
                    generation_id, attempt + 1,
                )
                return data
            if status in ("failed", "error"):
                raise RuntimeError(
                    f"Generation {generation_id} failed: "
                    f"{data.get('error', 'unknown')}"
                )

            logger.debug(
                "Generation %s status: %s (poll %d/%d)",
                generation_id, status, attempt + 1, max_attempts,
            )
            time.sleep(poll_interval)

        raise TimeoutError(
            f"Generation {generation_id} did not complete "
            f"within {max_attempts * poll_interval}s"
        )
