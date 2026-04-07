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
    build_designations_template,
    build_motion_plan_from_authorized_storyboard,
    route_motion_assignments,
)


def _authorized_storyboard() -> dict:
    return {
        "run_id": "RUN-MOTION-001",
        "source_manifest": None,
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
    assert "recommendation_summary" in plan
    assert all(isinstance(row.get("recommendation"), dict) for row in plan["slides"])


def test_build_motion_plan_emits_source_anchored_recommendations_from_storyboard_manifest(tmp_path: Path) -> None:
    storyboard = _authorized_storyboard()
    source_manifest = tmp_path / "storyboard.json"
    source_manifest.write_text(
        json.dumps(
            {
                "slides": [
                    {
                        "slide_id": "slide-01",
                        "fidelity": "creative",
                        "source_ref": "extracted.md#SRC-1 (crossroads framing)",
                        "visual_description": "Creative framing slide about a clinician dilemma at a crossroads.",
                    },
                    {
                        "slide_id": "slide-02",
                        "fidelity": "literal-text",
                        "source_ref": "extracted.md#SRC-2 (objective list)",
                        "visual_description": "literal-text objective list.",
                    },
                    {
                        "slide_id": "slide-03",
                        "fidelity": "literal-visual",
                        "source_ref": "extracted.md#SRC-3 (roadmap journey)",
                        "visual_description": "literal-visual roadmap journey diagram.",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    storyboard["source_manifest"] = str(source_manifest)

    plan = build_motion_plan_from_authorized_storyboard(
        storyboard,
        motion_enabled=True,
        motion_budget={"max_credits": 24, "model_preference": "pro"},
    )

    by_id = {row["slide_id"]: row for row in plan["slides"]}
    assert by_id["slide-01"]["recommendation"]["source_anchor"] == "extracted.md#SRC-1 (crossroads framing)"
    assert by_id["slide-01"]["recommendation"]["motion_type"] == "video"
    assert by_id["slide-02"]["recommendation"]["motion_type"] == "static"
    assert by_id["slide-02"]["recommendation"]["confidence"] == "high"
    assert by_id["slide-03"]["recommendation"]["motion_type"] == "animation"
    assert plan["recommendation_summary"]["video"] == 1
    assert plan["recommendation_summary"]["animation"] == 1


def test_build_designations_template_exposes_recommendations_but_leaves_operator_choice_empty() -> None:
    plan = build_motion_plan_from_authorized_storyboard(
        _authorized_storyboard(),
        motion_enabled=True,
        motion_budget={"max_credits": 24, "model_preference": "pro"},
    )

    template = build_designations_template(plan)

    assert template["slide-01"]["motion_type"] is None
    assert template["slide-01"]["recommended_motion_type"] in {"static", "video", "animation"}
    assert template["slide-01"]["recommendation_source_anchor"] == "slide-01"
    assert template["slide-01"]["recommendation_confidence"] in {"high", "medium", "low"}


def test_build_motion_plan_rejects_duplicate_slide_ids() -> None:
    storyboard = _authorized_storyboard()
    storyboard["authorized_slides"].append({"slide_id": "slide-01", "card_number": 99})

    with pytest.raises(MotionPlanError, match="duplicate slide_id"):
        build_motion_plan_from_authorized_storyboard(
            storyboard,
            motion_enabled=True,
            motion_budget={"max_credits": 12, "model_preference": "std"},
        )


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
            "slide-01": {"motion_type": "static"},
            "slide-02": {
                "motion_type": "video",
                "motion_brief": "Animate the chart growth",
                "motion_duration_seconds": 5.0,
                "override_reason": "Testing explicit non-static override.",
            },
            "slide-03": {
                "motion_type": "animation",
                "guidance_notes": "Pulse labels in sequence",
                "motion_duration_seconds": 7.0,
                "override_reason": "Testing explicit animation override.",
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
    assert isinstance(by_id["slide-02"]["recommendation"], dict)


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
            "slide-01": {"motion_type": "static"},
            "slide-02": {"motion_type": "video", "override_reason": "Video route test."},
            "slide-03": {"motion_type": "animation", "override_reason": "Animation path test."},
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
            {
                "slide-01": {"motion_type": "static"},
                "slide-02": {"motion_type": "static"},
                "slide-03": {"motion_type": "static"},
                "slide-99": {"motion_type": "video"},
            },
        )


def test_apply_motion_designations_rejects_incomplete_coverage() -> None:
    plan = build_motion_plan_from_authorized_storyboard(
        _authorized_storyboard(),
        motion_enabled=True,
        motion_budget={"max_credits": 12, "model_preference": "std"},
    )
    with pytest.raises(MotionPlanError, match="incomplete; missing slide_id values"):
        apply_motion_designations(
            plan,
            {"slide-01": {"motion_type": "static"}},
        )


def test_apply_motion_designations_requires_explicit_motion_type_even_when_recommendations_exist() -> None:
    plan = build_motion_plan_from_authorized_storyboard(
        _authorized_storyboard(),
        motion_enabled=True,
        motion_budget={"max_credits": 12, "model_preference": "std"},
    )
    template = build_designations_template(plan)
    for slide_id, entry in template.items():
        entry["motion_type"] = "static" if slide_id != "slide-02" else None

    with pytest.raises(MotionPlanError, match="must be explicitly set"):
        apply_motion_designations(plan, template)


def test_apply_motion_designations_requires_override_reason_when_operator_differs() -> None:
    plan = build_motion_plan_from_authorized_storyboard(
        _authorized_storyboard(),
        motion_enabled=True,
        motion_budget={"max_credits": 12, "model_preference": "std"},
    )
    with pytest.raises(MotionPlanError, match="override_reason is required"):
        apply_motion_designations(
            plan,
            {
                "slide-01": {"motion_type": "video"},
                "slide-02": {"motion_type": "static"},
                "slide-03": {"motion_type": "static"},
            },
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
                "slide-01": {"motion_type": "video", "motion_duration_seconds": 10.0, "override_reason": "Budget overrun test."},
                "slide-02": {"motion_type": "video", "motion_duration_seconds": 10.0, "override_reason": "Budget overrun test."},
                "slide-03": {"motion_type": "static"},
            },
        )


def test_motion_plan_cli_build_and_apply_runtime_entrypoint() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        authorized = root / "authorized-storyboard.yaml"
        plan_path = root / "motion-plan.yaml"
        final_path = root / "motion-plan-final.yaml"
        designations = root / "designations.yaml"
        recommended_template = root / "designations-template.json"

        authorized.write_text(yaml.safe_dump(_authorized_storyboard(), sort_keys=False), encoding="utf-8")
        designations.write_text(
            yaml.safe_dump(
                {
                    "slide-01": {"motion_type": "static"},
                    "slide-02": {
                        "motion_type": "video",
                        "motion_duration_seconds": 5.0,
                        "motion_brief": "Animate the growth chart",
                        "override_reason": "Operator wants motion here.",
                    },
                    "slide-03": {"motion_type": "animation", "guidance_notes": "Pulse labels", "override_reason": "Operator wants manual animation here."},
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
                "--designations-output",
                str(recommended_template),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert build.returncode == 0, build.stdout + build.stderr
        assert plan_path.exists()
        assert recommended_template.exists()

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
