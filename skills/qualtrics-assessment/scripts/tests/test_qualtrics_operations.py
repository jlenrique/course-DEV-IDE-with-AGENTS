"""Tests for qualtrics_operations.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "qualtrics_operations.py"
SPEC = importlib.util.spec_from_file_location("qualtrics_operations", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def sample_plan() -> dict:
    return {
        "survey_name": "Module 01 Knowledge Check",
        "objectives": [
            {"id": "LO1", "text": "Identify key concepts"},
            {"id": "LO2", "text": "Apply concepts to scenarios"},
        ],
        "questions": [
            {
                "type": "multiple_choice",
                "prompt": "Which option best describes concept A?",
                "choices": ["Option 1", "Option 2", "Option 3"],
                "learning_objective_id": "LO1",
            },
            {
                "type": "text_entry",
                "prompt": "Describe one practical application.",
                "learning_objective_id": "LO2",
            },
        ],
    }


class _FakeQualtricsClient:
    def __init__(self) -> None:
        self.created_surveys: list[dict] = []
        self.created_questions: list[dict] = []
        self.updated_options: list[dict] = []

    def create_survey(
        self,
        name: str,
        *,
        language: str = "EN",
        project_category: str = "CORE",
    ) -> dict:
        self.created_surveys.append(
            {
                "name": name,
                "language": language,
                "project_category": project_category,
            }
        )
        return {"SurveyID": "SV_TEST_1", "name": name}

    def create_question(
        self,
        survey_id: str,
        question_text: str,
        question_type: str = "MC",
        *,
        choices=None,
        selector: str = "SAVR",
    ) -> dict:
        self.created_questions.append(
            {
                "survey_id": survey_id,
                "question_text": question_text,
                "question_type": question_type,
                "selector": selector,
                "choices": choices,
            }
        )
        return {"QuestionID": f"QID{len(self.created_questions)}"}

    def update_survey_options(
        self,
        survey_id: str,
        *,
        question_numbering: bool = True,
        progress_bar: bool = True,
    ) -> dict:
        self.updated_options.append(
            {
                "survey_id": survey_id,
                "question_numbering": question_numbering,
                "progress_bar": progress_bar,
            }
        )
        return {"ok": True}


def test_validate_rejects_unknown_objective() -> None:
    plan = sample_plan()
    plan["questions"][0]["learning_objective_id"] = "MISSING"

    with pytest.raises(MODULE.AssessmentValidationError):
        MODULE.validate_assessment_plan(plan)


def test_dry_run_skips_api_calls() -> None:
    plan = sample_plan()

    def _factory():
        raise AssertionError("Client factory should not be called in dry-run")

    result = MODULE.create_assessment_from_plan(plan, dry_run=True, client_factory=_factory)

    assert result["status"] == "dry-run"
    assert result["survey_id"] is None
    assert len(result["objective_trace"]) == 2


def test_create_assessment_calls_client() -> None:
    plan = sample_plan()
    fake = _FakeQualtricsClient()

    result = MODULE.create_assessment_from_plan(
        plan,
        dry_run=False,
        client_factory=lambda: fake,
    )

    assert result["status"] == "created"
    assert result["survey_id"] == "SV_TEST_1"
    assert len(result["created_question_ids"]) == 2
    assert len(fake.created_surveys) == 1
    assert len(fake.created_questions) == 2
    assert len(fake.updated_options) == 1


def test_choices_list_is_normalized() -> None:
    choices = MODULE._choice_payload({"choices": ["A", "B"]})

    assert choices == {
        "1": {"Display": "A"},
        "2": {"Display": "B"},
    }


def test_language_uses_style_default(monkeypatch: pytest.MonkeyPatch) -> None:
    plan = sample_plan()
    fake = _FakeQualtricsClient()

    monkeypatch.setattr(
        MODULE,
        "_load_style_defaults",
        lambda: {
            "default_survey_language": "ES",
            "question_numbering": True,
            "progress_bar": False,
        },
    )

    result = MODULE.create_assessment_from_plan(
        plan,
        dry_run=False,
        client_factory=lambda: fake,
    )

    assert result["style"]["language"] == "ES"
    assert fake.created_surveys[0]["language"] == "ES"


def test_dry_run_rejects_unsupported_question_type() -> None:
    plan = sample_plan()
    plan["questions"][0]["type"] = "unsupported"

    with pytest.raises(MODULE.AssessmentValidationError):
        MODULE.create_assessment_from_plan(plan, dry_run=True)


def test_dry_run_rejects_invalid_choices_type() -> None:
    plan = sample_plan()
    plan["questions"][0]["choices"] = "A,B,C"

    with pytest.raises(MODULE.AssessmentValidationError):
        MODULE.create_assessment_from_plan(plan, dry_run=True)
