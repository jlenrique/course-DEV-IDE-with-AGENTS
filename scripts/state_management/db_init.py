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

CREATE TABLE IF NOT EXISTS observability_events (
    event_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id              TEXT NOT NULL,
    event_type          TEXT NOT NULL,
    gate                TEXT,
    run_mode            TEXT NOT NULL,
    fidelity_o_count    INTEGER,
    fidelity_i_count    INTEGER,
    fidelity_a_count    INTEGER,
    quality_scores_json TEXT,
    agent_metrics_json  TEXT,
    payload_json        TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES production_runs(run_id)
);

CREATE TABLE IF NOT EXISTS run_context_links (
    link_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL,
    linked_run_id   TEXT NOT NULL,
    link_type       TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES production_runs(run_id),
    FOREIGN KEY (linked_run_id) REFERENCES production_runs(run_id)
);

CREATE TABLE IF NOT EXISTS asset_evolution (
    evolution_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id               TEXT NOT NULL,
    asset_id             TEXT NOT NULL,
    version              INTEGER NOT NULL,
    content_hash         TEXT,
    decision_rationale   TEXT,
    metadata_json        TEXT,
    created_at           TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES production_runs(run_id)
);

CREATE TABLE IF NOT EXISTS learning_objective_map (
    mapping_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id               TEXT NOT NULL,
    asset_id             TEXT NOT NULL,
    objective_id         TEXT NOT NULL,
    validation_status    TEXT NOT NULL,
    aligned_at           TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES production_runs(run_id)
);

CREATE TABLE IF NOT EXISTS deployment_events (
    deployment_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id               TEXT NOT NULL,
    platform             TEXT NOT NULL,
    status               TEXT NOT NULL,
    details_json         TEXT,
    deployed_at          TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES production_runs(run_id)
);

CREATE INDEX IF NOT EXISTS idx_coordination_run
    ON agent_coordination(run_id);

CREATE INDEX IF NOT EXISTS idx_quality_gates_run
    ON quality_gates(run_id);

CREATE INDEX IF NOT EXISTS idx_observability_events_run
    ON observability_events(run_id);

CREATE INDEX IF NOT EXISTS idx_observability_events_mode
    ON observability_events(run_mode);

CREATE INDEX IF NOT EXISTS idx_run_context_links_run
    ON run_context_links(run_id);

CREATE INDEX IF NOT EXISTS idx_asset_evolution_run
    ON asset_evolution(run_id);

CREATE INDEX IF NOT EXISTS idx_learning_objective_map_run
    ON learning_objective_map(run_id);

CREATE INDEX IF NOT EXISTS idx_deployment_events_run
    ON deployment_events(run_id);
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
