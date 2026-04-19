# Story 31-4: Blueprint Producer

**Status:** done
**Closed:** 2026-04-18 (BMAD-closed)
**Created:** 2026-04-18
**Epic:** 31 - Tri-phasic contract primitives + gates (FOUNDATION)
**Sprint key:** `31-4-blueprint-producer`
**Branch:** `dev/lesson-planner`
**Points:** 5
**Depends on:** **31-3 (done)** - consumes `ModalityProducer`, `ProductionContext`, `ProducedAsset`, `ModalityRef="blueprint"`, and the registry backfill seam for `producer_class_path`.
**Blocks:** **29-3** (Irene blueprint co-author), **31-5** (Quinn-R two-branch gate), and the blueprint branch of the later trial-run acceptance path - those stories need a real produced blueprint artifact rather than a placeholder.

---

## TL;DR

Ship the first concrete `ModalityProducer`: a `BlueprintProducer` that turns a `PlanUnit` marked for blueprint handling into a markdown blueprint artifact with a deterministic prompt/template fill and an explicit human-review checkpoint, then returns a valid `ProducedAsset` for downstream fanout and Quinn-R gating.

## Story

As the **Lesson Planner MVP blueprint-production owner**,
I want **a minimal but real blueprint producer that implements the 31-3 `ModalityProducer` contract and emits a markdown blueprint artifact with a required human-review checkpoint**,
So that **Marcus can route blueprint-scoped plan units to a concrete producer, downstream stories can consume a real blueprint asset instead of hand-waved placeholders, and the MVP trial path has a reviewable "APP can't produce the final deliverable alone" branch.**

## Background - Why This Story Exists

31-3 intentionally stopped at the contract seam: it shipped the closed modality registry, the `ModalityProducer` ABC, `ProductionContext`, and `ProducedAsset`, but it left the first real producer implementation for 31-4. The plan holds 31-4 as a single 5-point story because the work is human-review-driven rather than architecture-heavy: the producer writes a blueprint markdown artifact, marks the human checkpoint explicitly, and returns a `ProducedAsset` that downstream consumers can reason over.

Two constraints matter more than feature breadth here:

- **The blueprint path must be concrete.** Downstream work cannot keep pretending that "blueprint" is a modality if there is no artifact, no file path, and no producer class path in the registry.
- **The human-review loop must stay explicit.** The producer may draft the artifact, but the artifact has to make the sign-off checkpoint obvious so later stories can accept the branch cleanly without implying that the system fully auto-produced the instructional asset.

31-4 therefore should stay narrow:

- one concrete producer implementation,
- one blueprint-specific context seam if truly needed,
- one markdown output format,
- one deterministic fill strategy with an injectable drafting seam,
- one explicit human-review checkpoint in the artifact body,
- one registry backfill for `blueprint`.

It should not try to solve 29-3's co-authoring protocol or 31-5's final acceptance logic. Those stories consume the artifact 31-4 emits.

## T1 Readiness

- **Gate mode:** `dual-gate`
- **K floor:** `K = 8`
- **Target collecting-test range:** `10-12`
- **Required readings:** `docs/dev-guide/story-cycle-efficiency.md`, `docs/dev-guide/dev-agent-anti-patterns.md`, `docs/dev-guide/pydantic-v2-schema-checklist.md`
- **Scaffold required:** no - this is not a schema-story
- **Anti-pattern categories in scope:** under-specified ABC implementation that forces a later story split; fake "LLM" behavior with no deterministic seam; writing a blueprint artifact that hides the human-review requirement; mutating `PlanUnit` / `ProductionContext` during production; widening 31-4 into 29-3's co-authoring or 31-5's gate logic
- **Runway / side-work dependency:** none - 31-3 closed the only hard prerequisite, and 30-1 can proceed independently in the Marcus refactor lane

## Acceptance Criteria

### Behavioral / Contract (AC-B.*)

1. **AC-B.1 - Canonical producer module.** A new module under `marcus/lesson_plan/` exposes the canonical 31-4 production surface:
   - `BlueprintProducer(ModalityProducer)`
   - a minimal blueprint-specific context seam only if needed beyond `ProductionContext`
   - helper(s) for deterministic blueprint markdown rendering and review-checkpoint emission kept local to the module

2. **AC-B.2 - ABC compliance and registry backfill.** `BlueprintProducer` is a concrete `ModalityProducer` with:
   - `modality_ref = "blueprint"`
   - `status = "ready"`
   - `produce(plan_unit, context) -> ProducedAsset`
   and `MODALITY_REGISTRY["blueprint"].producer_class_path` is backfilled to the canonical dotted import path for this class.

