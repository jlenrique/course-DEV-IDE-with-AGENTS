# Story 31-5: Quinn-R Two-Branch Gate

**Status:** done
**Closed:** 2026-04-19 (BMAD-closed)
**Created:** 2026-04-19
**Epic:** 31 - Tri-phasic contract primitives + gates (FOUNDATION)
**Sprint key:** `31-5-quinn-r-two-branch`
**Branch:** `dev/lesson-planner`
**Points:** 5
**Depends on:** **31-1 (done)** - consumes `LessonPlan`, `PlanUnit`, `PlanRef`, and the locked scope/rationale contract; **31-4 (done)** - consumes real blueprint artifacts and the review-marker discipline established by the blueprint branch.
**Related upstream/downstream surfaces:** **29-2**, **29-3**, **30-4**, **32-1**, **32-3** - 29-2 consumes prior Declined rationales, 29-3 emits `blueprint_signoff`, 30-4 later fans plan outcomes downstream, 32-1 inserts the 4A baton handoff, and 32-3 needs a concrete step-13 gate for the trial-run smoke path.
**Blocks:** **32-1** (workflow wiring), **32-3** (trial-run smoke harness), and the final blueprint/Declined branch of the Lesson Planner MVP acceptance path - those stories need a concrete step-13 gate artifact rather than prose-only gate logic.

---

## TL;DR

Ship a deterministic Quinn-R step-13 gate that evaluates every `PlanUnit` against one of two accepted branches: a non-blueprint unit passes only if a produced asset has already cleared quality review, while a blueprint unit passes only if Irene + writer sign-off has been recorded. Out-of-scope units stay in the tree as audited Declined nodes, and the gate emits a machine-readable carry-forward record that 29-2 can preload on the next run.

## Story

As the **Lesson Planner MVP step-13 quality-gate owner**,
I want **a real Quinn-R two-branch gate that classifies each plan unit into quality-passed, blueprint-signed, or Declined-with-rationale**,
So that **trial-run acceptance has a concrete per-unit gate, out-of-scope decisions remain auditable, and Irene can reuse prior Declined rationales instead of re-diagnosing settled ground from scratch**.

## Background - Why This Story Exists

31-4 and 29-3 made the blueprint branch real: there is now a concrete blueprint artifact plus a typed `blueprint_signoff` pointer. 29-2 also already named the carry-forward seam for prior Declined rationales, but that seam currently has no authoritative producer. 31-5 is the story that closes both gaps.

The MVP plan is explicit that the Quinn-R gate is not a whole-plan thumbs-up. It is a **per-unit assertion**:

- produced asset passes quality, or
- blueprint was reviewed and signed by Irene plus the writer.

That means the gate has to stay unit-granular and audit-friendly. It also cannot "drop" out-of-scope units just because they do not need a produced asset. Declined units remain first-class plan members with a preserved rationale. Their role in 31-5 is to produce a durable audit trail and a carry-forward payload that 29-2 can consume later.

Two boundaries matter:

- **31-5 must not impersonate Quinn-R's broader quality-review system.** The story only needs a deterministic gate surface that consumes already-known quality-pass facts for produced assets.
- **31-5 must not rewrite schema families.** The schema carriers already exist in 31-1 and 29-3. The story should add gate logic and emitted audit artifacts, not a new Lesson Plan schema version.

## T1 Readiness

- **Gate mode:** `dual-gate`
- **K floor:** `K = 8`
- **Target collecting-test range:** `10-12`
- **Required readings:** `docs/dev-guide/story-cycle-efficiency.md`, `docs/dev-guide/dev-agent-anti-patterns.md`, `docs/dev-guide/pydantic-v2-schema-checklist.md`
- **Scaffold required:** no - this is not a schema-story
- **Anti-pattern categories in scope:** silently dropping out-of-scope units from the gate; treating a blueprint draft as equivalent to a blueprint sign-off; leaking 31-5 logic into 29-3 or 32-1; mutating the live `LessonPlan` while evaluating step-13; inventing a new schema family instead of reusing 31-1 + 29-3 carriers
- **Runway / side-work dependency:** none - 31-1, 31-4, and 29-3 already landed the input surfaces this gate consumes

## Acceptance Criteria

### Behavioral / Contract (AC-B.*)

1. **AC-B.1 - Canonical Quinn-R gate module.** A new module under `marcus/lesson_plan/` exposes the canonical 31-5 surface:
   - a deterministic per-unit gate evaluator,
   - typed result models for the gate summary and the per-unit verdict,
   - a helper that extracts prior Declined rationales in a format directly consumable by 29-2,
   - and a deterministic artifact-emission helper for the step-13 audit record.

