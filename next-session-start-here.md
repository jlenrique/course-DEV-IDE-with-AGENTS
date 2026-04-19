# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> **Current objective:** land MVP ratification (plan §F4 party-mode green-light) against the **preflight-flags doc**, then investigate the three at-session-close regressions surfaced by the 2026-04-19 full-suite run.

## Immediate Next Action

1. Run the BMAD Session Protocol Session START.
2. Confirm branch. Session closed on `master` (concurrent sessions merged `dev/lesson-planner` back to master).
3. Use `_bmad-output/implementation-artifacts/sprint-status.yaml` as the canonical status source.
4. **Triage the three at-session-close regressions** (see "At-session-close regressions" below) BEFORE stamping MVP-complete — each is a concurrent-session landing that has not been reconciled with the full suite.
5. **Read the MVP Ratification Preflight Flags** at [_bmad-output/maps/lesson-planner-mvp-ratification-preflight-flags.md](_bmad-output/maps/lesson-planner-mvp-ratification-preflight-flags.md) before convening the F4 bmad-party-mode green-light round.
6. After triage + preflight: convene F4 party-mode round, record per-flag verdict, proceed to MVP-complete or block per verdict.

## Repo State

- **Lesson Planner MVP: all 22 planned stories BMAD-closed** plus one post-audit follow-on (`32-2a`). Epic 32 retrospective remains `optional`.
- **Closed this session:**
  - `32-2a-inventory-hardening` (1pt, single-gate, 2026-04-19) — inventory factory wiring + module-path fix + `_resolve_status` `review`-status tolerance + step 08/09/10 `deferred=True`.
  - `32-4-maya-journey-walkthrough` (3pts, single-gate, 2026-04-19) — operator pantomime walkthrough + canned SME fixture + operator markdown + 9 collecting test functions (14 nodeids).
- **Authored this session (no code):**
  - [_bmad-output/maps/lesson-planner-mvp-ratification-preflight-flags.md](_bmad-output/maps/lesson-planner-mvp-ratification-preflight-flags.md) — 5 named flags for F4 party-mode round.
  - UX-rendering-layer row in [_bmad-output/maps/deferred-work.md](_bmad-output/maps/deferred-work.md) (`## MVP-deferred: rendered UX layer`).
  - Backend-faithfulness preamble in [_bmad-output/maps/maya-journey/maya-walkthrough.md](_bmad-output/maps/maya-journey/maya-walkthrough.md).
  - F4 row amended in [_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md](_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md) §F4 to require reading preflight doc aloud.

## At-session-close regressions (3)

Full regression at 2026-04-19 session close: **1899 passed / 2 failed / 1 collection error / 4 skipped / 27 deselected / 2 xfailed**. None of the three failures are from this session's 32-2a or 32-4 work — all three are concurrent-session landings that have not been reconciled with the full suite. Surface for investigation at next session START:

- **`tests/contracts/test_tracy_postures.py` — ImportError at collection**. `from skills.bmad_agent_tracy.scripts.posture_dispatcher import PostureDispatcher` fails because `tests/conftest.py::_SKILL_SCRIPTS` namespace-module hack creates `skills` as a `types.ModuleType` with `__path__ = []`, which shadows the real `skills/__init__.py` package and breaks all other skills subpackage imports. The hack was authored for `skills.pre_flight_check.scripts` (dashed dir) but overreaches. Fix options: (a) only install the namespace-hack if a real `skills` package isn't already loaded; (b) extend the hack to register `skills.bmad_agent_tracy.scripts` too; (c) keep the hack narrowly scoped and re-import the real `skills` package after. Direct `python -c "from skills.bmad_agent_tracy..."` works — this is pytest-specific.
- **`tests/contracts/test_30_1_zero_test_edits.py::test_no_preexisting_test_files_modified_in_30_1` — AssertionError (30-1 zero-edit invariant violated)**. The baseline commit pinned by 30-2b (`d1a788c`) is out of date vs. current master — concurrent-session commits (32fea9b, b98aad6, etc.) touched pre-existing test files within the 30-1 allowlist boundary. Fix: roll the baseline forward to the latest green commit and regenerate the `_ALLOWED_MODIFIED_PATHS_UNDER_TESTS` allowlist.
- **`tests/test_marcus_workflow_runner_32_1.py::test_hud_pipeline_contains_4a_between_04x_and_05` — AssertionError `'04A' not in ['01', '02', '02A', '03', '04', '04.5', ...]`**. The HUD pipeline currently surfaces `04.5` but not the expected `04A` stage label. Concurrent session `b98aad6 (chore(lockstep): enforce 04A workflow parity and venv structural-walk usage)` touched `scripts/utilities/structural_walk.py` and multiple workflow docs; the 04A label threading into `run_hud.py` is incomplete or was reverted.

