# Story 29-3: Irene Blueprint Co-author

**Status:** done
**Closed:** 2026-04-18 (BMAD-closed)
**Created:** 2026-04-18
**Epic:** 29 - Enhanced Irene
**Sprint key:** `29-3-irene-blueprint-coauthor`
**Branch:** `dev/lesson-planner`
**Points:** 3
**Depends on:** **31-4 (done)** - consumes the concrete `BlueprintProducer`, its markdown artifact contract, and the stable human-review markers emitted by `marcus.lesson_plan.blueprint_producer`; **29-2 (done)** - keeps Irene's deterministic diagnostic voice and import seam inside `marcus.lesson_plan` rather than inventing a parallel private protocol.
**Related upstream/downstream surfaces:** **31-1**, **31-5**, **32-3** - 31-1 owns the `PlanUnit` contract that must carry the new optional sign-off pointer, 31-5 later consumes the pointer for the Quinn-R alternate branch, and 32-3's trial harness eventually needs a real co-authored blueprint acceptance path instead of a placeholder.
**Blocks:** **31-5** (Quinn-R two-branch gate) and the blueprint branch of the later trial-run acceptance path - both need a concrete sign-off pointer on `PlanUnit`, not just a raw markdown draft with unchecked boxes.

---

## TL;DR

Ship the minimal Irene-side co-authoring protocol for blueprint artifacts: validate a 31-4 `ProducedAsset`, write a deterministic sign-off sidecar artifact for Irene + writer approval, and emit a typed `plan_unit.blueprint_signoff` pointer so downstream stories can treat the blueprint branch as real and auditable.

## Story

As the **Lesson Planner MVP Irene blueprint co-author owner**,
I want **a deterministic co-authoring helper that turns a 31-4 blueprint draft into a signed-off pointer attached to the originating `PlanUnit`**,
So that **Quinn-R and the trial harness can tell the difference between "draft exists" and "Irene plus the human writer actually approved the blueprint branch."**

## Background - Why This Story Exists

31-4 intentionally stopped at the artifact seam. It proved the blueprint modality is real by emitting a markdown draft plus stable human-review markers, but it explicitly refused to invent the final `plan_unit.blueprint_signoff` pointer. That deferred seam is 29-3.

The key constraint is that 29-3 is not another blueprint producer. The draft already exists. 29-3's job is narrower:

- verify that the incoming artifact is really the 31-4 blueprint branch for this `PlanUnit`,
- capture a deterministic Irene + writer sign-off record in a stable sidecar artifact,
- attach a typed pointer to the `PlanUnit` so later stories can branch on "signed blueprint" without scraping markdown ad hoc.

That means this story is allowed one small schema extension on the Lesson Plan family: an optional `blueprint_signoff` field on `PlanUnit`. It should stay additive, reviewable, and minimal. It should not reopen 31-4's producer contract, emit anything to the Lesson Plan log, or pre-implement 31-5's gate logic.

## T1 Readiness

- **Gate mode:** `single-gate`
- **K floor:** `K = 6`
- **Target collecting-test range:** `8-9`
- **Required readings:** `docs/dev-guide/story-cycle-efficiency.md`, `docs/dev-guide/dev-agent-anti-patterns.md`, `docs/dev-guide/pydantic-v2-schema-checklist.md`
- **Scaffold required:** no - this is not a schema-story
- **Anti-pattern categories in scope:** hiding sign-off state in freeform markdown only; mutating the 31-4 draft in place without a typed pointer; inventing 31-5 gate logic inside 29-3; emitting directly to the Lesson Plan log; widening `PlanUnit` with an overbuilt workflow object instead of a minimal pointer
- **Runway / side-work dependency:** none - 31-4 and 29-2 already landed the only required seams

## Acceptance Criteria

### Behavioral / Contract (AC-B.*)

