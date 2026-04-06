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

## C2) Gate 6B Operator Packet (Mandatory)

- [ ] Produce literal-visual operator packet at <bundle-dir>/literal-visual-operator-packet.md.
- [ ] Confirm packet includes, per literal-visual slide: source context, Irene constraints, acceptance checks, and the expected dispatch-ready source (`image_url` or `preintegration_png_path`).
- [ ] If a slide uses `preintegration_png_path`, confirm operator completed the required Gamma/manual build and downloaded the local PNG.
- [ ] If a slide uses hosted `image_url`, confirm the URL is the approved dispatch source and no local PNG build is required for that card.
- [ ] Block Prompt 7 until all required literal-visual cards are operator-ready.

## D) Gary Dispatch and Validation

- [ ] Before publish/dispatch side effects, present pre-dispatch report of literal-visual cards + local PNG paths + site_repo_url and obtain explicit operator confirmation.
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

## E2) Double-Dispatch Winner Selection (Conditional)

- [ ] If `DOUBLE_DISPATCH` is enabled, confirm selection inputs match the documented dispatch outcome:
  - [ ] both variant sets passed validation, or
  - [ ] one side failed and the surviving side is explicitly auto-selected per slide with fallback recorded in `variant-selection.json`.
- [ ] Present paired A/B review and record per-slide picks in <bundle-dir>/variant-selection.json.
- [ ] Confirm the authorized storyboard collapses to the winner-only deck before any downstream motion or narration work.

## E3) Motion Workflow (Conditional)

- [ ] If `MOTION_ENABLED` is enabled, run Gate 2M on the authorized winner deck only.
- [ ] Write <bundle-dir>/motion-designations.json and <bundle-dir>/motion_plan.yaml.
- [ ] Confirm every authorized slide has Gate 2M coverage.
- [ ] Complete motion generation/import and close Motion Gate before Irene Pass 2.

## F) Irene Pass 2 and Grounding

- [ ] Delegate Irene Pass 2 using approved gary_slide_output.
- [ ] Confirm narration grounding is based on approved local slide PNGs in gary_slide_output.
- [ ] Treat literal_visual_publish as provenance/audit context only.
- [ ] Ensure perception_artifacts are present (provided or regenerated inline) and aligned to slide IDs.
- [ ] If `MOTION_ENABLED` is enabled, confirm `motion_plan.yaml` fully covers the authorized deck and approved non-static assets are perception-confirmed before final handoff.

## F2) Storyboard Review B (Post-Irene, Pre-Audio)

- [ ] Regenerate storyboard using gary dispatch payload + segment-manifest.yaml so each row can show slide + narration context.
- [ ] Read manifest-derived summary and obtain explicit operator approval for slide+script alignment.
- [ ] Do not start downstream audio/script finalization (for example ElevenLabs generation) until this approval is captured.

## G) Handoff Integrity

- [ ] Segment IDs match between narration script and segment manifest.
- [ ] visual_file fields for static-hold segments point to Gary local PNG paths.
- [ ] source_ref values are populated and traceable.
- [ ] Save compact run receipt with validator outcomes and next action.

## Notes (Out of Scope for This Tracked Checklist)

- In ad-hoc mode, preintegration_png_path is not allowed.
