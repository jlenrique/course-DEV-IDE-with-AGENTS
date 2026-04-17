# Archived: Prompt-pack pre-prompt operator sections (v4.2, pre-Story-26-6)

**Source commit:** `bd5de8c` (last commit before the strip)
**Strip date:** 2026-04-17
**Story ref:** [26-6 Marcus Production-Readiness Capabilities](../../../_bmad-output/implementation-artifacts/26-6-marcus-production-readiness-capabilities.md)
**Superseded by:** [`docs/dev-guide/marcus-capabilities.md`](../../dev-guide/marcus-capabilities.md)

## Why this content was stripped

Before Story 26-6, the prompt-pack v4.2 document at
[`docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`](../production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md)
carried a **Run Constants** and **Initialization Instructions** section the
operator was expected to hand-transcribe into `run-constants.yaml`. The pack
displayed UPPERCASE flat keys (`RUN_ID`, `MOTION_BUDGET_MAX_CREDITS`); the
validator at `scripts/utilities/run_constants.py` enforces lowercase snake_case
with nested `motion_budget:` and `slide_mode_proportions:` blocks.

This doc-vs-code schema drift halted the **2026-04-17 APC C1-M1 Tejal trial at
Prompt 1** when `emit-preflight-receipt.py` rejected the operator-authored
`run-constants.yaml`.

Story 26-6 moved this authoring concern into Marcus as capabilities **PR-PF**
(Preflight) and **PR-RC** (Run-Constants author + validate). The pack doc no
longer asks the operator to transcribe schemas by hand; Marcus authors the
canonical lowercase-nested YAML directly.

This archive preserves the stripped content verbatim so the 2026-04-17 halt
context is not lost.

---

## Preserved content

```markdown
## Pre-Run Checklist (Visual-Led Profile)

> **Audience: OPERATOR.** Complete this checklist before issuing Prompt 1 to Marcus.

Before starting a visual-led production run:
- [ ] Set `EXPERIENCE_PROFILE: visual-led` in run-constants.yaml
- [ ] Confirm `MOTION_ENABLED: true` and budget set
- [ ] Verify run-constants.yaml `slide_mode_proportions` match the canonical visual-led profile: `creative: 0.60`, `literal-visual: 0.25`, `literal-text: 0.15`
- [ ] Verify `CLUSTER_DENSITY` matches the canonical experience profile (`default` for visual-led, `rich` for text-led)
- [ ] Verify Irene packet carries the same proportions forward
- [ ] HIL: Favor creative slides for visual impact, literal-visual for direct anchoring
- [ ] Post-run: Document profile impact on quality gates

## Run Constants (set once)

> **Audience: OPERATOR.** Persist these values as `run-constants.yaml` in the bundle root before the first prompt.

- RUN_ID: C1-M1-PRES-20260415
- LESSON_SLUG: apc-c1m1-tejal
- BUNDLE_PATH: course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260415
- PRIMARY_SOURCE_FILE: course-content/courses/APC C1-M1 Tejal 2026-03-29.pdf
- OPTIONAL_CONTEXT_ASSETS: course-content/courses/APC Content Roadmap.jpg
- THEME_SELECTION: hil-2026-apc-nejal-A
- THEME_PARAMSET_KEY: hil-2026-apc-nejal-A
- EXECUTION_MODE: tracked/default
- QUALITY_PRESET: production
- REQUESTED_CONTENT_TYPE: narrated-lesson-with-video-or-animation
- MOTION_ENABLED: true
- MOTION_BUDGET_MAX_CREDITS: 125
- MOTION_BUDGET_MODEL_PREFERENCE: pro
- DOUBLE_DISPATCH: true
- EXPERIENCE_PROFILE: visual-led
- CLUSTER_DENSITY: default

Operator rule:
- Do not change run constants mid-run.
- `MOTION_ENABLED: true` requires an explicit positive budget.
- `DOUBLE_DISPATCH` changes only the Gary selection branch, not the rest of the workflow.
- Marcus must ask the operator in plain language: "Should the visuals lead, or should the text lead for this lesson?"
- Do not ask the operator to choose an `experience_profile` by name.
- Mapping rule for persisted run constants:
  - visuals lead → `experience_profile: visual-led`
  - text lead → `experience_profile: text-led`
  - no preference stated → omit `experience_profile` and preserve legacy behavior

## Initialization Instructions

> **Audience: OPERATOR.** Create the bundle and verify paths before issuing Prompt 1.

Before starting the production run:
1. Create bundle directory:
   ```powershell
   mkdir course-content\staging\tracked\source-bundles\apc-c1m1-tejal-20260415
   ```
2. Create `run-constants.yaml` in the bundle root with the Run Constants values above. Use a prior run's file as a template if helpful (e.g. `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260409/run-constants.yaml`).
3. Set `experience_profile: visual-led` and populate `slide_mode_proportions` from the canonical visual-led profile in `state/config/experience-profiles.yaml`:
   ```yaml
   experience_profile: visual-led
   slide_mode_proportions:
     creative: 0.60
     literal-visual: 0.25
     literal-text: 0.15
   ```
4. Verify all paths resolve — primary source PDF and context assets exist at the declared locations.
5. Confirm `CLUSTER_DENSITY: default` matches the canonical visual-led profile in `state/config/experience-profiles.yaml`. This activates G1.5 cluster planning (Prompt 5B) and G4-16..19 cluster narration governance.
```
