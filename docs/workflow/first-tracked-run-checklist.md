# First Tracked Run Checklist (Storyboard + Git Hosting)

Purpose: quick operator checklist for the first tracked/default production run that includes storyboard review and literal-visual Git-host staging.

## A) Session and Mode

- [ ] Confirm execution mode is tracked/default (not ad-hoc).
- [ ] Confirm quality preset for the run (draft, production, or regulated).
- [ ] Run session readiness + preflight and record clean pass receipt.

## B) Pass 1 and Pre-Dispatch Contract

- [ ] Approve Irene Pass 1 artifacts at Gate 1.
- [ ] Build pre-dispatch artifacts under the active bundle:
  - [ ] g2-slide-brief.md
  - [ ] gary-slide-content.json
  - [ ] gary-fidelity-slides.json
  - [ ] gary-diagram-cards.json
  - [ ] gary-theme-resolution.json
  - [ ] gary-outbound-envelope.yaml
- [ ] Ensure every slide has exactly one fidelity mode.

## C) Literal-Visual Input Readiness

For each literal-visual card in gary-diagram-cards.json:

- [ ] Provide one dispatch-ready source:
  - [ ] HTTPS image_url, or
  - [ ] local preintegration_png_path (tracked/default only).
- [ ] If any preintegration_png_path is used, provide site_repo_url.
- [ ] If run mode is ad-hoc, do not use preintegration_png_path.

## D) Gary Dispatch and Validation

- [ ] Execute Gary mixed-fidelity dispatch.
- [ ] If local preintegration assets were used, confirm literal_visual_publish exists and shows preintegration_ready=true.
- [ ] Run validate-gary-dispatch-ready.py against <bundle-dir>/gary-dispatch-result.json.
- [ ] Stop and remediate on any fail status before user-facing Gate 2.

## E) Storyboard and Gate 2

- [ ] Generate storyboard from Gary dispatch payload.
- [ ] Confirm storyboard shows all slides in order.
- [ ] Confirm remote assets remain remote links (not false missing flags).
- [ ] Read summary and get explicit Gate 2 approval in chat.
- [ ] Write <bundle-dir>/authorized-storyboard.json (fail closed on overwrite).

## F) Irene Pass 2 and Grounding

- [ ] Delegate Irene Pass 2 using approved gary_slide_output.
- [ ] Confirm narration grounding is based on approved local slide PNGs in gary_slide_output.
- [ ] Treat literal_visual_publish as provenance/audit context only.
- [ ] Ensure perception_artifacts are present (provided or regenerated inline) and aligned to slide IDs.

## G) Handoff Integrity

- [ ] Segment IDs match between narration script and segment manifest.
- [ ] visual_file fields for static-hold segments point to Gary local PNG paths.
- [ ] source_ref values are populated and traceable.
- [ ] Save compact run receipt with validator outcomes and next action.

## Notes (Out of Scope for This Tracked Checklist)

- In ad-hoc mode, preintegration_png_path is not allowed.
