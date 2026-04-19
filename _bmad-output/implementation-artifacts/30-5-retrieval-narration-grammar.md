# Story 30-5: Retrieval Narration Grammar

**Status:** done
**Created:** 2026-04-19
**Closed:** 2026-04-19 (BMAD-closed)
**Epic:** 30 - Enhanced Marcus (duality + 4A loop)
**Sprint key:** `30-5-retrieval-narration-grammar`
**Branch:** `dev/lesson-planner`
**Points:** 2
**Depends on:** **28-2 (done)** - Tracy now emits the three real posture result shapes (`embellish`, `corroborate`, `gap-fill`) plus the ambiguity / fail-closed boundaries this story has to narrate cleanly; **29-2 (done)** - the diagnostician already names the source-fitness seam and keeps Marcus-side prose deterministic, so 30-5 should follow the same "small typed helper, no orchestration" discipline.
**Related upstream/downstream surfaces:** **30-3b**, **28-3**, **30-4** - 30-3b needs a real Marcus-side sentence layer before it can surface Tracy provenance in the 4A loop; 28-3 and 30-4 later consume the same research posture outcomes but should not reinvent the wording.
**Blocks:** **30-3b** - the dials + sync reassessment story explicitly depends on 30-5 landing first so Marcus can surface Tracy-provenance postures in Maya-facing language without ad hoc copy.

---

## TL;DR

Ship one narrow Marcus-side grammar module that turns Tracy posture results into one Maya-facing sentence per posture, with a single canonical import seam and a small focused test slice. This story is wording and contract only; it does not dispatch research, write to the log, or implement the 4A loop.

## Story

As the **Lesson Planner MVP Marcus wording owner for Tracy-backed research turns**,
I want **one deterministic sentence template per Tracy posture that Marcus can speak in Maya-facing voice**,
So that **30-3b can surface embellish / corroborate / gap-fill outcomes consistently without inventing copy inline or leaking Tracy's internal result shape into the live conversation surface**.

## Background - Why This Story Exists

The MVP plan inserted 30-5 because Sally flagged a real UX gap: Tracy can now return structured posture results, but Marcus still lacks a stable sentence layer for surfacing those outcomes in the voice Maya hears. Without that layer, 30-3b would either:

- hardcode fragile one-off copy directly into the 4A loop, or
- leak Tracy's internal posture/result shape into a Maya-facing path.

30-5 fixes that gap before 30-3b opens. The implementation should stay narrow:

- consume a Tracy-style posture result,
- normalize the posture naming seam (`gap-fill` vs `gap_fill`) without reopening 28-2,
- render one sentence template per posture with consistent cadence,
- reject unusable inputs explicitly so 30-3b can choose its own fallback behavior later.

This story is **not** a retry/fallback design story, not a Tracy dispatch story, and not a 4A orchestration story. It is the wording seam that those later stories depend on.

## T1 Readiness

- **Gate mode:** `single-gate`
- **K floor:** `K = 4`
- **Target collecting-test range:** `5-6`
- **Required readings:** `docs/dev-guide/story-cycle-efficiency.md`, `docs/dev-guide/dev-agent-anti-patterns.md`, `docs/dev-guide/pydantic-v2-schema-checklist.md`
- **Scaffold required:** no - this is not a schema-story
- **Anti-pattern categories in scope:** inventing 30-3b dialogue flow inside 30-5; leaking internal routing or Tracy jargon into Maya-facing copy; branching into one-off special-case prose per result shape instead of one template per posture; mutating Tracy result payloads instead of reading them; hiding invalid inputs behind permissive fallback text
- **Runway / side-work dependency:** none - 28-2 and 29-2 already landed the only upstream seams needed here

## Acceptance Criteria

### Behavioral / Contract (AC-B.*)

1. **AC-B.1 - Canonical grammar module.** A new production module lands at `marcus/lesson_plan/retrieval_narration_grammar.py` and exposes the canonical 30-5 surface for turning a Tracy result payload into a Marcus sentence.

2. **AC-B.2 - One sentence template per posture.** The module renders exactly one consistent sentence template for each supported posture:
   - `embellish`
   - `corroborate`
   - `gap-fill` / `gap_fill` (normalized to the same branch)

3. **AC-B.3 - Corroborate stays one template with classification slots.** The corroborate branch may vary only by a small classification slot (`supporting`, `contrasting`, `mentioning` or equivalent wording), not by whole-template branching. This preserves the "one template per posture" rule while still surfacing whether the evidence supports, challenges, or merely discusses the claim.

