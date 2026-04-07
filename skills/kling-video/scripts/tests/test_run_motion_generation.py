"""Tests for the internal Gate 7E Kling backend."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml

MODULE_PATH = Path(__file__).resolve().parents[1] / "run_motion_generation.py"
SPEC = importlib.util.spec_from_file_location("run_motion_generation", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _motion_plan(slide_id: str = "slide-01", other_slide: bool = False) -> dict[str, object]:
    slides: list[dict[str, object]] = [
        {
            "slide_id": slide_id,
            "card_number": 1,
            "motion_type": "video",
            "motion_brief": "Busy hospital corridor with a fatigued physician.",
            "motion_asset_path": None,
            "motion_source": "kling",
            "motion_duration_seconds": 5.0,
            "motion_status": "pending",
            "estimated_credits": 8.0,
            "credits_consumed": 0.0,
        }
    ]
    if other_slide:
        slides.append(
            {
                "slide_id": "slide-02",
                "card_number": 2,
                "motion_type": "static",
                "motion_brief": None,
                "motion_asset_path": None,
                "motion_source": None,
                "motion_duration_seconds": None,
                "motion_status": None,
                "estimated_credits": 0.0,
                "credits_consumed": 0.0,
            }
        )
    return {
        "motion_plan_version": 1,
        "run_id": "RUN-123",
        "motion_enabled": True,
        "motion_budget": {"max_credits": 24.0, "model_preference": "pro"},
        "summary": {
            "static": 0,
            "video": 1,
            "animation": 0,
            "estimated_credits": 8.0,
            "credits_consumed": 0.0,
        },
        "slides": slides,
    }


def _write_plan(path: Path, payload: dict[str, object]) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _read_plan(path: Path) -> dict[str, object]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _mock_download_to(path: Path):
    def _download(url: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"mp4-bytes")
        return output_path

    return _download


def test_runner_happy_path_submits_polls_validates_and_patches_plan(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    motion_plan = bundle / "motion_plan.yaml"
    _write_plan(motion_plan, _motion_plan())

    client = Mock()
    client.text_to_video.return_value = {"data": {"task_id": "task-123"}}
    client.wait_for_completion.return_value = {
        "data": {
            "task_status": "succeed",
            "task_result": {"videos": [{"url": "https://cdn.example.com/video.mp4", "duration": "5.0"}]},
            "task_info": {"external_task_info": {"entity": {"final_unit_deduction": 2.5}}},
        }
    }
    client.download_video.side_effect = _mock_download_to(bundle / "motion" / "slide-01_motion.mp4")

    result = MODULE.run_motion_generation_for_slide(
        motion_plan_path=motion_plan,
        slide_id="slide-01",
        repo_root=tmp_path,
        client=client,
        poll_interval=0,
        max_attempts=2,
        timeout_seconds=1,
    )

    assert result["status"] == "generated"
    assert result["task_id"] == "task-123"
    updated = _read_plan(motion_plan)
    row = updated["slides"][0]
    assert row["motion_status"] == "generated"
    assert row["motion_asset_path"] == "bundle/motion/slide-01_motion.mp4"
    assert row["credits_consumed"] == 2.5
    assert row["provider_task_id"] == "task-123"
    assert (bundle / "motion-generation-slide-01.progress.json").exists()
    assert (bundle / "motion-generation-slide-01.json").exists()
    client.text_to_video.assert_called_once()
    assert "sound" not in client.text_to_video.call_args.kwargs
    client.wait_for_completion.assert_called_once_with(
        "task-123",
        task_type="text2video",
        poll_interval=0,
        max_attempts=2,
        timeout_seconds=1,
    )


def test_runner_is_idempotent_when_terminal_asset_already_exists(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    motion_dir = bundle / "motion"
    motion_dir.mkdir(parents=True)
    asset = motion_dir / "slide-01_motion.mp4"
    asset.write_bytes(b"mp4-bytes")
    plan = _motion_plan()
    row = plan["slides"][0]
    row["motion_status"] = "generated"
    row["motion_asset_path"] = "bundle/motion/slide-01_motion.mp4"
    row["provider_task_id"] = "task-123"
    motion_plan = bundle / "motion_plan.yaml"
    _write_plan(motion_plan, plan)

    client = Mock()
    result = MODULE.run_motion_generation_for_slide(
        motion_plan_path=motion_plan,
        slide_id="slide-01",
        repo_root=tmp_path,
        client=client,
    )

    assert result["status"] == "existing"
    client.text_to_video.assert_not_called()
    client.wait_for_completion.assert_not_called()


def test_runner_recovers_from_existing_submitted_progress_without_resubmitting(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    motion_plan = bundle / "motion_plan.yaml"
    _write_plan(motion_plan, _motion_plan())
    progress = bundle / "motion-generation-slide-01.progress.json"
    progress.write_text(
        json.dumps(
            {
                "status": "submitted",
                "task_id": "task-resume",
                "operation": "text2video",
                "model_name": "kling-v2-6",
                "mode": "pro",
                "estimated_credits": 8.0,
                "requested_duration_seconds": 5.0,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    client = Mock()
    client.wait_for_completion.return_value = {
        "data": {
            "task_status": "succeed",
            "task_result": {"videos": [{"url": "https://cdn.example.com/resume.mp4", "duration": "5.0"}]},
        }
    }
    client.download_video.side_effect = _mock_download_to(bundle / "motion" / "slide-01_motion.mp4")

    result = MODULE.run_motion_generation_for_slide(
        motion_plan_path=motion_plan,
        slide_id="slide-01",
        repo_root=tmp_path,
        client=client,
        poll_interval=0,
        max_attempts=2,
        timeout_seconds=1,
    )

    assert result["task_id"] == "task-resume"
    client.text_to_video.assert_not_called()
    client.wait_for_completion.assert_called_once()


def test_runner_rejects_duplicate_active_workers_for_same_slide(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    motion_plan = bundle / "motion_plan.yaml"
    _write_plan(motion_plan, _motion_plan())
    (bundle / "motion-generation-slide-01.lock").write_text("busy", encoding="utf-8")

    with pytest.raises(MODULE.MotionGenerationError, match="already active"):
        MODULE.run_motion_generation_for_slide(
            motion_plan_path=motion_plan,
            slide_id="slide-01",
            repo_root=tmp_path,
            client=Mock(),
        )


def test_runner_fails_closed_on_empty_result_and_keeps_row_unresolved(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    motion_plan = bundle / "motion_plan.yaml"
    _write_plan(motion_plan, _motion_plan())

    client = Mock()
    client.text_to_video.return_value = {"data": {"task_id": "task-bad"}}
    client.wait_for_completion.return_value = {"data": {"task_status": "succeed", "task_result": {"videos": []}}}

    with pytest.raises(MODULE.MotionGenerationError, match="No video URL found"):
        MODULE.run_motion_generation_for_slide(
            motion_plan_path=motion_plan,
            slide_id="slide-01",
            repo_root=tmp_path,
            client=client,
            poll_interval=0,
            max_attempts=2,
            timeout_seconds=1,
        )

    updated = _read_plan(motion_plan)
    row = updated["slides"][0]
    assert row["motion_status"] == "pending"
    assert "No video URL found" in row["last_generation_error"]
    receipt = json.loads((bundle / "motion-generation-slide-01.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "error"


def test_runner_patches_only_target_slide_row(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    motion_plan = bundle / "motion_plan.yaml"
    _write_plan(motion_plan, _motion_plan(other_slide=True))

    client = Mock()
    client.text_to_video.return_value = {"data": {"task_id": "task-123"}}
    client.wait_for_completion.return_value = {
        "data": {
            "task_status": "succeed",
            "task_result": {"videos": [{"url": "https://cdn.example.com/video.mp4", "duration": "5.0"}]},
        }
    }
    client.download_video.side_effect = _mock_download_to(bundle / "motion" / "slide-01_motion.mp4")

    MODULE.run_motion_generation_for_slide(
        motion_plan_path=motion_plan,
        slide_id="slide-01",
        repo_root=tmp_path,
        client=client,
        poll_interval=0,
        max_attempts=2,
        timeout_seconds=1,
    )

    updated = _read_plan(motion_plan)
    row_one = updated["slides"][0]
    row_two = updated["slides"][1]
    assert row_one["motion_status"] == "generated"
    assert row_two["slide_id"] == "slide-02"
    assert row_two["motion_status"] is None
    assert row_two["motion_asset_path"] is None
