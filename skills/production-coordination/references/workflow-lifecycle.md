# Workflow Lifecycle

## Purpose

Defines the production run state machine, stage transition rules, and recovery procedures. This is the authoritative reference for how runs progress through their lifecycle.

## Run State Machine

```

Run baton lifecycle in parallel with run state:
- `create`/run start: initialize baton (`manage_baton.py init`)
- gate transitions: update baton gate (`manage_baton.py update-gate`)
- `completed` or `cancelled`: clear baton (`manage_baton.py close` via `manage_run.py`)
planning → in-progress → [stage cycle] → completed
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
            stage: working      stage: awaiting-review
                    │                    │
                    │              ┌─────┴─────┐
                    │              ▼           ▼
                    │         approved    revision-requested
                    │              │           │
                    │              ▼           ▼
                    │         (next stage)   working (loop)
                    │
                    └─► failed (terminal — requires user decision)
```

## Run-Level States

| State | Meaning | Transitions To |
|-------|---------|----------------|
| `planning` | Run created, plan not yet confirmed | `in-progress`, `cancelled` |
| `in-progress` | User confirmed plan, stages executing | `completed`, `failed` |
| `completed` | All stages approved, run finalized | Terminal |
| `failed` | Unrecoverable error — user must decide | `in-progress` (retry), `cancelled` |
| `cancelled` | User abandoned the run | Terminal |

## Stage-Level States

| State | Meaning | Transitions To |
|-------|---------|----------------|
| `pending` | Stage not yet started | `working` |
| `working` | Specialist executing this stage | `awaiting-review`, `failed` |
| `awaiting-review` | Human checkpoint — waiting for user decision | `approved`, `revision-requested` |
| `approved` | User approved this stage's output | Terminal for this stage |
| `revision-requested` | User requested changes | `working` (revision loop) |
| `failed` | Stage execution failed | `working` (retry) |

## Stage Sequencing Rules

1. Stages execute in the order defined by `generate-production-plan.py` content type workflows
2. A stage cannot start until the previous stage is `approved` (dependency chain)
3. Human checkpoint stages (`checkpoint`) block advancement until explicitly approved
4. Revision loops return to `working` with revision feedback attached
5. The final stage approval triggers run-level transition to `completed`

## Recovery

If a run is interrupted (session ends, tool failure):
- Run state persists in SQLite — Marcus reads it on next activation via `read-mode-state.py`
- Marcus reports: "We have an active run from last session — [run details]. Want to continue?"
- Stages already approved are preserved; only the current stage needs re-execution

## Mode Awareness

- **Default mode**: Full state tracking. Run records persist. Patterns and chronology updated on completion.
- **Ad-hoc mode**: Runs still recorded (for session tracking) but flagged `mode: ad-hoc`. State writes to patterns/chronology suppressed. Assets route to scratch.
