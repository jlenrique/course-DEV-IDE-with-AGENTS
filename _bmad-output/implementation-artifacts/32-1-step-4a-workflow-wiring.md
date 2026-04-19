# Story 32.1: Step 4A Workflow Wiring

**Status:** done

## T1 Readiness

- [x] T1.0: Gate mode: single-gate
- [x] T1.0: K floor: 4
- [x] T1.0: Target collecting-test range: 5-7
- [x] T1.0: Required readings: docs/dev-guide/dev-agent-anti-patterns.md, docs/dev-guide/story-cycle-efficiency.md, docs/dev-guide/pydantic-v2-schema-checklist.md, _bmad-output/planning-artifacts/lesson-planner-mvp-plan.md, _bmad-output/implementation-artifacts/30-4-plan-lock-fanout.md, scripts/utilities/validate_lesson_planner_story_governance.py
- [x] T1.0: Scaffold requirement: false
- [x] T1.1: Read required docs
- [x] T1.2: Run governance validator
- [x] T1.3: Confirm deps done
- [x] T1.4: Confirm surfaces resolve
- [x] T1.5: Runway pre-work consumed
- [x] T1.6: Regression baseline captured

As Marcus (workflow orchestrator),
I want to insert the 4A loop between step 04 gate and step 05 execution,
so that baton handoff contracts are explicit and downstream step 05+ always run from a locked, plan-ref-carrying state.

## Acceptance Criteria

1. Workflow runner includes a concrete 4A stage between step 04 and step 05.
2. Runner wiring invokes `Facade.run_4a(...)` before step 05 handoff.
3. Baton handoff contract surface includes locked plan revision and digest.
4. Pipeline metadata/HUD step list reflects inserted 4A stage.
5. Focused tests prove stage insertion order and handoff contract behavior.
6. K floor met (K ≥ 4).
7. Governance validator PASS.

## Tasks / Subtasks

- [x] T1: Readiness gate
- [x] T2: Add 32-1 workflow runner seam with explicit 4A insertion
- [x] T3: Add baton handoff contract model and route helper
- [x] T4: Update pipeline/HUD step metadata to include step 4A
- [x] T5: Add focused tests for wiring and handoff contracts
- [x] T6: Run focused + related validations (pytest, ruff, governance)
- [x] T7: Update closeout artifacts (story, sprint-status, next-session)

## Dev Notes

- Reuse existing `Facade.run_4a` integration as the single conversation-loop entry.
- Preserve single-writer discipline; no direct log write shortcuts in workflow wiring.
- Keep baton payload compact: revision + digest + source/target step IDs.
- Keep wiring deterministic and testable with dependency injection.

### Project Structure Notes

- Expected surfaces: `marcus/orchestrator/` + `scripts/utilities/run_hud.py` + focused tests.

### References

- Epic 32
- Story 30-4
- Lesson Planner MVP plan

## Dev Agent Record

### Agent Model Used

Codex 5.3

### Completion Notes List

- Story file authored retroactively because sprint ledger carried 32-1 but no story artifact existed.
- Implemented `marcus/orchestrator/workflow_runner.py` with explicit 04A insertion helper and a typed baton handoff contract (`lesson_plan_revision` + `lesson_plan_digest`) after `Facade.run_4a(...)`.
- Updated `scripts/utilities/run_hud.py` pipeline metadata to include `04A` between `04.5` and `05`.
- Added focused tests in `tests/test_marcus_workflow_runner_32_1.py` for insertion order, idempotency, handoff payload correctness, empty-plan rejection, and HUD stage ordering.
- Formal `bmad-code-review` pass completed with MUST-FIX patches applied (canonical `04A` normalization and empty-plan guard at workflow seam).
- Verification: `tests/test_marcus_workflow_runner_32_1.py` + `tests/test_run_hud.py` passed (`44 passed`), targeted `ruff` passed, governance validator PASS.

### File List

- _bmad-output/implementation-artifacts/32-1-step-4a-workflow-wiring.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- next-session-start-here.md
- marcus/orchestrator/workflow_runner.py
- scripts/utilities/run_hud.py
- tests/test_marcus_workflow_runner_32_1.py
