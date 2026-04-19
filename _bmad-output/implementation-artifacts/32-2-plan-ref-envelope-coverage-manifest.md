# Story 32-2: Plan-Ref Envelope Coverage Manifest

**Status:** done
**Created:** 2026-04-18
**Epic:** 32 — Step 4A landing + trial-run harness
**Sprint key:** `32-2-plan-ref-envelope-coverage-manifest`
**Branch:** `dev/lesson-planner`
**Points:** 3
**Depends on:** **31-2 (done)** — consumes `assert_plan_fresh`, `StalePlanRefError`, `LessonPlanLog.latest_plan_revision()`, and the plan-ref duck-typing contract from `marcus/lesson_plan/log.py`.
**Related upstream/downstream surfaces:** **30-2b**, **30-4**, **31-4**, **31-5**, **32-1**, **32-3** — these stories either emit or consume the envelopes that 32-2 audits.
**Blocks:** **32-3** (trial-run smoke harness) — smoke cannot claim "trial-run-ready" until envelope plan-ref coverage is enumerated and proven.

---

## TL;DR

Ship a `coverage-manifest` verifier that enumerates every Lesson Planner downstream envelope surface (steps 05→13), proves each one carries `{lesson_plan_revision, lesson_plan_digest}`, and records whether each surface actually gates itself with `assert_plan_fresh(...)` before processing.

## Story

As the **Lesson Planner MVP contract-audit author**,
I want **a `coverage-manifest` artifact and verifier that enumerates all downstream envelope producers and consumers against the shared plan-ref contract**,
So that **trial runs cannot proceed on hand-waved freshness assumptions, and every envelope in the 05→13 path is forced to either prove plan-ref coverage or fail the audit explicitly**.

## Background — Why This Story Exists

31-1 established the typed `PlanRef` shape (`lesson_plan_revision`, `lesson_plan_digest`). 31-2 established the operational freshness gate via `assert_plan_fresh(envelope)` and documented that **32-2 is the story that audits coverage across all downstream envelopes 05→13**. Ruling amendment 14 then refined 32-2 away from "generic audit logic" into a specific deliverable: a `coverage-manifest` verifier whose output becomes a precondition for 32-3's trial-run smoke harness.

This story is intentionally narrow. It does not create the downstream envelopes themselves. It creates the contract-audit surface that verifies whether those envelopes, as introduced by other stories, actually carry the required plan-ref fields and freshness-gate behavior. That is why the audit logic lives on top of 31-2's log module rather than duplicating the staleness rules in each future story.

When 32-2 closes, downstream trial validation has a single source of truth for:

- which story/module owns each step-05→13 envelope surface,
- whether that surface carries `lesson_plan_revision`,
- whether it carries `lesson_plan_digest`,
- whether it calls `assert_plan_fresh(...)`,
- and whether the surface is implemented, deferred, or intentionally exempt.

## T1 Readiness

- **Gate mode:** `single-gate` per `docs/dev-guide/story-cycle-efficiency.md`
- **K floor:** `K = 6`
- **Target collecting-test range:** `8-9`
- **Required readings:** `docs/dev-guide/story-cycle-efficiency.md`, `docs/dev-guide/dev-agent-anti-patterns.md`, `docs/dev-guide/pydantic-v2-schema-checklist.md`
- **Scaffold required:** yes — instantiate from `docs/dev-guide/scaffolds/schema-story/` or `scripts/utilities/instantiate_schema_story_scaffold.py`
- **Anti-pattern categories in scope:** over-testing without named coverage gaps; schema drift between artifact and verifier; fake freshness checks that only assert field presence without calling `assert_plan_fresh`; hard-coding future envelope inventory in ways that break when emitters land
- **Runway pre-work available:** scaffold instantiation and fixture planning can happen before the implementation lane opens; no authoritative implementation should start until the emitting-story inventory below is re-confirmed against current sprint state

## Acceptance Criteria

### Behavioral / Schema (AC-B.*)