4. **AC-B.4 - Marcus voice discipline.** Every rendered sentence is Maya-facing and consistent with the established Marcus voice discipline:
   - first person singular,
   - present tense,
   - no internal routing tokens (`intake`, `orchestrator`),
   - ends as an invitation to proceed.

5. **AC-B.5 - Narrow input contract.** The canonical renderer accepts a Tracy-style result mapping and reads only the fields needed for wording:
   - `status`
   - `posture`
   - corroborate classification when present
   It does not depend on broader orchestrator state, log state, or lesson-plan mutation.

6. **AC-B.6 - Explicit rejection of unusable inputs.** The module raises a named error for:
   - unknown posture values,
   - non-success Tracy results,
   - malformed corroborate payloads with missing classification
   30-5 does not invent the recovery UX; later stories can decide how to fallback.

7. **AC-B.7 - Canonical downstream import seam.** Downstream code can import the wording seam through:

   ```python
   from marcus.lesson_plan.retrieval_narration_grammar import render_retrieval_narration
   ```

8. **AC-B.8 - No orchestration side effects.** 30-5 does not dispatch retrieval, emit to the lesson-plan log, touch `marcus.facade`, or open any 4A loop state. It is a pure wording/helper seam only.

### Test / Verification (AC-T.*)

1. **AC-T.1 - Embellish template pin.** A focused test proves a successful Tracy embellish payload renders the pinned embellish sentence shape.
2. **AC-T.2 - Corroborate classification matrix.** A parametrized test proves the corroborate template stays structurally identical while the classification slot varies across supporting / contrasting / mentioning.
3. **AC-T.3 - Gap-fill normalization pin.** A focused test proves both `gap-fill` and `gap_fill` route to the same gap-fill sentence template.
4. **AC-T.4 - Non-success payload rejection.** A focused test proves failed Tracy results are rejected explicitly rather than rendered as if they were usable.
5. **AC-T.5 - Unknown posture rejection.** A focused test proves unknown posture strings fail with the named error.
6. **AC-T.6 - Voice-register contract.** A contract-style test proves the rendered sentences stay first-person, avoid internal routing tokens, and end in an invitation/question shape.

### Closeout / Integration (AC-C.*)

1. **AC-C.1 - 30-3b handoff is straightforward.** After 30-5, 30-3b can surface Tracy posture outcomes by calling one renderer rather than inventing wording inline.
2. **AC-C.2 - Tracy result shapes remain the source of truth.** 30-5 consumes 28-2's posture outputs as-is; it does not reopen Tracy contracts.
3. **AC-C.3 - No schema/version churn.** 30-5 does not change Lesson Plan schema families, fit-report carriers, or package-wide version fields.

## File Impact (preliminary - refined at `bmad-dev-story`)

- **NEW:** `marcus/lesson_plan/retrieval_narration_grammar.py` - canonical posture-to-sentence renderer
- **NEW:** `tests/test_retrieval_narration_grammar.py`
- **NEW:** `tests/contracts/test_retrieval_narration_grammar_voice_register.py`

## Tasks / Subtasks (preliminary - refined at `bmad-dev-story`)

- [x] T1 - Author the canonical retrieval narration grammar module with a named error and a single public renderer.
- [x] T2 - Implement the three posture branches with one template per posture and a normalized gap-fill seam.
- [x] T3 - Add focused behavior + contract tests inside the `5-6` collecting-test target range.
- [x] T4 - Run focused verification and the single-gate post-dev review lane before closure.

## Test Plan

`tests_added >= K` with **K = 4**.

**Target range:** `5-6` collecting tests per `docs/dev-guide/story-cycle-efficiency.md`.

Keep the families tight:

- one embellish family,
- one corroborate classification family,
- one gap-fill normalization family,
- one invalid-input family,
- one voice-register family.

If the count rises above 6, the Dev Agent Record must name the concrete extra coverage gap being purchased.

## Out of Scope

- Tracy dispatch behavior or result-shape redesign.
- `30-3b` conversation flow, retries, or fallback UX.
- Any lesson-plan log emission or orchestrator write-path work.
- Any `marcus.facade` mutation or live 4A loop implementation.
- Any schema bump or package-wide contract rewrite.

## Dependencies on Ruling Amendments / Prior Findings

