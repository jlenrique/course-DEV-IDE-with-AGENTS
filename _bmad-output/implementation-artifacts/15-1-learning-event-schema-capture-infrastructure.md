# Story 15.1: Learning Event Schema & Capture Infrastructure

**Epic:** 15 — Learning & Compound Intelligence
**Status:** backlog
**Sprint key:** `15-1-learning-event-schema-capture-infrastructure`
**Added:** 2026-04-06
**Depends on:** At least one tracked trial run completed. Existing gate coordinator, quality gate, and ad-hoc ledger infrastructure.

## Summary

Define and implement a canonical learning-event schema that captures every meaningful production event (gate approval, revision, waiver, circuit break, quality failure, fidelity failure, first-pass approval, manual override). Integrate capture hooks with the existing gate coordinator and quality gate infrastructure so events are recorded automatically during production runs.

## Goals

1. Canonical learning-event schema in YAML.
2. Per-run learning ledger appended automatically at gate decisions.
3. Integration with existing gate coordinator (`scripts/utilities/` quality gate infrastructure).
4. Respect ad-hoc ledger boundary (FR91 — Story 4A-6).
5. Extensible schema for future event types.

## Existing Infrastructure To Build On

- `scripts/utilities/ad_hoc_persistence_guard.py` — ad-hoc event tracking pattern (FR91, Story 4A-6)
- `state/runtime/ad-hoc-observability/` — existing observability hooks from Epic 4A-5
- Quality gate coordination code from Stories 4-2 and 4A — gate decision points
- `skills/production-coordination/` — workflow stage management, run lifecycle
- Production run lifecycle from Story 4-1 — run state tracking
- `skills/bmad-agent-fidelity-assessor/` (Vera) — fidelity failure events at gates
- `skills/bmad-agent-quality-reviewer/` (Quinn-R) — quality failure/revision events
- `_bmad/memory/*/` — sidecar pattern (15 sidecars) — eventual target for routed learning
- `state/config/` — YAML config pattern for schemas

## Key Files

- `state/config/learning-event-schema.yaml` — new: canonical event schema definition
- `scripts/utilities/learning_event_capture.py` — new: event creation, validation, append functions
- Run directory `{run_dir}/learning-events.yaml` — new: per-run learning ledger
- `skills/production-coordination/` — update: wire capture hooks into gate coordination

## Acceptance Criteria

1. Schema defined in `state/config/learning-event-schema.yaml` with fields: `run_id`, `gate`, `event_type` (approval | revision | waiver | circuit_break | quality_failure | fidelity_failure | first_pass_approval | manual_override), `artifact_type`, `producing_specialist`, `reviewing_specialist`, `human_decision`, `root_cause_classification`, `accepted_remediation`, `learning_targets[]`, `timestamp`.
2. `learning_event_capture.py` provides: `create_event(...)`, `validate_event(event, schema)`, `append_to_ledger(event, run_dir)`.
3. Events appended to `{run_dir}/learning-events.yaml` as a YAML list.
4. Capture hooks integrate with existing gate coordinator — events recorded when gate decisions occur.
5. Ad-hoc runs capture events to their ad-hoc ledger (existing FR91 boundary respected; `ad_hoc_persistence_guard.py` pattern followed).
6. Schema is extensible: new `event_type` values can be added without breaking existing consumers.
7. Unit tests: schema validation (valid/invalid events), append behavior, ad-hoc boundary enforcement.
8. Integration test: simulated gate decision produces correctly structured learning event.
