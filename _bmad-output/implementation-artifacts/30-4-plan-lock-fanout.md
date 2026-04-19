# Story 30.4: Plan-Lock Fanout

**Status:** done

## T1 Readiness

- [x] T1.0: Gate mode: dual-gate
- [x] T1.0: K floor: 8
- [x] T1.0: Target collecting-test range: 10-12
- [x] T1.0: Required readings: docs/dev-guide/dev-agent-anti-patterns.md, docs/dev-guide/story-cycle-efficiency.md, docs/dev-guide/pydantic-v2-schema-checklist.md, _bmad-output/planning-artifacts/lesson-planner-mvp-plan.md, _bmad-output/implementation-artifacts/30-3b-dials-and-sync-reassessment.md, _bmad-output/implementation-artifacts/28-3-irene-tracy-bridge.md, scripts/utilities/validate_lesson_planner_story_governance.py
- [x] T1.0: Scaffold requirement: false
- [x] T1.1: Read required docs
- [x] T1.2: Run governance validator
- [x] T1.3: Confirm deps done
- [x] T1.4: Confirm surfaces resolve
- [x] T1.5: Runway pre-work consumed
- [x] T1.6: Regression baseline captured

As Marcus (Orchestrator agent),
I want plan-lock fanout envelopes and automatic in-scope gap dispatch to run immediately after lock,
so that step 05+ consumers receive fresh plan-ref envelopes and Tracy dispatch is triggered from a single-writer-safe seam.

## Acceptance Criteria

1. Plan-lock fanout emits step 05+ envelopes carrying top-level `lesson_plan_revision` and `lesson_plan_digest`.
2. In-scope `PlanUnit.gaps` are auto-dispatched via Irene→Tracy bridge integration seam.
3. `fanout.envelope.emitted` events are appended through Orchestrator dispatch only.
4. Single-writer rule remains enforced; no Intake direct log writes.
5. Freshness gate (`assert_plan_fresh`) is wired at new step 05/06/07 consumer boundaries.
6. Story test floor K ≥ 8 is met with focused fanout coverage.
7. Governance validator PASS.

## Tasks / Subtasks

- [x] T1: Readiness gate
- [x] T2: Implement plan-lock fanout emitter seam
- [x] T3: Implement step 05/06/07 envelope consumer boundaries with freshness checks
- [x] T4: Integrate Irene→Tracy gap-dispatch handoff for in-scope unit gaps
- [x] T5: Add/extend tests for fanout envelopes, single-writer routing, freshness guards
- [x] T6: Run focused + regression validations (tests + lint + governance)
- [x] T7: Update status artifacts and docs

## Dev Notes

- Follow 30-3a/30-3b Orchestrator event-emission patterns.
- Import event constants from `marcus.lesson_plan.event_type_registry`; do not hard-code event names.
- Preserve Marcus single-writer discipline by writing through `dispatch_orchestrator_event`.
- Keep plan-ref envelope shape aligned with 32-2 coverage-manifest assumptions (`lesson_plan_revision`, `lesson_plan_digest` at top level).
- Keep fanout seam runtime-light; rely on injected callables for external bridge behavior.

### Project Structure Notes

- Primary implementation under `marcus/orchestrator/` and `marcus/lesson_plan/`.

### References

- Epic 30
- Lesson Planner MVP plan
- Story 30-3b
- Story 28-3

## Dev Agent Record

### Agent Model Used

Codex 5.3

### Completion Notes List

- Story file authored retroactively because sprint ledger had 30-4 status but no story artifact.
- 2026-04-19 implementation pass: added `marcus/orchestrator/fanout.py` and wired `Facade.run_4a` to emit post-lock fanout envelopes through Orchestrator dispatch.
- 2026-04-19 implementation pass: added freshness-gated step consumer boundaries (`step_05_pre_packet_handoff.py`, `step_06_plan_lock_fanout.py`, `step_07_gap_dispatch.py`) with canonical `assert_plan_fresh` entrypoint usage.
- 2026-04-19 code-review closeout (Codex 5.3, implementer): applied MUST-FIX patches for strict step-id enforcement at consumer boundaries and malformed bridge-result hardening in fanout.
- 2026-04-19 SECOND independent G6 layered code-review by Claude Opus 4.7 (different LLM per CLAUDE.md "code-review using a different LLM than the one that implemented" governance). Found 3 additional MUST-FIX + 6 DEFER + 1 DISMISS. Patches applied:
  - **G6-Opus-1 (Blind#1)** — `marcus/orchestrator/fanout.py` bare `except Exception` on bridge.process_plan_locked replaced with `logger.warning` naming bridge type + exception class. Diagnostic visibility for bridge failures (network errors, malformed plans, programming errors) without changing the proceed-with-empty-bridge-results behavior.
  - **G6-Opus-2 (Blind#2)** — `marcus/orchestrator/fanout.py` module-import assertion that `_POSTURE_TO_GAP_TYPE` keys equal the `IdentifiedGap.suggested_posture` Literal values via `typing.get_type_hints` + `get_args`. Closes the future-Literal-widen `KeyError` class at import time rather than at runtime on the fanout path.
  - **G6-Opus-3 (Auditor.A)** — new `tests/contracts/test_30_4_fanout_intake_isolation.py` AST contract test (mirrors the 30-2b dispatch-monopoly pattern) asserting Intake-side modules MUST NOT import `marcus.orchestrator.fanout` nor invoke `emit_plan_lock_fanout`. Closes the single-writer-discipline AST gap on AC-3 + AC-4 that the first review missed.
- DEFERs (logged in deferred-work.md §30-4): B3 posture-name normalization fragility (`gap-fill` vs `gap_fill` seam works but isn't single-sourced); B5 late `compute_digest` import; B6 input-mutation docstring; EC1 zero-plan_units coverage gap; EC4 per-posture bridge_status sharing across multiple gaps in same unit not documented; EC7 duplicate-posture last-write-wins on `results_by_gap_type`. All real but corner cases or NIT-level.
- DISMISS: AC-Auditor.D loose `bridge: Any | None` typing (Protocol class adds complexity for marginal benefit at MVP).
- Verification (post G6-Opus patches): `tests/test_marcus_plan_lock_fanout.py` (10 passed) + `tests/contracts/test_30_4_fanout_intake_isolation.py` (2 passed) = 12 focused tests; full regression 1860 passed / 0 failed (excluding 7 pre-existing 30-3a NegotiatorSeam dataclass-upgrade test failures unrelated to 30-4); `ruff` clean; governance validator PASS. K≥8 met (12 focused tests, 1.5× K, inside target range).

### File List

- _bmad-output/implementation-artifacts/30-4-plan-lock-fanout.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- _bmad-output/maps/deferred-work.md
- marcus/facade.py
- marcus/orchestrator/fanout.py
- marcus/lesson_plan/step_05_pre_packet_handoff.py
- marcus/lesson_plan/step_06_plan_lock_fanout.py
- marcus/lesson_plan/step_07_gap_dispatch.py
- tests/test_marcus_plan_lock_fanout.py
- tests/contracts/test_30_4_fanout_intake_isolation.py