1. **AC-B.1 - Canonical co-author module.** A new module under `marcus/lesson_plan/` exposes the canonical 29-3 surface:
   - `coauthor_blueprint(...) -> PlanUnit`
   - a named exception type for invalid blueprint co-author inputs
   - helper(s) for deterministic sign-off artifact rendering kept local to the module

2. **AC-B.2 - Typed sign-off pointer on `PlanUnit`.** `marcus.lesson_plan.schema.PlanUnit` gains an optional `blueprint_signoff` field whose value is a typed pointer object, not a raw dict/string. The pointer is additive-only and machine-readable.

3. **AC-B.3 - Incoming blueprint artifact is validated.** The co-author path fails explicitly unless the supplied `ProducedAsset`:
   - has `modality_ref="blueprint"`,
   - targets the same `plan_unit.unit_id`,
   - points at an existing markdown artifact under the repo,
   - still carries the stable 31-4 review markers.

4. **AC-B.4 - Deterministic sign-off sidecar artifact.** `coauthor_blueprint(...)` writes one deterministic sign-off markdown artifact under a stable repo-relative output root and returns a `PlanUnit` copy whose `blueprint_signoff` pointer names both the 31-4 blueprint artifact and the new sign-off artifact.

5. **AC-B.5 - Irene + writer approval are explicit.** The sign-off pointer includes explicit Irene/writer approval booleans plus a timezone-aware `signed_at` timestamp. The sign-off markdown echoes both approval statements in stable, testable headings/markers.

6. **AC-B.6 - No direct emission or gate logic.** 29-3 does not emit to the Lesson Plan log, does not call `emit_fit_report(...)`, and does not implement 31-5's final pass/fail branch. It only prepares the typed pointer that 31-5 will later consume.

7. **AC-B.7 - Additive schema discipline only.** 29-3 may extend the Lesson Plan shape family only by adding the optional `blueprint_signoff` field / definition plus the matching schema snapshot and changelog updates. No breaking shape changes; no fit-report schema drift; no package-wide version churn.

8. **AC-B.8 - Canonical downstream import seam is explicit.** Downstream code can import the co-author seam via:

   ```python
   from marcus.lesson_plan.blueprint_coauthor import coauthor_blueprint
   ```

### Test / Verification (AC-T.*)

1. **AC-T.1 - Public-surface smoke.** A smoke test proves `coauthor_blueprint` imports cleanly and returns a `PlanUnit`.
2. **AC-T.2 - Sign-off pointer write contract.** A focused test proves a valid 31-4 blueprint asset yields a sign-off artifact on disk and an updated `plan_unit.blueprint_signoff` pointer.
3. **AC-T.3 - Asset mismatch rejection.** Tests cover non-blueprint assets, wrong `unit_id`, and missing artifact files.
4. **AC-T.4 - 31-4 review-marker dependency.** A test proves 29-3 rejects a blueprint markdown file that is missing the stable 31-4 review markers.
5. **AC-T.5 - Deterministic path contract.** With a fixed timestamp input, repeated co-author passes over the same unit and asset yield the same sign-off artifact path and pointer values.
6. **AC-T.6 - Schema pointer parity.** Contract tests prove `PlanUnit.blueprint_signoff` is present in the Pydantic model, present in `lesson_plan.v1.schema.json`, and remains optional.
7. **AC-T.7 - No direct emission boundary.** A grep or contract test proves 29-3 production code does not call log-emission surfaces directly.
8. **AC-T.8 - Timezone awareness.** `blueprint_signoff.signed_at` is timezone-aware.

### Closeout / Integration (AC-C.*)

1. **AC-C.1 - Repo-relative paths only.** Both the existing blueprint artifact path and the new sign-off artifact path are repo-relative strings suitable for downstream audit and test fixtures.
2. **AC-C.2 - 31-5 branch becomes straightforward.** After 29-3, 31-5 can answer "blueprint signed by Irene and writer?" through the typed pointer without scraping human prose.
3. **AC-C.3 - 31-4 remains untouched conceptually.** 29-3 consumes the 31-4 artifact contract as-is; it does not reopen the producer contract or rewrite the blueprint draft shape.

