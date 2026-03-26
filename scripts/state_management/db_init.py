"""SQLite database initialization for runtime coordination state.

Creates the coordination database with tables for production runs,
agent coordination events, and quality gate decisions.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from scripts.utilities.file_helpers import project_root

DB_PATH = project_root() / "state" / "runtime" / "coordination.db"

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

CREATE INDEX IF NOT EXISTS idx_coordination_run
    ON agent_coordination(run_id);

CREATE INDEX IF NOT EXISTS idx_quality_gates_run
    ON quality_gates(run_id);
"""


def init_database(db_path: str | Path | None = None) -> Path:
    """Create the coordination database with all required tables.

    Args:
        db_path: Override path for the database file.
                 Defaults to ``state/runtime/coordination.db``.

    Returns:
        Path to the created database file.
    """
    db_path = Path(db_path) if db_path else DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(SCHEMA_SQL)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.commit()
    finally:
        conn.close()

    return db_path