1. **AC-B.1 — `coverage-manifest` artifact shape.** A new module under `marcus/lesson_plan/` defines the typed manifest surface for this story. The top-level manifest includes:
   - `schema_version: str`
   - `generated_at: datetime`
   - `source_story_key: str`
   - `surfaces: list[CoverageSurface]`
   - `summary: CoverageSummary`

2. **AC-B.2 — `CoverageSurface` enumerates one envelope contract surface.** Each entry captures:
   - `step_id: Literal["05", "06", "07", "08", "09", "10", "11", "12", "13"]`
   - `surface_name: str`
   - `owner_story_key: str`
   - `module_path: str`
   - `artifact_kind: Literal["envelope", "produced-asset", "fit-report", "gate-payload", "manifest-entry"]`
   - `plan_ref_mode: Literal["top-level-fields", "nested-plan-ref"]`
   - `has_lesson_plan_revision: bool`
   - `has_lesson_plan_digest: bool`
   - `assert_plan_fresh_required: bool`
   - `assert_plan_fresh_verified: bool`
   - `status: Literal["implemented", "pending", "deferred"]`
   - `notes: str`

3. **AC-B.3 — manifest inventory is explicit, story-owned, and concrete.** The verifier ships with a module-level inventory covering the downstream contract surfaces expected across steps 05→13, keyed by the producing story that introduces them. The inventory must name at least these story-owned surfaces:
   - `30-2b` pre-packet envelope emission
   - `30-4` plan-lock fanout envelopes (the start of the 05+ branch)
   - `31-4` blueprint-producer output surface
   - `31-5` Quinn-R gate payload / branch result surface
   - any concrete `ProducedAsset`-consumer boundaries that inherit the plan-ref fields from `marcus/lesson_plan/produced_asset.py`
   The inventory may include `pending` surfaces for not-yet-landed stories, but they must be explicit rather than inferred from thin air. One abstract family row is NOT enough; each real producer/consumer boundary gets its own manifest entry.

4. **AC-B.4 — plan-ref verification distinguishes top-level vs nested contracts.** The verifier supports both:
   - surfaces that expose `lesson_plan_revision` and `lesson_plan_digest` directly as top-level attributes, and
   - surfaces that carry a nested `plan_ref: PlanRef` object.
   The manifest records which mode applies per surface and validates accordingly.

5. **AC-B.5 — freshness-gate verification is stronger than field presence.** For each surface marked `assert_plan_fresh_required=True`, the verifier must prove more than "these fields exist." The verification mechanism is **AST-based source inspection over the named owner module and concrete consumer entrypoint**, with import-path-aware symbol tracing back to `marcus.lesson_plan.log.assert_plan_fresh`. Accepted proofs are limited to:
   - direct invocation of the imported canonical symbol, or
   - a same-module local wrapper that itself calls the imported canonical symbol and is invoked on the live entry path before downstream processing.
   Loose grep matches, same-name counterfeit helpers, dead wrappers, comment-only claims, or wrappers that call the canonical symbol on the wrong object do not count.

6. **AC-B.6 — pending surfaces are first-class, not silent omissions.** If a future emitting story has not landed yet, its surface remains in the manifest with `status="pending"` and `assert_plan_fresh_verified=False`. A surface may remain `pending` only when BOTH of these are true:
   - the named owning story is not yet `done` in `sprint-status.yaml`, and
   - the named `module_path` / consumer entrypoint does not yet exist in the codebase.
   If the code surface exists, or the owning story is already `done`, `pending` is illegal and the verifier must fail on stale inventory state. `deferred` is reserved for explicitly logged follow-up work, not for hiding landed-but-unverified surfaces.

7. **AC-B.7 — summary rollup is machine-readable.** `CoverageSummary` reports:
   - total surfaces
   - implemented surfaces
   - pending surfaces
   - surfaces with full plan-ref coverage
   - surfaces missing one or both fields
   - surfaces missing freshness-gate verification
   - whether the manifest is `trial_ready`
   `trial_ready` is true only if every implemented surface has full plan-ref coverage and verified freshness gating.

