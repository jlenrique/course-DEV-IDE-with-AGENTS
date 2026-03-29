"""Unit tests for the Canvas woodshed snapshot helper."""

from __future__ import annotations

from scripts.api_clients import canvas_client as module


class _NoCourseClient:
    def list_courses(self, **params):
        if False:  # pragma: no cover
            yield {}


class _HappyClient:
    def list_courses(self, **params):
        yield {"id": 77, "name": "Sandbox"}

    def get_course(self, course_id):
        return {"id": course_id, "name": "Sandbox"}

    def list_modules(self, course_id, **params):
        yield {"id": 1, "name": "Module A"}
        yield {"id": 2, "name": "Module B"}

    def list_pages(self, course_id, **params):
        yield {"id": 10}

    def list_assignments(self, course_id, **params):
        yield {"id": 20}
        yield {"id": 21}

    def list_quizzes(self, course_id, **params):
        yield {"id": 30}


def test_reproduce_course_snapshot_handles_missing_courses(monkeypatch) -> None:
    monkeypatch.setattr(module, "CanvasClient", lambda: _NoCourseClient())

    result = module.reproduce_course_snapshot()

    assert result["status"] == "no-courses"
    assert result["module_count"] == 0


def test_reproduce_course_snapshot_returns_counts(monkeypatch) -> None:
    monkeypatch.setattr(module, "CanvasClient", lambda: _HappyClient())

    result = module.reproduce_course_snapshot()

    assert result["status"] == "ok"
    assert result["course"]["id"] == 77
    assert result["module_count"] == 2
    assert result["page_count"] == 1
    assert result["assignment_count"] == 2
    assert result["quiz_count"] == 1


def test_reproduce_course_snapshot_rejects_empty_course_id(monkeypatch) -> None:
    monkeypatch.setattr(module, "CanvasClient", lambda: _HappyClient())

    result = module.reproduce_course_snapshot(course_id="   ")

    assert result["status"] == "error"
    assert "empty" in result["reason"]
