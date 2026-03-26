# /// script
# requires-python = ">=3.10"
# ///
"""Tests for manage_run.py — production run lifecycle management.

Self-contained: can run directly with `python test_manage_run.py`.
Uses temporary in-memory SQLite databases.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import manage_run


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS production_runs (
    run_id         TEXT PRIMARY KEY,
    purpose        TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'pending',
    preset         TEXT NOT NULL DEFAULT 'draft',
    context_json   TEXT,
    course_code    TEXT,
    module_id      TEXT,
    started_at     TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at   TEXT,
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS agent_coordination (
    event_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id         TEXT NOT NULL,
    agent_name     TEXT NOT NULL,
    action         TEXT NOT NULL,
    payload_json   TEXT,
    timestamp      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES production_runs(run_id)
);

CREATE TABLE IF NOT EXISTS quality_gates (
    gate_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id         TEXT NOT NULL,
    stage          TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'pending',
    reviewer       TEXT,
    findings_json  TEXT,
    score          REAL,
    decided_at     TEXT,
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES production_runs(run_id)
);
"""

SAMPLE_STAGES = [
    {"stage": "outline", "specialist": "content-creator", "description": "Draft outline"},
    {"stage": "slides", "specialist": "gamma-specialist", "description": "Generate slides"},
    {"stage": "review", "specialist": "quality-reviewer", "description": "Quality review"},
    {"stage": "checkpoint", "specialist": "human", "description": "User approval"},
]


class TempDB:
    """Context manager that provides a temporary SQLite database with schema."""

    def __init__(self) -> None:
        self._tmpfile = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.path = self._tmpfile.name
        self._tmpfile.close()

    def __enter__(self) -> "TempDB":
        conn = sqlite3.connect(self.path)
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        conn.close()
        return self

    def __exit__(self, *args: object) -> None:
        try:
            Path(self.path).unlink(missing_ok=True)
        except OSError:
            pass


def _create_run(db_path: str, run_id: str = "TEST-RUN-001", stages: list | None = None) -> dict:
    """Helper to create a run for testing."""
    stages = stages or SAMPLE_STAGES
    args = [
        "--db", db_path,
        "create",
        "--run-id", run_id,
        "--purpose", "Test production run",
        "--content-type", "lecture-slides",
        "--course", "C1",
        "--module", "M2",
        "--lesson", "L3",
        "--stages-json", json.dumps(stages),
    ]
    ns = manage_run.build_parser().parse_args(args)
    return manage_run.cmd_create(ns)


class TestCreateRun(unittest.TestCase):
    def test_create_basic(self) -> None:
        with TempDB() as db:
            result = _create_run(db.path)
            self.assertEqual(result["run_id"], "TEST-RUN-001")
            self.assertEqual(result["status"], "planning")
            self.assertEqual(result["stages_count"], 4)

    def test_create_auto_id(self) -> None:
        with TempDB() as db:
            args = manage_run.build_parser().parse_args([
                "--db", db.path,
                "create",
                "--content-type", "assessment",
                "--course", "C1",
                "--module", "M3",
            ])
            result = manage_run.cmd_create(args)
            self.assertIn("C1", result["run_id"])
            self.assertIn("M3", result["run_id"])

    def test_create_duplicate_id(self) -> None:
        with TempDB() as db:
            _create_run(db.path, "DUP-001")
            result = _create_run(db.path, "DUP-001")
            self.assertIn("error", result)
            self.assertIn("already exists", result["error"])


class TestAdvanceRun(unittest.TestCase):
    def test_advance_first_stage(self) -> None:
        with TempDB() as db:
            _create_run(db.path)
            args = manage_run.build_parser().parse_args(["--db", db.path, "advance", "TEST-RUN-001"])
            result = manage_run.cmd_advance(args)
            self.assertEqual(result["stage_index"], 1)
            self.assertEqual(result["advanced_to"]["stage"], "slides")
            self.assertEqual(result["status"], "in-progress")

    def test_advance_nonexistent(self) -> None:
        with TempDB() as db:
            args = manage_run.build_parser().parse_args(["--db", db.path, "advance", "NOPE"])
            result = manage_run.cmd_advance(args)
            self.assertIn("error", result)

    def test_advance_past_end(self) -> None:
        with TempDB() as db:
            _create_run(db.path, stages=[{"stage": "only", "specialist": "test"}])
            args = manage_run.build_parser().parse_args(["--db", db.path, "advance", "TEST-RUN-001"])
            result = manage_run.cmd_advance(args)
            self.assertIn("error", result)


class TestCheckpoint(unittest.TestCase):
    def test_checkpoint_current(self) -> None:
        with TempDB() as db:
            _create_run(db.path)
            args = manage_run.build_parser().parse_args(["--db", db.path, "checkpoint", "TEST-RUN-001"])
            result = manage_run.cmd_checkpoint(args)
            self.assertEqual(result["status"], "awaiting-review")

            conn = sqlite3.connect(db.path)
            gates = conn.execute("SELECT * FROM quality_gates WHERE run_id = 'TEST-RUN-001'").fetchall()
            conn.close()
            self.assertEqual(len(gates), 1)


