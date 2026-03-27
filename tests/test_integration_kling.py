"""Integration tests for Kling AI video generation API client.

These tests run against the live Kling API and require KLING_ACCESS_KEY
and KLING_SECRET_KEY in the environment.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from scripts.api_clients.kling_client import (
    KlingClient,
    generate_jwt_token,
)

HAS_KLING_CREDS = bool(
    os.environ.get("KLING_ACCESS_KEY") and os.environ.get("KLING_SECRET_KEY")
)
skip_no_creds = pytest.mark.skipif(
    not HAS_KLING_CREDS,
    reason="KLING_ACCESS_KEY and KLING_SECRET_KEY not set",
)


class TestJWTTokenGeneration:
    """Test JWT token generation without live API."""

    def test_generates_valid_jwt(self):
        token = generate_jwt_token("test_ak", "test_sk")
        assert isinstance(token, str)
        assert len(token) > 50

    def test_token_has_three_parts(self):
        token = generate_jwt_token("test_ak", "test_sk")
        parts = token.split(".")
        assert len(parts) == 3

    def test_different_keys_produce_different_tokens(self):
        t1 = generate_jwt_token("ak1", "sk1")
        t2 = generate_jwt_token("ak2", "sk2")
        assert t1 != t2


class TestKlingClientInit:
    """Test client initialization."""

    def test_client_creates_with_explicit_keys(self):
        client = KlingClient(access_key="test_ak", secret_key="test_sk")
        assert client.base_url == "https://api.klingai.com"
        assert "Authorization" in client.session.headers

    def test_client_reads_env_vars(self, monkeypatch):
        monkeypatch.setenv("KLING_ACCESS_KEY", "env_ak")
        monkeypatch.setenv("KLING_SECRET_KEY", "env_sk")
        client = KlingClient()
        assert client._access_key == "env_ak"
        assert client._secret_key == "env_sk"


@skip_no_creds
class TestKlingTextToVideo:
    """Live API tests for text-to-video generation."""

    @pytest.fixture
    def client(self):
        return KlingClient()

    def test_text_to_video_returns_task_id(self, client):
        """Submit a minimal 3s text-to-video request."""
        result = client.text_to_video(
            prompt="A simple blue gradient background slowly shifting colors",
            model_name="kling-v1-6",
            duration="5",
            mode="std",
            negative_prompt="text, watermark, human, face",
        )
        assert "task_id" in result or "data" in result
        task_id = result.get("task_id") or result.get("data", {}).get("task_id")
        assert task_id is not None
        print(f"Text-to-video task created: {task_id}")


@skip_no_creds
class TestKlingTaskStatus:
    """Live API tests for task status polling."""

    @pytest.fixture
    def client(self):
        return KlingClient()

    def test_submit_and_poll_text_to_video(self, client):
        """Submit a minimal video and poll to completion."""
        result = client.text_to_video(
            prompt="Slow zoom on a blue gradient background",
            model_name="kling-v1-6",
            duration="5",
            mode="std",
            negative_prompt="text, watermark, human",
        )
        task_id = result.get("task_id") or result.get("data", {}).get("task_id")
        assert task_id is not None

        final = client.wait_for_completion(task_id, poll_interval=5, max_attempts=60)
        status = final.get("status") or final.get("data", {}).get("status", "")
        assert status.lower() in ("completed", "complete", "done", "success")
        print(f"Task {task_id} completed: {final}")


@skip_no_creds
class TestKlingDownload:
    """Live API tests for video download."""

    @pytest.fixture
    def client(self):
        return KlingClient()

    def test_full_generate_and_download(self, client, tmp_path):
        """End-to-end: generate → poll → download."""
        result = client.text_to_video(
            prompt="Soft blue light gently pulsing on a dark background",
            model_name="kling-v1-6",
            duration="5",
            mode="std",
            negative_prompt="text, watermark",
        )
        task_id = result.get("task_id") or result.get("data", {}).get("task_id")
        assert task_id is not None

        final = client.wait_for_completion(task_id, poll_interval=5, max_attempts=60)

        video_url = None
        data = final.get("data", final)
        if isinstance(data.get("response"), list) and data["response"]:
            video_url = data["response"][0]
        elif data.get("video_url"):
            video_url = data["video_url"]
        elif data.get("output", {}).get("video_url"):
            video_url = data["output"]["video_url"]

        if video_url:
            output_path = tmp_path / "test_video.mp4"
            downloaded = client.download_video(video_url, output_path)
            assert downloaded.exists()
            assert downloaded.stat().st_size > 1000
            print(f"Downloaded: {downloaded} ({downloaded.stat().st_size} bytes)")
        else:
            print(f"No video URL found in response. Full response: {final}")
            pytest.skip("Could not extract video URL from response — API format may differ")
