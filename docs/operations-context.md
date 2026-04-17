# Operations Context

Purpose: compact high-signal context for production operations sessions. Use this instead of the full implementation-history narrative in `docs/project-context.md` when the goal is to open, run, or close a production shift safely.

## Current State

- Project implementation is complete through Epics 1-14 plus SB.
- Epics 19-24 (interstitial clustering) are in active development — Wave 1 complete (20b-3, 22-1, 21-5), Wave 2 (Epic 20c) in progress.
- Active narrated workflow family has two templates:
  - `narrated-deck-video-export` for standard narrated runs
  - `narrated-lesson-with-video-or-animation` for motion-enabled narrated runs
- `DOUBLE_DISPATCH` is an optional Gary-stage branch inside either workflow, not a third workflow family.
- `CLUSTER_DENSITY` is an optional run constant; when non-`none`, enables G1.5 Cluster Plan gate and cluster dispatch sequencing.
- `EXPERIENCE_PROFILE` is an optional run constant; when set, Marcus must resolve it through the Creative Director contract path before specialist delegation.
- `structural_walk` is the canonical structural readiness check.

## Canonical Control Docs

- Startup: `docs/workflow/production-session-start.md`
- Operator flow: `docs/workflow/production-operator-card-v4.md`
- First tracked run quick path: `docs/workflow/first-tracked-run-quickstart.md`
- Full tracked checklist: `docs/workflow/first-tracked-run-checklist.md`
- Standard prompt pack: `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md`
- Motion prompt pack: `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- Descript handoff specialist (post-compositor, pre–operator handoff): `skills/bmad-agent-desmond/SKILL.md` — emits `assembly-bundle/DESMOND-OPERATOR-BRIEF.md` with **`## Automation Advisory`** (prompt **14.5** in both v4.1 and v4.2 packs)
- Cluster workflow: `docs/workflow/cluster-workflow.md`
- A/B tuning loop: `docs/workflow/operator-script-v4.2-irene-ab-loop.md`
- Artifact contract: `docs/workflow/trial-run-pass2-artifacts-contract.md`
- Gate ownership: `docs/fidelity-gate-map.md`
- Judgment boundaries: `docs/lane-matrix.md`

## Run Invariants

- Marcus is the user-facing orchestrator for production runs.
- After compositor (**prompt 14**), **prompt 14.5** requires a **Desmond** operator brief (`DESMOND-OPERATOR-BRIEF.md`) before final Descript handoff (**prompt 15**); compositor output alone is not sufficient for pack completion.
- Production runs use `tracked/default`, not `ad-hoc`.
- Prompt 2A operator directives are mandatory before ingestion.
- Prompt 6B blocks Prompt 7 until literal-visual operator readiness is explicit.
- Storyboard A is required after Gary dispatch and before Gate 2 approval.
- If `DOUBLE_DISPATCH` is enabled, the workflow must collapse to a winner deck before Irene Pass 2 or motion planning.
- If `MOTION_ENABLED` is enabled, Gate 2M and Motion Gate must both close before Irene Pass 2.
- If `CLUSTER_DENSITY` is non-`none`, G1.5 (Cluster Plan Validation) must pass before cluster dispatch, and G2.5 (Cluster Coherence Validation) must pass after Gary cluster dispatch (G3) and before Storyboard A / HIL Gate 2.
- If `EXPERIENCE_PROFILE` is set, Marcus must freeze the resolved `experience_profile` in `run-constants.yaml` and carry the resolved `narration_profile_controls` forward in the Pass 2 envelope before downstream narration work.
- Storyboard B is required after Irene Pass 2 and before downstream audio/script finalization.

## Canonical Commands

- Structural walk, standard:
  - `python -m scripts.utilities.structural_walk --workflow standard`
- Structural walk, motion:
  - `python -m scripts.utilities.structural_walk --workflow motion`
- Structural walk, cluster:
  - `python -m scripts.utilities.structural_walk --workflow cluster`
- Session readiness + preflight:
  - `.venv/Scripts/python.exe -m scripts.utilities.app_session_readiness --with-preflight`
- Tracked bundle readiness:
  - `.venv/Scripts/python.exe -m scripts.utilities.app_session_readiness --with-preflight --bundle-dir <path-to-bundle>`

## What To Confirm At Shift Open

- correct workspace and branch
- correct execution mode and quality preset
- readiness/preflight pass
- correct prompt pack for the selected workflow
- `run-constants.yaml` frozen in the active tracked bundle
- clear owner and next action for any active or blocked runs

## Stop Conditions

- any critical readiness/preflight failure
- missing or mismatched tracked bundle constants
- unclear workflow selection
- unresolved literal-visual readiness
- unresolved winner selection
- incomplete Gate 2M or Motion Gate on motion runs
- missing Storyboard B approval before audio/script finalization

## Notes

- `docs/project-context.md` remains the full project-history/context document.
- This file is for operations-only sessions where startup speed and low cognitive load matter more than implementation history.
- For the first official tracked trial run, start from a fresh tracked bundle at source extraction / ingestion rather than resuming a previously prepared staging bundle unless you explicitly re-designate that older bundle as the canonical run.
