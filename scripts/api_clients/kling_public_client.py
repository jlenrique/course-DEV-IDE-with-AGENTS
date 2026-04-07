"""Exploratory client for Kling's newer 3.0 / Singapore API surface.

This client intentionally lives alongside the validated JWT-based client
instead of replacing it. The repo's production-safe lane remains on
``api.klingai.com`` with ``kling-v2-6`` until this Singapore-surface path is
proven stable through the validation lane.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

import requests

from scripts.api_clients.base_client import BaseAPIClient
from scripts.api_clients.kling_client import generate_jwt_token

logger = logging.getLogger(__name__)

KLING_PUBLIC_BASE_URL = "https://api-singapore.klingai.com"
POLL_INTERVAL = 5
MAX_POLL_ATTEMPTS = 120
TOKEN_LIFETIME = 1800


def _normalize_mode(mode: str) -> str:
    value = str(mode).strip().lower()
    if value in {"std", "standard"}:
        return "std"
    if value in {"pro", "professional"}:
        return "pro"
    return value


def _normalize_model_name(model_name: str, mode: str) -> str:
    """Pass through known Kling model ids while allowing fallback aliases."""
    name = str(model_name).strip()
    normalized_mode = _normalize_mode(mode)
    mapping = {
        ("kling-v2.6", "std"): "kling-v2-6",
        ("kling-v2.6", "pro"): "kling-v2-6",
        ("kling-v3.0", "std"): "kling-v3-0",
        ("kling-v3.0", "pro"): "kling-v3-0",
    }
    return mapping.get((name, normalized_mode), name)


def _extract_video_url(payload: dict[str, Any]) -> str | None:
    data = payload.get("data")
    if isinstance(data, dict):
        task_result = data.get("task_result")
        if isinstance(task_result, dict):
            videos = task_result.get("videos")
            if isinstance(videos, list) and videos:
                first = videos[0]
                if isinstance(first, dict) and isinstance(first.get("url"), str):
                    return first["url"]
    output = payload.get("output")
    if isinstance(output, dict):
        video_url = output.get("video_url")
        if isinstance(video_url, str):
            return video_url
    response = payload.get("response")
    if isinstance(response, list) and response and isinstance(response[0], str):
        return response[0]
    video_url = payload.get("video_url")
    if isinstance(video_url, str):
        return video_url
    return None


def _extract_duration(payload: dict[str, Any]) -> str | None:
    data = payload.get("data")
    if isinstance(data, dict):
        task_result = data.get("task_result")
        if isinstance(task_result, dict):
            videos = task_result.get("videos")
            if isinstance(videos, list) and videos:
                first = videos[0]
                if isinstance(first, dict) and isinstance(first.get("duration"), (str, int, float)):
                    return str(first["duration"])
    output = payload.get("output")
    if isinstance(output, dict) and isinstance(output.get("duration"), (str, int, float)):
        return str(output["duration"])
    duration = payload.get("duration")
    if isinstance(duration, (str, int, float)):
        return str(duration)
    return None


def _normalize_status_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Bridge newer exploratory responses into the repo's existing shape."""
    if isinstance(payload.get("data"), dict):
        return payload

    task_status = (
        payload.get("status")
        or payload.get("task_status")
        or payload.get("state")
        or ""
    )
    normalized = {
        "data": {
            "task_id": payload.get("task_id") or payload.get("id"),
            "task_status": task_status,
            "task_status_msg": payload.get("message") or payload.get("error"),
            "task_result": {
                "videos": [],
            },
        }
    }
    video_url = _extract_video_url(payload)
    if video_url:
        normalized["data"]["task_result"]["videos"].append(
            {
                "url": video_url,
                "duration": _extract_duration(payload),
            }
        )
    return normalized


