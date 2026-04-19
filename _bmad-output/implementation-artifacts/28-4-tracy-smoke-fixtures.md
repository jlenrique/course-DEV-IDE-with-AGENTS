# Story 28-4: Tracy Smoke Fixtures

**Status:** done
**Created:** 2026-04-19
**Epic:** 28 - Tracy the Detective
**Sprint key:** `28-4-tracy-smoke-fixtures`
**Branch:** `dev/lesson-planner`
**Points:** 3
**Depends on:** **28-2 (done)** - Tracy's three posture contracts are real and stable enough to pin with canned fixtures; **28-3 (done, contextual)** - the bridge now consumes Tracy outputs, so the fixture suite should be usable for later bridge/trial smoke without inventing a second fake result shape.
**Related upstream/downstream surfaces:** **30-5**, **32-3**, **trial-run operator evidence** - 30-5 already consumes Tracy posture outcomes in Marcus voice, 32-3 will need canned research artifacts in the end-to-end smoke path, and the trial-run acceptance checklist explicitly calls for all three Tracy modes to be exercised.
**Blocks:** no critical-path story directly, but this is the dedicated regression pin for Tracy before the trial-run harness opens.

---

## TL;DR

Ship a committed Tracy smoke-fixture suite covering `embellish`, `corroborate`, and `gap-fill`, plus a tiny loader/helper seam so later stories and trial-run checks can consume the same canonical fixtures instead of hand-rolling mock outputs again.

## Story

As the **Lesson Planner MVP Tracy regression owner**,
I want **committed smoke fixtures that cover all three Tracy research postures with stable input/result pairs**,
So that **trial-run and regression paths can prove Tracy still emits the right shapes without depending on live provider behavior or ad hoc mocks**.

## Background - Why This Story Exists

28-2 proved Tracy's three postures at the unit-test level, but those tests are still mostly synthetic mocks embedded in the test file. The MVP plan explicitly calls for "canned research fixtures (DOCX + scite.ai) covering all 3 modes" so the trial-run path can reuse them later.

`28-4` should stay narrow:

- define one canonical fixture location,
- commit a small, readable set of posture fixtures,
- provide one tiny loader/catalog seam so downstream tests do not hardcode file paths,
- pin that each fixture is schema-valid and posture-correct.

This story does **not** add new provider behavior, does **not** reopen Tracy's dispatcher contract, and does **not** try to simulate the full end-to-end lesson-plan flow. It is the reusable smoke-fixture layer that later stories can consume.

## T1 Readiness

- **Gate mode:** `single-gate`
- **K floor:** `K = 6`
- **Target collecting-test range:** `8-9`
- **Required readings:** `docs/dev-guide/story-cycle-efficiency.md`, `docs/dev-guide/dev-agent-anti-patterns.md`, `docs/dev-guide/pydantic-v2-schema-checklist.md`
- **Scaffold required:** no - this is not a schema-story
- **Anti-pattern categories in scope:** inventing a second Tracy output shape just for fixtures; leaving fixture paths undocumented or scattered; using only in-test dict literals instead of committed artifacts; baking live provider assumptions into the smoke path; creating a helper so broad it becomes a second dispatcher
- **Runway / side-work dependency:** none - 28-2 already landed the only required contract

## Acceptance Criteria

### Behavioral / Contract (AC-B.*)

1. **AC-B.1 - Canonical smoke-fixture catalog.** A committed fixture set lands under a stable Tracy-appropriate path in `tests/fixtures/` and covers the three supported postures:
   - `embellish`
   - `corroborate`
   - `gap-fill`

2. **AC-B.2 - Fixture pairs include both brief and result.** Each smoke scenario stores:
   - a minimal Tracy input brief suitable for `PostureDispatcher.select_posture(...)` or direct posture intent,
   - a canonical Tracy result payload in the existing suggested-resources shape.

3. **AC-B.3 - Corroborate fixture preserves scite classification nuance.** The corroborate smoke data includes both supporting and contrasting examples so later smoke paths can prove Tracy still handles "disconfirming is a result type within corroborate" instead of drifting toward a fake fourth posture.

4. **AC-B.4 - Tiny loader/helper seam only.** A small Tracy-side helper module exposes the canonical fixture catalog and returns parsed fixture data for downstream tests. It is read-only and does not dispatch providers.

