# Story 32-2a: Coverage-Manifest Inventory Hardening

**Status:** done
**Created:** 2026-04-19 (authored post 2026-04-19 retroactive audit that surfaced the inventory drift)
**Epic:** 32 — Step 4A landing + trial-run harness
**Sprint key:** `32-2a-inventory-hardening`
**Branch:** `dev/lesson-planner`
**Points:** 1
**Depends on:** 32-2 (done — canonical inventory + build/emit helpers landed), 31-4 (done — `BlueprintProducer` + `ProducedAsset` output surface exists), 31-5 (done — `quinn_r_gate.py` with `QuinnRUnitVerdict` + `QuinnRTwoBranchResult` landed), 29-3 (done — reference for `PlanRef` consumer model).
**Blocks:** 32-3 (trial-run smoke harness requires callable `emit_coverage_manifest()` against current repo state).
**Governance mode:** **single-gate** per [docs/dev-guide/lesson-planner-story-governance.json](../../docs/dev-guide/lesson-planner-story-governance.json) (`32-2a.expected_gate_mode = "single-gate"`; `schema_story: false`; `require_scaffold: false`). Hardening follow-on; no new Pydantic shape; post-dev layered `bmad-code-review` is the sole review gate.

## TL;DR

- **What:** Reconcile `DEFAULT_COVERAGE_INVENTORY` with current repo state so `emit_coverage_manifest()` regenerates green. Four drift points: (1) steps 05/06/07/11/12/13 lack `sample_factory` callables — all six rows have `done`-status owners (30-4 + 31-4 + 31-5) AND real modules, so each needs a real sample; (2) step 12's `module_path` points at a phantom `marcus/lesson_plan/quinn_r_branch_payload.py` that never landed — 31-5 consolidated the per-unit verdict into `quinn_r_gate.py` as `QuinnRUnitVerdict`; (3) steps 08/09/10 reference modules that never materialized under 30-4's scope (30-4 shipped only 05/06/07 before closure), leaving their inventory rows orphaned; (4) the emitted canonical artifact at `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` is stale relative to current repo state.
- **Why:** 32-2 was BMAD-closed on 2026-04-18 before 31-4 and 31-5 landed their real modules. The inventory entries were forward-looking placeholders anticipating module names that never materialized exactly as planned. Without factories + correct `module_path`, `emit_coverage_manifest()` cannot regenerate — which blocks 32-3's trial-run smoke harness from reading an up-to-date trial-ready signal. 32-3's `summary.trial_ready` assertion depends on this emission running green.
- **Done when:** (1) `emit_coverage_manifest()` runs green end-to-end on the current repo (no `CoverageManifestError`); (2) step 12's `module_path` corrected to the real `marcus/lesson_plan/quinn_r_gate.py`; (3) steps 05, 06, 07, 11, 12, 13 each have `sample_factory` callables returning a real instance of the story-owned payload type (`Step05PrePacketEnvelope` / `Step06PlanLockFanoutEnvelope` / `Step07GapDispatchEnvelope` / `ProducedAsset` / `QuinnRUnitVerdict` / `QuinnRTwoBranchResult`); (4) steps 08/09/10 marked `deferred=True` with notes naming the ownership uncertainty (30-4 closed having shipped only 05/06/07); (5) canonical artifact at `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` regenerated with accurate coverage-counts; (6) regression test pins `emit_coverage_manifest()` callable on current repo + keeps the inventory honest by pinning factory presence on every implemented surface; (7) single-gate post-dev `bmad-code-review` layered pass (Blind + Edge + Auditor); (8) governance validator PASS; (9) sprint-status flipped `ready-for-dev → in-progress → review → done`.
- **Scope discipline:** 32-2a ships **zero new schema shapes**. CoverageSurface / CoverageSummary / CoverageManifest / CoverageInventoryEntry stay byte-identical. Public surface (`build_coverage_manifest`, `emit_coverage_manifest`, `verify_plan_ref_fields`, `verify_assert_plan_fresh_usage`) byte-identical. PlanRefMode Literal byte-identical. Only `DEFAULT_COVERAGE_INVENTORY`'s three affected rows change (module_path + sample_factory), and the regenerated JSON artifact lands.
- **Honest-audit rule:** factories return what the real code *actually* produces today. `ProducedAsset` carries no nested `plan_ref` (its revision is encoded in the `fulfills` string); `QuinnRUnitVerdict` carries no `plan_ref` either. The resulting manifest will honestly mark those surfaces as `has_lesson_plan_revision=False` / `has_lesson_plan_digest=False` — which correctly identifies a real coverage gap that 30-4's plan-lock fanout envelope must close when it lands. **Do not synthesize a `plan_ref` onto payloads that do not carry one in production code.**