2. **AC-B.2 - Per-unit verdicts preserve plan order.** Evaluating a `LessonPlan` emits exactly one gate verdict per `PlanUnit`, preserving input order. The gate summary also exposes an overall `passed` boolean derived from the ordered unit-level verdicts.

3. **AC-B.3 - Non-blueprint branch requires a quality-passed produced asset.** For any unit whose `scope_decision.scope` is not `blueprint` and not `out-of-scope`, the gate passes only when:
   - at least one `ProducedAsset` exists for that unit, and
   - at least one of that unit's asset refs has been explicitly marked quality-passed.
   Missing assets or missing quality-pass facts fail the unit explicitly.

4. **AC-B.4 - Blueprint branch requires completed sign-off.** For any unit whose `scope_decision.scope == "blueprint"`, the gate passes only when `plan_unit.blueprint_signoff` exists and records both `irene_review_complete=True` and `writer_signoff_complete=True`. A blueprint draft by itself is not enough.

5. **AC-B.5 - Declined units remain audited, not omitted.** For any unit whose `scope_decision.scope == "out-of-scope"`, the gate does not demand a produced asset. Instead it emits a Declined audit record that preserves:
   - `unit_id`
   - the plan-unit rationale verbatim
   - enough context for later carry-forward use
   Units without a Declined rationale fail explicitly; "out-of-scope with empty why" is not admissible.

6. **AC-B.6 - 29-2 carry-forward seam is concrete.** The gate result exposes prior Declined rationales in a typed form that can be passed directly into `diagnose_lesson_plan(..., prior_declined_rationales=...)` without adapter glue or schema guessing.

7. **AC-B.7 - Deterministic emitted audit artifact.** A helper emits one deterministic JSON artifact under a stable repo-relative output path for the gate result. The artifact includes:
   - fresh `plan_ref`
   - overall gate verdict
   - ordered per-unit verdicts
   - ordered Declined-rationale carry-forward entries
   - timezone-aware `evaluated_at`

8. **AC-B.8 - No schema bump in 31-5.** 31-5 consumes `LessonPlan`, `ProducedAsset`, and `BlueprintSignoff` as already defined. It does not change `lesson_plan.v1.schema.json`, `ProducedAsset`, or the fit-report transport.

9. **AC-B.9 - Canonical downstream import seam is explicit.** Downstream code can import the gate via:

   ```python
   from marcus.lesson_plan.quinn_r_gate import evaluate_quinn_r_two_branch_gate
   ```

### Test / Verification (AC-T.*)

1. **AC-T.1 - Public-surface smoke.** A smoke test proves the canonical evaluation helper imports cleanly and returns typed gate-result models.
2. **AC-T.2 - Produced-asset branch passes with explicit quality approval.** A non-blueprint unit with a matching produced asset and a quality-passed asset ref clears the gate.
3. **AC-T.3 - Produced-asset branch fails without quality approval.** A non-blueprint unit with no approved asset fails explicitly and records the missing-approval reason.
4. **AC-T.4 - Blueprint branch requires sign-off.** A blueprint-scoped unit with completed Irene + writer sign-off passes; the same unit without completed sign-off fails.
5. **AC-T.5 - Declined audit emission.** An out-of-scope unit with a non-empty rationale produces a carry-forward Declined record and does not require a produced asset.
6. **AC-T.6 - Empty Declined rationale is rejected.** An out-of-scope unit with an empty rationale fails explicitly.
7. **AC-T.7 - Ordered carry-forward seam.** The helper that extracts prior Declined rationales returns `PriorDeclinedRationale` entries in plan order.
8. **AC-T.8 - Deterministic artifact emission.** Re-emitting the gate result with the same fixed timestamp yields byte-identical JSON content and stable artifact path.
9. **AC-T.9 - No direct log-emission boundary.** A contract or grep test proves 31-5 production code does not call the 31-2 log write path.
10. **AC-T.10 - Package export seam.** If `marcus.lesson_plan.__init__` is updated, tests pin the export surface directly.

### Closeout / Integration (AC-C.*)

1. **AC-C.1 - Repo-relative artifact path.** The emitted step-13 artifact lives at a stable repo-relative path suitable for manual inspection and downstream tests.
2. **AC-C.2 - 29-2 seam remains narrow.** 31-5 emits carry-forward Declined rationales only; it does not alter 29-2's diagnostician logic.
3. **AC-C.3 - 32-1 / 32-3 branch becomes testable.** The emitted gate result is concrete enough for workflow wiring and trial-run smoke tests to consume without reopening 31-5 design questions.

