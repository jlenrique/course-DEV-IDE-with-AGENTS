"""Tests for canvas_operations.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "canvas_operations.py"
SPEC = importlib.util.spec_from_file_location("canvas_operations", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class _PassingChecker:
    @staticmethod
    def run_accessibility_check(content: str, target_grade: float = 12.0) -> dict:
        return {
            "status": "pass",
            "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
            "findings": [],
            "reading_level": min(target_grade, 10.0),
        }


class _FailingChecker:
    @staticmethod
    def run_accessibility_check(content: str, target_grade: float = 12.0) -> dict:
        return {
            "status": "fail",
            "summary": {"total": 1, "critical": 1, "high": 0, "medium": 0, "low": 0},
            "findings": [
                {
                    "severity": "critical",
                    "location": "line 1",
                    "description": "Image reference missing alt text",
                    "fix_suggestion": "Add alt text",
                }
            ],
        }


class FakeCanvasClient:
    def __init__(self, fail_on_module_item: bool = False) -> None:
        self.base_url = "https://canvas.example/api/v1"
        self._next_id = 100
        self._modules: list[dict] = []
        self._assignments: list[dict] = []
        self._deletes: list[str] = []
        self.fail_on_module_item = fail_on_module_item

    def _id(self) -> int:
        self._next_id += 1
        return self._next_id

    def get_self(self) -> dict:
        return {"id": 1, "name": "Canvas Bot"}

    def list_courses(self):
        yield {"id": 9001, "name": "Sandbox"}

    def create_module(self, course_id, name, position=None, require_sequential_progress=False):
        module = {"id": self._id(), "name": name}
        self._modules.append(module)
        return module

    def create_page(self, course_id, title, body, published=False, editing_roles="teachers"):
        page_id = self._id()
        return {"id": page_id, "url": f"page-{page_id}", "title": title}

    def create_assignment(
        self,
        course_id,
        name,
        submission_types=None,
        points_possible=None,
        description="",
        published=False,
    ):
        assignment = {"id": self._id(), "name": name}
        self._assignments.append(assignment)
        return assignment

    def post(self, endpoint, data=None, **kwargs):
        if endpoint.endswith("/discussion_topics"):
            return {"id": self._id(), "title": data.get("title")}
        if "/modules/" in endpoint and endpoint.endswith("/items"):
            if self.fail_on_module_item:
                raise MODULE.APIError("module item create failed")
            return {"id": self._id()}
        raise AssertionError(f"Unexpected endpoint: {endpoint}")

    def list_modules(self, course_id, **params):
        yield from self._modules

    def delete(self, endpoint, **kwargs):
        self._deletes.append(endpoint)
        return {}


class FailDeleteCanvasClient(FakeCanvasClient):
    def delete(self, endpoint, **kwargs):
        if "/modules/" in endpoint:
            raise MODULE.APIError("module delete failed")
        return super().delete(endpoint, **kwargs)


def sample_manifest() -> dict:
    return {
        "course_id": 42,
        "modules": [
            {
                "name": "Module A",
                "require_sequential_progress": True,
                "pages": [
                    {
                        "title": "Welcome",
                        "body": "# Heading\nAccessible instructional content.",
                    }
                ],
                "assignments": [
                    {
                        "name": "Quiz 1",
                        "description": "Learner check-in prompt",
                        "submission_types": ["online_text_entry"],
                        "points_possible": 10,
                    }
                ],
                "discussions": [
                    {
                        "title": "Discussion 1",
                        "message": "# Prompt\nShare your approach.",
                    }
                ],
            }
        ],
    }


def test_validate_manifest_requires_modules() -> None:
    with pytest.raises(MODULE.DeploymentError):
        MODULE.validate_manifest({})


def test_validate_manifest_rejects_duplicate_module_names() -> None:
    manifest = {
        "course_id": 42,
        "modules": [{"name": "Module A"}, {"name": "Module A"}],
    }

    with pytest.raises(MODULE.DeploymentError):
        MODULE.validate_manifest(manifest)


def test_accessibility_gate_blocks_deployment(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeCanvasClient()
    monkeypatch.setattr(MODULE, "CanvasClient", lambda: fake)
    monkeypatch.setattr(MODULE, "_load_accessibility_checker", lambda: _FailingChecker)

    result = MODULE.deploy_manifest(sample_manifest())

    assert result["status"] == "blocked"
    assert "Accessibility pre-check failed" in result["reason"]


def test_dry_run_returns_confirmation_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeCanvasClient()
    monkeypatch.setattr(MODULE, "CanvasClient", lambda: fake)
    monkeypatch.setattr(MODULE, "_load_accessibility_checker", lambda: _PassingChecker)

    result = MODULE.deploy_manifest(sample_manifest(), dry_run=True)

    assert result["status"] == "dry-run"
    assert result["confirmation_urls"]["course"].endswith("/courses/42")


def test_deploy_success_creates_entities(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeCanvasClient()
    monkeypatch.setattr(MODULE, "CanvasClient", lambda: fake)
    monkeypatch.setattr(MODULE, "_load_accessibility_checker", lambda: _PassingChecker)

    result = MODULE.deploy_manifest(sample_manifest())

    assert result["status"] == "deployed"
    assert result["created"]["modules"]
    assert result["created"]["pages"]
    assert result["created"]["assignments"]
    assert result["created"]["discussions"]
    assert result["module_structure_verification"]["status"] == "pass"


def test_course_id_falls_back_to_first_course(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeCanvasClient()
    monkeypatch.setattr(MODULE, "CanvasClient", lambda: fake)
    monkeypatch.setattr(MODULE, "_load_accessibility_checker", lambda: _PassingChecker)

    manifest = sample_manifest()
    manifest.pop("course_id")
    monkeypatch.setattr(MODULE, "_load_style_defaults", lambda: {})

    result = MODULE.deploy_manifest(manifest, dry_run=True)

    assert result["course_id"] == 9001


def test_scope_check_can_block_deploy(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeCanvasClient()
    monkeypatch.setattr(MODULE, "CanvasClient", lambda: fake)
    monkeypatch.setattr(MODULE, "_load_accessibility_checker", lambda: _PassingChecker)
    monkeypatch.setenv("CANVAS_REQUIRED_SCOPES", "courses:read,courses:write")
    monkeypatch.setenv("CANVAS_TOKEN_SCOPES", "courses:read")

    result = MODULE.deploy_manifest(sample_manifest())

    assert result["status"] == "blocked"
    assert result["scope_check"]["status"] == "fail"


def test_failure_triggers_rollback(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeCanvasClient(fail_on_module_item=True)
    monkeypatch.setattr(MODULE, "CanvasClient", lambda: fake)
    monkeypatch.setattr(MODULE, "_load_accessibility_checker", lambda: _PassingChecker)

    result = MODULE.deploy_manifest(sample_manifest())

    assert result["status"] == "failed"
    assert result["rollback"]["attempted"] >= 1


def test_verify_module_structure_detects_missing_module(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeCanvasClient()
    fake._modules = [{"id": 1, "name": "Only Module"}]
    result = MODULE.verify_module_structure(fake, 42, ["Only Module", "Missing Module"])

    assert result["status"] == "fail"
    assert "Missing Module" in result["missing_modules"]


def test_verify_module_structure_detects_out_of_order() -> None:
    fake = FakeCanvasClient()
    fake._modules = [
        {"id": 1, "name": "Module B"},
        {"id": 2, "name": "Module A"},
    ]

    result = MODULE.verify_module_structure(fake, 42, ["Module A", "Module B"])

    assert result["status"] == "fail"
    assert result["in_order"] is False


def test_rollback_partial_failures_are_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FailDeleteCanvasClient(fail_on_module_item=True)
    monkeypatch.setattr(MODULE, "CanvasClient", lambda: fake)
    monkeypatch.setattr(MODULE, "_load_accessibility_checker", lambda: _PassingChecker)

    result = MODULE.deploy_manifest(sample_manifest())

    assert result["status"] == "failed"
    assert result["rollback"]["failed"] >= 1