## File Impact (preliminary - refined at `bmad-dev-story`)

- **NEW:** `marcus/lesson_plan/blueprint_coauthor.py` - Irene + writer sign-off helper and deterministic sidecar emission
- **UPDATED:** `marcus/lesson_plan/schema.py` - optional `BlueprintSignoff` pointer on `PlanUnit`
- **UPDATED:** `marcus/lesson_plan/schema/lesson_plan.v1.schema.json` - additive optional pointer field + `$defs` entry
- **UPDATED:** `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` - additive Lesson Plan shape-family note for 29-3
- **UPDATED:** `tests/contracts/fixtures/lesson_plan/lesson_plan_v1_0.json`
- **UPDATED:** `tests/contracts/test_lesson_plan_json_schema_parity.py`
- **NEW:** `tests/test_blueprint_coauthor.py`
- **NEW:** `tests/contracts/test_blueprint_coauthor_no_emit_boundary.py`

## Tasks / Subtasks (preliminary - refined at `bmad-dev-story`)

- [x] T1 - Author the canonical 29-3 co-author module and validate the incoming 31-4 blueprint asset contract.
- [x] T2 - Add the minimal optional `BlueprintSignoff` pointer to `PlanUnit` and update the lesson-plan schema artifacts.
- [x] T3 - Emit the deterministic sign-off sidecar artifact and attach the typed pointer to the returned `PlanUnit`.
- [x] T4 - Add focused behavior + contract tests inside the `8-9` collecting-test target range.
- [x] T5 - Run focused regression and the single-gate post-dev review lane before closure.

## Test Plan

`tests_added >= K` with **K = 6**.

**Target range:** `8-9` collecting tests per `docs/dev-guide/story-cycle-efficiency.md`.

Keep the families tight:

- one smoke/import family,
- one sign-off write contract family,
- one mismatch / missing-artifact rejection family,
- one review-marker dependency family,
- one deterministic-path family,
- one schema-pointer parity family,
- one no-direct-emission boundary family.

If the count rises above 9, the Dev Agent Record must name the concrete extra coverage gap being purchased.

## Out of Scope

- Rewriting or re-rendering the 31-4 blueprint draft body.
- Quinn-R step-13 pass/fail logic; that is 31-5.
- Any log emission or Marcus-Orchestrator write-path work.
- Any Tracy or Marcus 4A behavior.
- Package-wide `marcus.lesson_plan.__init__` re-export expansion unless a concrete downstream need appears.

## Dependencies on Ruling Amendments / Prior Findings

- **Lesson Planner MVP plan / sprint-status contract** - 29-3 is the story that emits `plan_unit.blueprint_signoff`.
- **31-4 AC-C.2** - the blueprint artifact is sufficient for later co-authoring, but 31-4 did not invent the final sign-off pointer protocol.
- **Story-cycle-efficiency single-gate classification** - 29-3 is precedent-heavy and peripheral, so it remains single-gate with post-dev review only.

## Risks

- **Markdown-scrape risk:** if the only sign-off state lives in prose, 31-5 will have to re-parse brittle text. Mitigation: typed pointer on `PlanUnit`.
- **Overbuilt workflow risk:** trying to encode a whole multi-step editorial process in 29-3. Mitigation: one deterministic sidecar artifact, one pointer.
- **Schema churn risk:** widening the Lesson Plan family too broadly. Mitigation: one optional pointer field only, additive.

## Dev Notes

### Architecture

29-3 belongs in `marcus.lesson_plan` because the pointer it emits is part of the shared Lesson Plan contract, not a private Irene-only helper. The cleanest shape is:

- 31-4 continues to own the blueprint draft artifact.
- 29-3 validates that draft and emits a separate sign-off sidecar artifact.
- `PlanUnit.blueprint_signoff` points to both artifact paths and the Irene/writer approvals.

That keeps the draft and the approval record separate while giving downstream stories one typed place to look.