8. **AC-B.8 — artifact emission path, format, and consumer contract are explicit.** The story emits one canonical JSON artifact at `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json`. The file is committed, diff-friendly, and ordered by `step_id`, then `owner_story_key`, then `surface_name`. `32-3` consumes this file directly and treats `summary.trial_ready` as a gating field rather than recomputing the audit independently. Re-running the verifier against unchanged inputs produces byte-stable output apart from `generated_at`.

### Test (AC-T.*)

1. **AC-T.1 — shape-stable contract test.** Pin the `coverage-manifest` schema surface with a dedicated contract test and `SCHEMA_CHANGELOG.md` gate.
2. **AC-T.2 — JSON-schema ↔ Pydantic parity.** Verify field presence, required/optional parity, enum fidelity, and `additionalProperties: false` discipline.
3. **AC-T.3 — no-leak grep test.** User-facing descriptions and manifest notes must not introduce `intake` / `orchestrator` leakage into Maya-facing prose; internal module paths are allowed where the artifact is explicitly engineering-only.
4. **AC-T.4 — top-level-field verification matrix.** Tests cover surfaces exposing `lesson_plan_revision` and `lesson_plan_digest` as direct attributes, including positive and missing-field cases.
5. **AC-T.5 — nested `plan_ref` verification matrix.** Tests cover surfaces exposing a nested `PlanRef`, including malformed nested payloads and parity with the top-level mode.
6. **AC-T.6 — `assert_plan_fresh` call-site detection.** Tests prove the verifier accepts:
   - direct `assert_plan_fresh(surface)` calls,
   - thin local wrappers around `assert_plan_fresh`,
   and rejects:
   - no call at all,
   - dead helper never invoked,
   - fake helper with the same name but no import path to `marcus.lesson_plan.log.assert_plan_fresh`,
   - wrappers that call the canonical symbol on the wrong object or off the live consumer path.
7. **AC-T.7 — pending-surface handling.** Pending future surfaces remain visible in the manifest and do not falsely mark `trial_ready=true`.
8. **AC-T.8 — summary rollup.** `trial_ready` flips false when any implemented surface lacks fields or freshness-gate verification.
9. **AC-T.9 — deterministic artifact ordering.** Manifest emission is stable across repeated runs.

### Contract Pinning (AC-C.*)

1. **AC-C.1 — `SCHEMA_CHANGELOG.md` entry.** Add a dedicated `Coverage Manifest v1.0` entry with `Migration: N/A`.
2. **AC-C.2 — explicit reference to 31-2 freshness contract.** The artifact and tests cite `marcus/lesson_plan/log.py` as the source of truth for the staleness-gate semantics; 32-2 does not re-specify those rules independently.
3. **AC-C.3 — inventory drift is intentional.** Adding or removing a named audited surface requires updating the manifest inventory and the story-owned contract tests in the same change.

## File Impact (preliminary — refined at bmad-dev-story)

- **NEW:** `marcus/lesson_plan/coverage_manifest.py` — typed manifest models + verifier + deterministic emitter.
- **NEW:** `marcus/lesson_plan/schema/coverage_manifest.v1.schema.json` — emitted JSON Schema for the artifact.
- **NEW:** `tests/contracts/test_coverage_manifest_shape_stable.py`
- **NEW:** `tests/contracts/test_coverage_manifest_json_schema_parity.py`
- **NEW:** `tests/contracts/test_no_intake_orchestrator_leak_coverage_manifest.py`
- **NEW:** `tests/test_coverage_manifest_plan_ref_verifier.py`
- **NEW:** `tests/test_coverage_manifest_assert_plan_fresh_detection.py`
- **NEW:** `tests/test_coverage_manifest_summary.py`
- **NEW:** `tests/fixtures/lesson_plan/coverage_manifest/` — call-site detection fixtures only; top-level vs nested field cases stay inline in tests.
- **APPENDED:** `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md`

## Tasks / Subtasks (preliminary — refined at bmad-dev-story)

