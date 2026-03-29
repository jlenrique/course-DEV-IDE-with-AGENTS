# Run State Schema

## Purpose

Documents the SQLite schema for production runs and the JSON envelope format used for agent communication.

This reference also documents how transient run authority (`run baton`) relates to persisted run state.

## SQLite Table: `production_runs`

Defined in `scripts/state_management/db_init.py`:

```sql
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
```

## `context_json` Envelope

The `context_json` column stores a JSON object with run-specific metadata:

```json
{
  "content_type": "lecture-slides",
  "module": "M2",
  "lesson": "L3",
  "learning_objectives": ["CLO-1", "CLO-2"],
  "mode": "default",
  "stages": [
    {"stage": "outline", "specialist": "content-creator", "status": "pending"},
    {"stage": "slides", "specialist": "gamma-specialist", "status": "pending"},
    {"stage": "review", "specialist": "quality-reviewer", "status": "pending"},
    {"stage": "checkpoint", "specialist": "human", "status": "pending"}
  ],
  "current_stage_index": 0,
  "revision_count": 0,
  "user_feedback": []
}
```

## Status Query Response

When `manage_run.py status` is called, it returns:

```json
{
  "run_id": "C1-M2-lecture-slides-20260326",
  "purpose": "Lecture slides for cardiac pharmacology",
  "status": "in-progress",
  "preset": "draft",
  "mode": "default",
  "content_type": "lecture-slides",
  "current_stage": {
    "index": 1,
    "stage": "slides",
    "specialist": "gamma-specialist",
    "status": "working"
  },
  "stages_completed": 1,
  "stages_total": 4,
  "created_at": "2026-03-26T15:30:00",
  "updated_at": "2026-03-26T15:45:00"
}
```

## Run Cancellation

`manage_run.py cancel <run_id>` sets run status to `cancelled` and clears any active baton for the run.

## Run Baton (Transient Authority Contract)

Authority is tracked separately from SQLite in lightweight JSON files at:

`state/runtime/run_baton.<run_id>.json`

The baton carries:
- `run_id`
- `orchestrator`
- `current_gate`
- `invocation_mode`
- `allowed_delegates`
- `escalation_target`
- `blocking_authority`

Use `manage_baton.py` to initialize, read, update, and close baton state.

## Related Tables

- `agent_coordination`: Records specialist delegation events during run execution
- `quality_gates`: Records checkpoint gate decisions (approval/rejection/revision)

Both reference `production_runs.run_id` as a foreign key.
