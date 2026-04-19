# Story 29-2: Gagne Diagnostician

**Status:** done
**Created:** 2026-04-18
**Epic:** 29 - Enhanced Irene
**Sprint key:** `29-2-gagne-diagnostician`
**Branch:** `dev/lesson-planner`
**Points:** 5
**Depends on:** **29-1 (done)** - consumes `FitReport`, `FitDiagnosis`, `validate_fit_report`, and the canonical fit-report import surface from `marcus/lesson_plan/fit_report.py`; **31-3 (done)** - consumes `get_modality_entry()` for `modality_ref` validity checks.
**Related upstream/downstream surfaces:** **31-1**, **31-5**, **30-3a**, **30-5**, **28-3** - 31-1 defines the schema carriers, 31-5 later emits prior Declined rationales, 30-3a and 30-5 consume Irene's fit verdicts, and 28-3 routes `IdentifiedGap` follow-up work from the same diagnostic seam.
**Blocks:** **30-3a** (4A skeleton and lock), **30-5** (retrieval narration grammar), **28-3** (Irene-Tracy bridge), and **29-3** (blueprint co-author) - each depends on a real Irene diagnostic artifact rather than hand-waved plan-unit commentary.

---

## TL;DR

Ship a deterministic Irene diagnostician that walks the Lesson Plan's Gagne events, emits one `FitDiagnosis` per `PlanUnit`, validates `modality_ref` against the 31-3 registry, carries forward prior Declined rationales when present, and returns a `FitReport` through the canonical 29-1 surface while staying inside the sync-only latency contract.

## Story

As the **Lesson Planner MVP diagnostician owner**,
I want **a deterministic Gagne-event diagnostic module that turns a live `LessonPlan` into a validated `FitReport` with stable recommendations and commentary**,
So that **Marcus can reason over Irene's source-fitness verdicts, downstream stories can consume a real fit-report artifact, and settled out-of-scope judgments are not re-diagnosed from scratch on every run**.

## Background - Why This Story Exists

29-1 intentionally stopped at the wrapper seam: it shipped the `FitReport` / `FitDiagnosis` transport, validator, serializer, and emission surface, but it did not decide how Irene should actually populate the diagnoses. That gap is 29-2's scope. The Lesson Plan schema from 31-1 already carries `source_fitness_diagnosis`, `weather_band`, `scope_decision`, `modality_ref`, and `gaps[]` on every `PlanUnit`; 29-2 is the story that consolidates those per-unit signals into a formal `FitReport`.

The governing constraint is not "make Irene smart at any cost." The constraint is "produce a stable, sync-only diagnosis artifact that downstream stories can trust." Murat's readiness gate in the MVP plan pins two properties here:

- **Latency:** p95 <= 30s over a 20-run batch, with any single run >45s treated as a failure.
- **Stability:** zero taxonomy variance across 10 consecutive runs on the same input.

That pushes 29-2 toward deterministic rule composition rather than freeform runtime improvisation. The story also carries forward 29-1's deferred duplicate-`unit_id` finding: duplicate diagnoses are naturally prevented here, at construction time, instead of being tolerated and then cleaned up downstream.

Finally, ruling amendment 15 named a concrete carry-forward behavior: when 31-5 later emits Declined-with-rationale records for out-of-scope units, the next Irene run must preload those rationales so it does not re-litigate already-settled ground. 29-2 therefore has to define an input seam for prior Declined rationales now, even if the full producer lands later.

## T1 Readiness

