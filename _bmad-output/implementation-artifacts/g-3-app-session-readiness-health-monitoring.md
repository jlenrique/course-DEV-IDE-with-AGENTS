# Story G.3: APP Session Readiness & Health Monitoring Service

**Epic:** G — Governance Synthesis & Intelligence Optimization  
**Status:** done
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

- [x] Add `scripts/` or `skills/` module (implemented at `scripts/utilities/app_session_readiness.py`) with `run_readiness(root) -> structured report`
- [x] Implement checks as small pure functions for testability
- [x] CLI: `python -m ...` exit code non-zero on fail, strict mode for warning escalation
- [x] Optional: `--with-preflight` flag calling into `run_preflight` after runtime checks
- [x] Tests under `tests/` (implemented at `tests/test_app_session_readiness.py`)
- [x] Update `docs/admin-guide.md` Pre-Flight / health section
- [x] Update both `skills/bmad-agent-marcus/SKILL.md` and `skills/pre-flight-check/SKILL.md` cross-reference

## References

- `_bmad-output/planning-artifacts/epics.md` — Story G.3
- `skills/pre-flight-check/SKILL.md`, `preflight_runner.py`
- `scripts/state_management/db_init.py`
- `docs/app-logging-evaluation.md`, `docs/app-logging-channels.md`
- `hooks/scripts/session-start.mjs` (placeholder — optional future wire-up)

## Dev Agent Record

### File List

- `scripts/utilities/app_session_readiness.py`
- `tests/test_app_session_readiness.py`
- `docs/admin-guide.md`
- `skills/bmad-agent-marcus/SKILL.md`
- `skills/pre-flight-check/SKILL.md`

### Change Log

- Added APP session readiness service with runtime checks for DB/schema, state paths, mode-state parsing, and import sanity.
- Added optional two-phase composition with existing pre-flight (`--with-preflight`).
- Added CLI behavior with JSON/human outputs and strict exit semantics.
- Added focused pytest coverage for pass/fail/warn and composition edge cases.
- Updated operator docs and Marcus/pre-flight skill references for invocation flow.

### Completion Notes

- AC1-AC7 satisfied.
- Adversarial review executed; critical/high findings mitigated before close.
- Validation executed: `tests/test_app_session_readiness.py` passing.
