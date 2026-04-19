# Story 28.3: Irene-Tracy Bridge

**Sprint key:** 28-3-irene-tracy-bridge
**Status:** ready-for-dev

## Story

As the BMAD Story Context Engine,
I want to build a bridge between Irene and Tracy,
so that an `IdentifiedGap` on an in-scope unit auto-dispatches at plan-lock, and dials dispatch per operator endorsement.

## Acceptance Criteria

**AC-1: Auto-Dispatch at Plan-Lock**
- When a `plan.locked` event occurs, any `IdentifiedGap` on an `in-scope` unit must automatically trigger a Tracy dispatch.

**AC-2: Dial Dispatching**
- Dials (e.g., enrich, corroborate, gap_fill) dispatch to Tracy based on operator endorsement.

**AC-3: Integration with Posture Dispatcher**
- The bridge must invoke the correct posture method via `PostureDispatcher.select_posture()` based on the gap type or dial.

## T1 Readiness

- **Gate Mode**: single-gate
- **K Floor**: 6
- **Target Collecting-Test Range**: 8 to 9
- **Required Readings**: 
  - `docs/dev-guide/story-cycle-efficiency.md`
  - `docs/dev-guide/dev-agent-anti-patterns.md`
  - `docs/dev-guide/pydantic-v2-schema-checklist.md`
- **Scaffold Required**: false

## Tasks / Subtasks

- [x] Task 1: Auto-Dispatch Logic
  - [x] Implement event listener for `plan.locked` to scan for `IdentifiedGap` on `in-scope` units.
  - [x] Trigger Tracy dispatch for each found gap.
- [x] Task 2: Dial Dispatch Logic
  - [x] Implement dispatching based on dial operator endorsements.
- [x] Task 3: Bridge Integration
  - [x] Connect Irene's output to `PostureDispatcher`.

## Dev Notes

### Architecture Compliance
- The bridge should live in `marcus/orchestrator` or where plan-lock events are handled (e.g. `marcus/orchestrator/dispatch.py` or similar). Wait, 30-4 handles plan-lock fanout. Since 30-4 is not done yet, the bridge might just be a utility function or a listener hook in `marcus/orchestrator` or `skills/bmad_agent_tracy/scripts/irene_bridge.py`. Let's put it in `skills/bmad_agent_tracy/scripts/irene_bridge.py`.

### Testing Requirements
- K=6 floor.
- Include tests for auto-dispatching `in-scope` gaps.
- Include tests for skipping `out-of-scope` gaps.
- Include tests for dial dispatching.

## References
- [Epic 28 Tracy Detective: _bmad-output/implementation-artifacts/epic-28-tracy-detective.md]
- [Lesson Planner MVP Plan: _bmad-output/planning-artifacts/lesson-planner-mvp-plan.md]

## Dev Agent Record

### Agent Model Used
Cline (highly skilled software engineer)

### Completion Notes List
- Implemented `IreneTracyBridge` to handle `process_plan_locked` and `process_dials`.
- Ensured strict filtering for `in-scope` decisions before attempting dispatch.
- Robust iteration added to handle missing or incorrectly typed gap and dial payloads without crashing.
- Test coverage added: 8 test nodes successfully cover all edge cases, in compliance with the 8-9 target range and the K=6 floor constraint.

### File List
- skills/bmad_agent_tracy/scripts/irene_bridge.py
- tests/contracts/test_irene_tracy_bridge.py

### Change Log
- 2026-04-19: Completed bridge implementation. Status: ready-for-dev → review.
- 2026-04-19: Completed bmad-code-review layered pass. Addressed type annotations and unhandled null dictionary/iteration risks. Status: review → done.
