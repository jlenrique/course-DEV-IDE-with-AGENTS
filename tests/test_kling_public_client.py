from __future__ import annotations

from pathlib import Path

from scripts.api_clients.kling_public_client import (
    KlingPublicClient,
    _normalize_mode,
    _normalize_model_name,
)


def test_normalize_mode_maps_repo_values() -> None:
    assert _normalize_mode("std") == "std"
    assert _normalize_mode("pro") == "pro"
    assert _normalize_mode("standard") == "std"


def test_normalize_model_name_maps_known_v26_ids() -> None:
    assert _normalize_model_name("kling-v2.6", "std") == "kling-v2-6"
    assert _normalize_model_name("kling-v3.0", "pro") == "kling-v3-0"
    assert _normalize_model_name("kling-video-o1", "pro") == "kling-video-o1"


def test_text_to_video_uses_public_payload_shape(monkeypatch) -> None:
    client = KlingPublicClient(access_key="ak", secret_key="sk")
    captured: dict[str, object] = {}

    def fake_post(endpoint: str, **kwargs: object) -> dict[str, object]:
        captured["endpoint"] = endpoint
        captured["json"] = kwargs["json"]
        return {"task_id": "task-123"}

    monkeypatch.setattr(client, "post", fake_post)

    result = client.text_to_video(
        "probe",
        model_name="kling-v2-6",
        mode="pro",
        duration="10",
    )

    assert result["task_id"] == "task-123"
    assert captured["endpoint"] == "/v1/videos/text2video"
    payload = captured["json"]
    assert payload["model_name"] == "kling-v2-6"
    assert payload["mode"] == "pro"
    assert "model" not in payload


def test_get_task_status_normalizes_top_level_payload(monkeypatch) -> None:
    client = KlingPublicClient(access_key="ak", secret_key="sk")

    def fake_get(endpoint: str, **kwargs: object) -> dict[str, object]:
        assert endpoint == "/v1/videos/task-789"
        return {
            "task_id": "task-789",
            "status": "succeed",
            "output": {"video_url": "https://cdn.example.com/video.mp4", "duration": 10},
        }

    monkeypatch.setattr(client, "get", fake_get)

    payload = client.get_task_status("task-789")

    assert payload["data"]["task_status"] == "succeed"
    assert payload["data"]["task_result"]["videos"][0]["url"] == "https://cdn.example.com/video.mp4"
    assert payload["data"]["task_result"]["videos"][0]["duration"] == "10"


def test_download_video_writes_mp4(monkeypatch, tmp_path: Path) -> None:
    client = KlingPublicClient(access_key="ak", secret_key="sk")

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def iter_content(self, chunk_size: int = 8192):
            del chunk_size
            yield b"video-bytes"

    monkeypatch.setattr("scripts.api_clients.kling_public_client.requests.get", lambda *args, **kwargs: FakeResponse())

    output = client.download_video("https://cdn.example.com/video.mp4", tmp_path / "clip.mp4")

    assert output.exists()
    assert output.read_bytes() == b"video-bytes"
