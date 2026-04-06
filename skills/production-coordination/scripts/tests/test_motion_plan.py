# /// script
# requires-python = ">=3.10"
# ///
"""Tests for Epic 14 Gate 2M motion plan helpers."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
SCRIPT = Path(__file__).resolve().parents[1] / "motion_plan.py"

from motion_plan import (
    MotionPlanError,
    apply_motion_designations,
    build_motion_plan_from_authorized_storyboard,
    route_motion_assignments,
)


def _authorized_storyboard() -> dict:
    return {
        "run_id": "RUN-MOTION-001",
        "authorized_slides": [
            {"slide_id": "slide-01", "card_number": 1},
            {"slide_id": "slide-02", "card_number": 2},
            {"slide_id": "slide-03", "card_number": 3},
        ],
    }


def test_build_motion_plan_defaults_to_static_rows() -> None:
    plan = build_motion_plan_from_authorized_storyboard(
        _authorized_storyboard(),
        motion_enabled=True,
        motion_budget={"max_credits": 24, "model_preference": "pro"},
    )

    assert plan["motion_enabled"] is True
    assert plan["summary"]["static"] == 3
    assert [row["motion_type"] for row in plan["slides"]] == ["static", "static", "static"]


def test_build_motion_plan_rejects_duplicate_slide_ids() -> None:
    storyboard = _authorized_storyboard()
    storyboard["authorized_slides"].append({"slide_id": "slide-01", "card_number": 99})

    with pytest.raises(MotionPlanError, match="duplicate slide_id"):
        build_motion_plan_from_authorized_storyboard(storyboard, motion_enabled=True)


def test_build_motion_plan_requires_budget_when_motion_enabled() -> None:
    with pytest.raises(MotionPlanError, match="motion_budget.max_credits"):
        build_motion_plan_from_authorized_storyboard(
            _authorized_storyboard(),
            motion_enabled=True,
        )


def test_apply_motion_designations_counts_and_estimates() -> None:
    plan = build_motion_plan_from_authorized_storyboard(
        _authorized_storyboard(),
        motion_enabled=True,
        motion_budget={"max_credits": 24, "model_preference": "pro"},
    )

    updated = apply_motion_designations(
        plan,
        {
            "slide-02": {
                "motion_type": "video",
                "motion_brief": "Animate the chart growth",
                "motion_duration_seconds": 5.0,
            },
            "slide-03": {
                "motion_type": "animation",
                "guidance_notes": "Pulse labels in sequence",
                "motion_duration_seconds": 7.0,
            },
        },
    )

    assert updated["summary"]["static"] == 1
    assert updated["summary"]["video"] == 1
    assert updated["summary"]["animation"] == 1
    assert updated["summary"]["estimated_credits"] == 8.0
    by_id = {row["slide_id"]: row for row in updated["slides"]}
    assert by_id["slide-02"]["motion_source"] == "kling"
    assert by_id["slide-03"]["motion_source"] == "manual"
    assert by_id["slide-02"]["motion_status"] == "pending"


def test_apply_motion_designations_is_noop_when_motion_disabled() -> None:
    plan = build_motion_plan_from_authorized_storyboard(
        _authorized_storyboard(),
        motion_enabled=False,
    )

    updated = apply_motion_designations(
        plan,
        {"slide-02": {"motion_type": "video", "motion_duration_seconds": 5.0}},
    )

    assert updated["summary"]["static"] == 3
    assert all(row["motion_type"] == "static" for row in updated["slides"])


def test_route_motion_assignments_returns_expected_buckets() -> None:
    plan = build_motion_plan_from_authorized_storyboard(
        _authorized_storyboard(),
        motion_enabled=True,
        motion_budget={"max_credits": 12, "model_preference": "std"},
    )
    plan = apply_motion_designations(
        plan,
        {
            "slide-02": {"motion_type": "video"},
            "slide-03": {"motion_type": "animation"},
        },
    )

    routing = route_motion_assignments(plan)

    assert [row["slide_id"] for row in routing["static"]] == ["slide-01"]
    assert [row["slide_id"] for row in routing["video"]] == ["slide-02"]
    assert [row["slide_id"] for row in routing["animation"]] == ["slide-03"]


def test_apply_motion_designations_rejects_unknown_slide_ids() -> None:
    plan = build_motion_plan_from_authorized_storyboard(
        _authorized_storyboard(),
        motion_enabled=True,
        motion_budget={"max_credits": 12, "model_preference": "std"},
    )
    with pytest.raises(MotionPlanError, match="unknown slide_id"):
        apply_motion_designations(
            plan,
            {"slide-99": {"motion_type": "video"}},
        )


def test_apply_motion_designations_rejects_total_budget_overrun() -> None:
    plan = build_motion_plan_from_authorized_storyboard(
        _authorized_storyboard(),
        motion_enabled=True,
        motion_budget={"max_credits": 12, "model_preference": "std"},
    )

    with pytest.raises(MotionPlanError, match="exceeds motion_budget.max_credits"):
        apply_motion_designations(
            plan,
            {
                "slide-01": {"motion_type": "video", "motion_duration_seconds": 10.0},
                "slide-02": {"motion_type": "video", "motion_duration_seconds": 10.0},
            },
        )


def test_motion_plan_cli_build_and_apply_runtime_entrypoint() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        authorized = root / "authorized-storyboard.yaml"
        plan_path = root / "motion-plan.yaml"
        final_path = root / "motion-plan-final.yaml"
        designations = root / "designations.yaml"

        authorized.write_text(yaml.safe_dump(_authorized_storyboard(), sort_keys=False), encoding="utf-8")
        designations.write_text(
            yaml.safe_dump(
                {
                    "slide-02": {
                        "motion_type": "video",
                        "motion_duration_seconds": 5.0,
                        "motion_brief": "Animate the growth chart",
                    }
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

        build = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "build",
                "--authorized-storyboard",
                str(authorized),
                "--output",
                str(plan_path),
                "--motion-enabled",
                "--motion-budget-max-credits",
                "12",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert build.returncode == 0, build.stdout + build.stderr
        assert plan_path.exists()

        apply = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "apply",
                "--motion-plan",
                str(plan_path),
                "--designations",
                str(designations),
                "--output",
                str(final_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert apply.returncode == 0, apply.stdout + apply.stderr

        routed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "route",
                "--motion-plan",
                str(final_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert routed.returncode == 0, routed.stdout + routed.stderr
        buckets = json.loads(routed.stdout)
        assert [row["slide_id"] for row in buckets["video"]] == ["slide-02"]