- **Gate mode:** `dual-gate` per `docs/dev-guide/story-cycle-efficiency.md`
- **K floor:** `K = 10`
- **Target collecting-test range:** `12-15`
- **Required readings:** `docs/dev-guide/story-cycle-efficiency.md`, `docs/dev-guide/dev-agent-anti-patterns.md`, `docs/dev-guide/pydantic-v2-schema-checklist.md`
- **Scaffold required:** no - this is not a schema-story
- **Anti-pattern categories in scope:** late invention of fit-report semantics inside downstream stories; duplicate diagnoses that silently collapse in 29-1's validator; fake latency compliance with no measured timing surface; modality recommendations that ignore the 31-3 registry; re-diagnosing prior Declined rationales instead of carrying them forward
- **Runway pre-work available:** fit-report seam and registry seam are already landed; 30-3a and 30-5 consumers can reference the diagnostician's import surface as soon as the module and tests are committed

## Acceptance Criteria

### Behavioral / Contract (AC-B.*)

1. **AC-B.1 - Canonical diagnostician module.** A new module under `marcus/lesson_plan/` exposes the 29-2 public surface:
   - `diagnose_lesson_plan(...) -> FitReport`
   - `diagnose_plan_unit(...) -> FitDiagnosis`
   - a typed carry-forward input seam for prior Declined rationales
   - explicit exception types for duplicate diagnosis targets or unsupported plan-unit shapes when needed

2. **AC-B.2 - One diagnosis per plan unit, stable ordering.** `diagnose_lesson_plan(...)` emits exactly one `FitDiagnosis` for each `LessonPlan.plan_units[*]`, preserving the input order. Duplicate `unit_id` targets in the produced diagnosis list are forbidden and fail fast before the report is returned.

3. **AC-B.3 - Hardcoded Gagne-event seam.** The diagnostician is intentionally hardcoded to the MVP Gagne-9 seam. It accepts the nine canonical `gagne-event-N` labels, preserves ordering from the input plan, and fails explicitly if the plan contains an unsupported `event_type` for this diagnostician mode instead of silently inventing a taxonomy.

4. **AC-B.4 - Registry-backed `modality_ref` validation.** If a `PlanUnit.modality_ref` is non-null, Irene validates it through `get_modality_entry(...)` from 31-3. Registered `ready` and `pending` modalities are both accepted as valid registry keys. Unknown modalities are reflected in the diagnosis output as a negative fit signal; they are not silently treated as valid strings.

5. **AC-B.5 - Diagnosis logic is deterministic and recommendation-bearing.** Each `FitDiagnosis` populates:
   - `unit_id`
   - `fitness`
   - `commentary`
   - `recommended_scope_decision`
   - `recommended_weather_band`
   using deterministic rules over the live `PlanUnit` surface (`source_fitness_diagnosis`, `weather_band`, `scope_decision`, `modality_ref`, `gaps[]`) plus any carry-forward Declined rationale.

6. **AC-B.6 - Prior Declined rationale carry-forward seam.** `diagnose_lesson_plan(...)` accepts an optional collection of prior Declined rationales keyed to `unit_id`. When a prior rationale exists for a unit and the live plan still points toward an out-of-scope verdict, the diagnostician carries that rationale forward into commentary instead of re-diagnosing settled ground from zero. Absence of prior rationale input is legal and does not change baseline behavior.

7. **AC-B.7 - Fit-report construction uses the canonical 29-1 seam.** The diagnostician returns a real `FitReport` with:
   - `schema_version="1.0"`
   - caller-supplied `source_ref`
   - fresh `plan_ref` built from the live `LessonPlan`
   - ordered `diagnoses`
   - timezone-aware `generated_at`
   - measured `irene_budget_ms`
   Before return, the report is run through `validate_fit_report(report, plan=plan)` so 29-2 cannot drift away from 29-1's transport contract.

8. **AC-B.8 - Sync-only latency measurement and named fallback contract.** The diagnostician measures elapsed runtime in milliseconds and records it in `FitReport.irene_budget_ms`. It also exposes a named fallback path for budget-breach handling: if the diagnostic pass breaches the configured budget threshold, the module can switch to a simpler commentary strategy while preserving one diagnosis per unit and a valid `FitReport`. The fallback path is explicit and testable; it is not an undocumented timeout side effect.