## File Impact (preliminary - refined at `bmad-dev-story`)

- **NEW:** `marcus/lesson_plan/quinn_r_gate.py` - per-unit step-13 gate logic + deterministic audit-artifact emission + Declined carry-forward seam
- **UPDATED:** `marcus/lesson_plan/__init__.py` - optional package re-exports for the canonical 31-5 public surface
- **NEW:** `tests/test_quinn_r_gate.py`
- **NEW:** `tests/contracts/test_quinn_r_gate_no_log_boundary.py`
- **NEW:** `tests/contracts/test_lesson_plan_package_exports_31_5.py` (only if package re-exports are added)

## Tasks / Subtasks (preliminary - refined at `bmad-dev-story`)

- [x] T1 - Author the canonical `quinn_r_gate` module with typed result models and the per-unit evaluation helper.
- [x] T2 - Implement the produced-asset quality-pass branch for non-blueprint units.
- [x] T3 - Implement the blueprint-signoff branch and the Declined-with-rationale audit branch.
- [x] T4 - Emit the deterministic step-13 JSON artifact and the 29-2 carry-forward seam.
- [x] T5 - Add focused unit + contract tests inside the `10-12` collecting-test target range.
- [x] T6 - Run focused regression and complete the dual-gate review lane before closure.

## Test Plan

`tests_added >= K` with **K = 8**.

**Target range:** `10-12` collecting tests per `docs/dev-guide/story-cycle-efficiency.md`.

Keep the families tight:

- one smoke/public-surface family,
- one produced-asset branch family,
- one blueprint-signoff branch family,
- one Declined audit family,
- one carry-forward seam family,
- one deterministic artifact family,
- one no-log-emission boundary family,
- one package-export family only if needed.

If the count rises above 12, the Dev Agent Record must name the specific extra coverage gap being purchased.

## Out of Scope

- Implementing Quinn-R's broader quality reviewer logic or scoring dimensions.
- Replacing 29-3's blueprint sign-off protocol.
- Reworking 31-2's log write path or emitting log events directly.
- Any 32-1 workflow-runner wiring.
- Any schema version bump for Lesson Plan carriers.

## Dependencies on Ruling Amendments / Prior Findings

- **R1 amendment 15** - Declined-with-rationale must become a concrete producer/consumer seam across 31-5 and 29-2.
- **31-4 / 29-3 landing state** - blueprint draft and sign-off are already real; 31-5 should consume them, not reinterpret them.
- **Story-cycle-efficiency dual-gate classification** - 31-5 remains dual-gate because a gate bug would poison the trial-run PDG.

## Risks

- **False-equivalence risk:** treating a blueprint draft as if it were already sign-off complete. Mitigation: explicit blueprint branch check on `blueprint_signoff`.
- **Audit-loss risk:** dropping Declined units from the gate summary because they produce no asset. Mitigation: make Declined audit a first-class branch.
- **Schema-sprawl risk:** inventing a new schema family just to serialize the result. Mitigation: keep 31-5 artifact-local and deterministic.
- **Cross-lane risk:** reaching into Epic 30 runtime wiring while 32-1 is still backlog. Mitigation: keep 31-5 at the artifact + decision layer only.

## Dev Notes

### Architecture

31-5 should stay inside `marcus.lesson_plan` because it consumes the shared Lesson Plan schema family, `ProducedAsset`, and `BlueprintSignoff`, and because 29-2 already imports from that package. The narrow implementation shape is:

- evaluate one plan at a time,
- accept the current `LessonPlan`,
- accept the currently available `ProducedAsset` list and a set of quality-passed asset refs,
- emit one ordered gate summary plus one deterministic artifact.

The gate should prefer explicit, typed results over a bag of dicts. 29-2's carry-forward seam already gives us the exact type worth reusing for Declined-rationale export: `PriorDeclinedRationale`.

### Anti-patterns

- Do not call 31-2 log write surfaces from 31-5.
- Do not mutate `plan_unit.blueprint_signoff` or any other part of the incoming `LessonPlan`.
- Do not silently treat missing quality approval as equivalent to "not reviewed yet but okay."
- Do not serialize a new lesson-plan schema family just to emit the result artifact.
- Do not make blueprint units pass through the plain produced-asset branch; they need completed sign-off.

### Canonical downstream import seam

Downstream code should be able to run:

```python
from marcus.lesson_plan.quinn_r_gate import (
    evaluate_quinn_r_two_branch_gate,
    emit_quinn_r_gate_artifact,
    extract_prior_declined_rationales,
)
```

That import path is the completion handshake for 31-5.

## Governance Closure Gates