### Anti-patterns

- Do not mutate the 31-4 blueprint draft in place and call that the sign-off protocol.
- Do not store sign-off state only as raw markdown text with no typed pointer.
- Do not emit to the log from 29-3.
- Do not widen the pointer into a speculative 31-5 gate object.

### Canonical downstream import seam

Downstream code should be able to run:

```python
from marcus.lesson_plan.blueprint_coauthor import coauthor_blueprint
```

That import path is the completion handshake for 29-3.

## Governance Closure Gates

- [x] Acceptance criteria met.
- [x] Governance validator passes.
- [x] Single-gate workflow completed: create-story -> dev-story -> post-dev code review.
- [x] Status artifacts refreshed in closeout order.

## Dev Agent Record

**Executed by:** Codex, following the Amelia / `bmad-agent-dev` workflow locally.
**Date:** 2026-04-18.

### Landed artifacts

- `marcus/lesson_plan/blueprint_coauthor.py` - canonical 29-3 co-author seam, 31-4 artifact validation, deterministic sidecar emission, and typed `PlanUnit` update path.
- `marcus/lesson_plan/schema.py` - new `BlueprintSignoff` model plus optional `PlanUnit.blueprint_signoff`.
- `marcus/lesson_plan/schema/lesson_plan.v1.schema.json` - additive optional pointer field + `$defs.BlueprintSignoff`.
- `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` - additive Lesson Plan v1.0 extension note for 29-3.
- `tests/test_blueprint_coauthor.py` - focused behavior slice for co-author flow, rejection paths, marker dependency, and deterministic output path.
- `tests/contracts/test_blueprint_coauthor_no_emit_boundary.py` - no-direct-emission boundary pin.
- `tests/contracts/fixtures/lesson_plan/lesson_plan_v1_0.json` - snapshot updated for the optional `blueprint_signoff` field.
- `tests/contracts/test_lesson_plan_json_schema_parity.py` - parity extended for `BlueprintSignoff`.

### Verification

- Governance validator:
  `python scripts/utilities/validate_lesson_planner_story_governance.py _bmad-output/implementation-artifacts/29-3-irene-blueprint-coauthor.md`
  -> `PASS`
- Focused 29-3 + schema slice:
  `py -3.13 -m pytest tests/test_blueprint_coauthor.py tests/contracts/test_blueprint_coauthor_no_emit_boundary.py tests/contracts/test_lesson_plan_shape_stable.py tests/contracts/test_lesson_plan_json_schema_parity.py tests/contracts/test_lesson_plan_schema_version_field_present.py tests/test_blueprint_producer.py -q`
  -> `38 passed`
- Ruff:
  `ruff check marcus/lesson_plan/blueprint_coauthor.py marcus/lesson_plan/schema.py tests/test_blueprint_coauthor.py tests/contracts/test_blueprint_coauthor_no_emit_boundary.py tests/contracts/test_lesson_plan_json_schema_parity.py`
  -> `All checks passed`

### Completion Notes

- 29-3 stays narrow: it consumes the 31-4 draft, emits a deterministic sign-off sidecar, and attaches a typed pointer. It does not rewrite the draft body, emit to the log, or pre-implement 31-5 gate logic.
- The Lesson Plan shape-family change is additive only: `PlanUnit.blueprint_signoff` remains optional, so pre-29-3 plans still validate without migration.
- Collecting-test footprint stayed within policy: 8 new tests across the dedicated 29-3 files, which lands inside the `8-9` target range for `K = 6`.

## Review Record

### Single-gate post-dev code review

**Workflow:** `bmad-code-review`, executed locally over the 29-3 diff slice.
**Verdict:** clear after two applied hardening patches.

- **APPLY (already landed):**
  - Reject non-blueprint `PlanUnit` inputs explicitly instead of relying on the artifact alone to imply branch legitimacy.
  - Reject traversal-style `ProducedAsset.asset_path` values before filesystem access.
- **DEFER:** none
- **DISMISS:** none