9. **AC-B.9 - Canonical caller boundary remains intact.** 29-2 constructs and validates `FitReport` instances but does not emit them to the log directly. `emit_fit_report(...)` remains Marcus-Orchestrator's canonical caller surface per 29-1.

### Test (AC-T.*)

1. **AC-T.1 - Public-surface smoke.** A smoke test proves `diagnose_lesson_plan` and `diagnose_plan_unit` import cleanly from the canonical module path and return `FitReport` / `FitDiagnosis` objects immediately usable by downstream callers.
2. **AC-T.2 - Deterministic replay.** Re-running the diagnostician against the same frozen `LessonPlan` input 10 consecutive times yields zero taxonomy drift across `fitness`, `recommended_scope_decision`, and `recommended_weather_band`.
3. **AC-T.3 - One-diagnosis-per-unit guarantee.** The returned diagnosis list length equals the plan-unit length, preserves order, and rejects duplicate `unit_id` targets before report return.
4. **AC-T.4 - Registry validity matrix.** Tests cover `modality_ref=None`, registered `ready`, registered `pending`, and unknown modality strings; unknown values must surface as a negative fit signal rather than a silent pass.
5. **AC-T.5 - Prior Declined rationale carry-forward.** When prior Declined rationale is supplied for a matching out-of-scope unit, commentary changes in a stable, explicit way; when no rationale is supplied, baseline commentary remains unchanged.
6. **AC-T.6 - Unsupported event-type rejection.** Plans that carry a non-Gagne event label into the diagnostician fail explicitly with a named exception or a precise `ValueError`.
7. **AC-T.7 - Fit-report contract compliance.** The returned report passes `validate_fit_report(report, plan=plan)` and carries a fresh `plan_ref`.
8. **AC-T.8 - Fallback-contract exercise.** A testable slow-path or injected timer proves the named fallback contract activates when the budget threshold is breached, while still returning a valid `FitReport`.
9. **AC-T.9 - Timezone awareness.** `generated_at` is timezone-aware and round-trips cleanly through 29-1's serializer.
10. **AC-T.10 - No direct emission boundary.** A grep or contract test proves 29-2 production code does not call `emit_fit_report(...)` directly.

### Contract Pinning / Closeout (AC-C.*)

1. **AC-C.1 - Package export surface.** If `marcus.lesson_plan.__init__` re-exports the new diagnostician helpers, tests pin the export surface directly.
2. **AC-C.2 - No schema bump.** 29-2 introduces no new Lesson Plan schema version and does not edit `SCHEMA_CHANGELOG.md`; it consumes the 31-1 / 29-1 shapes as-is.
3. **AC-C.3 - Downstream import seam is explicit.** The story names the canonical import path downstream consumers must use when 29-2 closes.

## File Impact (preliminary - refined at bmad-dev-story)

- **NEW:** `marcus/lesson_plan/gagne_diagnostician.py` - deterministic Irene diagnosis logic + prior-rationale seam + budget fallback
- **UPDATED:** `marcus/lesson_plan/__init__.py` - optional package re-exports for the diagnostician surface
- **NEW:** `tests/test_gagne_diagnostician.py`
- **NEW:** `tests/contracts/test_gagne_diagnostician_no_emit_boundary.py`
- **NEW:** `tests/contracts/test_lesson_plan_package_exports_29_2.py` (only if package re-exports are added)

## Tasks / Subtasks (preliminary - refined at bmad-dev-story)

- [x] T1 - Author the diagnostician module with clear public helpers and typed carry-forward input seam.
- [x] T2 - Implement deterministic per-unit fitness / recommendation logic over the existing `LessonPlan` schema.
- [x] T3 - Enforce one-diagnosis-per-unit and duplicate-target rejection.
- [x] T4 - Validate non-null `modality_ref` through the 31-3 registry surface.
- [x] T5 - Build the returned `FitReport` through the 29-1 contract and measure elapsed budget.
- [x] T6 - Implement the named fallback contract for budget-breach handling.
- [x] T7 - Add targeted unit + contract tests within the `12-15` collecting-test budget.
- [x] T8 - Run focused regression, then the dual-gate review lane.