- [x] T1 — Reconfirm the 05→13 emitting-surface inventory against current landed stories before implementation starts.
- [x] T2 — Instantiate the schema-story scaffold for `coverage_manifest`.
- [x] T3 — Author typed manifest models and deterministic emitter.
- [x] T4 — Encode the explicit step-05→13 inventory with owner-story metadata.
- [x] T5 — Implement top-level and nested plan-ref verification.
- [x] T6 — Implement `assert_plan_fresh` call-site / wrapper detection.
- [x] T7 — Emit JSON Schema artifact.
- [x] T8 — Author contract tests.
- [x] T9 — Author verifier behavior tests and fixture cases.
- [x] T10 — Append `SCHEMA_CHANGELOG.md`.
- [x] T11 — Full regression + ruff.
- [x] T12 — Single post-dev review + patch cycle, then closeout hygiene.

## Test Plan

`tests_added ≥ K` with **K = 6**.

**Target range:** `8-9` collecting tests per `docs/dev-guide/story-cycle-efficiency.md`.

The test surface should stay narrow. Budget it as conceptual families, not matrix theater:

- one contract pin family,
- one parity family,
- one no-leak family,
- one top-level vs nested plan-ref family (inline factories/stubs, not file-fixture sprawl),
- one freshness-gate detection family,
- one summary/determinism family.

If the count rises above 9, the Dev Agent Record must name the concrete coverage gap.

## Out of Scope

- Implementing any step-05→13 envelope producers themselves.
- Retrofitting future stories before those stories open.
- Replacing `assert_plan_fresh` with a new freshness mechanism.
- Deduping duplicate log events or compacting the Lesson Plan log.
- End-to-end trial smoke; that belongs to 32-3.

## Dependencies on Ruling Amendments

- **R1 amendment 14** — 32-2 is refined into a coverage-manifest verifier rather than generic audit logic.
- **31-2 carry-forward contract** — every envelope 05→13 carries `{lesson_plan_revision, lesson_plan_digest}` and uses `assert_plan_fresh(...)`; 32-2 audits that claim.
- **Story-cycle-efficiency single-gate policy** — 32-2 is precedent-heavy and narrow, so it remains single-gate.

## Risks

- **Inventory drift risk:** future stories may rename envelope surfaces. Mitigation: inventory is explicit and story-owned rather than regex-discovered magic.
- **False-positive call-site detection risk:** wrapper detection could over-match helpers that do not actually call `assert_plan_fresh`. Mitigation: tests require import-path-aware verification.
- **Over-testing risk:** the verifier invites combinatorial matrices. Mitigation: keep tests at the conceptual-surface level, not every future envelope permutation.

## Dev Notes

### Architecture

32-2 sits between the foundational plan/log contract (`31-1`, `31-2`) and the end-to-end harness (`32-3`). It is the audit seam that says "before we run trial smoke, do the downstream envelopes actually preserve plan freshness semantics?" That makes it a contract-enforcement story, not a workflow story.

The manifest should treat `PlanRef` and `ProducedAsset` as canonical precedent surfaces rather than inventing a second plan-ref vocabulary. `marcus.lesson_plan.log.assert_plan_fresh` remains the single operational source of truth.

### Anti-patterns (dev-agent WILL get these wrong without explicit warning)

Reference `docs/dev-guide/dev-agent-anti-patterns.md` for the shared catalog. Story-specific traps:

- Do not equate "field exists" with "freshness is enforced."
- Do not silently skip future step surfaces because their emitters are pending.
- Do not encode the inventory as a brittle grep over string literals alone.
- Do not let `pending` become a hiding place for already-landed code surfaces.
- Do not let fixture-heavy matrix expansion turn a K=6 story into another 5x-overrun.

### Source Tree (new + touched)

```text
marcus/lesson_plan/coverage_manifest.py
marcus/lesson_plan/schema/coverage_manifest.v1.schema.json
tests/contracts/test_coverage_manifest_shape_stable.py
tests/contracts/test_coverage_manifest_json_schema_parity.py
tests/contracts/test_no_intake_orchestrator_leak_coverage_manifest.py
tests/test_coverage_manifest_plan_ref_verifier.py
tests/test_coverage_manifest_assert_plan_fresh_detection.py
tests/test_coverage_manifest_summary.py
tests/fixtures/lesson_plan/coverage_manifest/
_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json
```

