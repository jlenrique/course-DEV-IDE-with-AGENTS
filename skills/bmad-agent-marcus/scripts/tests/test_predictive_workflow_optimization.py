"""Tests for predictive_workflow_optimization.py (Story 10.1)."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "predictive_workflow_optimization.py"
SPEC = importlib.util.spec_from_file_location("predictive_workflow_optimization", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _context(stages: list[dict[str, str]], mode: str = "default") -> str:
    return json.dumps({"mode": mode, "stages": stages})


class TestPredictiveWorkflowOptimization(unittest.TestCase):
    def test_predictive_recommendation_uses_similar_runs_and_excludes_ad_hoc(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "coordination.db"
            conn = sqlite3.connect(str(db_path))
            conn.executescript(
                """
                CREATE TABLE production_runs (
                    run_id TEXT PRIMARY KEY,
                    purpose TEXT NOT NULL,
                    status TEXT NOT NULL,
                    preset TEXT NOT NULL,
                    context_json TEXT,
                    course_code TEXT,
                    module_id TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );
                """
            )

            stages_fast = [
                {
                    "stage": "draft",
                    "specialist": "content-creator",
                    "stage_started_at": "2026-01-01T00:00:00",
                    "stage_completed_at": "2026-01-01T00:10:00",
                },
                {
                    "stage": "review",
                    "specialist": "quality-reviewer",
                    "stage_started_at": "2026-01-01T00:10:00",
                    "stage_completed_at": "2026-01-01T00:35:00",
                },
                {
                    "stage": "publish",
                    "specialist": "canvas-specialist",
                    "stage_started_at": "2026-01-01T00:35:00",
                    "stage_completed_at": "2026-01-01T00:40:00",
                },
            ]
            stages_slow = [
                {
                    "stage": "draft",
                    "specialist": "content-creator",
                    "stage_started_at": "2026-01-02T00:00:00",
                    "stage_completed_at": "2026-01-02T00:12:00",
                },
                {
                    "stage": "review",
                    "specialist": "quality-reviewer",
                    "stage_started_at": "2026-01-02T00:12:00",
                    "stage_completed_at": "2026-01-02T00:45:00",
                },
                {
                    "stage": "publish",
                    "specialist": "canvas-specialist",
                    "stage_started_at": "2026-01-02T00:45:00",
                    "stage_completed_at": "2026-01-02T00:50:00",
                },
            ]

            rows = [
                (
                    "RUN-1",
                    "prod",
                    "completed",
                    "production",
                    _context(stages_fast, mode="default"),
                    "C1",
                    "M1",
                    "2026-01-01T00:00:00",
                    "2026-01-01T00:40:00",
                    "2026-01-01T00:00:00",
                    "2026-01-01T00:40:00",
                ),
                (
                    "RUN-2",
                    "prod",
                    "completed",
                    "production",
                    _context(stages_slow, mode="default"),
                    "C1",
                    "M1",
                    "2026-01-02T00:00:00",
                    "2026-01-02T00:50:00",
                    "2026-01-02T00:00:00",
                    "2026-01-02T00:50:00",
                ),
                (
                    "RUN-ADHOC",
                    "sandbox",
                    "completed",
                    "production",
                    _context(stages_fast, mode="ad-hoc"),
                    "C1",
                    "M1",
                    "2026-01-03T00:00:00",
                    "2026-01-03T00:40:00",
                    "2026-01-03T00:00:00",
                    "2026-01-03T00:40:00",
                ),
            ]

            conn.executemany(
                """
                INSERT INTO production_runs
                (
                    run_id,
                    purpose,
                    status,
                    preset,
                    context_json,
                    course_code,
                    module_id,
                    started_at,
                    completed_at,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            conn.commit()
            conn.close()

            result = MODULE.suggest_predictive_workflow(
                run_context={
                    "course_code": "C1",
                    "module_id": "M1",
                    "preset": "production",
                },
                db_path=db_path,
                write_report=False,
            )

            self.assertEqual(result["similar_runs_considered"], 2)
            self.assertEqual(result["ad_hoc_runs_excluded"], 1)
            self.assertEqual(
                result["workflow_sequence_recommendation"]["recommended_sequence"],
                ["draft", "review", "publish"],
            )
            self.assertEqual(result["predicted_bottlenecks"][0]["stage"], "review")
            self.assertEqual(set(result["options"].keys()), {"accept", "modify", "override"})

    def test_predictive_recommendation_falls_back_when_db_missing(self) -> None:
        result = MODULE.suggest_predictive_workflow(
            run_context={
                "course_code": "C9",
                "module_id": "M9",
                "preset": "production",
                "stages": [
                    {"stage": "draft"},
                    {"stage": "review"},
                ],
            },
            db_path=Path("missing-file.db"),
            write_report=False,
        )

        self.assertEqual(result["similar_runs_considered"], 0)
        self.assertEqual(
            result["workflow_sequence_recommendation"]["recommended_sequence"],
            ["draft", "review"],
        )
        self.assertEqual(result["workflow_sequence_recommendation"]["confidence"], "low")


if __name__ == "__main__":
    unittest.main()
