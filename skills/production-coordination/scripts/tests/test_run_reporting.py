# /// script
# requires-python = ">=3.10"
# ///
"""Tests for run_reporting.py."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import run_reporting


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS production_runs (
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

CREATE TABLE IF NOT EXISTS quality_gates (
    gate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    status TEXT NOT NULL,
    reviewer TEXT,
    findings_json TEXT,
    score REAL,
    decided_at TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS agent_coordination (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    action TEXT NOT NULL,
    payload_json TEXT,
    timestamp TEXT
);

CREATE TABLE IF NOT EXISTS observability_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    gate TEXT,
    run_mode TEXT NOT NULL,
    fidelity_o_count INTEGER,
    fidelity_i_count INTEGER,
    fidelity_a_count INTEGER,
    quality_scores_json TEXT,
    agent_metrics_json TEXT,
    payload_json TEXT,
    created_at TEXT NOT NULL
);
"""


class TempDB:
    def __init__(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.path = Path(self._tmp.name)
        self._tmp.close()

    def __enter__(self) -> "TempDB":
        conn = sqlite3.connect(str(self.path))
        conn.executescript(SCHEMA_SQL)

        context = {
            "mode": "default",
            "stages": [
                {
                    "stage": "draft",
                    "status": "approved",
                    "stage_started_at": "2026-01-01T00:00:00",
                    "stage_completed_at": "2026-01-01T00:10:00",
                },
                {
                    "stage": "review",
                    "status": "approved",
                    "stage_started_at": "2026-01-01T00:10:00",
                    "stage_completed_at": "2026-01-01T00:25:00",
                },
            ],
        }
        conn.execute(
            """
            INSERT INTO production_runs
            (run_id, purpose, status, preset, context_json, course_code, module_id, started_at, completed_at, created_at, updated_at)
            VALUES ('RUN-REP', 'report test', 'completed', 'production', ?, 'C1', 'M1', '2026-01-01T00:00:00', '2026-01-01T00:25:00', '2026-01-01T00:00:00', '2026-01-01T00:25:00')
            """,
            (json.dumps(context),),
        )
        conn.execute(
            """
            INSERT INTO production_runs
            (run_id, purpose, status, preset, context_json, course_code, module_id, started_at, completed_at, created_at, updated_at)
            VALUES ('RUN-BASE', 'baseline', 'completed', 'draft', '{"mode": "default"}', 'C1', 'M1', '2026-01-01T00:00:00', '2026-01-01T00:30:00', '2026-01-01T00:00:00', '2026-01-01T00:30:00')
            """
        )
        conn.execute(
            """
            INSERT INTO production_runs
            (run_id, purpose, status, preset, context_json, course_code, module_id, started_at, completed_at, created_at, updated_at)
            VALUES ('RUN-ADHOC', 'sandbox', 'completed', 'draft', '{"mode": "ad-hoc"}', 'C1', 'M1', '2026-01-01T00:00:00', '2026-01-01T00:05:00', '2026-01-01T00:00:00', '2026-01-01T00:05:00')
            """
        )

        conn.execute(
            """
            INSERT INTO quality_gates (run_id, stage, status, reviewer, score, decided_at, created_at)
            VALUES ('RUN-REP', 'review', 'pass', 'quinn-r', 0.95, '2026-01-01T00:24:00', '2026-01-01T00:24:00')
            """
        )
        conn.execute(
            """
            INSERT INTO agent_coordination (run_id, agent_name, action, payload_json, timestamp)
            VALUES ('RUN-REP', 'gamma-specialist', 'completed', '{}', '2026-01-01T00:20:00')
            """
        )
        conn.execute(
            """
            INSERT INTO observability_events
            (run_id, event_type, gate, run_mode, fidelity_o_count, fidelity_i_count, fidelity_a_count, quality_scores_json, agent_metrics_json, payload_json, created_at)
            VALUES ('RUN-REP', 'gate_result', 'review', 'default', 0, 0, 0, '{"reviewer": 0.95}', '{}', '{"passed": true}', '2026-01-01T00:24:00')
            """
        )

        conn.commit()
        conn.close()
        return self

    def __exit__(self, *args: object) -> None:
        self.path.unlink(missing_ok=True)


class TestRunReporting(unittest.TestCase):
    def test_generate_report(self) -> None:
        with TempDB() as db:
            report = run_reporting.generate_run_report(
                run_id="RUN-REP",
                db_path=db.path,
                write_report=False,
                capture_learning=False,
            )
            self.assertEqual(report["run_id"], "RUN-REP")
            self.assertEqual(report["status"], "completed")
            self.assertGreater(len(report["stage_metrics"]), 0)
            self.assertGreaterEqual(report["quality_gate_results"]["count"], 1)
            self.assertTrue(report["comparative_analysis"]["ad_hoc_excluded"])
            self.assertEqual(report["comparative_analysis"]["baseline_count"], 1)

    def test_capture_learning_handles_empty_lists(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            report = {
                "run_id": "RUN-EMPTY",
                "bottlenecks": [],
                "observability": {},
                "optimization_recommendations": [],
            }

            with patch.object(run_reporting, "project_root", return_value=Path(td)):
                with patch.object(
                    run_reporting,
                    "enforce_ad_hoc_boundary",
                    return_value={"allowed": True, "code": "ALLOWED_DEFAULT_MODE", "reason": "ok"},
                ):
                    result = run_reporting._capture_learning_insights(report, "default")

            self.assertTrue(result["captured"])
            target = Path(result["path"])
            self.assertTrue(target.exists())
            contents = target.read_text(encoding="utf-8")
            self.assertIn("Longest stage: n/a", contents)
            self.assertIn("Recommendation: n/a", contents)


if __name__ == "__main__":
    unittest.main()
