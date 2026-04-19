# First Tracked Trial Run Quickstart

Purpose: fatigue-friendly operator path for the first real tracked/default run. Use this when you want the shortest safe route through the control flow without re-reading the full prompt packs.

Primary references:
- `docs/workflow/production-session-start.md`
- `docs/workflow/production-operator-card-v4.md`
- `docs/workflow/first-tracked-run-checklist.md`

## Before You Start

- Confirm execution mode is `tracked/default`, not `ad-hoc`.
- Confirm the quality preset: `draft`, `production`, or `regulated`.
- If operating a specific tracked bundle, run readiness/preflight with `--bundle-dir <path-to-bundle>`.
- Keep the readiness/preflight receipt.
- Confirm which workflow applies:
  - standard narrated run -> `production-prompt-pack-v4.1-narrated-deck-video-export.md`
  - motion-enabled narrated run -> `production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`

## Run Sequence

1. Open the shift and confirm workspace, branch, and active run context.
2. Complete Prompt 04A (Lesson Plan coauthoring + scope lock) after ingestion quality and before Prompt 4.75.
3. If `EXPERIENCE_PROFILE` is set, run Prompt 4.75 Creative Directive before Irene Pass 1.
4. Complete Gate 1 and approve Irene Pass 1 artifacts.
5. Build the pre-dispatch bundle:
   - `g2-slide-brief.md`
   - `gary-slide-content.json`
   - `gary-fidelity-slides.json`
   - `gary-diagram-cards.json`
   - `gary-theme-resolution.json`
   - `gary-outbound-envelope.yaml`
6. Verify every slide has exactly one fidelity mode.
7. For each literal-visual card, provide exactly one dispatch-ready source:
   - `image_url`, or
   - `preintegration_png_path` in tracked/default mode only
8. If `CLUSTER_DENSITY` is not `none`, run Prompt 6.2 (cluster prompts) and 6.3 (dispatch sequencing).
9. If any `preintegration_png_path` is used, include `site_repo_url`.
10. Produce the Gate 6B packet at `<bundle-dir>/literal-visual-operator-packet.md`.
11. Do not dispatch Prompt 7 until all required literal-visual cards are operator-ready.
12. Present the pre-dispatch summary, get explicit approval, and run Gary mixed-fidelity dispatch.
13. Validate the dispatch result with `validate-gary-dispatch-ready.py`.
14. If `CLUSTER_DENSITY` is not `none`, run G2.5 coherence before Storyboard A.
15. Generate Storyboard A from the dispatch payload and get explicit Gate 2 approval.
16. Write `authorized-storyboard.json`.
17. If `DOUBLE_DISPATCH` is enabled:
    - record `variant-selection.json`
    - allow documented surviving-side fallback if one branch failed
    - collapse to the winner deck before narration or motion continues
18. If `MOTION_ENABLED` is enabled:
    - run Gate 2M on the authorized winner deck only
    - write `motion-designations.json` and `motion_plan.yaml`
    - complete motion generation/import
    - close Motion Gate before Irene Pass 2
19. Run Irene Pass 2 using approved `gary_slide_output`.
20. Regenerate Storyboard B and get approval before downstream audio/script finalization.
21. Save a compact run receipt with outcomes, blockers, and next action.

## Stop Conditions

- Stop on any failed readiness or preflight check.
- Stop on any dispatch validation failure.
- Stop if storyboard approval is not explicit.
- Stop if `DOUBLE_DISPATCH` winner collapse is unresolved.
- Stop if motion is enabled but Gate 2M or Motion Gate is incomplete.
- Stop if Storyboard B approval is missing before audio/script work.

## Output To Keep

- readiness/preflight receipt
- `gary-dispatch-result.json`
- `authorized-storyboard.json`
- `variant-selection.json` if used
- `motion_plan.yaml` if used
- final run receipt with next action
