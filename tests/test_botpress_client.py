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


def test_send_message_payload_uses_default_bot_and_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = BotpressClient(api_key="k", bot_id="bot-1")
    captured: dict[str, object] = {}

    def fake_post(endpoint: str, json: dict[str, object] | None = None) -> dict[str, object]:
        captured["endpoint"] = endpoint
        captured["json"] = json or {}
        return {"ok": True}

    monkeypatch.setattr(client, "post", fake_post)
    result = client.send_message("conv-1", "hello world")

    assert result == {"ok": True}
    assert captured["endpoint"] == "/chat/messages"
    assert captured["json"] == {
        "botId": "bot-1",
        "conversationId": "conv-1",
        "userId": "user",
        "type": "text",
        "payload": {"text": "hello world"},
    }


def test_detect_intent_payload_includes_conversation_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = BotpressClient(api_key="k", bot_id="bot-1")
    captured: dict[str, object] = {}

    def fake_post(endpoint: str, json: dict[str, object] | None = None) -> dict[str, object]:
        captured["endpoint"] = endpoint
        captured["json"] = json or {}
        return {"intent": "greeting"}

    monkeypatch.setattr(client, "post", fake_post)
    result = client.detect_intent("hi", conversation_id="conv-9")

    assert result == {"intent": "greeting"}
    assert captured["endpoint"] == "/chat/intents"
    assert captured["json"] == {
        "botId": "bot-1",
        "text": "hi",
        "conversationId": "conv-9",
    }
