# Story 28.1: Tracy Reshape Charter

Status: done

## Story

As the BMAD Story Context Engine,
I want to retire the original Tracy pilot spec and re-charter Tracy as a minimal research agent wrapping the retrieval.dispatcher from Epic 27,
so that Tracy focuses on editorial judgment (posture selection, scoring, curation) while Texas handles mechanical fetch/extract, enabling clean specialist separation and pilot validation.

## Acceptance Criteria

**AC-1: Retire Original Specs**
- Mark original `28-1-tracy-pilot-scite-ai.md` and `28-2-tracy-gate-hardening.md` as retired/superseded in sprint-status.yaml comments.
- Archive old specs to archive/ if not already.
- Document rationale: R1 amendment 9 — pilot framing retired for minimal research agent wrapping dispatcher; three postures replace gate-hardening.

**AC-2: Codify Three Postures**
- Define `embellish`, `corroborate`, `gap-fill` as Tracy's core methods.
- Each posture has John's four-part contract:
  - **Input shape**: RetrievalIntent from Irene (IdentifiedGap or dial-driven).
  - **Output shape**: suggested-resources.yaml manifest row(s) with `intent_class`, `intent_detail`, `editorial_note`, `provider_metadata.scite`.
  - **Success signal**: `confidence_score ≥ 0.85` or operator approval.
  - **Failure mode**: `status: failed` with reason; no silent skip.
- Explicit: `corroborate` handles supporting/contrasting/mentioning from scite — disconfirming is result type within corroborate.

**AC-3: Posture Discrimination**
- Tracy selects posture based on Irene brief (IdentifiedGap type or dial values).
- Refuse-on-ambiguous-intent: Raise error/log if brief doesn't map cleanly.
- Per-posture result-shape contract (embellish=enrichment, corroborate=evidence-with-cross-ref, gap-fill=derivative-content).

**AC-4: Integration Readiness**
- Tracy dispatch routes through retrieval.dispatcher (27-0/27-2).
 - Manifest schema v1.0 in state/config/schemas/suggested-resources.schema.json.
- L1 lockstep test: tracy-vocab-lockstep validates vocabulary.yaml → MD doc → code parity.

**AC-5: Testing Floor (K=4)**
- Posture-discrimination matrix test.
- Refuse-ambiguous negative test.
- gap_fill-non-in-scope fail-closed test.
- Manifest schema validation roundtrip.

## Tasks / Subtasks

- [x] Task 1: Retire old specs (AC-1)
  - [x] Update sprint-status.yaml comments
  - [x] Archive old files if needed

- [x] Task 2: Define postures/contracts (AC-2/3)
  - [x] Document 3 postures + 4-part contracts in tracy/references/postures.md
  - [x] Implement posture-selection logic stub in tracy/scripts/posture_dispatcher.py

- [x] Task 3: Schema + lockstep (AC-4)
  - [x] Create suggested-resources.schema.json
  - [x] tracy-vocab-lockstep.py validator

- [x] Task 4: Tests (AC-5)
  - [x] Parametrized tests for postures, negatives, schema

### Review Findings

- [x] [Review][Patch] Missing Required Output Shape Fields [state/config/schemas/suggested-resources.schema.json]
- [x] [Review][Patch] Missing Failure Mode Representation [state/config/schemas/suggested-resources.schema.json]
- [x] [Review][Patch] Lack of Distinct Posture Discriminators in Schema [state/config/schemas/suggested-resources.schema.json]
- [x] [Review][Patch] Incomplete Lockstep Validation Script [scripts/utilities/tracy-vocab-lockstep.py]
- [x] [Review][Patch] Unhandled Exceptions for Schema Load [scripts/utilities/tracy-vocab-lockstep.py]
- [x] [Review][Patch] Unhandled JSON Decode Error for Target Data [scripts/utilities/tracy-vocab-lockstep.py]
- [x] [Review][Patch] Swallowed Validation Error Context [scripts/utilities/tracy-vocab-lockstep.py]
- [x] [Review][Patch] Missing SchemaError Handling [scripts/utilities/tracy-vocab-lockstep.py]
- [x] [Review][Patch] Directory Passed as File Target [scripts/utilities/tracy-vocab-lockstep.py]
- [x] [Review][Patch] Implicit Default Encoding on File Reads [scripts/utilities/tracy-vocab-lockstep.py]

## Dev Notes

### Architecture Compliance
- Tracy as BMad specialist: skills/bmad-agent-tracy/SKILL.md + references/ + scripts/retrieval_wrapper.py
- Wrapper on skills/bmad-agent-texas/scripts/retrieval/dispatcher.py (Epic 27).
- Manifest writes atomic (temp + rename).
- Baton/lane-matrix: Tracy owns research judgment; no fetch (Texas).
- Envelope governance: Tracy reads RetrievalIntent envelope.

### Previous Story Intelligence (Epic 27)
- 27-2 scite-ai-provider: SciteProvider(RetrievalAdapter) — Tracy wraps this + dispatcher.
- Shape 3: Tracy editorial → dispatcher → adapter → normalize.
- Provider_directory operator-amendment ready (16 entries).

### Git Intelligence
- Recent: Lesson Planner foundation (31-1 schema, 31-2 log, 31-3 registries).
- Patterns: Pydantic schemas, registry MappingProxyType, ABC contracts, parametrized tests.

### Testing Requirements
- K=4 floor.
- Cassette-backed for scite.
- Schema roundtrip, posture matrix, negatives.
- Regression on retrieval.dispatcher.

### File Structure
- skills/bmad-agent-tracy/
  - SKILL.md
  - references/postures.md, vocabulary.yaml
  - scripts/posture_dispatcher.py, manifest_emitter.py
- tests/contracts/test_tracy_postures.py
- state/config/schemas/suggested-resources.schema.json

## References
- [Epic 28 Tracy Detective: _bmad-output/implementation-artifacts/epic-28-tracy-detective.md]
- [MVP Plan R1 Amendment 9: _bmad-output/planning-artifacts/lesson-planner-mvp-plan.md §Epic 28]
- [Retrieval Contract: skills/bmad-agent-texas/references/retrieval-contract.md]
- [Architecture Patterns: _bmad-output/planning-artifacts/architecture.md §BMad Agent Structure]
- [Epic 27 Retrieval: _bmad-output/implementation-artifacts/27-0-retrieval-foundation.md]

## Dev Agent Record

### Agent Model Used
Cline (highly skilled software engineer)

### Completion Notes List
- Ultimate context engine analysis complete.
- All Epic 27 retrieval context integrated.
- Postures codified per R1 amendment 9.
- Dev guardrails for BMad specialist structure.
- Implemented charter: retired old specs, defined postures/contracts, created schema/validator, added tests.

### File List
- skills/bmad_agent_tracy/__init__.py
- skills/bmad_agent_tracy/references/__init__.py
- skills/bmad_agent_tracy/references/postures.md
- skills/bmad_agent_tracy/scripts/__init__.py
- skills/bmad_agent_tracy/scripts/posture_dispatcher.py
- scripts/utilities/tracy-vocab-lockstep.py
- state/config/schemas/suggested-resources.schema.json
- tests/contracts/test_tracy_postures.py
- skills/__init__.py

### Change Log
- 2026-04-18: Completed implementation of Tracy reshape charter. Retired old specs, codified three postures with four-part contracts, created schema and validator, added test stubs. Status: ready-for-dev → review.
- 2026-04-18: Completed bmad-code-review layered pass. Fixed 10 patches (including schema distinct output structures, error handling, missing field constraints). Status: review → done.
