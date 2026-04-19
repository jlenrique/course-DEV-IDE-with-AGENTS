"""Contract tests for Story 31-5 log-boundary discipline."""

from __future__ import annotations

from pathlib import Path


def test_quinn_r_gate_does_not_call_lesson_plan_log_write_surface() -> None:
    module_text = Path("marcus/lesson_plan/quinn_r_gate.py").read_text(encoding="utf-8")
    forbidden_tokens = [
        "LessonPlanLog",
        "append_event(",
        "write_event(",
        "emit_fit_report(",
        "from marcus.lesson_plan.log import",
    ]
    for token in forbidden_tokens:
        assert token not in module_text

