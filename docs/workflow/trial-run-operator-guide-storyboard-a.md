---
title: Trial Run Operator Guide — Storyboard A (C1M1)
status: ready
updated: 2026-04-11
---

## Purpose
Concise, operator-facing steps to run a Storyboard A trial production using the v4.3 pipeline (prompting, dispatch, coherence validation) and C1M1 source materials. Prompt numbering aligns with the v4.2 prompt pack where possible to preserve operator context.

**SPOC rule:** Marcus remains the single point of contact for the operator; specialist execution details route through Marcus.

## Inputs
- Primary: `course-content/courses/APC C1-M1 Tejal 2026-03-29.pdf`
- Secondary: `course-content/courses/APC Content Roadmap.jpg`
- Optional: `course-content/courses/APC C1-M1 Tejal 2026-03-29.docx`
- Bundle directory: `course-content/staging/storyboard-a-trial/` (already initialized)
- Canonical prior bundle for reuse (tracked/default): `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260409-motion/`
- Run constants (save as `run-constants.yaml` in the bundle):
```yaml
run_id: "SB-A-TRIAL-001"
lesson_slug: "c1m1-tejal"
bundle_path: "course-content/staging/storyboard-a-trial"
primary_source_file: "course-content/courses/APC C1-M1 Tejal 2026-03-29.pdf"
optional_context_assets:
  - "course-content/courses/APC Content Roadmap.jpg"
theme_selection: "theme-a"
theme_paramset_key: "preset-a"
execution_mode: "tracked/default"
quality_preset: "production"
cluster_density: "sparse"
double_dispatch: false
motion_enabled: false
requested_content_type: "narrated-lesson-with-video-or-animation"
```

## Commands (operator executes)
> Use the repo-local interpreter for production runs: `.\.venv\Scripts\python.exe` (mirrors prompt pack v4.2).

1) Prompt 1 — Preflight & readiness  
   `.\.venv\Scripts\python.exe scripts/utilities/app_session_readiness.py --with-preflight`
2) Prompt 5B — Cluster gate (G1.5)  
   `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/run-g1.5-cluster-gate.py --bundle-dir course-content/staging/storyboard-a-trial`
3) Prompt 6.2 — Prompt rendering (cluster-aware prompt pack)
   `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/cluster_prompt_engineering.py --cluster course-content/staging/storyboard-a-trial/clusters.json`
4) Prompt 6.3 — Dispatch plan (cluster sequencing)
   `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/cluster_dispatch_sequencing.py --clusters course-content/staging/storyboard-a-trial/clusters-list.json`
5) Prompt 7.5 — Coherence validation (cluster-aware, G2.5)  
   `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/cluster_coherence_validation.py --manifest course-content/staging/storyboard-a-trial/segment-manifest.yaml --outputs course-content/staging/storyboard-a-trial/outputs.yaml`

## Operator Prompts to Marcus (copy/paste; real bundle)
Use the canonical bundle from the last full run:
`course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260409-motion`

1) Prompt 1 — Init + Preflight:  
   “Marcus, load run `C1-M1-PRES-20260409` using the bundle at `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260409-motion` and its `run-constants.yaml`. Confirm preflight status.”
2) Prompt 5B — G1.5 Cluster Plan Gate:  
   “Marcus, run the G1.5 cluster gate on that bundle and report PASS/FAIL with errors.”
3) Prompt 6.2 — Cluster Prompting:  
   “Marcus, render cluster-aware prompts for all clusters in this bundle using `state/config/prompting.yaml`; return prompt_ids, hashes, and token budgets.”
4) Prompt 6.3 — Cluster Dispatch Plan:  
   “Marcus, build the dispatch plan with `state/config/dispatch.yaml` (priority_size_id, batch_size=2, max_concurrency=4); return plan_hash and batch schedule.”
5) Prompt 7 — Generation (reuse existing assets if present):  
   “Marcus, if assets already exist in the bundle, reference them; otherwise execute Gamma generation per dispatch plan, applying interstitial visual constraints and cluster metadata.”
6) Prompt 7.5 — Cluster Coherence Validation (G2.5):  
   “Marcus, run cluster coherence validation with `state/config/validation.yaml`; report decision, report_hash, and any violations.”
7) Prompt 7.6 — HIL Packet:  
   “Marcus, assemble the HIL packet for Storyboard A with outputs, validations, and operator checklist; await my approval.”

## HIL Checklist
- G1.5 PASS recorded
- Prompt hashes recorded
- Dispatch plan hash recorded
- Coherence report hash recorded
- Violations resolved/accepted
- Final operator approval logged

## Notes
- ffmpeg is auto-resolved from `.venv` or `bin/ffmpeg.exe`; no manual override needed unless setting `FFMPEG_BINARY`.
- All configs are in `state/config`: `prompting.yaml`, `dispatch.yaml`, `validation.yaml`.
- Use the v4.3 prompt pack for detailed background and rationale.
- Theme and visual constraints are applied via `theme_id` and `image_options` in Gamma API calls for proper styling.

## Cluster Constants & Initialization (operator reference)
These values are already present in `course-content/staging/storyboard-a-trial/run-constants.yaml` and are valid for the trial run.

```yaml
run_id: "SB-A-TRIAL-001"
lesson_slug: "c1m1-tejal"
bundle_path: "course-content/staging/storyboard-a-trial"
primary_source_file: "course-content/courses/APC C1-M1 Tejal 2026-03-29.pdf"
optional_context_assets:
  - "course-content/courses/APC Content Roadmap.jpg"
theme_selection: "theme-a"
theme_paramset_key: "preset-a"
execution_mode: "tracked/default"
quality_preset: "production"
requested_content_type: "narrated-lesson-with-video-or-animation"
cluster_density: "sparse"
double_dispatch: false
motion_enabled: false
```

Cluster artifacts already exist in the bundle and should be reused for the trial:
- `clusters.json`
- `clusters-list.json`
- `cluster-plan-review.md`
- `g1.5-cluster-gate-receipt.json`

Concrete cluster values (from `clusters.json`) for reference:
- `cluster_id`: `c1`
- `goal`: “Explain the core concept with supporting interstitial emphasis.”
- `intents`: `introduce`, `emphasize`
- `constraints.visual_constraints`: palette `navy`, accent `teal`, layout `single-column`
- `slides`: `s-1`, `s-2`
- `priority`: `2`
- `size`: `2`

## Initialization Checklist (before Prompt 1)
- Confirm the bundle path exists: `course-content/staging/storyboard-a-trial/`
- Confirm `run-constants.yaml` matches the values above.
- Confirm `clusters.json` and `segment-manifest.yaml` are present in the bundle.
- Confirm source files exist in `course-content/courses/` (PDF + optional assets).
- Confirm prompt/config files exist in `state/config` (`prompting.yaml`, `dispatch.yaml`, `validation.yaml`).