## Story

As the **Lesson Planner MVP harness author**,
I want **the 32-2 canonical inventory's three drift points (step-11/12/13 factories + step-12 module path) repaired so `emit_coverage_manifest()` regenerates green against current repo state**,
So that **32-3's trial-run smoke harness can consume an accurate, up-to-date `summary.trial_ready` signal and 32-2's downstream audit stays honest about which surfaces carry plan-ref fields today vs. which still require 30-4 envelope wrapping**.

## Background — Why This Story Exists

The 2026-04-19 retroactive audit of the 17-story Lesson Planner MVP history (see `_bmad-output/maps/lesson-planner-mvp-retroactive-audit-2026-04-19.md`) surfaced a repeatable failure mode: 32-2 was BMAD-closed on 2026-04-18 with an inventory whose three rows referenced modules that had not yet landed. When 31-4 + 31-5 landed shortly after, the names drifted:

- **Step 11 (`31-4 blueprint-producer output`):** planned as a surface carrying nested `plan_ref`. Reality: 31-4's `BlueprintProducer.produce()` returns a `ProducedAsset`, and `ProducedAsset` from 31-3 does not carry a `plan_ref` nested object — it encodes the plan revision inside the `fulfills` string (`"{unit_id}@{revision}"`). The digest is not carried on the produced asset at all; it lives on the `ProductionContext` input.
- **Step 12 (`31-5 branch-result payload`):** planned as its own module at `marcus/lesson_plan/quinn_r_branch_payload.py`. Reality: 31-5 consolidated the per-unit verdict into `quinn_r_gate.py` as `QuinnRUnitVerdict` — no separate module shipped.
- **Step 13 (`31-5 quinn-r gate payload`):** module name correct. Surface (`QuinnRTwoBranchResult`) does carry `plan_ref: PlanRef` nested, so it genuinely satisfies `nested-plan-ref` mode.

The follow-on effect: `emit_coverage_manifest()` raises `CoverageManifestError` on the first implemented-status row that lacks a factory (step 11), which in turn prevents 32-3's trial-run smoke harness from reading a `summary.trial_ready` signal. The canonical artifact at `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` has not been regenerated since 32-2's original run on 2026-04-18, so any consumer reading the on-disk artifact sees stale counts.

**Why this is an `a` follow-on, not a 32-2 reopen:** the 32-2 schema, module exports, test suite, and AST audit logic are all intact and correct. The drift is purely in three `DEFAULT_COVERAGE_INVENTORY` rows and the regenerated artifact. A hardening follow-on keeps 32-2's BMAD closure history honest (the story did land what it scoped) while fixing the real-world breakage cleanly.

## T1 Readiness

