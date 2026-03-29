"""Unit tests for WondercraftClient."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from scripts.api_clients.base_client import APIError
from scripts.api_clients.wondercraft_client import WondercraftClient


def test_base_url_normalized_to_v1() -> None:
    client = WondercraftClient(api_key="k", base_url="https://api.wondercraft.ai")
    assert client.base_url.endswith("/v1")


def test_check_connectivity_handles_auth_error_as_reachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = WondercraftClient(api_key="k")

    def fake_request_raw(method: str, endpoint: str, **kwargs: object) -> SimpleNamespace:
        raise APIError("unauthorized", status_code=401)

    monkeypatch.setattr(client, "_request_raw", fake_request_raw)

    result = client.check_connectivity()
    assert result["reachable"] is True
    assert result["status_code"] == 401


def test_wait_for_job_success(monkeypatch: pytest.MonkeyPatch) -> None:
    client = WondercraftClient(api_key="k")
    statuses = iter([{"status": "processing"}, {"status": "completed", "id": "job-1"}])

    monkeypatch.setattr(client, "get_job_status", lambda job_id: next(statuses))
    monkeypatch.setattr("scripts.api_clients.wondercraft_client.time.sleep", lambda _: None)

    result = client.wait_for_job("job-1", poll_interval=0, max_attempts=5)
    assert result["status"] == "completed"


def test_wait_for_job_failed_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    client = WondercraftClient(api_key="k")

    monkeypatch.setattr(
        client,
        "get_job_status",
        lambda job_id: {"status": "failed", "message": "bad script"},
    )

    with pytest.raises(RuntimeError, match="bad script"):
        client.wait_for_job("job-2", poll_interval=0, max_attempts=2)


def test_create_scripted_podcast_includes_voice_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = WondercraftClient(api_key="k")
    captured: dict[str, object] = {}

    def fake_post(endpoint: str, json: dict[str, object] | None = None) -> dict[str, object]:
        captured["endpoint"] = endpoint
        captured["json"] = json or {}
        return {"id": "pod-1"}

    monkeypatch.setattr(client, "post", fake_post)
    result = client.create_scripted_podcast(
        "Podcast",
        "Script",
        voice_id="voice-7",
    )

    assert result == {"id": "pod-1"}
    assert captured["endpoint"] == "/podcast/scripted"
    assert captured["json"] == {
        "title": "Podcast",
        "script": "Script",
        "voiceId": "voice-7",
    }