3. **AC-B.3 - Blueprint-only scope guard.** The producer fails explicitly when asked to produce a non-blueprint target. At minimum, the implementation rejects any `PlanUnit` whose `scope_decision` is present and not blueprint-aligned, or whose `modality_ref` conflicts with `"blueprint"`. It must not silently produce artifacts for unrelated modalities.

4. **AC-B.4 - Deterministic markdown artifact.** `produce(...)` writes one markdown artifact per `PlanUnit` to a deterministic repo-relative output path and returns a matching `ProducedAsset`. The markdown includes, at minimum:
   - a stable title/header derived from the plan unit,
   - a concise summary of the source lesson-plan context,
   - a structured blueprint body filled through a deterministic template/fill seam,
   - an explicit human-review checkpoint section.

5. **AC-B.5 - Human-review checkpoint is first-class.** The emitted markdown contains a named review section that makes it clear the artifact is a blueprint draft awaiting human sign-off. The checkpoint must be machine-locatable by tests through stable markers or headings; it cannot be left to vague prose.

6. **AC-B.6 - Valid `ProducedAsset` return.** The returned asset:
   - uses `modality_ref="blueprint"`,
   - carries the source `plan_unit.unit_id`,
   - writes `fulfills=f"{plan_unit.unit_id}@{context.lesson_plan_revision}"`,
   - uses a timezone-aware `created_at`,
   - points `asset_path` at the markdown file actually written.

7. **AC-B.7 - Deterministic fill seam, not live-network dependence.** The producer exposes a bounded drafting seam for blueprint-body fill:
   - default behavior is deterministic and repo-testable,
   - an optional injectable drafting function / renderer may be provided for richer fill behavior,
   - no live network or model call is required for the default path or the automated tests.

8. **AC-B.8 - No schema bump in 31-4.** 31-4 ships a produced artifact and registry backfill only. It does not change `LessonPlan`, `PlanUnit`, `FitReport`, or `ProducedAsset` schema families, and it does not pre-implement `plan_unit.blueprint_signoff` or 31-5's gate payloads.

9. **AC-B.9 - Canonical downstream import seam is explicit.** Downstream code can import the producer via:

   ```python
   from marcus.lesson_plan.blueprint_producer import BlueprintProducer
   ```

   Re-export through `marcus.lesson_plan.__init__` is optional, not required.

### Test / Verification (AC-T.*)

1. **AC-T.1 - Public-surface smoke.** A smoke test proves `BlueprintProducer` imports cleanly and is instantiable.
2. **AC-T.2 - ABC contract.** Tests assert the concrete class advertises `modality_ref="blueprint"` and `status="ready"` and returns a valid `ProducedAsset`.
3. **AC-T.3 - Registry backfill.** A test pins `MODALITY_REGISTRY["blueprint"].producer_class_path` to the concrete dotted path and keeps `status="ready"`.
4. **AC-T.4 - Blueprint-only guard.** Tests cover rejection of non-blueprint `scope_decision` / conflicting `modality_ref` surfaces.
5. **AC-T.5 - Artifact write contract.** A test proves `produce(...)` writes exactly one markdown artifact to the expected deterministic path and that `ProducedAsset.asset_path` matches the written file.
6. **AC-T.6 - Human-review checkpoint markers.** Tests assert the markdown contains the named human-review section and stable sign-off markers.
7. **AC-T.7 - Deterministic replay.** Re-running `produce(...)` with the same `PlanUnit` + context yields the same markdown body and stable `asset_path` aside from the allowed timestamp field on `ProducedAsset`.
8. **AC-T.8 - Injected fill seam.** A testable injected drafting function can override the default body fill without breaking the review-checkpoint contract or the `ProducedAsset` contract.
9. **AC-T.9 - No schema drift.** Contract or grep tests prove 31-4 does not edit `SCHEMA_CHANGELOG.md` and does not add a schema bump to the Lesson Planner shape families.
10. **AC-T.10 - No Marcus-duality prose leak.** User-facing markdown template text and module docstrings do not leak the forbidden duality tokens in human-facing prose.

### Closeout / Integration (AC-C.*)

1. **AC-C.1 - Output path is repo-relative and reviewable.** The output path for produced blueprint artifacts is a stable repo-relative location suitable for downstream tests and manual review.
2. **AC-C.2 - 29-3 seam remains open, not pre-solved.** The artifact is sufficient for later co-authoring, but 31-4 does not invent 29-3's final sign-off pointer protocol.
3. **AC-C.3 - 31-5 branch becomes testable.** The emitted artifact and review markers are concrete enough that 31-5 can later accept a blueprint-signed branch without revisiting 31-4's production contract.

## File Impact (preliminary - refined at `bmad-dev-story`)