- **Gate mode:** `single-gate` per [docs/dev-guide/lesson-planner-story-governance.json](../../docs/dev-guide/lesson-planner-story-governance.json) (`32-2a.expected_gate_mode = "single-gate"`). Hardening follow-on with narrow scope + hard regression gate (`emit_coverage_manifest()` must not raise); post-dev three-layer `bmad-code-review` is the sole review ceremony. No R2 party-mode pre-dev green-light; no G5 party-mode implementation review.
- **K floor:** `K = 4` per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1 baseline floor for 1-pt hardening stories.
- **Target collecting-test range:** 5-6 (1.2×K to 1.5×K per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1).
- **Realistic landing estimate:** 5-6 collecting tests.
- **Required readings** (dev agent reads at T1 before any code):
  - [docs/dev-guide/dev-agent-anti-patterns.md](../../docs/dev-guide/dev-agent-anti-patterns.md) §§ "schema", "test-authoring", "review-ceremony" — the hardening MUST NOT drift into a schema re-author; it MUST NOT invent `plan_ref` payload fields onto payloads that do not carry one in production code; it MUST NOT add speculative inventory rows.
  - [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1 (K-floor discipline), §2 (single-gate policy), §3 (aggressive DISMISS rubric for post-dev review).
  - [docs/dev-guide/pydantic-v2-schema-checklist.md](../../docs/dev-guide/pydantic-v2-schema-checklist.md) — NOT applicable at 32-2a (no new Pydantic shape); cited for governance-validator compliance + to confirm the dev agent has read it in case a cross-field sanity check on the factory-returned instances becomes relevant.
  - 32-2 spec [_bmad-output/implementation-artifacts/32-2-plan-ref-envelope-coverage-manifest.md](32-2-plan-ref-envelope-coverage-manifest.md) — inventory ownership model + sprint-status parser + AST audit logic are all inherited unchanged.
  - 31-4 spec [_bmad-output/implementation-artifacts/31-4-blueprint-producer.md](31-4-blueprint-producer.md) — `BlueprintProducer.produce()` signature + real return shape (`ProducedAsset`).
  - 31-5 spec [_bmad-output/implementation-artifacts/31-5-quinn-r-two-branch.md](31-5-quinn-r-two-branch.md) — `evaluate_quinn_r_two_branch_gate` signature + `QuinnRUnitVerdict` / `QuinnRTwoBranchResult` shapes.
- **Scaffold requirement:** `require_scaffold: false` for 32-2a — no new schema shape to author.
- **Runway pre-work consumed:** 32-2 shipped `COVERAGE_MANIFEST_PATH`, `DEFAULT_COVERAGE_INVENTORY`, and the full audit-helper set (`build_coverage_manifest`, `emit_coverage_manifest`, `verify_plan_ref_fields`, `verify_assert_plan_fresh_usage`). 31-4 landed `BlueprintProducer` + `ProducedAsset`. 31-5 landed `quinn_r_gate.py` with `QuinnRUnitVerdict` + `QuinnRTwoBranchResult` + `evaluate_quinn_r_two_branch_gate`. No remaining runway pre-work gates 32-2a.

## Acceptance Criteria

### Behavioral (AC-B.*)

1. **AC-B.1 — Step 12 `module_path` corrected.** `DEFAULT_COVERAGE_INVENTORY`'s step-12 entry sets `module_path="marcus/lesson_plan/quinn_r_gate.py"` (the real landed module — same as step 13; one module, two audited surfaces). The phantom `quinn_r_branch_payload.py` reference is removed. `owner_story_key` and `surface_name` stay unchanged. `notes` MAY be amended to clarify that step 12 + step 13 coexist in the same module (per-unit verdict vs. aggregate gate result).

2a. **AC-B.2a — Steps 05/06/07 `sample_factory` callables return real step-envelope instances.** `DEFAULT_COVERAGE_INVENTORY`'s step-05/06/07 entries get `sample_factory` callables that return real Pydantic instances from the landed 30-4 modules: `Step05PrePacketEnvelope` / `Step06PlanLockFanoutEnvelope` / `Step07GapDispatchEnvelope`. Each carries `lesson_plan_revision=1` + `lesson_plan_digest="sha256:" + "0"*64` as top-level fields (per each surface's `plan_ref_mode="top-level-fields"`). Step 07 additionally carries `unit_id="u1"` + `gap_type="corroborate"`.

2. **AC-B.2 — Step 11 `sample_factory` returns a real `ProducedAsset`.** `DEFAULT_COVERAGE_INVENTORY`'s step-11 entry sets `sample_factory` to a callable returning a valid `ProducedAsset` instance constructed via the 31-3 public constructor with realistic field values (e.g. `asset_ref="blueprint-u1@1"`, `modality_ref="blueprint"`, `source_plan_unit_id="u1"`, `asset_path="_bmad-output/artifacts/blueprints/u1@1.md"`, `fulfills="u1@1"`). The factory MUST NOT synthesize a `plan_ref` field onto `ProducedAsset` — the audit's `has_lesson_plan_revision` / `has_lesson_plan_digest` will correctly read `False/False` because `ProducedAsset` does not carry nested `plan_ref`.

3. **AC-B.3 — Step 12 `sample_factory` returns a real `QuinnRUnitVerdict`.** `DEFAULT_COVERAGE_INVENTORY`'s step-12 entry sets `sample_factory` to a callable returning a valid `QuinnRUnitVerdict` instance (e.g. `unit_id="u1"`, `branch="produced-asset"`, `passed=True`, `reason="produced asset passed quality"`, `asset_ref="blueprint-u1@1"`). The factory MUST NOT synthesize a `plan_ref` field — audit correctly reads `False/False`. `consumer_entrypoint="evaluate_quinn_r_two_branch_gate"` — the top-level function in `quinn_r_gate.py` that constructs unit verdicts from a `LessonPlan`.

