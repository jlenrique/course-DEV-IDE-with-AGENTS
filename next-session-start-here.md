# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> For production operations, pair it with `docs/operations-context.md` and the workflow docs it points to.

## Current State (as of 2026-04-08, post-closeout target)

- Active branch after closeout: `master`
- Expected git state after closeout: clean working tree, `master` pushed and aligned with `origin/master`
- Active tracked run to resume: `C1-M1-PRES-20260406`
- Canonical bundle: `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260406-motion`
- Run status in APP tracking: `blocked`
- Stop point: Storyboard B is complete and published for HIL review; downstream audio, ElevenLabs generation, and assembly have not started
- Workflow family in use: `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- Gate summary:
  - Gate 2: approved
  - Gate 2M: approved
  - Motion Gate: approved
  - Irene Pass 2 validator: passed
  - Vera G4: passed
  - Storyboard B: ready for explicit HIL disposition
- Motion summary:
  - `MOTION_ENABLED: true`
  - only slide 1 is non-static
  - approved downstream motion asset is fixed and should remain the source of truth
- Superseded run note: `C1-M1-PRES-20260404` was cancelled during closeout so the ledger now points to a single canonical tracked run

## Immediate Next Action

1. Checkout the next working branch and resume the blocked tracked run:
   - `git checkout master`
   - `git pull --ff-only origin master`
   - `git checkout ops/c1m1-trial-storyboard-b-hil`
2. Review Storyboard B and record an explicit HIL decision:
   - approve as-is and proceed
   - request storyboard/script remediation before audio
3. If approved, reopen `C1-M1-PRES-20260406` from its blocked state and proceed to the downstream audio stage; do not rerun Irene Pass 2 unless HIL feedback actually requires it.
4. Preserve the approved slide-1 motion asset binding exactly as-is throughout downstream work.

## Branch Metadata

```bash
git checkout master
git pull --ff-only origin master
git checkout ops/c1m1-trial-storyboard-b-hil
```

## Hot-Start Paths

- `docs/operations-context.md`
- `docs/workflow/production-session-start.md`
- `docs/workflow/production-session-wrapup.md`
- `docs/workflow/human-in-the-loop.md`
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260406-motion/run-constants.yaml`
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260406-motion/pass2-envelope.json`
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260406-motion/narration-script.md`
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260406-motion/segment-manifest.yaml`
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260406-motion/motion_plan.yaml`
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260406-motion/storyboard/storyboard.json`
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260406-motion/storyboard/index.html`
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260406-motion/vera-g4-fidelity-trace-report.yaml`
- `exports/storyboard-C1-M1-PRES-20260406-storyboard-b-rerender-20260408-0433-publish-receipt.json`
- Approved slide-1 motion asset:
  - `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260406-motion/motion/apc-c1m1-tejal-20260406-motion-card-01_motion_8s_slowtail.mp4`
- Live Storyboard B review URL:
  - `https://jlenrique.github.io/assets/storyboards/storyboard-b-rerender-20260408-0433/C1-M1-PRES-20260406/index.html`

## Open Items To Carry Forward

- Storyboard B still needs explicit HIL disposition before any audio generation or assembly.
- If HIL requests changes, decide whether the fix is Storyboard-only or requires Irene Pass 2 regeneration.
- Downstream audio stage has not started; no ElevenLabs artifacts should be assumed to exist for this run.
- `run_reporting.py` was repaired for mixed naive/offset-aware timestamps during closeout; if the next session relies on reporting, use the updated script and keep timestamps offset-aware where possible.
- `state/config/runs/C1-M1-PRES-20260406/` now exists as the run-scoped context directory for the canonical tracked run.

## Known Gotchas

- For motion segments, `visual_file` remains the approved still slide and `motion_asset_path` carries the approved playback MP4; do not collapse them into one field.
- For motion-first narration, the script may use the slide once for orientation, but should primarily speak to the visible action in the approved clip.
- Storyboard B now intentionally shows both the approved still and a paused motion preview for slide 1; that is the intended review model, not a temporary workaround.
- The run-scoped perception cache for `C1-M1-PRES-20260406` was cleared during closeout because it held stale low-confidence slide entries from before the repaired Pass 2.
- PowerShell may surface stderr as `NativeCommandError`; check `$LASTEXITCODE` before assuming a command failed.