### Testing Standards (inherited)

- Pydantic v2 idioms per `docs/dev-guide/pydantic-v2-schema-checklist.md`
- Anti-patterns per `docs/dev-guide/dev-agent-anti-patterns.md`
- Gate discipline per `docs/dev-guide/story-cycle-efficiency.md`
- Scaffold default for schema-shape stories via `docs/dev-guide/scaffolds/schema-story/`

### References

- `_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md` — Epic 32 row, amendment 14, readiness item R4
- `_bmad-output/implementation-artifacts/31-1-lesson-plan-schema.md` — `PlanRef` contract source
- `_bmad-output/implementation-artifacts/31-2-lesson-plan-log.md` — `assert_plan_fresh` contract and explicit 32-2 audit carry-forward
- `docs/dev-guide/story-cycle-efficiency.md`
- `docs/dev-guide/dev-agent-anti-patterns.md`
- `docs/dev-guide/pydantic-v2-schema-checklist.md`
- `docs/dev-guide/scaffolds/schema-story/`
- `scripts/utilities/instantiate_schema_story_scaffold.py`

## Governance Closure Gates (per CLAUDE.md)

- [x] Acceptance criteria met.
- [x] Automated verification (pytest + ruff + pre-commit hooks).
- [x] Single post-dev review completed.
- [x] Review triage recorded as APPLY / DEFER / DISMISS where needed.
- [x] `sprint-status.yaml` and hot-start docs updated in closeout order.

## Dev Agent Record

**Executed by:** Codex, following the Amelia / `bmad-agent-dev` workflow locally after subagent spawning proved unreliable in this run.
**Date:** 2026-04-18.

### Landed artifacts

| Artifact | Status | Notes |
|----------|--------|-------|
| `marcus/lesson_plan/coverage_manifest.py` | NEW | Typed manifest models, explicit inventory, AST/import-path-aware freshness-gate verification, deterministic emitter, and sprint-status drift detection. |
| `marcus/lesson_plan/schema/coverage_manifest.v1.schema.json` | NEW | JSON Schema artifact for `CoverageManifest`, `CoverageSurface`, and `CoverageSummary`. |
| `marcus/lesson_plan/__init__.py` | TOUCH | Public package exports extended with the 32-2 coverage-manifest surface. |
| `tests/contracts/test_coverage_manifest_shape_stable.py` | NEW | AC-T.1 + AC-C.1 shape pin and changelog gate. |
| `tests/contracts/test_coverage_manifest_json_schema_parity.py` | NEW | AC-T.2 schema parity gate. |
| `tests/contracts/test_no_intake_orchestrator_leak_coverage_manifest.py` | NEW | AC-T.3 no-leak guard. |
| `tests/test_coverage_manifest_plan_ref_verifier.py` | NEW | AC-T.4 + AC-T.5 top-level vs nested plan-ref verification. |
| `tests/test_coverage_manifest_assert_plan_fresh_detection.py` | NEW | AC-T.6 direct-call vs wrapper vs counterfeit detection matrix. |
| `tests/test_coverage_manifest_summary.py` | NEW | AC-T.7 + AC-T.8 + AC-T.9 summary, determinism, and sprint-status parsing coverage. |
| `tests/fixtures/lesson_plan/coverage_manifest/*.py` | NEW | Five call-site fixtures for direct, live-wrapper, dead-wrapper, counterfeit-helper, and wrong-object cases. |
| `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` | NEW | Canonical emitted audit artifact consumed by 32-3. |
| `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` | TOUCH | Added `Coverage Manifest v1.0` entry. |

### Verification