class KlingPublicClient(BaseAPIClient):
    """Client for the newer Singapore 3.0-capable Kling surface.

    Auth stays on AccessKey + SecretKey with generated Bearer token.
    """

    def __init__(
        self,
        access_key: str | None = None,
        secret_key: str | None = None,
    ) -> None:
        self._access_key = access_key or os.environ.get("KLING_ACCESS_KEY", "")
        self._secret_key = secret_key or os.environ.get("KLING_SECRET_KEY", "")
        self._token_expiry = 0

        token = self._ensure_token()
        super().__init__(
            base_url=KLING_PUBLIC_BASE_URL,
            auth_header="Authorization",
            auth_prefix="Bearer",
            api_key=token,
            timeout=60,
            default_headers={"Content-Type": "application/json"},
        )

    def _ensure_token(self) -> str:
        now = int(time.time())
        if now >= self._token_expiry - 60:
            token = generate_jwt_token(self._access_key, self._secret_key)
            self._token_expiry = now + TOKEN_LIFETIME
            if hasattr(self, "session"):
                self.session.headers["Authorization"] = f"Bearer {token}"
            return token
        return self.session.headers.get("Authorization", "").replace("Bearer ", "")

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        self._ensure_token()
        return super()._request(method, endpoint, **kwargs)

    def _request_raw(self, method: str, endpoint: str, **kwargs: Any) -> requests.Response:
        self._ensure_token()
        return super()._request_raw(method, endpoint, **kwargs)

    def text_to_video(
        self,
        prompt: str,
        *,
        model_name: str = "kling-v2-6",
        duration: str = "5",
        aspect_ratio: str = "16:9",
        mode: str = "std",
        negative_prompt: str | None = None,
        sound: bool | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model_name": _normalize_model_name(model_name, mode),
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "mode": _normalize_mode(mode),
        }
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        if sound is not None:
            payload["sound"] = sound
        return self.post("/v1/videos/text2video", json=payload)

    def image_to_video(
        self,
        image_url: str,
        *,
        prompt: str = "",
        model_name: str = "kling-v2-6",
        duration: str = "5",
        aspect_ratio: str = "16:9",
        mode: str = "std",
        end_image_url: str | None = None,
        negative_prompt: str | None = None,
        sound: bool | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model_name": _normalize_model_name(model_name, mode),
            "image": image_url,
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "mode": _normalize_mode(mode),
        }
        if end_image_url:
            payload["end_image"] = end_image_url
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        if sound is not None:
            payload["sound"] = sound
        return self.post("/v1/videos/image2video", json=payload)

    def get_task_status(self, task_id: str, task_type: str = "text2video") -> dict[str, Any]:
        try:
            payload = self.get(f"/v1/videos/{task_type}/{task_id}")
            return _normalize_status_payload(payload)
        except Exception:
            payload = self.get(f"/v1/videos/{task_id}")
            return _normalize_status_payload(payload)

    def wait_for_completion(
        self,
        task_id: str,
        task_type: str = "text2video",
        poll_interval: int = POLL_INTERVAL,
        max_attempts: int = MAX_POLL_ATTEMPTS,
        timeout_seconds: int | None = None,
    ) -> dict[str, Any]:
        started_at = time.monotonic()
        for attempt in range(max_attempts):
            data = self.get_task_status(task_id, task_type=task_type)
            data_block = data.get("data", {}) if isinstance(data.get("data"), dict) else {}
            status = (
                data.get("status")
                or data_block.get("status")
                or data_block.get("task_status")
                or ""
            )
            status_normalized = str(status).lower()
            if status_normalized in {"completed", "complete", "done", "success", "succeed"}:
                logger.info("Singapore-surface task %s completed after %d polls", task_id, attempt + 1)
                return data
            if status_normalized in {"failed", "error"}:
                error_msg = (
                    data.get("error_message")
                    or data_block.get("task_status_msg")
                    or "unknown error"
                )
                raise RuntimeError(f"Task {task_id} failed: {error_msg}")
            elapsed = time.monotonic() - started_at
            if timeout_seconds is not None and elapsed >= timeout_seconds:
                raise TimeoutError(f"Task {task_id} did not complete within {timeout_seconds}s")
            time.sleep(poll_interval)
        raise TimeoutError(f"Task {task_id} did not complete within {max_attempts * poll_interval}s")

    def download_video(self, video_url: str, output_path: str | Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(video_url, stream=True, timeout=120)
        response.raise_for_status()
        with open(output_path, "wb") as handle:
            for chunk in response.iter_content(chunk_size=8192):
                handle.write(chunk)
        return output_path
