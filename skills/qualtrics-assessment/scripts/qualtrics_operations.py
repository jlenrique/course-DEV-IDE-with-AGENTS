# /// script
# requires-python = ">=3.10"
# ///
"""Qualtrics assessment orchestration for the Assessment Architect.

This script validates assessment plans, enforces objective-to-item traceability,
and executes Qualtrics survey/question creation through the shared QualtricsClient.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from scripts.api_clients.qualtrics_client import QualtricsClient

PROJECT_ROOT = Path(__file__).resolve().parents[3]
STYLE_GUIDE_PATH = PROJECT_ROOT / "state" / "config" / "style_guide.yaml"


class AssessmentValidationError(Exception):
    """Raised when an assessment plan fails objective-trace validation."""


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _load_style_defaults() -> dict[str, Any]:
    if not STYLE_GUIDE_PATH.exists():
        return {}
    raw = yaml.safe_load(STYLE_GUIDE_PATH.read_text(encoding="utf-8")) or {}
    return raw.get("tool_parameters", {}).get("qualtrics", {})


def load_assessment_plan(plan_path: Path | str) -> dict[str, Any]:
    path = Path(plan_path)
    if not path.exists():
        raise FileNotFoundError(f"Assessment plan not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _normalize_objective_map(objectives: list[dict[str, Any]]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for index, objective in enumerate(objectives, start=1):
        if not isinstance(objective, dict):
            raise AssessmentValidationError(
                f"objectives[{index}] must be an object"
            )
        objective_id = str(objective.get("id", "")).strip()
        objective_text = str(objective.get("text", "")).strip()
        if not objective_id:
            raise AssessmentValidationError(
                f"objectives[{index}] requires non-empty 'id'"
            )
        if not objective_text:
            raise AssessmentValidationError(
                f"objectives[{index}] requires non-empty 'text'"
            )
        if objective_id in normalized:
            raise AssessmentValidationError(
                f"Duplicate objective id detected: {objective_id}"
            )
        normalized[objective_id] = objective_text
    return normalized


def validate_assessment_plan(plan: dict[str, Any]) -> dict[str, Any]:
    survey_name = str(plan.get("survey_name", "")).strip()
    if not survey_name:
        raise AssessmentValidationError("Assessment plan requires non-empty survey_name")

    objectives_raw = plan.get("objectives")
    if not isinstance(objectives_raw, list) or not objectives_raw:
        raise AssessmentValidationError("Assessment plan requires non-empty objectives list")
    objectives = _normalize_objective_map(objectives_raw)

    questions = plan.get("questions")
    if not isinstance(questions, list) or not questions:
        raise AssessmentValidationError("Assessment plan requires non-empty questions list")

    objective_hits = {objective_id: 0 for objective_id in objectives}

    for q_index, question in enumerate(questions, start=1):
        if not isinstance(question, dict):
            raise AssessmentValidationError(f"questions[{q_index}] must be an object")

        prompt = str(question.get("prompt", "")).strip()
        if not prompt:
            raise AssessmentValidationError(
                f"questions[{q_index}] requires non-empty prompt"
            )

        objective_id = str(question.get("learning_objective_id", "")).strip()
        if not objective_id:
            raise AssessmentValidationError(
                f"questions[{q_index}] requires learning_objective_id"
            )
        if objective_id not in objectives:
            raise AssessmentValidationError(
                f"questions[{q_index}] references unknown learning_objective_id '{objective_id}'"
            )

        objective_hits[objective_id] += 1

    uncovered = [obj_id for obj_id, count in objective_hits.items() if count == 0]
    if uncovered:
        raise AssessmentValidationError(
            f"Objectives without mapped questions: {uncovered}"
        )

    return {
        "survey_name": survey_name,
        "objective_hits": objective_hits,
        "objective_count": len(objectives),
        "question_count": len(questions),
    }


def _choice_payload(question: dict[str, Any]) -> dict[str, dict[str, str]] | None:
    choices = question.get("choices")
    if choices is None:
        return None

    if isinstance(choices, dict):
        normalized: dict[str, dict[str, str]] = {}
        for key, value in choices.items():
            normalized[str(key)] = {
                "Display": str(value.get("Display", "")) if isinstance(value, dict) else str(value)
            }
        return normalized

    if isinstance(choices, list):
        normalized = {}
        for idx, choice in enumerate(choices, start=1):
            normalized[str(idx)] = {"Display": str(choice)}
        return normalized

    raise AssessmentValidationError("Question choices must be dict, list, or omitted")


def _question_shape(question: dict[str, Any]) -> tuple[str, str]:
    question_type = str(question.get("type", "multiple_choice")).strip().lower()

    if question_type in {"multiple_choice", "mc", "single_choice"}:
        return "MC", "SAVR"
    if question_type in {"multiple_answer", "multi_answer", "mavr"}:
        return "MC", "MAVR"
    if question_type in {"text", "text_entry", "te"}:
        return "TE", "SL"
    if question_type in {"matrix", "likert"}:
        return "Matrix", "Likert"

    raise AssessmentValidationError(f"Unsupported question type: {question_type}")


def _objective_trace(plan: dict[str, Any], objective_hits: dict[str, int]) -> list[dict[str, Any]]:
    objective_text = {
        str(item["id"]): str(item["text"])
        for item in plan.get("objectives", [])
        if isinstance(item, dict)
    }
    trace: list[dict[str, Any]] = []
    for objective_id, count in objective_hits.items():
        trace.append(
            {
                "learning_objective_id": objective_id,
                "objective_text": objective_text.get(objective_id, ""),
                "question_count": count,
            }
        )
    return trace


def create_assessment_from_plan(
    plan: dict[str, Any],
    *,
    dry_run: bool = False,
    client_factory=QualtricsClient,
) -> dict[str, Any]:
    validation = validate_assessment_plan(plan)
    style_defaults = _load_style_defaults()

    language = str(
        plan.get(
            "language",
            style_defaults.get("default_survey_language", "EN"),
        )
    ).strip() or "EN"

    warnings: list[str] = []

    # Dry-run must validate the same question shape constraints as execute mode.
    for question in plan.get("questions", []):
        _question_shape(question)
        _choice_payload(question)

    if dry_run:
        return {
            "status": "dry-run",
            "survey_id": None,
            "survey_name": validation["survey_name"],
            "style": {
                "language": language,
                "question_numbering": bool(style_defaults.get("question_numbering", True)),
                "progress_bar": bool(style_defaults.get("progress_bar", True)),
            },
            "objective_trace": _objective_trace(plan, validation["objective_hits"]),
            "created_question_ids": [],
            "warnings": warnings,
            "errors": [],
            "timestamp": _now_iso(),
        }

    client = client_factory()

    survey = client.create_survey(validation["survey_name"], language=language)
    survey_id = str(survey.get("id") or survey.get("SurveyID") or "").strip()
    if not survey_id:
        raise AssessmentValidationError(
            "Qualtrics create_survey response missing survey identifier"
        )

    if hasattr(client, "update_survey_options"):
        try:
            client.update_survey_options(
                survey_id,
                question_numbering=bool(style_defaults.get("question_numbering", True)),
                progress_bar=bool(style_defaults.get("progress_bar", True)),
            )
        except Exception as exc:  # pragma: no cover - best-effort compatibility
            warnings.append(f"Could not apply survey option defaults: {exc}")

    created_question_ids: list[str] = []

    for question in plan.get("questions", []):
        q_type, selector = _question_shape(question)
        created = client.create_question(
            survey_id,
            question_text=str(question["prompt"]),
            question_type=q_type,
            selector=selector,
            choices=_choice_payload(question),
        )
        created_id = str(created.get("QuestionID") or created.get("id") or "").strip()
        if created_id:
            created_question_ids.append(created_id)
        else:
            warnings.append("Question created but response did not include QuestionID")

    return {
        "status": "created",
        "survey_id": survey_id,
        "survey_name": validation["survey_name"],
        "style": {
            "language": language,
            "question_numbering": bool(style_defaults.get("question_numbering", True)),
            "progress_bar": bool(style_defaults.get("progress_bar", True)),
        },
        "objective_trace": _objective_trace(plan, validation["objective_hits"]),
        "created_question_ids": created_question_ids,
        "warnings": warnings,
        "errors": [],
        "timestamp": _now_iso(),
    }


def create_assessment_from_plan_file(
    plan_path: Path | str,
    *,
    dry_run: bool = False,
    output_path: Path | str | None = None,
) -> dict[str, Any]:
    plan = load_assessment_plan(plan_path)
    result = create_assessment_from_plan(plan, dry_run=dry_run)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Qualtrics assessment operations")
    parser.add_argument("--plan", required=True, help="Path to assessment plan YAML")
    parser.add_argument("--dry-run", action="store_true", help="Validate and preview only")
    parser.add_argument("--output", help="Optional JSON output path")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    try:
        result = create_assessment_from_plan_file(
            args.plan,
            dry_run=args.dry_run,
            output_path=args.output,
        )
    except (FileNotFoundError, AssessmentValidationError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}))
        raise SystemExit(2) from exc

    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result.get("status") in {"created", "dry-run"} else 1)


if __name__ == "__main__":
    main()
