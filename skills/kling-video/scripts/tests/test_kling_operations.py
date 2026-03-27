"""Tests for kling_operations.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import Mock

MODULE_PATH = Path(__file__).resolve().parents[1] / "kling_operations.py"
SPEC = importlib.util.spec_from_file_location("kling_operations", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class TestExtractionHelpers:
    def test_extract_video_url(self) -> None:
        data = {
            "data": {
                "task_result": {
                    "videos": [{"url": "https://cdn.example.com/test.mp4", "duration": "5.0"}]
                }
            }
        }
        assert MODULE._extract_video_url(data) == "https://cdn.example.com/test.mp4"
        assert MODULE._extract_duration(data) == "5.0"

    def test_extract_video_url_missing(self) -> None:
        data = {"data": {"task_result": {"videos": []}}}
        assert MODULE._extract_video_url(data) is None
        assert MODULE._extract_duration(data) is None


class TestRunTextToVideo:
    def test_full_flow_returns_structured_result(self, tmp_path: Path) -> None:
        client = Mock()
        client.text_to_video.return_value = {"data": {"task_id": "task-123"}}
        client.wait_for_completion.return_value = {
            "data": {
                "task_result": {
                    "videos": [{"url": "https://cdn.example.com/test.mp4", "duration": "5.0"}]
                }
            }
        }
        downloaded = tmp_path / "out.mp4"
        client.download_video.return_value = downloaded

        result = MODULE.run_text_to_video(
            "test prompt",
            client=client,
            output_dir=tmp_path,
            filename="out.mp4",
        )

        assert result["task_id"] == "task-123"
        assert result["operation"] == "text2video"
        assert result["output_path"] == str(downloaded)
        client.text_to_video.assert_called_once()
        client.wait_for_completion.assert_called_once_with("task-123", task_type="text2video")
        client.download_video.assert_called_once()


class TestRunImageToVideo:
    def test_full_flow_returns_structured_result(self, tmp_path: Path) -> None:
        client = Mock()
        client.image_to_video.return_value = {"data": {"task_id": "task-456"}}
        client.wait_for_completion.return_value = {
            "data": {
                "task_result": {
                    "videos": [{"url": "https://cdn.example.com/test2.mp4", "duration": "5.0"}]
                }
            }
        }
        downloaded = tmp_path / "img.mp4"
        client.download_video.return_value = downloaded

        result = MODULE.run_image_to_video(
            "https://example.com/image.png",
            prompt="animate gently",
            client=client,
            output_dir=tmp_path,
            filename="img.mp4",
        )

        assert result["task_id"] == "task-456"
        assert result["operation"] == "image2video"
        assert result["output_path"] == str(downloaded)
        client.image_to_video.assert_called_once()
        client.wait_for_completion.assert_called_once_with("task-456", task_type="image2video")


class TestRunLipSync:
    def test_full_flow_returns_structured_result(self, tmp_path: Path) -> None:
        client = Mock()
        client.lip_sync.return_value = {"data": {"task_id": "task-789"}}
        client.wait_for_completion.return_value = {
            "data": {
                "task_result": {
                    "videos": [{"url": "https://cdn.example.com/lipsync.mp4", "duration": "6.1"}]
                }
            }
        }
        downloaded = tmp_path / "lip.mp4"
        client.download_video.return_value = downloaded

        result = MODULE.run_lip_sync(
            "https://example.com/video.mp4",
            "https://example.com/audio.mp3",
            client=client,
            output_dir=tmp_path,
            filename="lip.mp4",
        )

        assert result["task_id"] == "task-789"
        assert result["operation"] == "lip-sync"
        assert result["output_path"] == str(downloaded)
        client.lip_sync.assert_called_once()
        client.wait_for_completion.assert_called_once_with("task-789", task_type="lip-sync")
