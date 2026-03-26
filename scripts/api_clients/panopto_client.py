"""Panopto API client for video platform management.

API Docs: https://{instance}/Panopto/api/docs/index.html
Auth: OAuth2 client credentials
"""

from __future__ import annotations

import logging
import os
from typing import Any

from scripts.api_clients.base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class PanoptoClient(BaseAPIClient):
    """Client for Panopto REST API.

    Uses OAuth2 client credentials flow to obtain an access token,
    then uses it as a Bearer token for subsequent requests.

    Args:
        base_url: Panopto instance URL.
            Defaults to ``PANOPTO_BASE_URL`` env var.
        client_id: OAuth2 client ID.
            Defaults to ``PANOPTO_CLIENT_ID`` env var.
        client_secret: OAuth2 client secret.
            Defaults to ``PANOPTO_CLIENT_SECRET`` env var.
    """

    def __init__(
        self,
        base_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        self._panopto_base = (
            base_url or os.environ.get("PANOPTO_BASE_URL", "")
        ).rstrip("/")
        self._client_id = client_id or os.environ.get(
            "PANOPTO_CLIENT_ID", ""
        )
        self._client_secret = client_secret or os.environ.get(
            "PANOPTO_CLIENT_SECRET", ""
        )
        super().__init__(
            base_url=f"{self._panopto_base}/Panopto/api/v1",
            auth_header="Authorization",
            auth_prefix="Bearer",
            api_key="",  # set after auth
        )
        self._token: str | None = None

    def authenticate(self) -> str:
        """Obtain OAuth2 access token via client credentials grant.

        Returns:
            The access token string.
        """
        import requests as req

        token_url = (
            f"{self._panopto_base}/Panopto/oauth2/connect/token"
        )
        resp = req.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        self.session.headers["Authorization"] = f"Bearer {self._token}"
        logger.info("Panopto authentication successful")
        return self._token

    def _ensure_auth(self) -> None:
        """Authenticate if no token is set."""
        if not self._token:
            self.authenticate()

    # -- Folders --

    def list_folders(
        self, parent_folder_id: str | None = None, **params: Any
    ) -> list[dict[str, Any]]:
        """List folders, optionally filtered by parent."""
        self._ensure_auth()
        if parent_folder_id:
            params["parentFolderId"] = parent_folder_id
        data = self.get("/folders", params=params)
        return data.get("Results", data) if isinstance(data, dict) else data

    def get_folder(self, folder_id: str) -> dict[str, Any]:
        """Get folder details by ID."""
        self._ensure_auth()
        return self.get(f"/folders/{folder_id}")

    def search_folders(self, query: str) -> list[dict[str, Any]]:
        """Search folders by name."""
        self._ensure_auth()
        data = self.get("/folders/search", params={"searchQuery": query})
        return data.get("Results", data) if isinstance(data, dict) else data

    # -- Sessions (videos) --

    def list_sessions(
        self, folder_id: str, **params: Any
    ) -> list[dict[str, Any]]:
        """List video sessions in a folder."""
        self._ensure_auth()
        data = self.get(
            f"/folders/{folder_id}/sessions", params=params
        )
        return data.get("Results", data) if isinstance(data, dict) else data

    def get_session(self, session_id: str) -> dict[str, Any]:
        """Get video session details."""
        self._ensure_auth()
        return self.get(f"/sessions/{session_id}")

    def search_sessions(self, query: str) -> list[dict[str, Any]]:
        """Search video sessions by name/description."""
        self._ensure_auth()
        data = self.get("/sessions/search", params={"searchQuery": query})
        return data.get("Results", data) if isinstance(data, dict) else data
