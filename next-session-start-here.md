# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> For production operations, pair it with `docs/operations-context.md` and the workflow docs it points to.

## Current State (as of 2026-04-08, post-closeout)

- Active branch after closeout: `master`
- Expected git state after closeout: clean working tree, `master` pushed and aligned with `origin/master`
- Last completed tracked run: `C1-M1-PRES-20260406` — **COMPLETED** (all 15 prompts executed, assembly bundle packaged)
- Canonical bundle: `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260406-motion`
- Run status in APP tracking: `completed`
- Workflow family used: `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- Gate summary (all passed):
  - Gate 2: approved
  - Gate 2M: approved
  - Motion Gate: approved
  - Irene Pass 2 validator: passed
  - Vera G4: passed
  - Storyboard B: HIL approved
  - Quinn-R Pre-Composition: PASS
  - Audio generation: 10/10 segments synthesized
  - Compositor: assembly bundle packaged
  - Operator handoff: complete
- Motion summary:
  - `MOTION_ENABLED: true`
  - Only slide 1 is non-static
  - Approved downstream motion asset is in assembly-bundle/motion/
- Voice: Marc B. Laurent (voice_id=o0t0Wz5oSDuuCV6p7rba)

## Immediate Next Action

1. Checkout the next working branch:
   ```bash
   git checkout master
   git pull --ff-only origin master
   git checkout -b ops/next-session
   ```
2. Decide what to work on next:
   - **Option A:** Begin a new production run (new lesson or re-run with different content).
   - **Option B:** Perform Descript composition using the assembly bundle (human operator task — see assembly guide at `[BUNDLE_PATH]/assembly-bundle/DESCRIPT-ASSEMBLY-GUIDE.md`).
   - **Option C:** Address backlog items from `_bmad-output/implementation-artifacts/sprint-status.yaml` (Epics 15-18 are in backlog).
3. The `C1-M1-PRES-20260406` assembly bundle is ready for human Descript composition at any time.

## Branch Metadata

```bash
git checkout master
git pull --ff-only origin master
git checkout -b ops/next-session
```

## Hot-Start Paths

- `docs/operations-context.md`
- `docs/workflow/production-session-start.md`
- `docs/workflow/production-session-wrapup.md`
- `docs/workflow/human-in-the-loop.md`
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260406-motion/assembly-bundle/DESCRIPT-ASSEMBLY-GUIDE.md`
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260406-motion/assembly-bundle/segment-manifest.yaml`
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (Epics 15-18 backlog)

## Open Items To Carry Forward

- Assembly bundle for C1-M1-PRES-20260406 is ready but has not yet been composed in Descript.
- Epics 15-18 remain in backlog in sprint-status.yaml.
- `run_reporting.py` was repaired for mixed naive/offset-aware timestamps in the prior session; use the updated script.

## Known Gotchas

- For motion segments, `visual_file` remains the approved still slide and `motion_asset_path` carries the approved playback MP4; do not collapse them into one field.
- PowerShell may surface stderr as `NativeCommandError`; check `$LASTEXITCODE` before assuming a command failed.
- The `--voice-selection` flag on `elevenlabs_operations.py` requires a matching `voice-selection.json` in the bundle with hash verification.