**None of these failures touch 32-2a or 32-4 artifacts.** A triage-first-then-F4 sequence keeps the ratification round clean.

## Recent Closures (prior sessions)

- **32-4-maya-journey-walkthrough** — BMAD-closed 2026-04-19
  - landed `marcus/orchestrator/maya_walkthrough.py` (~360 LOC) + 7-section canned SME fixture + operator markdown
  - 9 collecting functions (14 nodeids; K=6 target 8-9 ceiling)
  - mid-dev scope discovery: `weather_band` is static; "card turns gold" pinned as ratified scope + rationale verbatim at the observable system level
  - layered review CLEAN PASS (0 PATCH / 1 DEFER / ~8 DISMISS)

- **32-2a-inventory-hardening** — BMAD-closed 2026-04-19
  - 6 sample_factory callables wired (steps 05/06/07/11/12/13) + step 12 module_path phantom fix + steps 08/09/10 `deferred=True` + `_resolve_status` relaxed for `{done, review}` statuses
  - regenerated canonical coverage-manifest artifact at `_bmad-output/maps/coverage-manifest/`
  - 6 collecting functions (K=4 target 5-6 ceiling); CLEAN PASS (0 PATCH / 1 DEFER)

- **32-3-trial-run-smoke-harness** — BMAD-closed
  - `marcus/orchestrator/trial_smoke_harness.py` with deterministic 01→13 traversal + Murat §6-E1 5x-consecutive stability check

- **32-1-step-4a-workflow-wiring** — BMAD-closed (but see "At-session-close regressions" above for HUD pipeline gap)

- **30-3b-dials-and-sync-reassessment** — BMAD-closed
- **30-4-plan-lock-fanout** — BMAD-closed
- **28-4-tracy-smoke-fixtures** — BMAD-closed
- **30-5-retrieval-narration-grammar** — BMAD-closed
- **31-5-quinn-r-two-branch** — BMAD-closed
- **28-3-irene-tracy-bridge** — BMAD-closed
- **28-2-tracy-three-modes** — BMAD-closed

## Startup Commands

```bash
git status
cat _bmad-output/implementation-artifacts/sprint-status.yaml
python scripts/utilities/validate_lesson_planner_story_governance.py _bmad-output/implementation-artifacts/32-4-maya-journey-walkthrough.md
python -m pytest -p no:cacheprovider --tb=no -q  # expect 3 failures to triage first
```

## Notes

- **MVP ratification preflight is required before F4 green-light.** The 5 flags in [_bmad-output/maps/lesson-planner-mvp-ratification-preflight-flags.md](_bmad-output/maps/lesson-planner-mvp-ratification-preflight-flags.md) cover: rendered-UX layer absence, §6-C terminal-vs-UI ambiguity, "card turns gold" semantic relocation, stub-dials "next sprint" commitment, retrospective scope.
- The Lesson Planner governance validator is active. Run it on any newly authored Lesson Planner story spec before treating the story as `ready-for-dev`.
- `32-4` and `32-2a` are the final stories authored in this session. All 22 planned Lesson Planner MVP stories are closed + 1 post-audit follow-on (32-2a).
- No deferred "UX rendering" work has been filed as a story — it lives as a cross-epic row in `deferred-work.md §MVP-deferred: rendered UX layer` awaiting a post-MVP epic scoping round.
