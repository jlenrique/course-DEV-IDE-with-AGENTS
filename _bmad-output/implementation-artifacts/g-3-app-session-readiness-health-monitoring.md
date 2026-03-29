# Story G.3: APP Session Readiness & Health Monitoring Service

**Epic:** G — Governance Synthesis & Intelligence Optimization  
**Status:** ready-for-dev  
**Sprint key:** `g-3-app-session-readiness-health-monitoring`  
**Added:** 2026-03-30

## Summary

Design and implement a **session readiness / health monitoring** path that validates **APP runtime infrastructure** (SQLite coordination DB, critical `state/` paths, mode file, key Python import sanity) and emits a **structured report** (JSON + human-readable). The service **composes with** the existing `skills/pre-flight-check/` tool/MCP checks rather than reimplementing them. Fully covered by **pytest**.

## Problem

Pre-flight today focuses on **tools** (MCP, APIs, Notion, Box). **Default-mode production** also requires `coordination.db`, writable runtime directories, and working imports for reporting/observability. Operators can open Cursor and chat while the persistence layer is broken — failures surface late.

## Goals

1. **Single entrypoint** (Python module/CLI) runnable at session start or on demand.
2. **Runtime checks** with explicit pass/fail/skip and resolution hints.
3. **Report artifact**: machine-readable (JSON stdout or file) + short text summary.
4. **Integration option**: document or implement composition with `preflight_runner.run_preflight()` (two-phase: runtime → tools).
5. **Tests**: missing DB, bad permissions, import failure simulation, happy path.
6. **Docs**: `docs/admin-guide.md` and/or `docs/user-guide.md` + Marcus pre-flight adjacent guidance.

## Non-goals (this story)

- Replacing `heartbeat_check.mjs` or duplicating Tier 1/2 API probes inside Python.
- Epic 10 predictive orchestration.
- Mandatory blocking Cursor startup unless explicitly configured (hooks remain optional / non-blocking by default).

## Dependencies

- **Epic 4** complete: `scripts/state_management/db_init.py`, `state/runtime/coordination.db` convention, production-coordination scripts.
- **Existing:** `skills/pre-flight-check/scripts/preflight_runner.py`, `docs/app-logging-channels.md`, `docs/admin-guide.md` (Pre-Flight section).

## Acceptance criteria (traceable)

| # | Criterion |
|---|-----------|
| AC1 | Service verifies coordination DB exists or can be created via documented init; validates expected tables (e.g. `production_runs`, `agent_coordination`, `quality_gates`) or runs a minimal query |
| AC2 | Service verifies critical paths under `state/` (e.g. `state/runtime`, `state/config`) exist and are writable |
| AC3 | When `state/runtime/mode_state.json` exists, it is readable JSON; invalid/missing handled as warning or fail per design doc |
| AC4 | Import or subprocess check for `observability_hooks` / `run_reporting` coupling does not silently swallow errors in the report |
| AC5 | JSON report includes `checks[]` with `name`, `status`, `detail`, optional `resolution`; top-level `overall_status` and timestamp |
| AC6 | `pytest` covers ≥4 scenarios including success and controlled failures |
| AC7 | Pre-flight skill or Marcus references updated so operators know “runtime readiness + tool pre-flight” sequence |

## Suggested implementation tasks

- [ ] Add `scripts/` or `skills/` module (e.g. `skills/app-readiness/` or `scripts/utilities/app_session_readiness.py`) with `run_readiness(root) -> ReadinessReport`
- [ ] Implement checks as small pure functions for testability
- [ ] CLI: `python -m ...` exit code non-zero on fail if `--strict`, zero with warnings-only if documented
- [ ] Optional: `--with-preflight` flag calling into `run_preflight` after runtime checks
- [ ] Tests under `tests/` or colocated `scripts/tests/`
- [ ] Update `docs/admin-guide.md` Pre-Flight / health section; `docs/user-guide.md` one paragraph
- [ ] Update `skills/bmad-agent-marcus/SKILL.md` or `skills/pre-flight-check/SKILL.md` cross-reference

## References

- `_bmad-output/planning-artifacts/epics.md` — Story G.3
- `skills/pre-flight-check/SKILL.md`, `preflight_runner.py`
- `scripts/state_management/db_init.py`
- `docs/app-logging-evaluation.md`, `docs/app-logging-channels.md`
- `hooks/scripts/session-start.mjs` (placeholder — optional future wire-up)

## Dev Agent Record

*(Populate during implementation: File List, Change Log, Completion Notes.)*
