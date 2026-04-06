# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> For production operations, pair this with `docs/operations-context.md` and the workflow docs it points to.

## Current State (as of 2026-04-06, post-epic-planning session)

- Active branch: `master`
- Expected git state after closeout: clean working tree, `master` pushed and aligned with `origin/master`
- Implementation status: Epics 1-14 plus SB are complete. Epics 15-18 are scoped with 24 story stubs (86 total stories).
- Active narrated workflow family has two prompt-pack docs:
  - `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md`
  - `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- `DOUBLE_DISPATCH` is an inline branch inside either workflow, not a third workflow.
- Structural walks are canonical and both workflows were validated last session:
  - standard walk: `READY`
  - standard dry-run: `READY`
  - motion walk: `READY`
- Future epic execution order: 17 → 18 → 15 → 16 (all backlog, gated on trial-run evidence for 15-16).

## Immediate Next Action

1. Create the next working branch for the first tracked trial run:
   - `git checkout master`
   - `git checkout -b ops/first-tracked-trial-run`
2. Choose the first concrete lesson or bundle to run.
3. Freeze `run-constants.yaml` for that bundle, run readiness with `--bundle-dir`, then run the appropriate structural walk.
4. Use the prompt harness as a conformance aid if you want a scripted operator transcript or watcher audit before the real trial run.
5. Execute the first tracked trial run through the standard narrated-deck workflow.

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

## New This Session — Future Epic Artifacts

- `_bmad-output/planning-artifacts/epics.md` — Epics 15-18 added at the end
- `_bmad-output/implementation-artifacts/15-*.md` — 7 story stubs (Epic 15: Learning)
- `_bmad-output/implementation-artifacts/16-*.md` — 5 story stubs (Epic 16: Autonomy)
- `_bmad-output/implementation-artifacts/17-*.md` — 5 story stubs (Epic 17: Research & Reference)
- `_bmad-output/implementation-artifacts/18-*.md` — 7 story stubs (Epic 18: Additional Assets)
- Story 15.7 is autoresearch-inspired agent judgment calibration harness

## Open Items To Carry Forward

- The first tracked trial run has not happened yet.
- A concrete lesson or bundle still needs to be selected and frozen for that run.
- `state/config/course_context.yaml` still contains placeholder module entries, so trial-run prep should rely on a specific chosen bundle rather than the unfinished global course map.
- The prompt harness is useful for conformance but is not a runtime executor.
- Epics 15-16 are gated on tracked trial run evidence — do not start them until at least one run generates real gate decisions and learning data.
- Epic 17 requires Consensus and Scite.ai API credentials to be provisioned in `.env`.
- Epic 18 is discovery-first — implementation stories are added only after discovery documents are approved.
- Story 15.7 (autoresearch-inspired calibration harness) needs labeled data from tracked runs before it can be implemented.

## Future Epic Seeds (carried forward)

- `learning` epic (15): seed doc at `_bmad-output/implementation-artifacts/app-three-layer-optimization-plans-2026-04-06.md` Plan 3
- `autonomy` epic (16): same plan doc Plans 1+2, plus `_bmad-output/implementation-artifacts/app-optimization-map-and-baseline-audit-2026-04-05.md`
- Sequencing: run tracked trials first, then shape epics from observed behavior
- Design guardrail: preserve specialist intelligence, harden deterministic boundaries, avoid replacing judgment with cheap automation

## Known Gotchas

- Use `docs/operations-context.md` for low-cognitive-load startup instead of re-reading the full implementation history.
- For tracked bundle shifts, readiness with `--bundle-dir` is required, not optional.
- If `DOUBLE_DISPATCH` is enabled, the run must collapse to a winner deck before Irene Pass 2 or motion planning.
- If `MOTION_ENABLED` is enabled, Gate 2M and Motion Gate must both close before Irene Pass 2.
- PowerShell may surface stderr as `NativeCommandError`; check `$LASTEXITCODE` before assuming the command failed.