## Test Plan

`tests_added >= K` with **K = 10**.

**Target range:** `12-15` collecting tests per `docs/dev-guide/story-cycle-efficiency.md`.

Keep the families tight and conceptual:

- one smoke/public-surface family,
- one deterministic replay family,
- one duplicate/order family,
- one modality-registry family,
- one carry-forward rationale family,
- one unsupported-event family,
- one fit-report contract family,
- one fallback-contract family,
- one no-direct-emission boundary family.

If the count rises above 15, the Dev Agent Record must name the concrete coverage gap per the efficiency policy.

## Out of Scope

- Emitting the `FitReport` to the Lesson Plan log; Marcus-Orchestrator still owns that.
- Replacing 29-1's validator or serializer.
- Any Tracy dispatch behavior; 28-3 consumes this story later.
- Blueprint co-authoring behavior; 29-3 owns that.
- 31-5's actual Declined-rationale producer format beyond the minimal carry-forward seam 29-2 needs now.

## Dependencies on Ruling Amendments / Prior Findings

- **R1 amendment 15** - prior Declined rationales must be consumable on the next Irene run.
- **29-1 deferred finding `#3-dedup`** - duplicate diagnosis targets are naturally owned by 29-2 at construction time.
- **31-3 consumer-contract fixture** - Irene validates `modality_ref` through the registry, not ad hoc string rules.
- **Story-cycle-efficiency dual-gate classification** - 29-2 carries latency and taxonomy-stability risk, so it stays dual-gate.

## Risks

- **Over-smart heuristics risk:** overfitting diagnosis logic beyond the existing schema fields bloats the story. Mitigation: keep 29-2 deterministic and schema-driven.
- **Latency theater risk:** claiming `<30s` without a measured timing surface. Mitigation: always record `irene_budget_ms` and test the fallback path.
- **Drift risk between diagnosis logic and downstream expectations:** 30-3a / 30-5 may later assume different semantics. Mitigation: document the import seam and keep the rule surface explicit in tests.
- **Carry-forward ambiguity risk:** 31-5 is not landed yet. Mitigation: accept a minimal typed seam keyed by `unit_id`, not a speculative future envelope.

## Dev Notes

### Architecture

29-2 belongs in `marcus.lesson_plan`, not an ad hoc Irene-only package, because the rest of the Lesson Planner contract surfaces already live there and downstream consumers expect one reviewable package seam. The diagnostician is Irene-authored behavior, but the artifact it returns is part of the shared Lesson Planner transport layer.

The module should treat 31-1's `LessonPlan` as the single source of truth for the current run, 31-3's registry as the single source of truth for modality validity, and 29-1's validator as the single source of truth for returned fit-report correctness. No duplicate schema, no second validator.

### Anti-patterns (dev-agent WILL get these wrong without explicit warning)

Reference `docs/dev-guide/dev-agent-anti-patterns.md` for the shared catalog. Story-specific traps:

- Do not call `emit_fit_report(...)` from Irene-side production code.
- Do not silently collapse duplicate diagnosis targets; fail fast.
- Do not treat unknown `modality_ref` values as valid just because the field type is `str | None`.
- Do not hand-wave the latency gate because the current implementation is fast; the measured surface and fallback contract are part of the story.
- Do not invent a speculative 31-5 payload schema; consume a minimal typed seam keyed by `unit_id`.

### Source Tree (new + touched)

```text
marcus/lesson_plan/gagne_diagnostician.py
marcus/lesson_plan/__init__.py
tests/test_gagne_diagnostician.py
tests/contracts/test_gagne_diagnostician_no_emit_boundary.py
tests/contracts/test_lesson_plan_package_exports_29_2.py   # only if re-exported
```