5. **AC-B.5 - Trial-run-friendly naming.** Fixture identifiers, filenames, and any helper constants are human-readable enough that a later trial-run harness can point to them directly in evidence output.

6. **AC-B.6 - No contract drift.** The fixture result payloads conform to the existing `suggested-resources.schema.json` and the current Tracy vocabulary-lockstep validator. `28-4` does not change the schema or Tracy's runtime output contract.

### Test / Verification (AC-T.*)

1. **AC-T.1 - Fixture catalog loads.** A focused test proves the new helper can enumerate and load the committed fixture suite.
2. **AC-T.2 - All smoke results are schema-valid.** A parametrized test validates every committed result payload with `validate_suggested_resources(...)`.
3. **AC-T.3 - Three posture coverage is pinned.** A test proves the suite covers all three postures exactly as expected.
4. **AC-T.4 - Corroborate classification coverage is pinned.** A test proves the corroborate smoke data includes at least supporting and contrasting classification examples.
5. **AC-T.5 - Brief/result posture parity.** A test proves each fixture's brief and result agree on the intended posture branch.
6. **AC-T.6 - Gap-fill scope discipline is pinned in the smoke data.** A test proves any gap-fill smoke brief remains `scope_decision == "in-scope"`.
7. **AC-T.7 - Loader path contract is stable.** A test proves the helper resolves fixture files from the committed canonical directory rather than from cwd-dependent relative guessing.
8. **AC-T.8 - Read-only boundary.** A contract-style test proves the helper module does not import Tracy dispatch/provider modules or perform network work.

### Closeout / Integration (AC-C.*)

1. **AC-C.1 - Later trial smoke can reuse the same artifacts.** The committed fixture suite is concrete enough for 32-3 or future trial-run checks to consume without re-authoring Tracy payloads.
2. **AC-C.2 - Existing Tracy contract tests remain the source-of-truth for behavior.** 28-4 adds smoke fixtures and reuse seams; it does not replace 28-2's contract tests.
3. **AC-C.3 - No runtime behavior changes.** 28-4 adds fixtures/helper/tests only; Tracy's live dispatcher behavior remains unchanged.

## File Impact (preliminary - refined at `bmad-dev-story`)

- **NEW:** `skills/bmad_agent_tracy/scripts/smoke_fixtures.py` - tiny read-only fixture catalog/loader seam
- **NEW:** `tests/fixtures/retrieval/tracy_smoke/README.md`
- **NEW:** `tests/fixtures/retrieval/tracy_smoke/*.json` - committed smoke scenarios
- **NEW:** `tests/test_tracy_smoke_fixtures.py`
- **NEW:** `tests/contracts/test_tracy_smoke_fixture_loader_boundary.py`

## Tasks / Subtasks (preliminary - refined at `bmad-dev-story`)

- [x] T1 - Author the canonical 28-4 story spec and commit a validator-clean fixture strategy.
- [x] T2 - Add the Tracy smoke fixture helper and the committed scenario files.
- [x] T3 - Add focused smoke-fixture tests inside the `8-9` collecting-test target range.
- [x] T4 - Run focused verification and the single-gate post-dev review lane before closure.

## Test Plan

`tests_added >= K` with **K = 6**.

**Target range:** `8-9` collecting tests per `docs/dev-guide/story-cycle-efficiency.md`.

Keep the families tight:

- one catalog-load family,
- one schema-validity family,
- one posture-coverage family,
- one corroborate-classification family,
- one brief/result parity family,
- one gap-fill scope family,
- one path-stability family,
- one loader-boundary family.

If the count rises above 9, the Dev Agent Record must name the concrete extra coverage gap being purchased.

## Out of Scope

- Any new retrieval/provider behavior.
- Any Tracy dispatcher refactor or output-shape redesign.
- Any Marcus/Irene orchestration work.
- Any live trial-run harness wiring.

## Dependencies on Ruling Amendments / Prior Findings

- **Lesson Planner MVP plan** - 28-4 is the explicit canned-fixture/regression-pin story for Tracy before trial-run work.
- **28-2 closure** - Tracy's posture contracts already exist and should be reused as-is.
- **Story-cycle-efficiency single-gate classification** - 28-4 remains a narrow post-dev-review-only story.

