# Story 28.2: Tracy Three Modes

**Sprint key:** 28-2-tracy-three-modes
**Status:** ready-for-dev

## Story

As the BMAD Story Context Engine,
I want Tracy to implement the three postures (embellish, corroborate, gap-fill) so that she can dispatch to the provider directory based on an IdentifiedGap or dial.
This ensures Tracy can fulfill her core research functions reliably and safely.

## Acceptance Criteria

**AC-1: Posture Implementations**
- Implement `tracy.embellish()`, `tracy.corroborate()`, and `tracy.gap_fill()`.
- Each posture must dispatch to the `provider_directory` using the appropriate inputs.

**AC-2: Posture Discrimination Matrix**
- Tracy must correctly select the appropriate posture based on the `IdentifiedGap` or dial.
- Include a refuse-on-ambiguous-intent negative test.

**AC-3: Per-Posture Result-Shape Contract**
- `embellish` must return an enrichment shape.
- `corroborate` must return an evidence-with-cross-ref shape.
- `gap_fill` must return a derivative-content shape.

**AC-4: Gap-Fill Scope Constraint**
- Implement a fail-closed negative test for `gap_fill` invoked with `scope_decision != in-scope`.

## T1 Readiness

- **Gate Mode**: dual-gate
- **K Floor**: 10
- **Target Collecting-Test Range**: 12 to 15
- **Required Readings**: 
  - `docs/dev-guide/story-cycle-efficiency.md`
  - `docs/dev-guide/dev-agent-anti-patterns.md`
  - `docs/dev-guide/pydantic-v2-schema-checklist.md`
- **Scaffold Required**: false

## Tasks / Subtasks

- [x] Task 1: Implement Posture Dispatching
  - [x] Implement `embellish()`, `corroborate()`, `gap_fill()`
- [x] Task 2: Implement Posture Discrimination
  - [x] Add logic to select posture based on IdentifiedGap/dial
  - [x] Add refuse-on-ambiguous-intent negative test
- [x] Task 3: Enforce Result-Shape Contracts
  - [x] Map each posture to its required output shape
- [x] Task 4: Enforce Scope Constraints
  - [x] Add check for `gap_fill` requiring `in-scope`
  - [x] Add fail-closed negative test

## Dev Notes

### Architecture Compliance
- Ensure `retrieval.dispatcher` is used for all provider dispatching.
- Follow the schema changes introduced in 28-1 and 31-1.

### Testing Requirements
- K=10 floor.
- Include posture-discrimination matrix tests.
- Include refuse-on-ambiguous-intent negative test.
- Include gap_fill out-of-scope fail-closed negative test.

## References
- [Epic 28 Tracy Detective: _bmad-output/implementation-artifacts/epic-28-tracy-detective.md]
- [Lesson Planner MVP Plan R1 Amendment 10: _bmad-output/planning-artifacts/lesson-planner-mvp-plan.md]

## Dev Agent Record

### Agent Model Used
Cline (highly skilled software engineer)

### Completion Notes List
- Implemented `embellish`, `corroborate`, and `gap_fill` postures dispatching to the underlying retrieval dispatcher.
- Developed the posture discrimination matrix handling `gap_type` and `dial` options.
- Added `AmbiguousIntentError` for unmatched intents.
- Added `OutOfScopeError` constraint for `gap_fill` requiring in-scope decision.
- Total test nodes: 17 (K floor 10). Exceeded target range (12-15) because parametrized cases for posture discrimination matrix generated 6 permutations to comprehensively ensure all input types route to the correct posture.

### File List
- skills/bmad_agent_tracy/scripts/posture_dispatcher.py
- tests/contracts/test_tracy_postures.py

### Change Log
- 2026-04-18: Completed implementation of Tracy Three Modes. Added dispatch methods, discrimination matrix, and tests. Status: ready-for-dev → review.
- 2026-04-18: Completed bmad-code-review layered pass. Addressed feedback on exception handling, sys.path modification, intent ambiguity logic, and collection casting. Status: review → done.