- **R1 amendment 3** - 30-5 exists specifically because Marcus needs a stable posture-sentence layer before 30-3b.
- **28-2 closure** - Tracy's three-mode contract is already real; 30-5 should consume it, not reinterpret it.
- **Story-cycle-efficiency single-gate classification** - 30-5 remains single-gate because it is a narrow sentence-template story, not a foundation or integration refactor.

## Risks

- **Ad hoc copy risk:** 30-3b could otherwise invent wording inline. Mitigation: ship one canonical renderer now.
- **Voice leak risk:** internal routing or Tracy jargon could surface to Maya. Mitigation: explicit voice-register contract test.
- **Shape drift risk:** later callers might pass malformed results silently. Mitigation: named explicit rejection on unusable inputs.

## Dev Notes

### Architecture

30-5 belongs in `marcus.lesson_plan` because it is a shared wording seam for the Lesson Planner path, but it should remain pure and lightweight. The right implementation shape is:

- a named error type,
- one public renderer,
- small private helpers for posture normalization and corroborate classification wording.

The renderer should consume a Tracy-style mapping and return one sentence string. Nothing more is needed for this story.

### Anti-patterns

- Do not call Tracy from 30-5.
- Do not import `LessonPlanLog` or write-path surfaces.
- Do not turn one posture into multiple whole-template variants.
- Do not swallow invalid inputs and render a vague sentence anyway.
- Do not touch `marcus.facade`; 30-3a / 30-3b own the live conversation surface.

### Canonical downstream import seam

Downstream code should be able to run:

```python
from marcus.lesson_plan.retrieval_narration_grammar import render_retrieval_narration
```

That import path is the completion handshake for 30-5.

## Governance Closure Gates

- [x] Acceptance criteria met.
- [x] Governance validator passes.
- [x] Single-gate workflow completed: create-story -> dev-story -> post-dev code review.
- [x] Status artifacts refreshed in closeout order.

## Dev Agent Record

**Executed by:** Codex, following the Amelia / `bmad-agent-dev` workflow locally.
**Date:** 2026-04-19.

### Landed artifacts

- `marcus/lesson_plan/retrieval_narration_grammar.py` - canonical Marcus-side renderer with one template per posture, normalized `gap-fill` seam, and explicit rejection of unusable Tracy payloads.
- `tests/test_retrieval_narration_grammar.py` - focused behavior slice for embellish, corroborate classification, gap-fill normalization, and invalid-input rejection.
- `tests/contracts/test_retrieval_narration_grammar_voice_register.py` - voice-register contract pin across the three successful posture branches.

### Verification

- Governance validator:
  `python scripts/utilities/validate_lesson_planner_story_governance.py _bmad-output/implementation-artifacts/30-5-retrieval-narration-grammar.md`
  -> `PASS`
- Focused 30-5 slice:
  `py -3.13 -m pytest tests/test_retrieval_narration_grammar.py tests/contracts/test_retrieval_narration_grammar_voice_register.py -q`
  -> `12 passed`
- Ruff:
  `ruff check marcus/lesson_plan/retrieval_narration_grammar.py tests/test_retrieval_narration_grammar.py tests/contracts/test_retrieval_narration_grammar_voice_register.py`
  -> `All checks passed`
- Pre-commit:
  `pre-commit run --files marcus/lesson_plan/retrieval_narration_grammar.py tests/test_retrieval_narration_grammar.py tests/contracts/test_retrieval_narration_grammar_voice_register.py _bmad-output/implementation-artifacts/30-5-retrieval-narration-grammar.md _bmad-output/implementation-artifacts/sprint-status.yaml`
  -> passed

### Completion Notes

- The implementation stayed intentionally narrow: one pure helper module, one named error, and no touch to the active 30-2b intake/orchestrator surfaces.
- The corroborate branch keeps one template while varying only the classification phrase, which satisfies Sally's "one template per posture" requirement without flattening supporting vs contrasting nuance.
- Collecting-test footprint landed inside policy: 5 collecting functions / 12 nodeids for `K = 4` and target range `5-6`.

## Review Record

### Single-gate post-dev code review

**Workflow:** local `bmad-code-review` style review over the 30-5 diff slice.
**Verdict:** clear with no material findings.

- **Blind Hunter:** clear - the module stays pure and introduces no hidden dispatch, log, or facade seam.
- **Edge Case Hunter:** clear - posture normalization, failed-status rejection, and missing corroborate classification are all pinned explicitly.
- **Acceptance Auditor:** clear - each accepted posture has a direct pin and the voice-register contract is covered separately.
- **APPLY:** none
- **DEFER:** none
- **DISMISS:** none