- **NEW:** `marcus/lesson_plan/blueprint_producer.py` - concrete blueprint producer + deterministic markdown rendering + human-review checkpoint
- **UPDATED:** `marcus/lesson_plan/modality_registry.py` - backfill `producer_class_path` for `blueprint`
- **NEW:** `tests/test_blueprint_producer.py`
- **NEW:** `tests/contracts/test_blueprint_producer_registry_contract.py`
- **NEW:** `tests/contracts/test_blueprint_producer_no_duality_leak.py`

## Tasks / Subtasks (preliminary - refined at `bmad-dev-story`)

- [x] T1 - Author the concrete `BlueprintProducer` module on top of the 31-3 ABC.
- [x] T2 - Define the deterministic markdown blueprint template / fill helpers and the explicit human-review checkpoint.
- [x] T3 - Implement the blueprint-only guard and valid `ProducedAsset` return path.
- [x] T4 - Backfill `MODALITY_REGISTRY["blueprint"].producer_class_path`.
- [x] T5 - Add focused behavior + contract tests inside the `10-12` collecting-test target range.
- [x] T6 - Run focused regression and the dual-gate review lane before closeout.

## Test Plan

`tests_added >= K` with **K = 8**.

**Target range:** `10-12` collecting tests per `docs/dev-guide/story-cycle-efficiency.md`.

Keep the families tight:

- one smoke/public-surface family,
- one ABC/ProducedAsset contract family,
- one registry-backfill family,
- one blueprint-only guard family,
- one artifact-write family,
- one deterministic replay family,
- one injected-fill family,
- one no-duality-leak family.

If the count rises above 12, the Dev Agent Record must name the specific extra coverage gap being purchased.

## Out of Scope

- Irene blueprint co-authoring protocol and any final `blueprint_signoff` pointer schema; that is 29-3.
- Quinn-R step-13 acceptance logic; that is 31-5.
- Gary/slides retrofit or any modality other than `blueprint`.
- Live model/network calls in the default production path.
- Any Marcus duality refactor work from 30-1.

## Dependencies on Ruling Amendments / Prior Findings

- **R1 amendment 7** - 31-4 stays a single 5-point story; do not split it into harness + implementation.
- **31-3 R2 pressure-test result** - the ABC is already "complete enough"; 31-4 should prove that instead of reopening the contract.
- **A5 trial-run acceptance criterion** - at least one blueprint path must later be able to emit a reviewable blueprint artifact for the Quinn-R alternate branch.
- **Story-cycle-efficiency dual-gate classification** - this story is novel, user-facing, and human-review-driven; it stays dual-gate.

## Risks

- **Template theater risk:** producing a file that looks like a blueprint but carries no stable review markers. Mitigation: make the checkpoint machine-locatable.
- **Overreach risk:** accidentally implementing 29-3 or 31-5 inside 31-4. Mitigation: artifact only, no sign-off pointer schema, no gate logic.
- **Live-call risk:** tying the producer to an online model call. Mitigation: default deterministic renderer; injected drafting seam only.
- **Cross-lane collision risk:** touching too many shared files while 30-1 is active. Mitigation: keep the public seam module-local; avoid unnecessary package re-export work.

## Dev Notes

### Architecture

31-4 is the first concrete producer on the 31-3 ABC. That means the story should validate the seam, not reinvent it. The simplest correct shape is:

- `BlueprintProducer` implements `produce(plan_unit, context)`.
- The producer writes a markdown file under a stable repo-relative output root.
- The producer returns a `ProducedAsset` pointing at that file.
- The emitted markdown states clearly that it is a draft awaiting human review/sign-off.

Because `ProductionContext` already has the 31-3 extensibility seam, 31-4 may subclass it only if an additional blueprint-specific field is truly needed. Avoid gratuitous model proliferation.

### Anti-patterns

- Do not bypass `ProducedAsset` and return an ad hoc dict or raw path.
- Do not silently treat every `PlanUnit` as blueprint-capable.
- Do not rely on `__init__.py` re-exports unless they buy a concrete downstream benefit; `30-1` is already moving shared package surfaces.
- Do not hide the human-review checkpoint inside freeform prose.
- Do not change Lesson Plan schema families in this story.

### Canonical downstream import seam

Downstream code should be able to run:

```python
from marcus.lesson_plan.blueprint_producer import BlueprintProducer
```

That module path is the completion handshake for 31-4.

## Governance Closure Gates

- [x] Acceptance criteria met.
- [x] Governance validator passes.
- [x] Dual-gate workflow completed: create-story -> dev-story -> post-dev code review.
- [x] Status artifacts refreshed in closeout order.

## Dev Agent Record

**Executed by:** Codex, following the Amelia / `bmad-agent-dev` workflow locally.
**Date:** 2026-04-18.

