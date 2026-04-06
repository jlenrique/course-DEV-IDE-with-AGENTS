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

## Immediate Next Action

1. Create the next working branch for operations and trial-run prep:
   - `git checkout master`
   - `git checkout -b ops/first-tracked-trial-run`
2. Choose the first concrete lesson or bundle to run.
3. Freeze `run-constants.yaml` for that bundle, run readiness with `--bundle-dir`, then run the appropriate structural walk.
4. Use the new prompt harness as a conformance aid if you want a scripted operator transcript or watcher audit before the real trial run.

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
- A concrete lesson or bundle still needs to be selected and frozen for that run.
- `state/config/course_context.yaml` still contains placeholder module entries, so trial-run prep should rely on a specific chosen bundle rather than the unfinished global course map.
- The new prompt harness is useful for prompt-pack conformance and artifact auditing, but it is not yet a runtime executor of Marcus code paths. If you want runtime proof later, build an execution harness rather than an evidence harness.
- If the next session changes workflow gates, required artifacts, or canonical control docs, update the structural-walk manifests and `docs/structural-walk.md` before closeout.

## Known Gotchas

- Use `docs/operations-context.md` for low-cognitive-load startup instead of re-reading the full implementation history.
- For tracked bundle shifts, readiness with `--bundle-dir` is required, not optional.
- If `DOUBLE_DISPATCH` is enabled, the run must collapse to a winner deck before Irene Pass 2 or motion planning.
- If `MOTION_ENABLED` is enabled, Gate 2M and Motion Gate must both close before Irene Pass 2.
- PowerShell may surface stderr as `NativeCommandError`; check `$LASTEXITCODE` before assuming the command failed.
