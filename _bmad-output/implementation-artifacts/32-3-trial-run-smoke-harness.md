# Story 32-3: Trial-Run Smoke Harness

**Status:** done
**Epic:** 32 - Step 4A landing + trial-run harness
**Sprint key:** `32-3-trial-run-smoke-harness`
**Points:** 5
**Gate mode:** dual-gate
**K floor:** 10
**Depends on:** 29-*, 30-*, 31-*, 32-1, 32-2, 32-2a

## T1 Readiness

- [x] T1.0: Gate mode: dual-gate
- [x] T1.0: K floor: 10
- [x] T1.0: Target collecting-test range: 12-15
- [x] T1.0: Required readings: docs/dev-guide/story-cycle-efficiency.md, docs/dev-guide/dev-agent-anti-patterns.md, docs/dev-guide/pydantic-v2-schema-checklist.md, _bmad-output/planning-artifacts/lesson-planner-mvp-plan.md, _bmad-output/implementation-artifacts/32-2-plan-ref-envelope-coverage-manifest.md, _bmad-output/implementation-artifacts/32-2a-inventory-hardening.md
- [x] T1.0: Scaffold requirement: false
- [x] T1.1: Governance validator PASS at ready-for-dev gate
- [x] T1.2: Dependency closure reconfirmed
- [x] T1.3: Existing seams inventoried (`pre_packet`, `workflow_runner`, `fanout`, `quinn_r_gate`, `coverage_manifest`)
- [x] T1.4: Baseline focused regression run captured

### Required readings

- `docs/dev-guide/story-cycle-efficiency.md`
- `docs/dev-guide/dev-agent-anti-patterns.md`
- `docs/dev-guide/pydantic-v2-schema-checklist.md`
- `_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md`
- `_bmad-output/implementation-artifacts/32-2-plan-ref-envelope-coverage-manifest.md`
- `_bmad-output/implementation-artifacts/32-2a-inventory-hardening.md`

## Story

As the Lesson Planner MVP release gate owner,
I want a deterministic smoke harness that drives a canned SME trial through the current 01->13 chain and records a trial-readiness assertion battery,
so that CI can enforce Murat's 5x-consecutive smoke stability requirement and expose trial-ready blockers as machine-readable evidence.

## Acceptance Criteria

1. A runnable smoke harness module exists under `marcus/orchestrator/` and executes a deterministic end-to-end path using existing seams.
2. The harness traverses intake pre-packet emission, 4A routing, plan-lock fanout boundaries, produced-asset branch input, Quinn-R gate evaluation, and coverage-manifest emission.
3. The harness emits a machine-readable report including ordered step coverage for 01->13 (with explicit deferred marks for currently deferred step surfaces).
4. A trial-readiness assertion battery is included in the report and sourced from `coverage_manifest.summary`.
5. Focused test coverage includes at least 10 tests (K>=10) and includes a 5x-consecutive stability check.
6. Governance validator passes and closeout artifacts are updated in order.

## Tasks / Subtasks

- [x] T1 readiness + governance gate
- [x] T2 implement `marcus/orchestrator/trial_smoke_harness.py`
- [x] T3 add focused smoke-harness tests (>=10)
- [x] T4 run focused validations (pytest, ruff, validator)
- [x] T5 dual-gate review pass and apply fixes
- [x] T6 close story artifact + sprint-status + hot-start updates

## Dev Agent Record

### Agent Model Used

Codex 5.3

### Completion Notes List

- Story artifact created because sprint ledger had a `32-3` row without a concrete dev artifact.
- Landed `marcus/orchestrator/trial_smoke_harness.py` with deterministic 01->13 smoke traversal through existing seams: pre-packet emission, 4A route, fanout boundary consumers, produced-asset branch input, Quinn-R gate evaluation, and coverage-manifest battery.
- Added machine-readable report models (`SmokeStepResult`, `TrialReadinessBattery`, `TrialSmokeReport`) and a structured failure-report fallback for fanout drift.
- Added focused test file `tests/test_trial_run_e2e.py` with 10 collecting tests including Murat §6-E1 5x-consecutive stability check.
- Ran governance validator, focused pytest slice, and targeted ruff lint clean.
- Dual-gate review pass executed with layered findings applied: fanout guard + replay scoping by plan revision.

### File List

- _bmad-output/implementation-artifacts/32-3-trial-run-smoke-harness.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- next-session-start-here.md
- marcus/orchestrator/trial_smoke_harness.py
- tests/test_trial_run_e2e.py