### Landed artifacts

- `marcus/lesson_plan/blueprint_producer.py` - concrete `BlueprintProducer`, deterministic markdown composition, human-review checkpoint markers, repo-relative output-path discipline, and injected body-renderer seam.
- `marcus/lesson_plan/modality_registry.py` - `blueprint` entry backfilled to `marcus.lesson_plan.blueprint_producer.BlueprintProducer`.
- `tests/test_blueprint_producer.py` - behavior slice covering instantiation, write contract, blueprint-only guard, deterministic replay, and injected renderer behavior.
- `tests/contracts/test_blueprint_producer_registry_contract.py` - registry backfill pin and no-schema-bump/public-surface contract.
- `tests/contracts/test_blueprint_producer_no_duality_leak.py` - module-text and rendered-markdown leak scan.
- `tests/contracts/test_modality_registry_stable.py` - current MVP producer-path expectation updated for the 31-4 backfill.
- `tests/test_modality_registry_query_api.py` - positive lookup expectation updated for the blueprint backfill state.

### Verification

- Governance validator: `python scripts/utilities/validate_lesson_planner_story_governance.py _bmad-output/implementation-artifacts/31-4-blueprint-producer.md`
- Focused 31-4 + 31-3 seam regression:
  `py -3.13 -m pytest tests/test_blueprint_producer.py tests/contracts/test_blueprint_producer_registry_contract.py tests/contracts/test_blueprint_producer_no_duality_leak.py tests/contracts/test_modality_registry_stable.py tests/test_modality_registry_query_api.py tests/test_modality_producer_abc_contract.py tests/test_produced_asset_fulfills.py -q`
  -> `100 passed`
- Focused 31-4 slice:
  `py -3.13 -m pytest tests/test_blueprint_producer.py tests/contracts/test_blueprint_producer_registry_contract.py tests/contracts/test_blueprint_producer_no_duality_leak.py -q`
  -> `11 passed`
- Ruff:
  `ruff check marcus/lesson_plan/blueprint_producer.py marcus/lesson_plan/modality_registry.py tests/test_blueprint_producer.py tests/contracts/test_blueprint_producer_registry_contract.py tests/contracts/test_blueprint_producer_no_duality_leak.py tests/contracts/test_modality_registry_stable.py tests/test_modality_registry_query_api.py`
  -> `All checks passed`
- Pre-commit:
  `pre-commit run --files ...31-4 touched files...`
  -> passed (`ruff`, orphan-reference detector, co-commit invariant)

### Completion Notes

- The producer stayed inside 31-4's intended boundary: artifact emission only, no schema bump, no 29-3 sign-off pointer, and no 31-5 gate logic.
- The public seam stayed module-local on purpose; `marcus/lesson_plan/__init__.py` was left untouched because the active `30-1` lane is already modifying shared package surfaces.
- Collecting-test footprint stayed inside policy: 11 tests across the dedicated 31-4 slice, which lands inside the `10-12` target range for `K = 8`.

## Review Record

### Dual-gate pre-dev review

**Mode:** local party-mode synthesis before `bmad-dev-story`.
**Verdict:** GREEN.

- **Winston:** GREEN - the 31-3 ABC was already sufficient; 31-4 should validate the seam with one real producer and avoid reopening contract design.
- **Murat:** GREEN - keep the test surface tight, verify artifact write + guard + registry backfill + deterministic replay, and avoid a new combinatorial fixture matrix.
- **Paige:** GREEN - the emitted markdown must state plainly that it is a review-bound draft, and the marker text must stay stable enough for downstream tests.
- **Quinn:** GREEN - do not pre-implement the 31-5 branch logic; the job here is to emit a real `ProducedAsset` plus review checkpoint that 31-5 can later consume.

No pre-dev riders were required after governance validation passed.

### Post-dev code review

**Workflow:** `bmad-code-review`, executed locally in layered form.
**Verdict:** clear after two expectation patches on the 31-3 registry seam.

- **Blind Hunter:** no correctness bugs in the new producer module. Output-root discipline, file write path, and `ProducedAsset` construction were coherent.
- **Edge Case Hunter:** the meaningful edge cases were the blueprint-only scope guard and deterministic replay. Both were covered and passed.
- **Acceptance Auditor:** two follow-up expectation patches were needed in pre-existing registry tests because 31-4 intentionally backfills `MODALITY_REGISTRY["blueprint"].producer_class_path`. Both were applied:
  - `tests/contracts/test_modality_registry_stable.py`
  - `tests/test_modality_registry_query_api.py`

**Triage summary**

- **APPLY:** 2 (existing registry expectation updates)
- **DEFER:** 0
- **DISMISS:** 0
