"""Botpress API client for chatbot management and conversation operations.

API: https://api.botpress.cloud/v1
Auth: Bearer token
"""

from __future__ import annotations

import logging
import os
from typing import Any

from scripts.api_clients.base_client import APIError, BaseAPIClient

logger = logging.getLogger(__name__)


class BotpressClient(BaseAPIClient):
    """Client for Botpress Cloud API.

    Args:
        api_key: Botpress token. Defaults to ``BOTPRESS_API_KEY`` env var.
        base_url: Botpress API base URL. Defaults to
            ``BOTPRESS_BASE_URL`` or ``https://api.botpress.cloud``.
        bot_id: Optional default bot identifier. Defaults to
            ``BOTPRESS_BOT_ID`` env var.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        bot_id: str | None = None,
    ) -> None:
        api_key = api_key or os.environ.get("BOTPRESS_API_KEY", "")
        raw_base = base_url or os.environ.get(
            "BOTPRESS_BASE_URL",
            "https://api.botpress.cloud",
        )
        normalized_base = raw_base.rstrip("/")
        if not normalized_base.endswith("/v1"):
            normalized_base = f"{normalized_base}/v1"

        self.default_bot_id = bot_id or os.environ.get("BOTPRESS_BOT_ID", "")
        super().__init__(
            base_url=normalized_base,
            auth_header="Authorization",
            auth_prefix="Bearer",
            api_key=api_key,
        )

    def _resolve_bot_id(self, bot_id: str | None) -> str:
        resolved = bot_id or self.default_bot_id
        if not resolved:
            raise ValueError(
                "Bot ID is required. Provide bot_id argument or set BOTPRESS_BOT_ID."
            )
        return resolved

    def check_connectivity(self) -> dict[str, Any]:
        """Check basic Botpress API reachability without mutating data."""
        try:
            response = self._request_raw("GET", "/admin/bots", params={"limit": 1})
            status_code = response.status_code
            url = response.url
        except APIError as exc:
            status_code = exc.status_code or 0
            url = f"{self.base_url}/admin/bots"

        return {
            "reachable": bool(status_code) and status_code < 500,
            "status_code": status_code,
            "url": url,
        }

    def list_bots(self, limit: int = 50) -> list[dict[str, Any]]:
        """List bots visible to the authenticated account."""
        data = self.get("/admin/bots", params={"limit": limit})
        if isinstance(data, dict):
            if "bots" in data and isinstance(data["bots"], list):
                return data["bots"]
            if "items" in data and isinstance(data["items"], list):
                return data["items"]
        return data if isinstance(data, list) else []

    def create_bot(self, name: str) -> dict[str, Any]:
        """Create a new bot."""
        return self.post("/admin/bots", json={"name": name})

    def create_conversation(
        self,
        user_id: str,
        *,
        bot_id: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Create a conversation for a user."""
        payload: dict[str, Any] = {
            "botId": self._resolve_bot_id(bot_id),
            "userId": user_id,
        }
        if tags:
            payload["tags"] = tags
        return self.post("/chat/conversations", json=payload)

    def send_message(
        self,
        conversation_id: str,
        text: str,
        *,
        bot_id: str | None = None,
        user_id: str = "user",
    ) -> dict[str, Any]:
        """Send a text message to a conversation."""
        payload = {
            "botId": self._resolve_bot_id(bot_id),
            "conversationId": conversation_id,
            "userId": user_id,
            "type": "text",
            "payload": {"text": text},
        }
        return self.post("/chat/messages", json=payload)

    def detect_intent(
        self,
        text: str,
        *,
        bot_id: str | None = None,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """Run NLU intent detection for input text."""
        payload: dict[str, Any] = {
            "botId": self._resolve_bot_id(bot_id),
            "text": text,
        }
        if conversation_id:
            payload["conversationId"] = conversation_id
        return self.post("/chat/intents", json=payload)

    def deploy_bot(self, bot_id: str | None = None) -> dict[str, Any]:
        """Trigger bot deployment for a target bot."""
        target = self._resolve_bot_id(bot_id)
        return self.post(f"/admin/bots/{target}/deploy")