### Canonical downstream import seam

When 29-2 closes, downstream code should be able to run:

```python
from marcus.lesson_plan.gagne_diagnostician import (
    diagnose_lesson_plan,
    diagnose_plan_unit,
)
```

That import path is the completion handshake for this story.

## Governance Closure Gates

- [x] Acceptance criteria met.
- [x] Automated verification green for the 29-2 scope.
- [x] Dual-gate workflow completed: create-story -> dev-story -> post-dev code review.
- [x] `sprint-status.yaml` and hot-start docs updated in closeout order.

## Dev Agent Record

**Executed by:** Codex, following the Amelia / `bmad-agent-dev` workflow locally after subagent spawning proved unreliable in this run.
**Date:** 2026-04-18.

### Landed artifacts

- `marcus/lesson_plan/gagne_diagnostician.py` - deterministic diagnostician with carry-forward rationale seam, registry-backed modality validation, duplicate-target rejection, and the named `summary-only` budget fallback.
- `marcus/lesson_plan/__init__.py` - package exports extended with the 29-2 public surface.
- `tests/test_gagne_diagnostician.py` - focused behavior and regression suite.
- `tests/contracts/test_gagne_diagnostician_no_emit_boundary.py` - canonical no-direct-emission boundary pin.
- `tests/contracts/test_lesson_plan_package_exports_29_2.py` - package-export contract pin.

### Verification

- Governance validator: `python scripts/utilities/validate_lesson_planner_story_governance.py _bmad-output/implementation-artifacts/29-2-gagne-diagnostician.md`
- Targeted 29-2 + 29-1 seam regression: `py -3.13 -m pytest tests/test_gagne_diagnostician.py tests/test_fit_report_validator.py tests/test_fit_report_smoke.py tests/contracts/test_gagne_diagnostician_no_emit_boundary.py tests/contracts/test_fit_report_canonical_caller.py tests/contracts/test_lesson_plan_package_exports_29_2.py -q` -> `28 passed`
- Focused 29-2 contract slice: `py -3.13 -m pytest tests/test_gagne_diagnostician.py tests/contracts/test_gagne_diagnostician_no_emit_boundary.py tests/contracts/test_lesson_plan_package_exports_29_2.py -q` -> `16 passed`
- Ruff: `ruff check marcus/lesson_plan/gagne_diagnostician.py tests/test_gagne_diagnostician.py tests/contracts/test_gagne_diagnostician_no_emit_boundary.py tests/contracts/test_lesson_plan_package_exports_29_2.py marcus/lesson_plan/__init__.py` -> `All checks passed`

### Completion Notes

- The diagnostician stays intentionally deterministic and schema-driven. It does not invent a second fit-report schema or bypass 29-1's validator.
- `modality_ref` validation is delegated to 31-3's registry, so pending modalities remain valid keys while unknown strings degrade the fit verdict explicitly.
- The 29-1 deferred duplicate-diagnosis concern now fails fast at construction time in 29-2 instead of being silently collapsed downstream.
- The carry-forward seam for prior Declined rationales is minimal and typed (`PriorDeclinedRationale` keyed by `unit_id`), which keeps 29-2 unblocked without speculating about 31-5's final transport artifact.
- Collecting-test footprint stayed inside budget: 13 collecting tests across the new 29-2 files, 16 pytest nodeids after parametrization.

## Review Record

### Dual-gate pre-dev review

The story was authored as `ready-for-dev` with the dual-gate policy, T1 readiness block, K-floor discipline, and downstream seam choices made explicit before implementation started. No additional pre-dev riders were required after governance validation passed.

### Post-dev code review

**Workflow:** `bmad-code-review`, executed locally.
**Verdict:** clear - no material findings after focused regression and linting.

- **APPLY:** none
- **DEFER:** none
- **DISMISS:** none
