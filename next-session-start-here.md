# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> For production operations, pair this with `docs/operations-context.md` and the workflow docs it points to.

## Current State (as of 2026-04-06, post-closeout target)

- Active branch: `master`
- Expected git state after closeout: clean working tree, `master` pushed and aligned with `origin/master`
- Implementation status: Epics 1-14 plus SB are complete.
- Active narrated workflow family has two prompt-pack docs:
  - `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md`
  - `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- `DOUBLE_DISPATCH` is an inline branch inside either workflow, not a third workflow.
- Structural walks are canonical and both workflows were re-run in this session:
  - standard walk: `READY`
  - standard dry-run: `READY`
  - motion walk: `READY`
- A new standard-v4.1 Marcus prompt harness now exists for transcript generation plus Quinn watcher auditing.
- Repo-declared next phase remains: begin tracked trial runs from the clean Epic 14 baseline.
- The first official tracked trial run should be a **fresh-start run**, not a resume of any previously staged bundle.
- Workflow selection for that first official trial is the **standard narrated slides + video workflow**:
  - `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md`

## Immediate Next Action

1. Create the next working branch for operations and trial-run prep:
   - `git checkout master`
   - `git checkout -b ops/first-tracked-trial-run`
2. Choose the first concrete lesson/source-doc set for the first official trial run.
3. Create a **new tracked bundle** and begin from source extraction / ingestion, not from an already-partially-prepared bundle.
4. Use the standard narrated slides + video workflow (`production-prompt-pack-v4.1-narrated-deck-video-export.md`).
5. Freeze `run-constants.yaml` for the new bundle, run readiness with `--bundle-dir`, then run the standard structural walk.
6. Use the new prompt harness only as a conformance aid if desired; do not treat an older staged bundle as the official first trial.

## Branch Metadata

```bash
git checkout master
git checkout -b ops/first-tracked-trial-run
```

## Hot-Start Paths

- `docs/operations-context.md`
- `docs/workflow/first-tracked-run-quickstart.md`
- `docs/workflow/first-tracked-run-checklist.md`
- `docs/workflow/production-session-start.md`
- `docs/workflow/production-session-wrapup.md`
- `docs/workflow/production-operator-card-v4.md`
- `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md`
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- `docs/structural-walk.md`
- `state/config/structural-walk/standard.yaml`
- `state/config/structural-walk/motion.yaml`
- `scripts/utilities/marcus_prompt_harness.py`
- `reports/prompt-harness/standard-v4.1/`

## Open Items To Carry Forward

- The first tracked trial run has not happened yet.
- A concrete lesson/source-doc set still needs to be selected for that run.
- The first official trial must start from fresh extraction and ingestion in a new tracked bundle.
- Existing staged tracked bundles may be consulted as reference material only; they are not the official first trial unless explicitly re-designated.
- `state/config/course_context.yaml` still contains placeholder module entries, so trial-run prep should rely on a specific chosen bundle rather than the unfinished global course map.
- The new prompt harness is useful for prompt-pack conformance and artifact auditing, but it is not yet a runtime executor of Marcus code paths. If you want runtime proof later, build an execution harness rather than an evidence harness.
- Strategic follow-up after trial runs: create a new BMAD epic on platform autonomy and a related BMAD epic on platform learning. Both are viewed as potentially transformational, but only if specialist-agent intelligence is deliberately cultivated rather than papered over with brittle automation.
- If the next session changes workflow gates, required artifacts, or canonical control docs, update the structural-walk manifests and `docs/structural-walk.md` before closeout.

## Future Epic Seeds

- `learning` epic seed:
  - primary source: `_bmad-output/implementation-artifacts/app-three-layer-optimization-plans-2026-04-06.md`
  - focus first on Plan 3: learning-event schema, tracked-run retrospectives, upstream-from-downstream feedback routing, synergy scorecards, and workflow-family learning
- `autonomy` epic seed:
  - use the same plan doc together with `_bmad-output/implementation-artifacts/app-optimization-map-and-baseline-audit-2026-04-05.md`
  - focus on bounded autonomy: where Marcus and specialists can act more independently without weakening governance, gates, handoff contracts, or human checkpoint authority
- Sequencing note:
  - do not open either epic in a vacuum
  - first use one or more tracked trial runs to generate real correction, waiver, approval, and failure data
  - then define the epics from observed workflow behavior, not only design theory
- Design guardrail for both epics:
  - preserve specialist intelligence
  - harden deterministic boundaries
  - avoid replacing pedagogy, visual reasoning, or evaluator judgment with cheap automation

## Known Gotchas

- Use `docs/operations-context.md` for low-cognitive-load startup instead of re-reading the full implementation history.
- For tracked bundle shifts, readiness with `--bundle-dir` is required, not optional.
- For the first official trial run, do not resume an already-partially-prepared tracked bundle; start from extraction of the chosen source docs.
- If `DOUBLE_DISPATCH` is enabled, the run must collapse to a winner deck before Irene Pass 2 or motion planning.
- If `MOTION_ENABLED` is enabled, Gate 2M and Motion Gate must both close before Irene Pass 2.
- PowerShell may surface stderr as `NativeCommandError`; check `$LASTEXITCODE` before assuming the command failed.
