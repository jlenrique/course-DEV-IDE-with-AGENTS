# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> **Current objective:** start Marcus trial production run from a clean post-harmonization baseline.
>
> **Deferred inventory status (2026-04-19):** 4 backlog epics (15, 16, 17, 18) / 4 deferred stories in active epics (20c-4, 20c-5, 20c-6, 20a-5) / 6 named-but-not-filed follow-ons. See [`_bmad-output/planning-artifacts/deferred-inventory.md`](_bmad-output/planning-artifacts/deferred-inventory.md) for reactivation triggers per entry. Binding consultation per [CLAUDE.md §Deferred inventory governance](CLAUDE.md).

## Session-Adjacent Update (2026-04-19)

- Epic 33 substrate story `33-2-pipeline-manifest-ssot` is now BMAD-closed (`done`).
- AC-B.15 was formally DEFERRED to `33-1a-build-v42-generator` per 33-1 Case C (no in-repo generator of record).
- Sprint reshape is recorded: `33-1a` now blocks `33-3` (replacing the prior direct 33-2 -> 33-3 handoff).
- **Deferred inventory governance landed 2026-04-19**: single index at [`deferred-inventory.md`](_bmad-output/planning-artifacts/deferred-inventory.md); retrospective hook + session-start-here line + CLAUDE.md governance section all in place.

## Immediate Next Action

1. Run the BMAD Session Protocol Session START.
2. Confirm branch. Session closed on `master` (concurrent sessions merged `dev/lesson-planner` back to master).
3. Use `_bmad-output/implementation-artifacts/sprint-status.yaml` as the canonical status source.
4. Confirm Step 0a harmonization report exists and review it: [reports/dev-coherence/2026-04-19-1546/harmonization-summary.md](reports/dev-coherence/2026-04-19-1546/harmonization-summary.md).
5. Review F4 party-mode verdict record: [_bmad-output/maps/lesson-planner-mvp-ratification-f4-verdict-2026-04-19.md](_bmad-output/maps/lesson-planner-mvp-ratification-f4-verdict-2026-04-19.md).
6. Re-run command set in `reports/dev-coherence/2026-04-19-1546/evidence/reverify-commands.md`, then begin trial run if all checks stay green.

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

## At-session-close regressions (3) — RESOLVED 2026-04-19

At 2026-04-19 session close the suite was **1899 passed / 2 failed / 1 collection error / 4 skipped / 27 deselected / 2 xfailed**. A-first remediation + B-step full harmonization were completed in-session and recorded under `reports/dev-coherence/2026-04-19-1546/`. Current re-verify status: **1910 passed / 4 skipped / 27 deselected / 2 xfailed**.

- **`tests/contracts/test_tracy_postures.py` — ImportError at collection**. **Resolved** by tightening package registration in `tests/conftest.py` so synthetic namespace modules do not shadow the real `skills` package.
- **`tests/contracts/test_30_1_zero_test_edits.py::test_no_preexisting_test_files_modified_in_30_1` — stale baseline pin**. **Resolved** by rolling `_PRE_30_1_BASELINE_COMMIT` forward to `4911fc4`.
- **`tests/test_marcus_workflow_runner_32_1.py::test_hud_pipeline_contains_4a_between_04x_and_05` — missing `04A` in HUD pipeline**. **Resolved** by restoring `04A` stage in `scripts/utilities/run_hud.py` between `04.5` and `05`.

All three failures were concurrent-session drift, not 32-2a/32-4 logic defects; they are now closed with traceable evidence.

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
python -m pytest tests/contracts/test_tracy_postures.py tests/contracts/test_30_1_zero_test_edits.py::test_no_preexisting_test_files_modified_in_30_1 tests/test_marcus_workflow_runner_32_1.py::test_hud_pipeline_contains_4a_between_04x_and_05 -q
python -m pytest -q
```

## Notes

- **MVP ratification preflight is required before F4 green-light.** The 5 flags in [_bmad-output/maps/lesson-planner-mvp-ratification-preflight-flags.md](_bmad-output/maps/lesson-planner-mvp-ratification-preflight-flags.md) cover: rendered-UX layer absence, §6-C terminal-vs-UI ambiguity, "card turns gold" semantic relocation, stub-dials "next sprint" commitment, retrospective scope.
- The Lesson Planner governance validator is active. Run it on any newly authored Lesson Planner story spec before treating the story as `ready-for-dev`.
- `32-4` and `32-2a` are the final stories authored in this session. All 22 planned Lesson Planner MVP stories are closed + 1 post-audit follow-on (32-2a).
- No deferred "UX rendering" work has been filed as a story — it lives as a cross-epic row in `deferred-work.md §MVP-deferred: rendered UX layer` awaiting a post-MVP epic scoping round.
