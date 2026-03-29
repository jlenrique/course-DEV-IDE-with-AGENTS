"""Unit tests for Kling polling behavior.

These tests do not call the live API.
"""

from __future__ import annotations

import pytest

from scripts.api_clients.kling_client import KlingClient


@pytest.fixture
def client() -> KlingClient:
    return KlingClient(access_key="test_ak", secret_key="test_sk")


def test_wait_for_completion_accepts_task_status_field(
    client: KlingClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = [
        {"data": {"task_status": "processing"}},
        {"data": {"task_status": "succeed"}},
    ]

    def fake_status(task_id: str, task_type: str = "text2video") -> dict[str, object]:
        return responses.pop(0)

    monkeypatch.setattr(client, "get_task_status", fake_status)
    monkeypatch.setattr("scripts.api_clients.kling_client.time.sleep", lambda _: None)

    result = client.wait_for_completion("task-1", poll_interval=0, max_attempts=5)
    assert result["data"]["task_status"] == "succeed"


def test_wait_for_completion_timeout_seconds_enforced(
    client: KlingClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_status(task_id: str, task_type: str = "text2video") -> dict[str, object]:
        return {"data": {"task_status": "processing"}}

    monotonic_values = iter([0.0, 0.6, 1.2, 1.2])

    monkeypatch.setattr(client, "get_task_status", fake_status)
    monkeypatch.setattr("scripts.api_clients.kling_client.time.sleep", lambda _: None)
    monkeypatch.setattr(
        "scripts.api_clients.kling_client.time.monotonic",
        lambda: next(monotonic_values),
    )

    with pytest.raises(TimeoutError, match="within 1s"):
        client.wait_for_completion(
            "task-timeout",
            poll_interval=0,
            max_attempts=10,
            timeout_seconds=1,
        )


def test_wait_for_completion_failed_task_raises_runtime_error(
    client: KlingClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_status(task_id: str, task_type: str = "text2video") -> dict[str, object]:
        return {
            "data": {
                "task_status": "failed",
                "task_status_msg": "quota exceeded",
            }
        }

    monkeypatch.setattr(client, "get_task_status", fake_status)

    with pytest.raises(RuntimeError, match="quota exceeded"):
        client.wait_for_completion("task-failed", poll_interval=0, max_attempts=2)
