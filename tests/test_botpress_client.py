"""Unit tests for BotpressClient."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from scripts.api_clients.base_client import APIError
from scripts.api_clients.botpress_client import BotpressClient


def test_base_url_normalized_to_v1() -> None:
    client = BotpressClient(api_key="k", base_url="https://api.botpress.cloud")
    assert client.base_url.endswith("/v1")


def test_check_connectivity_handles_auth_error_as_reachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = BotpressClient(api_key="k")

    def fake_request_raw(method: str, endpoint: str, **kwargs: object) -> SimpleNamespace:
        raise APIError("forbidden", status_code=403)

    monkeypatch.setattr(client, "_request_raw", fake_request_raw)

    result = client.check_connectivity()
    assert result["reachable"] is True
    assert result["status_code"] == 403


def test_check_connectivity_success(monkeypatch: pytest.MonkeyPatch) -> None:
    client = BotpressClient(api_key="k")

    def fake_request_raw(method: str, endpoint: str, **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(status_code=200, url="https://api.botpress.cloud/v1/admin/bots")

    monkeypatch.setattr(client, "_request_raw", fake_request_raw)

    result = client.check_connectivity()
    assert result["reachable"] is True
    assert result["status_code"] == 200


def test_create_conversation_requires_bot_id() -> None:
    client = BotpressClient(api_key="k", bot_id="")

    with pytest.raises(ValueError, match="Bot ID is required"):
        client.create_conversation("user-1")