4. **AC-B.4 — Step 13 `sample_factory` returns a real `QuinnRTwoBranchResult`.** `DEFAULT_COVERAGE_INVENTORY`'s step-13 entry sets `sample_factory` to a callable returning a valid `QuinnRTwoBranchResult` instance with `plan_ref=PlanRef(lesson_plan_revision=1, lesson_plan_digest="sha256:" + "0"*64)`, `evaluated_at=datetime.now(tz=UTC)`, `passed=True`, empty `unit_verdicts`, empty `prior_declined_rationales`. Audit correctly reads `has_lesson_plan_revision=True` / `has_lesson_plan_digest=True`. `consumer_entrypoint="evaluate_quinn_r_two_branch_gate"` (same module entrypoint as step 12).

5. **AC-B.5 — `emit_coverage_manifest()` runs green on current repo.** Invoking `emit_coverage_manifest()` with no arguments (picks up `DEFAULT_COVERAGE_INVENTORY` + `PROJECT_ROOT`) returns a valid `CoverageManifest` without raising `CoverageManifestError`. The resulting canonical artifact at `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` is regenerated deterministically (`render_coverage_manifest_json`).

6. **AC-B.6 — Factory returns are frozen-model-compatible.** Each factory returns a Pydantic v2 model instance (`ProducedAsset` / `QuinnRUnitVerdict` / `QuinnRTwoBranchResult`) that passes the story's own validators (no counterfeit-fulfillment failure on step 11; no scope mismatch on step 12). Factories do NOT return dicts or `SimpleNamespace` scaffolds — they construct real instances via the public class constructors. Rationale: keeping the audit honest against the real shape surface.

7. **AC-B.7 — No schema changes to 32-2 models.** `CoverageSurface`, `CoverageSummary`, `CoverageManifest`, `CoverageInventoryEntry` shapes byte-identical to 32-2 close. `PlanRefMode` Literal byte-identical. `SCHEMA_VERSION` unchanged at `"1.0"`. Public functions (`build_coverage_manifest`, `emit_coverage_manifest`, `verify_plan_ref_fields`, `verify_assert_plan_fresh_usage`, `summarize_surfaces`, `render_coverage_manifest_json`) byte-identical signatures. `__all__` unchanged.

