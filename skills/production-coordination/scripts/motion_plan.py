# /// script
# requires-python = ">=3.10"
# ///
"""Run-scoped Gate 2M motion plan helpers for Epic 14.

The motion plan is the pre-Irene source of truth for motion designations.
It binds Gate 2M choices to the Epic 12 authorized winner deck, then later
hydrates those decisions into Irene's segment manifest.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.utilities.motion_budgeting import (
    MODEL_CREDIT_ESTIMATES,
    estimate_motion_credits,
    normalize_motion_mode,
)

MOTION_TYPES = {"static", "video", "animation"}
MODEL_PREFERENCES = set(MODEL_CREDIT_ESTIMATES)


class MotionPlanError(ValueError):
    """Invalid Gate 2M plan or designation payload."""


def _base_budget(
    motion_budget: dict[str, Any] | None,
    *,
    require_max_credits: bool = False,
) -> dict[str, Any]:
    budget = motion_budget or {}
    raw_model_preference = str(budget.get("model_preference") or "std")
    model_preference = normalize_motion_mode(raw_model_preference)
    if model_preference != raw_model_preference.strip().lower():
        raise MotionPlanError(
            f"motion_budget.model_preference must be one of {sorted(MODEL_PREFERENCES)}"
        )
    max_credits = budget.get("max_credits")
    if require_max_credits and not isinstance(max_credits, (int, float)):
        raise MotionPlanError("motion_enabled requires motion_budget.max_credits")
    if require_max_credits and isinstance(max_credits, (int, float)) and float(max_credits) <= 0:
        raise MotionPlanError("motion_budget.max_credits must be a positive number")
    return {
        "max_credits": float(max_credits) if isinstance(max_credits, (int, float)) else None,
        "model_preference": model_preference,
    }
def build_motion_plan_from_authorized_storyboard(
    authorized_storyboard: dict[str, Any],
    *,
    motion_enabled: bool = False,
    motion_budget: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a Gate 2M motion plan from the Epic 12 winner deck."""
    slides = authorized_storyboard.get("authorized_slides", [])
    if not isinstance(slides, list) or not slides:
        raise MotionPlanError("authorized_storyboard must contain authorized_slides")

    seen_slide_ids: set[str] = set()
    plan_rows: list[dict[str, Any]] = []
    for slide in slides:
        if not isinstance(slide, dict):
            continue
        slide_id = str(slide.get("slide_id") or "").strip()
        if not slide_id:
            raise MotionPlanError("authorized_slides entries require slide_id")
        if slide_id in seen_slide_ids:
            raise MotionPlanError(
                f"authorized_storyboard is not canonical; duplicate slide_id {slide_id!r}"
            )
        seen_slide_ids.add(slide_id)
        plan_rows.append(
            {
                "slide_id": slide_id,
                "card_number": slide.get("card_number"),
                "motion_type": "static",
                "motion_brief": None,
                "guidance_notes": None,
                "motion_asset_path": None,
                "motion_source": None,
                "motion_duration_seconds": None,
                "motion_status": None,
                "estimated_credits": 0.0,
            }
        )

    budget = _base_budget(motion_budget, require_max_credits=motion_enabled)
    return {
        "motion_plan_version": 1,
        "run_id": authorized_storyboard.get("run_id"),
        "motion_enabled": motion_enabled,
        "motion_budget": budget,
        "summary": {
            "static": len(plan_rows),
            "video": 0,
            "animation": 0,
            "estimated_credits": 0.0,
            "credits_consumed": 0.0,
        },
        "slides": plan_rows,
    }