## Risks

- **Fixture drift risk:** later tests might fork their own fake Tracy payloads. Mitigation: one canonical directory + tiny loader seam.
- **Overbuilt helper risk:** a loader that becomes a second dispatcher. Mitigation: read-only catalog only.
- **Schema drift risk:** fixture payloads could stop matching the live schema silently. Mitigation: direct validation test against the existing lockstep validator.

## Dev Notes

### Architecture

The helper should live with Tracy under `skills/bmad_agent_tracy/scripts/` because it is Tracy-owned fixture data, but the actual artifacts belong under `tests/fixtures/` so they are visible and reusable from the broader test harness.

The right implementation shape is:

- a small catalog constant naming the scenarios,
- one helper to resolve the canonical fixture directory,
- one helper to load a named scenario from disk.

No runtime dispatch, no network, no state mutation.

### Canonical downstream import seam

Downstream code should be able to run:

```python
from smoke_fixtures import load_tracy_smoke_fixture, list_tracy_smoke_fixtures
```

from the Tracy scripts path in the same way existing Tracy tests already import `posture_dispatcher`.

## Governance Closure Gates

- [x] Acceptance criteria met.
- [x] Governance validator passes.
- [x] Single-gate workflow completed: create-story -> dev-story -> post-dev code review.
- [x] Status artifacts refreshed in closeout order.

## Dev Agent Record

**Executed by:** Codex, following the Amelia / `bmad-agent-dev` workflow locally.
**Date:** 2026-04-19.

### Landed artifacts

- `skills/bmad_agent_tracy/scripts/smoke_fixtures.py`
- `tests/fixtures/retrieval/tracy_smoke/README.md`
- `tests/fixtures/retrieval/tracy_smoke/embellish_examples.json`
- `tests/fixtures/retrieval/tracy_smoke/corroborate_supporting.json`
- `tests/fixtures/retrieval/tracy_smoke/corroborate_contrasting.json`
- `tests/fixtures/retrieval/tracy_smoke/gap_fill_background.json`
- `tests/test_tracy_smoke_fixtures.py`
- `tests/contracts/test_tracy_smoke_fixture_loader_boundary.py`

### Verification

- `python scripts/utilities/validate_lesson_planner_story_governance.py _bmad-output/implementation-artifacts/28-4-tracy-smoke-fixtures.md`
- `py -3.13 -m pytest tests/test_tracy_smoke_fixtures.py tests/contracts/test_tracy_smoke_fixture_loader_boundary.py -q`
- `ruff check skills/bmad_agent_tracy/scripts/smoke_fixtures.py tests/test_tracy_smoke_fixtures.py tests/contracts/test_tracy_smoke_fixture_loader_boundary.py`
- `pre-commit run --files skills/bmad_agent_tracy/scripts/smoke_fixtures.py tests/fixtures/retrieval/tracy_smoke/README.md tests/fixtures/retrieval/tracy_smoke/embellish_examples.json tests/fixtures/retrieval/tracy_smoke/corroborate_supporting.json tests/fixtures/retrieval/tracy_smoke/corroborate_contrasting.json tests/fixtures/retrieval/tracy_smoke/gap_fill_background.json tests/test_tracy_smoke_fixtures.py tests/contracts/test_tracy_smoke_fixture_loader_boundary.py _bmad-output/implementation-artifacts/28-4-tracy-smoke-fixtures.md`

### Completion Notes

- Landed a read-only Tracy-owned smoke-fixture loader under `skills/bmad_agent_tracy/scripts/` and committed four canonical posture fixtures under `tests/fixtures/retrieval/tracy_smoke/`.
- Kept the suite inside the declared target range by collapsing parametrized families into loop-based assertions, yielding `9` collecting tests against the `8-9` target.
- No runtime Tracy dispatch behavior changed; the story adds reusable regression artifacts only.

## Review Record

### Single-gate post-dev code review

GREEN. No post-verification patch set remained after tightening the test loader and collapsing parametrized collection back into the declared `8-9` range. Final review triage: `0 APPLY / 0 DEFER / 0 DISMISS`.
