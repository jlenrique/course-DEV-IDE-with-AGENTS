# Baton Lifecycle

## Purpose

Define the lightweight runtime authority contract used during active production runs.

The baton is a JSON file in `state/runtime/` and is intentionally separate from the SQLite run record. It coordinates authority, not run history.

## Baton Schema

```json
{
  "run_id": "C1-M1-P2S1-VID-001",
  "orchestrator": "marcus",
  "current_gate": "G2",
  "invocation_mode": "delegated",
  "allowed_delegates": [
    "content-creator",
    "gamma-specialist",
    "fidelity-assessor",
    "quality-reviewer"
  ],
  "escalation_target": "marcus",
  "blocking_authority": "human",
  "active": true,
  "created_at": "2026-03-28T10:15:00",
  "updated_at": "2026-03-28T10:20:00"
}
```

Required fields:
- `run_id`
- `orchestrator`
- `current_gate`
- `invocation_mode`
- `allowed_delegates`
- `escalation_target`
- `blocking_authority`

## Script Commands

- Initialize baton:
  - `manage_baton.py init <run_id> --current-gate G0 --allowed-delegate content-creator ...`
- Read baton:
  - `manage_baton.py get --run-id <run_id>`
- Update gate:
  - `manage_baton.py update-gate <run_id> <gate>`
- Check specialist invocation:
  - `manage_baton.py check-specialist <specialist>`
  - `manage_baton.py check-specialist <specialist> --delegated-call --run-id <run_id>`
  - `manage_baton.py check-specialist <specialist> --standalone-mode`
- Close baton:
  - `manage_baton.py close --run-id <run_id>`

## Direct Specialist Invocation Rule

When a baton is active and a specialist is invoked directly, default behavior is redirect:

"Marcus is running [run_id], currently at [gate]. Redirect, or enter standalone consult mode?"

Specialist proceeds only when either:
- invocation is delegated by Marcus and specialist is in `allowed_delegates`, or
- user explicitly requests standalone consult mode.

## Standalone Consult Guardrail

Standalone consult mode allows specialist interaction while a run baton is active, but it must not mutate active production run state:
- no `manage_run.py` state transitions for the active run
- no baton `current_gate` updates
- no authority changes to the active baton

## Closeout Semantics

Baton is cleared when:
- `manage_run.py complete <run_id>` succeeds, or
- `manage_run.py cancel <run_id>` succeeds, or
- explicit close command is called

Clear means transient baton file is removed from `state/runtime/`.
