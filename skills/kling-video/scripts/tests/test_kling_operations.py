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


class TestMotionBudgeting:
    def test_resolve_motion_mode_downgrades_from_pro_when_budget_hit(self) -> None:
        result = MODULE.resolve_motion_mode(
            duration_seconds=5.0,
            motion_budget={"max_credits": 5, "model_preference": "pro"},
        )

        assert result["mode"] == "std"
        assert result["downgraded_from"] == "pro"
        assert result["estimated_credits"] == 4.0

    def test_resolve_motion_mode_raises_when_even_std_exceeds_budget(self) -> None:
        try:
            MODULE.resolve_motion_mode(
                duration_seconds=10.0,
                motion_budget={"max_credits": 3, "model_preference": "std"},
            )
        except RuntimeError as exc:
            assert "budget ceiling" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("Expected budget ceiling failure")


class TestGenerateMotionClip:
    def test_prefers_image_to_video_when_source_image_exists(self, tmp_path: Path) -> None:
        client = Mock()
        client.image_to_video.return_value = {"data": {"task_id": "task-456"}}
        client.wait_for_completion.return_value = {
            "data": {"task_result": {"videos": [{"url": "https://cdn.example.com/test2.mp4", "duration": "5.0"}]}}
        }
        client.download_video.return_value = tmp_path / "slide-02_motion.mp4"

        result = MODULE.generate_motion_clip(
            {
                "slide_id": "slide-02",
                "source_image_url": "https://example.com/slide.png",
                "motion_brief": "Animate the chart growth",
                "narration_intent": "Explain the trend clearly",
                "motion_duration_seconds": 5.0,
            },
            motion_budget={"max_credits": 24, "model_preference": "pro"},
            output_dir=tmp_path,
            client=client,
        )

        assert result["slide_id"] == "slide-02"
        assert result["operation"] == "image2video"
        assert result["model_used"] == "pro"
        assert result["credits_consumed"] == 8.0
        client.image_to_video.assert_called_once()
        client.text_to_video.assert_not_called()
        assert "sound" not in client.image_to_video.call_args.kwargs

    def test_falls_back_to_text_to_video_without_image_url(self, tmp_path: Path) -> None:
        client = Mock()
        client.text_to_video.return_value = {"data": {"task_id": "task-123"}}
        client.wait_for_completion.return_value = {
            "data": {"task_result": {"videos": [{"url": "https://cdn.example.com/test.mp4", "duration": "6.0"}]}}
        }
        client.download_video.return_value = tmp_path / "slide-03_motion.mp4"

        result = MODULE.generate_motion_clip(
            {
                "slide_id": "slide-03",
                "motion_brief": "Show the process unfolding step by step",
                "motion_duration_seconds": 6.0,
            },
            motion_budget={"max_credits": 12, "model_preference": "std"},
            output_dir=tmp_path,
            client=client,
        )

        assert result["operation"] == "text2video"
        assert result["model_used"] == "std"
        assert result["self_assessment"].startswith("text-to-video fallback")
        client.text_to_video.assert_called_once()
        assert "sound" not in client.text_to_video.call_args.kwargs