- Governance validator: `python scripts/utilities/validate_lesson_planner_story_governance.py _bmad-output/implementation-artifacts/32-2-plan-ref-envelope-coverage-manifest.md` → **PASSED**
- Targeted 32-2 suite: `python -m pytest tests/contracts/test_coverage_manifest_shape_stable.py tests/contracts/test_coverage_manifest_json_schema_parity.py tests/contracts/test_no_intake_orchestrator_leak_coverage_manifest.py tests/test_coverage_manifest_plan_ref_verifier.py tests/test_coverage_manifest_assert_plan_fresh_detection.py tests/test_coverage_manifest_summary.py -q` → **10 passed**
- Focused Lesson Planner regression: `python -m pytest tests/contracts/test_coverage_manifest_shape_stable.py tests/contracts/test_coverage_manifest_json_schema_parity.py tests/contracts/test_no_intake_orchestrator_leak_coverage_manifest.py tests/contracts/test_lesson_plan_shape_stable.py tests/contracts/test_lesson_plan_json_schema_parity.py tests/contracts/test_scope_decision_transition_event.py tests/contracts/test_event_envelope_shape_stable.py tests/test_coverage_manifest_plan_ref_verifier.py tests/test_coverage_manifest_assert_plan_fresh_detection.py tests/test_coverage_manifest_summary.py tests/test_lesson_plan_log_staleness.py tests/test_lesson_plan_log_single_writer.py tests/test_lesson_plan_log_read_api.py tests/test_lesson_plan_log_named_events.py tests/test_lesson_plan_log_monotonic.py tests/test_lesson_plan_log_g6_hardening.py tests/test_lesson_plan_log_atomic_write.py tests/test_lesson_plan_log_append_only.py tests/test_scope_decision_transitions.py tests/test_event_envelope_mutation_revalidates.py tests/test_digest_determinism.py tests/test_datetime_utc_enforcement.py tests/test_plan_revision_monotonicity.py tests/test_actor_fields_maya_serialization_safe.py -q` → **186 passed, 1 skipped**
- Ruff: `python -m ruff check ...` on all touched 32-2 files → **passed**
- Pre-commit: `python -m pre_commit run --files ...` on all touched 32-2 files → **passed**
- Full repo `python -m pytest -q` is **not fully green in this environment** because unrelated retrieval/Texas tests require optional packages (`responses`, `docx`) that are not installed. Those collection errors are outside 32-2 scope.

### Completion Notes

- Emitted the canonical coverage-manifest artifact at `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json`.
- Current audit result is intentionally conservative: all 9 downstream surfaces are still `pending`, so `summary.trial_ready` is `false` until the emitting stories land.
- Post-dev review surfaced and applied two unambiguous fixes:
  - unknown `owner_story_key` values now fail fast with `CoverageManifestError` instead of silently degrading to `pending`
  - sprint-status parsing now supports letter-suffixed story keys such as `30-2b` and `30-3a`
- `next-session-start-here.md` was checked during closeout and already remained aligned on `29-1`, so no hot-start edit was needed there.

## Review Record

### Single party-mode pre-dev review — 2026-04-18

**Panel:** Winston / Murat / Paige / Dr. Quinn
**Mode:** single advisory round during `bmad-create-story` authoring (used once; does not change the story's single-gate policy)
**Verdict:** YELLOW with convergent riders — all applied before `ready-for-dev`

**Applied riders:**

- Canonical emitted artifact path and `32-3` consumer contract made explicit.
- `assert_plan_fresh` verification pinned to AST + import-path-aware tracing over the live consumer entrypoint.
- `implemented` vs `pending` rules tightened so stale inventory state fails.
- Abstract family coverage disallowed; one manifest row per actual producer/consumer boundary.
- Fixture scope capped to call-site detection cases only.
- Test-family budget clarified to preserve the `K=6`, target `8-9` discipline.

### Single post-dev code review — 2026-04-18

**Workflow:** `bmad-code-review`, executed locally because subagent spawning was unreliable in this run.
**Diff scope:** current 32-2 implementation files against `HEAD`, including new untracked story assets.
**Verdict:** CLEAR after **2 APPLY / 0 DEFER / 0 DISMISS**.

**Applied findings:**

- **APPLY:** inventory rows with an unknown `owner_story_key` now raise `CoverageManifestError` immediately instead of silently appearing as `pending`.
- **APPLY:** `_load_story_statuses()` now recognizes letter-suffixed Lesson Planner story keys (`30-2b`, `30-3a`, etc.), and the regression suite covers that parser behavior explicitly.