- [x] Acceptance criteria met.
- [x] Governance validator passes.
- [x] Dual-gate workflow completed: create-story -> dev-story -> post-dev code review.
- [x] Status artifacts refreshed in closeout order.

## Dev Agent Record

**Executed by:** Codex, following the Amelia / `bmad-agent-dev` workflow locally.
**Date:** 2026-04-19.

### Landed artifacts

- `marcus/lesson_plan/quinn_r_gate.py` - canonical step-13 gate with typed result models, produced-asset branch, blueprint-signoff branch, Declined audit branch, deterministic JSON rendering, and 29-2 carry-forward extraction helper.
- `marcus/lesson_plan/__init__.py` - package exports extended with the 31-5 public seam.
- `tests/test_quinn_r_gate.py` - focused behavior suite covering all three gate branches plus deterministic artifact emission.
- `tests/contracts/test_quinn_r_gate_no_log_boundary.py` - no-direct-log-emission contract.
- `tests/contracts/test_lesson_plan_package_exports_31_5.py` - package export pin.

### Verification

- Governance validator:
  `python scripts/utilities/validate_lesson_planner_story_governance.py _bmad-output/implementation-artifacts/31-5-quinn-r-two-branch.md`
- Focused 31-5 slice:
  `py -3.13 -m pytest tests/test_quinn_r_gate.py tests/contracts/test_quinn_r_gate_no_log_boundary.py tests/contracts/test_lesson_plan_package_exports_31_5.py -q`
  -> `11 passed`
- Focused seam regression:
  `py -3.13 -m pytest tests/test_quinn_r_gate.py tests/contracts/test_quinn_r_gate_no_log_boundary.py tests/contracts/test_lesson_plan_package_exports_31_5.py tests/test_blueprint_coauthor.py tests/test_gagne_diagnostician.py -q`
  -> `31 passed`
- Ruff:
  `ruff check marcus/lesson_plan/quinn_r_gate.py marcus/lesson_plan/__init__.py tests/test_quinn_r_gate.py tests/contracts/test_quinn_r_gate_no_log_boundary.py tests/contracts/test_lesson_plan_package_exports_31_5.py`
  -> `All checks passed`
- Pre-commit:
  `pre-commit run --files marcus/lesson_plan/quinn_r_gate.py marcus/lesson_plan/__init__.py tests/test_quinn_r_gate.py tests/contracts/test_quinn_r_gate_no_log_boundary.py tests/contracts/test_lesson_plan_package_exports_31_5.py _bmad-output/implementation-artifacts/31-5-quinn-r-two-branch.md _bmad-output/implementation-artifacts/sprint-status.yaml`
  -> passed (`ruff`, orphan-reference detector, co-commit invariant)

### Completion Notes

- The gate stayed narrow: it consumes existing `LessonPlan`, `ProducedAsset`, and `BlueprintSignoff` seams without bumping schema families or touching the 31-2 log path.
- Blueprint units now require actual Irene + writer sign-off at step 13 rather than being treated as equivalent to a plain produced asset.
- Declined units stay first-class in the emitted result and produce ordered `PriorDeclinedRationale` entries that 29-2 can preload directly on the next run.
- Collecting-test footprint landed inside policy: 11 tests across the dedicated 31-5 slice for `K = 8` / target `10-12`.

## Review Record

### Dual-gate pre-dev review

**Mode:** local party-mode synthesis before `bmad-dev-story`.
**Verdict:** GREEN.

- **Winston:** GREEN - keep the result typed and artifact-local; this is a gate consumer, not a new schema family.
- **Murat:** GREEN - test the three real branches directly and keep the count inside the `10-12` target band.
- **Paige:** GREEN - Declined rationale must remain verbatim and the emitted artifact should be legible to future reviewers.
- **Quinn:** GREEN - blueprint draft is not enough; only completed Irene + writer sign-off should satisfy the alternate branch.

No pre-dev riders were required after governance validation passed.

### Post-dev code review

**Workflow:** `bmad-code-review`, executed locally in layered form.
**Verdict:** clear - no material findings after focused regression and boundary review.

- **Blind Hunter:** no structural bugs in the new typed gate surface or artifact emission helper.
- **Edge Case Hunter:** the high-value edge cases were missing scope, missing Declined rationale, missing quality approval, and missing blueprint sign-off. All are covered and pass/fail explicitly.
- **Acceptance Auditor:** the implementation satisfies the intended split: produced-asset branch for non-blueprint units, sign-off branch for blueprint units, Declined audit branch for out-of-scope units, and no log-write leakage.

**Triage summary**

- **APPLY:** 0
- **DEFER:** 0
- **DISMISS:** 0