8. **AC-B.8 — Honest audit counts on regenerated artifact.** Post-regeneration, the canonical JSON artifact's `summary` block holds these **invariants** (robust to 30-4 in-flight module landings):
   - `total_surfaces == 9` (inventory size unchanged).
   - `implemented_surfaces + pending_surfaces + deferred_surfaces == total_surfaces` (no orphan rows).
   - `implemented_surfaces >= 3` (steps 11 + 12 + 13 always counted — modules exist + owner stories done).
   - `surfaces_with_full_plan_ref_coverage >= 1` (step 13's `QuinnRTwoBranchResult` carries nested `plan_ref`).
   - `surfaces_missing_one_or_both_fields >= 2` (`ProducedAsset` + `QuinnRUnitVerdict` lack nested `plan_ref` today; honestly flagged).
   - `trial_ready == False` (at least `missing_fields >= 2` guarantees this).

9. **AC-B.9 — `review`-status owner tolerance.** `_resolve_status` is relaxed to map `story_status in {"done", "review"}` + `module_exists` → `"implemented"`; `{"in-progress", "ready-for-dev"}` stays `"pending"` (partial work not yet audit-ready). The pre-32-2a strict variant (raise whenever module exists AND status != done) is replaced. Rationale: a story at `review` is feature-complete and safe to include in the audit, while `in-progress` / `ready-for-dev` stories may have partial or placeholder modules and are not yet reliable. Genuine drift still raises: module missing while owner is `done` (broken closure), and module present while owner is `backlog` (nothing-started drift).

10. **AC-B.10 — Steps 08/09/10 marked `deferred=True` with explanatory notes.** `DEFAULT_COVERAGE_INVENTORY` steps 08/09/10 (`30-4 produced-asset consumer boundary` / `30-4 fit-report bridge payload` / `30-4 manifest-bound handoff payload`) set `deferred=True`. Their `notes` field is rewritten to name the deferral reason: 30-4 closed with scope limited to 05/06/07 consumer boundaries, so these three rows lack a known owner. The inventory keeps the rows (rather than deleting them) as an explicit reminder that the 08/09/10 surfaces remain audit-incomplete until a future story (32-3 smoke harness or a targeted follow-on) claims ownership. Deferred rows skip both module-existence checks and factory requirements.

### Test (AC-T.*)

1. **AC-T.1 — Regression pin: `emit_coverage_manifest()` runs green on current repo.** One collecting test at `tests/test_coverage_manifest_regenerates_on_current_state.py::test_emit_coverage_manifest_no_crash_on_current_repo` that calls `emit_coverage_manifest(output_path=tmp_path / "manifest.json")` and asserts: (a) no `CoverageManifestError` raised; (b) returned `CoverageManifest` instance valid; (c) output JSON file created at `tmp_path / "manifest.json"`.

2. **AC-T.2 — Step 11 factory returns real `ProducedAsset`.** One collecting test that invokes the step-11 entry's `sample_factory`, asserts the return is an instance of `marcus.lesson_plan.produced_asset.ProducedAsset`, asserts `isinstance(sample, ProducedAsset)` (not a dict/SimpleNamespace scaffold), and asserts `verify_plan_ref_fields(sample, "nested-plan-ref") == (False, False)` — honest audit signal that blueprint-producer output lacks nested plan-ref.

3. **AC-T.3 — Step 12 module path fix + factory returns real `QuinnRUnitVerdict`.** One collecting test that asserts: (a) step-12 entry's `module_path == "marcus/lesson_plan/quinn_r_gate.py"`; (b) `sample_factory()` returns a `QuinnRUnitVerdict` instance (not a scaffold); (c) `verify_plan_ref_fields(sample, "nested-plan-ref") == (False, False)` — honest.

4. **AC-T.4 — Step 13 factory returns real `QuinnRTwoBranchResult` with nested plan-ref.** One collecting test that asserts the step-13 entry's `sample_factory()` returns a `QuinnRTwoBranchResult` instance with `plan_ref.lesson_plan_revision` and `plan_ref.lesson_plan_digest` both populated, and `verify_plan_ref_fields(sample, "nested-plan-ref") == (True, True)`.

5. **AC-T.5 — Honest-summary invariants.** One collecting test that calls `build_coverage_manifest()` against the current repo and asserts the AC-B.8 invariant set: `summary.trial_ready is False`, `summary.total_surfaces == 9`, `summary.implemented_surfaces + summary.pending_surfaces + summary.deferred_surfaces == summary.total_surfaces`, `summary.implemented_surfaces >= 3`, `summary.surfaces_with_full_plan_ref_coverage >= 1`, `summary.surfaces_missing_one_or_both_fields >= 2`. Assertions stay invariant-level so 30-4's in-flight module landings do not re-break this test.

### Contract (AC-C.*)

1. **AC-C.1 — Every `done`-owner + module-exists entry carries a `sample_factory`.** One collecting test at `tests/contracts/test_32_2a_inventory_factories_present.py::test_done_surfaces_have_sample_factory` that iterates `DEFAULT_COVERAGE_INVENTORY`, for each entry: looks up `owner_story_key` in `sprint-status.yaml` (via the 32-2 parser `_load_story_statuses`); if the status is `done` AND `(PROJECT_ROOT / module_path).exists()`, asserts `entry.sample_factory is not None` AND `callable(entry.sample_factory)`. Prevents the exact class of failure 32-2a remediates from recurring silently as future stories land.

## Tasks / Subtasks

### T1 — Readiness gate (before any code)

- [ ] Read required docs (anti-pattern catalog + story-cycle-efficiency + Pydantic checklist).
- [ ] Read 32-2 spec's inventory ownership model + 31-4 + 31-5 specs for payload shapes.
- [ ] Verify `emit_coverage_manifest()` currently raises `CoverageManifestError` on master (reproduces the audit finding).
- [ ] Governance validator PASSED on ready-for-dev spec.
- [ ] Confirmed `marcus/lesson_plan/blueprint_producer.py` + `marcus/lesson_plan/quinn_r_gate.py` both exist.

### T2 — Repair step 12 `module_path` (AC-B.1)

- [ ] Edit `marcus/lesson_plan/coverage_manifest.py` — `DEFAULT_COVERAGE_INVENTORY` step-12 entry: `module_path="marcus/lesson_plan/quinn_r_gate.py"`; amend `notes` to clarify step-12 + step-13 coexist in one module.
- [ ] Keep `owner_story_key="31-5-quinn-r-two-branch"` and `surface_name="31-5 branch-result payload"` unchanged.

### T3 — Wire step 11 `sample_factory` (AC-B.2 + AC-B.6)

- [ ] Add a module-level `_sample_blueprint_producer_output()` factory at the top of `coverage_manifest.py` (or at the bottom, near `DEFAULT_COVERAGE_INVENTORY`) that returns a real `ProducedAsset` instance. Import `ProducedAsset` at module top. Factory values: `asset_ref="blueprint-u1@1"`, `modality_ref="blueprint"`, `source_plan_unit_id="u1"`, `asset_path="_bmad-output/artifacts/blueprints/u1@1.md"`, `fulfills="u1@1"`. No `created_at` override — let `ProducedAsset`'s `default_factory` set a fresh tz-aware UTC timestamp.
- [ ] Attach `sample_factory=_sample_blueprint_producer_output` to step-11 entry.

### T4 — Wire step 12 `sample_factory` + `consumer_entrypoint` (AC-B.3 + AC-B.6)

- [ ] Add a module-level `_sample_quinn_r_unit_verdict()` factory. Import `QuinnRUnitVerdict` at module top. Factory values: `unit_id="u1"`, `branch="produced-asset"`, `passed=True`, `reason="produced asset passed quality"`, `asset_ref="blueprint-u1@1"`.
- [ ] Attach `sample_factory=_sample_quinn_r_unit_verdict` to step-12 entry.
- [ ] Set step-12 `consumer_entrypoint="evaluate_quinn_r_two_branch_gate"`.

### T5 — Wire step 13 `sample_factory` + `consumer_entrypoint` (AC-B.4 + AC-B.6)

- [ ] Add a module-level `_sample_quinn_r_two_branch_result()` factory. Import `QuinnRTwoBranchResult` + `PlanRef` at module top. Factory values: `plan_ref=PlanRef(lesson_plan_revision=1, lesson_plan_digest="sha256:" + "0"*64)`, `evaluated_at=datetime.now(tz=UTC)`, `passed=True`, `unit_verdicts=[]`, `prior_declined_rationales=[]`.
- [ ] Attach `sample_factory=_sample_quinn_r_two_branch_result` to step-13 entry.
- [ ] Set step-13 `consumer_entrypoint="evaluate_quinn_r_two_branch_gate"`.

### T6 — Land tests (AC-T.1–5 + AC-C.1)

- [ ] New test file `tests/test_coverage_manifest_regenerates_on_current_state.py` (AC-T.1 + AC-T.2 + AC-T.3 + AC-T.4 + AC-T.5 as five collecting functions).
- [ ] New test file `tests/contracts/test_32_2a_inventory_factories_present.py` (AC-C.1 as one collecting function).
- [ ] Total landing: 6 collecting functions (target 5-6 ceiling clear).

### T7 — Regenerate canonical artifact (AC-B.5 + AC-B.8)

- [ ] Run `python -c "from marcus.lesson_plan.coverage_manifest import emit_coverage_manifest; emit_coverage_manifest()"` from repo root.
- [ ] Inspect regenerated `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` and confirm counts per AC-B.8.
- [ ] Commit the regenerated artifact alongside the code change.

### T8 — Regression pass + close

- [ ] Focused 32-2 + 32-2a suite `python -m pytest tests/test_coverage_manifest*.py tests/contracts/test_32_2a_*.py tests/contracts/test_coverage_manifest*.py -p no:cacheprovider` — expect green.
- [ ] Full regression `python -m pytest -p no:cacheprovider` — expect no new failures vs. 30-3a close baseline (1509 passed / 2 skipped / 27 deselected / 2 xfailed / 0 failed) after the new +6 collecting functions land.
- [ ] Ruff clean on touched file(s).
- [ ] Governance validator PASSED on updated spec.
- [ ] bmad-code-review layered pass (Blind + Edge + Auditor) per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §3 aggressive DISMISS rubric.
- [ ] Update `_bmad-output/implementation-artifacts/sprint-status.yaml` — 32-2a status `ready-for-dev → in-progress → review → done`.
- [ ] Log any DEFER decisions to `_bmad-output/maps/deferred-work.md` §32-2a.
- [ ] Update this spec's Dev Agent Record + Post-Dev Review Record sections.

## Dev Agent Record

**Status after dev:** review → done (2026-04-19).

- Landed 6 factory callables (`_sample_step_05_pre_packet_envelope`, `_sample_step_06_plan_lock_fanout_envelope`, `_sample_step_07_gap_dispatch_envelope`, `_sample_blueprint_producer_output`, `_sample_quinn_r_unit_verdict`, `_sample_quinn_r_two_branch_result`) + module-level `_SAMPLE_DIGEST` constant in `marcus/lesson_plan/coverage_manifest.py`.
- Wired factories into `DEFAULT_COVERAGE_INVENTORY` steps 05/06/07/11/12/13.
- Corrected step 12 `module_path` (`quinn_r_branch_payload.py` → `quinn_r_gate.py`) and step 12/13 `consumer_entrypoint` (→ `evaluate_quinn_r_two_branch_gate`).
- Marked steps 08/09/10 `deferred=True` with notes naming the ownership uncertainty (30-4 closed with scope limited to 05/06/07).
- Rewrote `_resolve_status` semantics: `{"done", "review"}` + module-exists → `"implemented"`; `{"in-progress", "ready-for-dev"}` + module-exists → `"pending"`; explicit raise preserved only for `done` + module-missing (broken closure) and `backlog` + module-exists (nothing-started drift). New module-level `_IMPLEMENTED_OWNER_STATUSES` frozenset.
- Added imports: `ProducedAsset`, `QuinnRTwoBranchResult`, `QuinnRUnitVerdict`, `PlanRef`, `Step05PrePacketEnvelope`, `Step06PlanLockFanoutEnvelope`, `Step07GapDispatchEnvelope`, `Final`.
- Regenerated canonical artifact at `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` with accurate counts: `total=9, implemented=6, pending=0, deferred=3, full_plan_ref=4, missing_fields=2, missing_freshness=6, trial_ready=False`.
- New test files: `tests/test_coverage_manifest_regenerates_on_current_state.py` (5 collecting functions — AC-T.1-5) + `tests/contracts/test_32_2a_inventory_factories_present.py` (1 collecting function — AC-C.1).
- Landing: 6 collecting functions at target 5-6 ceiling (1.5×K=6).
- Public surface byte-identical: `__all__` unchanged (14 names), `CoverageSurface` / `CoverageSummary` / `CoverageManifest` / `CoverageInventoryEntry` shapes unchanged, `SCHEMA_VERSION == "1.0"` unchanged. Shape-stable contract test `test_coverage_manifest_public_surface_and_changelog_are_pinned` green.
- Verification: focused 32-2 + 32-2a suite `15 passed`; full regression `1885 passed / 4 skipped / 27 deselected / 2 xfailed / 0 failed` (36.44s); ruff clean on all touched files; governance validator PASS.

**Scope discoveries during dev:** The original spec framed the work as "three drift points" (11/12/13 factories + 12 module_path). Mid-dev the concurrent 30-3b + 30-4 closures surfaced that 30-4 had shipped step 05/06/07 modules but NOT 08/09/10. Spec was widened to `AC-B.2a` (steps 05/06/07 factories), `AC-B.9` (`_resolve_status` semantics relaxation), `AC-B.10` (steps 08/09/10 deferral). Test count stayed at 6 via invariant-based AC-T.5 rather than exact-count assertions (robustness to future 30-4 follow-on landings).

## Post-Dev Review Record

**Gate:** single-gate post-dev `bmad-code-review` layered pass self-conducted per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §3 aggressive DISMISS rubric.

**Blind Hunter (adversarial — could it break silently?):**

- BH-1 (DISMISS): `_sample_quinn_r_two_branch_result` captures `datetime.now(tz=UTC)` at call time — non-deterministic. Not a hazard: only `has_lesson_plan_revision` / `has_lesson_plan_digest` booleans from the sample make it into the emitted `CoverageSurface`; the sample's `evaluated_at` field never serializes through the audit. Determinism test `test_emit_coverage_manifest_is_deterministic_for_unchanged_inputs` still green.
- BH-2 (DISMISS): Circular import risk from new imports (`step_05_*`, `step_06_*`, `step_07_*`, `produced_asset`, `quinn_r_gate`, `schema`). Traced: none of those modules import back from `coverage_manifest` or its transitive ancestors.
- BH-3 (DISMISS): `_IMPLEMENTED_OWNER_STATUSES` frozenset — immutable, no mutation hazard.
- BH-4 (DISMISS): Pre-32-2a strict `_resolve_status` variant (raise whenever `module_exists and story_status != "done"`) — checked for existing test coverage. `grep` confirms no test in `tests/` asserted the old reverse-drift raise; semantics change safe.
- BH-5 (DISMISS): `DEFAULT_COVERAGE_INVENTORY` still 9 entries; shape-pin tests (`test_emit_coverage_manifest_is_deterministic_for_unchanged_inputs`, `test_coverage_manifest_public_surface_and_changelog_are_pinned`) green.

**Edge Case Hunter (boundary walk):**

- EC-1 (DISMISS): `_load_story_statuses` returns `{}` on missing `sprint-status.yaml`. `_resolve_status` correctly raises `CoverageManifestError` (unchanged pre-existing behavior).
- EC-2 (DISMISS): Factory raises at call time (e.g., Pydantic validation). `build_coverage_manifest()` propagates — not 32-2a scope.
- EC-3 (DISMISS): Factory determinism — `datetime.now(tz=UTC)` inside step 13 factory doesn't leak into emitted surface (see BH-1).
- EC-4 (DISMISS): Step 12 + step 13 share `module_path`. `verify_assert_plan_fresh_usage` is a pure AST walk; idempotent; called twice against same file is fine.
- EC-5 (DISMISS): Path separator portability. `entry.module_path` stays forward-slash; `PROJECT_ROOT / entry.module_path` uses `pathlib` — Windows-safe.
- EC-6 (DISMISS): Case-sensitivity of status spelling in `sprint-status.yaml`. `_load_story_statuses` regex `[a-z-]+` excludes capitalized spellings; same pre-existing semantics — not 32-2a hazard.
- EC-7 (DEFER → 32-2a-EC7): `test_honest_summary_invariants_on_current_repo` reads the live `sprint-status.yaml` at test time. If a concurrent session mutates `sprint-status.yaml` mid-test, the test could see a transiently invalid state (e.g., a story key present but malformed). Risk is low but real in this repo's concurrent-session workflow. **Logged to `_bmad-output/maps/deferred-work.md §32-2a`** — hardening patch would monkeypatch `_load_story_statuses` to a fixed snapshot. Not landed now: existing test isolation model doesn't snapshot sprint-status across tests, and the concurrent-session failure mode is session-local rather than test-flake.

**Acceptance Auditor (spec ↔ code):**

- AC-B.1 (step 12 module_path fix) ✅
- AC-B.2 (step 11 ProducedAsset factory) ✅
- AC-B.2a (steps 05/06/07 envelope factories) ✅
- AC-B.3 (step 12 QuinnRUnitVerdict factory + consumer_entrypoint) ✅
- AC-B.4 (step 13 QuinnRTwoBranchResult factory with nested PlanRef) ✅
- AC-B.5 (`emit_coverage_manifest()` green on current repo) ✅
- AC-B.6 (factories return real Pydantic instances, not scaffolds) ✅ — AC-T.2-4 all use `isinstance(sample, <real-type>)`.
- AC-B.7 (no schema shape changes) ✅ — `__all__` unchanged, CoverageSurface/Summary/Manifest/Entry field sets unchanged, `SCHEMA_VERSION == "1.0"` unchanged, shape-stable contract test green.
- AC-B.8 (invariant counts on artifact) ✅ — AC-T.5 asserts 6 invariants; all green.
- AC-B.9 (`_resolve_status` relaxation) ✅ — `_IMPLEMENTED_OWNER_STATUSES = {"done", "review"}`; both error paths preserved (done+missing / backlog+exists).
- AC-B.10 (steps 08/09/10 `deferred=True` with notes) ✅
- AC-T.1-5 (5 behavioral tests) ✅ — all green
- AC-C.1 (contract: every implemented entry has callable factory) ✅

**Review verdict:** CLEAN PASS. **0 PATCH** / **1 DEFER** (EC-7 concurrent-session snapshot hardening → `deferred-work.md §32-2a`) / **~5 DISMISS** per §3 aggressive rubric.

**K discipline:** K=4 floor. Landing 6 collecting functions at 1.5×K ceiling (exact target-range top). No coverage-gap justification required; inside 1.2-1.5× window.

**Regression:** default suite `1885 passed / 4 skipped / 27 deselected / 2 xfailed / 0 failed` (36.44s). No new failures vs. pre-32-2a baseline.

**Governance:** validator PASS both at `ready-for-dev` gate and final gate.