def apply_motion_designations(
    motion_plan: dict[str, Any],
    designations: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Apply Gate 2M designations to the run-scoped motion plan."""
    plan = deepcopy(motion_plan)
    if not plan.get("motion_enabled", False):
        return plan

    budget = _base_budget(plan.get("motion_budget"), require_max_credits=bool(plan.get("motion_enabled", False)))
    known_slide_ids = {
        str(row.get("slide_id") or "").strip()
        for row in plan.get("slides", [])
        if isinstance(row, dict)
    }
    unknown_designations = sorted(set(designations) - known_slide_ids)
    if unknown_designations:
        raise MotionPlanError(
            "Gate 2M designation payload contains unknown slide_id values: "
            + ", ".join(unknown_designations)
        )
    static_count = 0
    video_count = 0
    animation_count = 0
    estimated_credits = 0.0

    for row in plan.get("slides", []):
        slide_id = str(row.get("slide_id") or "").strip()
        choice = designations.get(slide_id, {})
        motion_type = str(choice.get("motion_type") or "static").strip().lower() or "static"
        if motion_type not in MOTION_TYPES:
            raise MotionPlanError(
                f"slide {slide_id}: motion_type must be one of {sorted(MOTION_TYPES)}"
            )

        row["motion_type"] = motion_type
        row["motion_brief"] = choice.get("motion_brief")
        row["guidance_notes"] = choice.get("guidance_notes")
        row["motion_status"] = "pending" if motion_type != "static" else None
        row["motion_source"] = (
            "kling" if motion_type == "video" else "manual" if motion_type == "animation" else None
        )
        row["motion_duration_seconds"] = choice.get("motion_duration_seconds")
        row["motion_asset_path"] = choice.get("motion_asset_path")

        if motion_type == "static":
            row["estimated_credits"] = 0.0
            static_count += 1
            continue

        duration_seconds = row["motion_duration_seconds"]
        if not isinstance(duration_seconds, (int, float)) or float(duration_seconds) <= 0:
            duration_seconds = 5.0 if motion_type == "video" else 6.0
            row["motion_duration_seconds"] = duration_seconds

        if motion_type == "video":
            credits = estimate_motion_credits(float(duration_seconds), budget["model_preference"])
            row["estimated_credits"] = credits
            estimated_credits += credits
            video_count += 1
        else:
            row["estimated_credits"] = 0.0
            animation_count += 1

    plan["summary"] = {
        "static": static_count,
        "video": video_count,
        "animation": animation_count,
        "estimated_credits": round(estimated_credits, 2),
        "credits_consumed": float(plan.get("summary", {}).get("credits_consumed", 0.0) or 0.0),
    }
    max_credits = budget.get("max_credits")
    if isinstance(max_credits, (int, float)) and estimated_credits > float(max_credits):
        raise MotionPlanError(
            "Gate 2M designation payload exceeds motion_budget.max_credits "
            f"(estimated={round(estimated_credits, 2)}, max_credits={float(max_credits)})"
        )
    return plan


def route_motion_assignments(motion_plan: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Return static/video/animation routing buckets from a plan."""
    routing = {"static": [], "video": [], "animation": []}
    for row in motion_plan.get("slides", []):
        if not isinstance(row, dict):
            continue
        motion_type = str(row.get("motion_type") or "static").strip().lower() or "static"
        routing.setdefault(motion_type, [])
        routing[motion_type].append(row)
    return routing


def load_motion_plan(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def write_motion_plan(path: str | Path, motion_plan: dict[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(motion_plan, sort_keys=False), encoding="utf-8")
    return target


def _load_yaml(path: str | Path) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise MotionPlanError(f"expected mapping in {path}")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage Gate 2M motion plans.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser(
        "build", help="Build a motion plan from an authorized storyboard."
    )
    build_parser.add_argument("--authorized-storyboard", required=True, type=Path)
    build_parser.add_argument("--output", required=True, type=Path)
    build_parser.add_argument("--motion-enabled", action="store_true")
    build_parser.add_argument("--motion-budget-max-credits", type=float, default=None)
    build_parser.add_argument("--motion-budget-model-preference", default="std")

    apply_parser = subparsers.add_parser(
        "apply", help="Apply Gate 2M designations to an existing motion plan."
    )
    apply_parser.add_argument("--motion-plan", required=True, type=Path)
    apply_parser.add_argument("--designations", required=True, type=Path)
    apply_parser.add_argument("--output", required=True, type=Path)

    route_parser = subparsers.add_parser(
        "route", help="Print routing buckets for an existing motion plan."
    )
    route_parser.add_argument("--motion-plan", required=True, type=Path)

    args = parser.parse_args(argv)

    try:
        if args.command == "build":
            authorized_storyboard = _load_yaml(args.authorized_storyboard)
            motion_plan = build_motion_plan_from_authorized_storyboard(
                authorized_storyboard,
                motion_enabled=bool(args.motion_enabled),
                motion_budget={
                    "max_credits": args.motion_budget_max_credits,
                    "model_preference": args.motion_budget_model_preference,
                },
            )
            output = write_motion_plan(args.output, motion_plan)
            print(json.dumps({"status": "ok", "motion_plan": str(output)}, indent=2))
            return 0

        if args.command == "apply":
            motion_plan = load_motion_plan(args.motion_plan)
            designations = _load_yaml(args.designations)
            updated = apply_motion_designations(motion_plan, designations)
            output = write_motion_plan(args.output, updated)
            print(json.dumps({"status": "ok", "motion_plan": str(output)}, indent=2))
            return 0

        if args.command == "route":
            motion_plan = load_motion_plan(args.motion_plan)
            print(json.dumps(route_motion_assignments(motion_plan), indent=2))
            return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