class TestApprove(unittest.TestCase):
    def test_approve_at_checkpoint(self) -> None:
        with TempDB() as db:
            _create_run(db.path)
            cp_args = manage_run.build_parser().parse_args(["--db", db.path, "checkpoint", "TEST-RUN-001"])
            manage_run.cmd_checkpoint(cp_args)

            args = manage_run.build_parser().parse_args(["--db", db.path, "approve", "TEST-RUN-001"])
            result = manage_run.cmd_approve(args)
            self.assertEqual(result["approved_stage"]["status"], "approved")
            self.assertEqual(result["next_action"], "advance")

    def test_approve_not_at_checkpoint(self) -> None:
        with TempDB() as db:
            _create_run(db.path)
            args = manage_run.build_parser().parse_args(["--db", db.path, "approve", "TEST-RUN-001"])
            result = manage_run.cmd_approve(args)
            self.assertIn("error", result)

    def test_approve_final_stage(self) -> None:
        with TempDB() as db:
            stages = [{"stage": "final", "specialist": "human"}]
            _create_run(db.path, stages=stages)
            manage_run.cmd_checkpoint(
                manage_run.build_parser().parse_args(["--db", db.path, "checkpoint", "TEST-RUN-001"])
            )
            args = manage_run.build_parser().parse_args(["--db", db.path, "approve", "TEST-RUN-001"])
            result = manage_run.cmd_approve(args)
            self.assertEqual(result["next_action"], "complete")


class TestComplete(unittest.TestCase):
    def test_complete_all_approved(self) -> None:
        with TempDB() as db:
            stages = [{"stage": "s1", "specialist": "t"}]
            _create_run(db.path, stages=stages)
            manage_run.cmd_checkpoint(
                manage_run.build_parser().parse_args(["--db", db.path, "checkpoint", "TEST-RUN-001"])
            )
            manage_run.cmd_approve(
                manage_run.build_parser().parse_args(["--db", db.path, "approve", "TEST-RUN-001"])
            )
            args = manage_run.build_parser().parse_args(["--db", db.path, "complete", "TEST-RUN-001"])
            result = manage_run.cmd_complete(args)
            self.assertEqual(result["status"], "completed")
            self.assertIn("completed_at", result)

    def test_complete_unapproved_stages(self) -> None:
        with TempDB() as db:
            _create_run(db.path)
            args = manage_run.build_parser().parse_args(["--db", db.path, "complete", "TEST-RUN-001"])
            result = manage_run.cmd_complete(args)
            self.assertIn("error", result)
            self.assertIn("unapproved", result)


class TestStatus(unittest.TestCase):
    def test_status_basic(self) -> None:
        with TempDB() as db:
            _create_run(db.path)
            args = manage_run.build_parser().parse_args(["--db", db.path, "status", "TEST-RUN-001"])
            result = manage_run.cmd_status(args)
            self.assertEqual(result["run_id"], "TEST-RUN-001")
            self.assertEqual(result["status"], "planning")
            self.assertEqual(result["stages_total"], 4)
            self.assertEqual(result["stages_completed"], 0)
            self.assertIsNotNone(result["current_stage"])

    def test_status_nonexistent(self) -> None:
        with TempDB() as db:
            args = manage_run.build_parser().parse_args(["--db", db.path, "status", "NOPE"])
            result = manage_run.cmd_status(args)
            self.assertIn("error", result)


class TestList(unittest.TestCase):
    def test_list_active(self) -> None:
        with TempDB() as db:
            _create_run(db.path, "RUN-A")
            _create_run(db.path, "RUN-B")
            args = manage_run.build_parser().parse_args(["--db", db.path, "list"])
            result = manage_run.cmd_list(args)
            self.assertEqual(result["count"], 2)

    def test_list_excludes_completed(self) -> None:
        with TempDB() as db:
            stages = [{"stage": "s1", "specialist": "t"}]
            _create_run(db.path, "RUN-DONE", stages=stages)
            manage_run.cmd_checkpoint(
                manage_run.build_parser().parse_args(["--db", db.path, "checkpoint", "RUN-DONE"])
            )
            manage_run.cmd_approve(
                manage_run.build_parser().parse_args(["--db", db.path, "approve", "RUN-DONE"])
            )
            manage_run.cmd_complete(
                manage_run.build_parser().parse_args(["--db", db.path, "complete", "RUN-DONE"])
            )
            _create_run(db.path, "RUN-ACTIVE")

            args = manage_run.build_parser().parse_args(["--db", db.path, "list"])
            result = manage_run.cmd_list(args)
            self.assertEqual(result["count"], 1)
            self.assertEqual(result["runs"][0]["run_id"], "RUN-ACTIVE")


class TestFullLifecycle(unittest.TestCase):
    """Integration test: full run from create through complete."""

    def test_full_lifecycle(self) -> None:
        with TempDB() as db:
            stages = [
                {"stage": "draft", "specialist": "content-creator"},
                {"stage": "review", "specialist": "human"},
            ]
            create_result = _create_run(db.path, "LIFECYCLE-001", stages=stages)
            self.assertEqual(create_result["status"], "planning")

            p = manage_run.build_parser()

            advance1 = manage_run.cmd_advance(p.parse_args(["--db", db.path, "advance", "LIFECYCLE-001"]))
            self.assertEqual(advance1["stage_index"], 1)

            cp = manage_run.cmd_checkpoint(p.parse_args(["--db", db.path, "checkpoint", "LIFECYCLE-001"]))
            self.assertEqual(cp["status"], "awaiting-review")

            approve = manage_run.cmd_approve(p.parse_args(["--db", db.path, "approve", "LIFECYCLE-001"]))
            self.assertEqual(approve["next_action"], "complete")

            # Approve first stage too (it was auto-approved by advance)
            # Complete the run
            complete = manage_run.cmd_complete(p.parse_args(["--db", db.path, "complete", "LIFECYCLE-001"]))
            self.assertEqual(complete["status"], "completed")

            status = manage_run.cmd_status(p.parse_args(["--db", db.path, "status", "LIFECYCLE-001"]))
            self.assertEqual(status["status"], "completed")
            self.assertEqual(status["stages_completed"], 2)


if __name__ == "__main__":
    unittest.main()
