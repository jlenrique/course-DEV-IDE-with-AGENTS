# Production Run Operator Card (v4)

Use this card during tracked/production runs through Irene Pass 2.

Prompt pack selection:
- `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md` for non-motion narrated runs
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` when `MOTION_ENABLED: true`

Contracts and validators:
- `docs/workflow/trial-run-pass2-artifacts-contract.md`
- `skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py`
- `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`
- `skills/bmad-agent-marcus/scripts/validate-source-bundle-confidence.py` (loads `run-constants.yaml` when present)
- `.\.venv\Scripts\python.exe -m scripts.utilities.run_constants --bundle-dir <bundle>` (optional path verification: `--verify-paths`)

Session launcher:
- `docs/workflow/production-session-launcher.md`

VS Code users: use the same production session launcher prompt. VS Code tasks for preflight are defined in `.vscode/tasks.json` (`APP: Session Readiness + Preflight`).

Interpreter rule:
- Use `.\.venv\Scripts\python.exe` for repo-local commands on this card.
- Do not use global `py`, `python`, or bare `pytest` during production operations.

---

## A) Run Setup (once)

Set values in the prompt pack Run Constants block:
- RUN_ID
- LESSON_SLUG
- BUNDLE_PATH
- PRIMARY_SOURCE_FILE
- OPTIONAL_CONTEXT_ASSETS
- THEME_SELECTION
- THEME_PARAMSET_KEY
- EXECUTION_MODE: tracked/default
- QUALITY_PRESET
- DOUBLE_DISPATCH: [true | false, default false]
- MOTION_ENABLED: [true | false, default false]
- MOTION_BUDGET_MAX_CREDITS: [required when `MOTION_ENABLED: true`]
- MOTION_BUDGET_MODEL_PREFERENCE: [std | pro, required when `MOTION_ENABLED: true`]

Operator rule:
- Do not change run constants mid-run.
- Execution mode must be tracked/default for production runs.
- Persist accepted constants as **`run-constants.yaml`** in the bundle root (contract §1B); use `app_session_readiness --bundle-dir ...` during shift open if you want an automated alignment check.
- `DOUBLE_DISPATCH` stays inside the selected prompt pack; it does not select a separate workflow template.
- For tracked-bundle shifts, treat the `--bundle-dir` readiness check as required, not optional.
- `MOTION_ENABLED` selects the motion prompt pack and adds Gate 2M plus Motion Gate obligations before Irene Pass 2.
- If `EXPERIENCE_PROFILE` is set, a Creative Directive (CD) step is mandatory before Irene Pass 1.

Fast path:
- For the condensed operator flow, use `docs/workflow/first-tracked-run-quickstart.md`.

---

## B) Gate Checklist (go/no-go)

### 1. Prompt 1: Preflight
- Run:
  - `.\.venv\Scripts\python.exe scripts/utilities/app_session_readiness.py --with-preflight`
  - `.\.venv\Scripts\python.exe -m scripts.utilities.emit_preflight_receipt --with-preflight --motion-enabled --bundle-dir [BUNDLE_PATH] --output [BUNDLE_PATH]/preflight-results.json`
  - `.\.venv\Scripts\python.exe -m scripts.utilities.venv_health_check`
- If `MOTION_ENABLED: true`, require motion-capable readiness path:
  - `.\.venv\Scripts\python.exe scripts/utilities/app_session_readiness.py --with-preflight --motion-enabled`
  - `.\.venv\Scripts\python.exe skills/pre-flight-check/scripts/preflight_runner.py --motion-enabled`
- Require all invoked checks to return `overall_status = pass`.
- Write `preflight-results.json`.
- Go/no-go: no go on any warn/fail.

### 2. Prompt 2: Source authority map
- Confirm direct/indirect consumer fields are present.
- Go/no-go: no go until approved.

### 2A. Prompt 2A: Operator Directives
- **Mandatory step.** Cannot skip.
- Confirm `operator-directives.md` is written with:
  - focus_directives (list or empty)
  - exclusion_directives (list or empty)
  - special_treatment_directives (list or empty)
  - OR explicit "no special directives" acknowledgment
- Go/no-go: no go until directives are recorded or explicitly waived.

### 3. Prompt 3: Ingestion evidence
- Confirm artifacts:
  - `extracted.md`, `metadata.json`, `ingestion-evidence.md`
- Confirm `operator_directive_applied` column populated for each source.
- Go/no-go: no go if planning-critical confidence medium/low without spot-check approval.

### 4. Prompt 4: Ingestion quality + G0
- Confirm `preflight-results.json` pass state rechecked.
- Confirm `irene-packet.md` section order is valid.
- Confirm operator exclusion directives are respected in G0 evaluation.
- Run/record G0 receipt.
- Go/no-go: no go if any fail.

### 04A. Prompt 04A: Lesson Plan Coauthoring + Scope Lock
- **Mandatory checkpoint.** Runs after Prompt 4 and before Prompt 4.75.
- Confirm Marcus and operator ratify per-unit scope decisions in plain language.
- Confirm `scope_decision.set` event(s) exist for this run revision.
- Confirm `plan.locked` exists for the same revision.
- Confirm a Step `04A` handoff/evidence record exists before Step `05`.
- Go/no-go: no go until 04A is complete and the locked plan revision is confirmed.

### 4.75. Prompt 4.75: Creative Directive Resolution (CD)
- **Skip if `EXPERIENCE_PROFILE` is not set.**
- Confirm `creative-directive.yaml` is written and validated.
- Confirm `run-constants.yaml` slide mode proportions match the directive.
- Confirm `state/config/narration-script-parameters.yaml` is updated with `narration_profile_controls`.
- Go/no-go: no go until the directive is validated and resolved.

### 5. Prompt 5: Irene Pass 1 + G1/G2
- Confirm one mode per slide.
- Confirm literal-visual spec cards are complete.
- Confirm operator directives are reflected in slide plan.
- Run/record G1 and G2 receipts.
- Go/no-go: no go until Gate 1 approval.

> **Optional A/B Loop:** If running Irene Pass 1 tuning, pause here and follow
> `docs/workflow/operator-script-v4.2-irene-ab-loop.md`. Resume at Prompt 6 once a winner is promoted.

### 6. Prompt 6: Pre-dispatch package
- Confirm required machine artifacts exist:
  - `g2-slide-brief.md`
  - `gary-slide-content.json`
  - `gary-fidelity-slides.json`
  - `gary-diagram-cards.json`
  - `gary-theme-resolution.json`
  - `gary-outbound-envelope.yaml`
  - `pre-dispatch-package-gary.md`
- Go/no-go: no go until approved.

### 6.2. Prompt 6.2: Cluster Prompt Engineering (conditional)
- **Skip if `CLUSTER_DENSITY` is none.**
- Confirm `cluster-prompts.json` is written from `clusters.json` using `state/config/prompting.yaml`.
- Go/no-go: no go if prompt engineering fails or file is empty.

### 6.3. Prompt 6.3: Cluster Dispatch Sequencing (conditional)
- **Skip if `CLUSTER_DENSITY` is none.**
- Confirm `cluster-dispatch-plan.json` is written from `clusters-list.json` using `state/config/dispatch.yaml`.
- Go/no-go: no go if `plan_hash` is missing or sequencing fails.

### 6B. Prompt 6B: Literal-visual operator checkpoint
- Confirm `literal-visual-operator-packet.md` exists and is complete for every literal-visual slide.
- Confirm operator readiness state is explicit for all required cards.
- Go/no-go: no go until all required literal-visual cards are operator-ready.

### 7. Prompt 7: Dispatch + Gate 2
- If `DOUBLE_DISPATCH: true`, Gary dispatches twice (variant A + variant B).
- Confirm outputs:
  - `gary-dispatch-result.json` (check `literal_visual_source` per literal-visual slide)
  - `gary-dispatch-run-log.json`
  - `gamma-export/...`
- Literal-visual dispatch uses **initial template attempt + one retry + composite fallback**:
  - `literal_visual_source: template` = Gamma rendered (best case)
  - `literal_visual_source: composite-preintegration` = local PNG composited
  - `literal_visual_source: composite-download` = URL downloaded and composited
  - All three produce valid 2400x1350 slide PNGs
- If composite fallback fired, verify the center-crop framing is acceptable for the specific image.
- Run G3.
- Run strict validator:
  - `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py --payload [BUNDLE_PATH]/gary-dispatch-result.json`
- Save validator output:
  - `gary-dispatch-validation-result.json`
- Confirm Storyboard A artifacts and approval:
  - `storyboard/storyboard.json`
  - `storyboard/index.html`
  - review page shows ordered slide thumbnails, script/script-notes panels, and provenance/orientation metadata
  - use the HTML review page for human review; treat JSON as the machine manifest
- Go/no-go: no go if validator `status=fail` or G3 fail.
- Then explicit Gate 2 approval.

### 7.5. Prompt 7.5: Cluster Coherence (G2.5) (conditional)
- **Skip if `CLUSTER_DENSITY` is none.**
- Confirm `cluster-coherence-report.json` exists.
- If coherence fails, run interstitial redispatch protocol and re-run G2.5.
- Go/no-go: no go until G2.5 passes or operator explicitly accepts violations.

### 7B. Prompt 7B: Variant Selection (double-dispatch only)
- **Skip if `DOUBLE_DISPATCH` is false.**
- Confirm paired-thumbnail selection storyboard presented to operator.
- Confirm per-slide A/B selection recorded in `variant-selection.json`.
- Confirm operator confirmation flag is set.
- Go/no-go: no go until all slides have a selected variant and operator confirms.

### 7C. Prompt 7C: Winner Authorization
- Confirm `authorized-storyboard.json` is written after Gate 2 approval.
- If `DOUBLE_DISPATCH: true`, confirm the authorized deck collapses to the selected winner deck only.
- Confirm downstream motion planning / Irene Pass 2 reference `authorized-storyboard.json`, not the review HTML.
- Go/no-go: no go until the canonical winner deck exists.

### 7D. Prompt 7D: Gate 2M Motion Designation
- **Skip if `MOTION_ENABLED` is false.**
- Confirm Marcus presents a recommendation set for every authorized slide before operator selection.
- Confirm every recommendation includes recommended motion type, rationale, source anchor, and confidence.
- Confirm every authorized slide has exactly one designation: `static`, `video`, or `animation`.
- Confirm any operator override of Marcus's recommendation includes `override_reason`.
- Confirm `motion-designations.json` and `motion_plan.yaml` exist.
- Confirm operator overrides remain possible and recommendations are not silently auto-applied.
- Go/no-go: no go until Gate 2M covers every authorized slide.

### 7E. Prompt 7E: Motion Generation / Import
- **Skip if `MOTION_ENABLED` is false.**
- Confirm `video` slides route to Kling and `animation` slides route to manual animation import.
- Confirm non-static rows acquire concrete asset paths and no intended row remains unresolved.
- Build the reviewer-facing inspection pack:
  - `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/build-pass2-inspection-pack.py --bundle [BUNDLE_PATH]`
- Confirm over-budget clips either downgrade once (`pro -> std`) or pause the run for operator action.
- Go/no-go: no go on silent partial continuation.

### 7F. Prompt 7F: Motion Gate
- **Skip if `MOTION_ENABLED` is false.**
- Confirm every non-static row in `motion_plan.yaml` is approved, or explicitly reset to static before Irene Pass 2.
- Go/no-go: no go until Motion Gate is cleanly closed.

### 8. Prompt 8: Irene Pass 2 handoff
- Confirm preconditions:
  - order 1..N, file_path present, source_ref present, perception_artifacts aligned, artifacts consistent
  - if `MOTION_ENABLED: true`, `motion_plan.yaml` fully covers the authorized deck
- Regenerate the handoff with the canonical Marcus helper before Irene runs:
  - `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/prepare-irene-pass2-handoff.py --bundle [BUNDLE_PATH]`
- Confirm `pass2-prep-receipt.json` exists and any stale prior Pass 2 root artifacts were archived under `recovery/archive/pass2-reruns/`.
- Delegate Irene Pass 2.
- Validate handoff envelope:
  - `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py --envelope [BUNDLE_PATH]/pass2-envelope.json`
  - confirm the validator passes the stricter Pass 2 semantics:
    - every authorized slide has at least one manifest segment
    - every segment has non-empty `narration_text`
    - every segment has at least one non-empty visual `narration_cue` traceable to perception and present in narration
    - every runtime-planned segment carries `timing_role`, `content_density`, `visual_detail_load`, `duration_rationale`, and `bridge_type`
  - runtime drift, weak timing rationale, and bridge-cadence gaps are treated as hard failures in strict mode (use advisory mode only when explicitly approved)
    - every non-static motion segment is still bound to the approved motion asset and has matching motion perception confirmation
- Run G4.
- Go/no-go: no go downstream if G4 critical findings.
- Regenerate Storyboard B (slide + script context) and get explicit approval before downstream audio/script finalization.

### 11B. ElevenLabs input package review
- Confirm a pre-synthesis package review is shown before any ElevenLabs spend.
- Require:
  - `elevenlabs-input-review.md`
  - locked script hash
  - locked manifest hash
  - selected voice id + preview/source
  - audio buffer
  - runtime-plan summary
  - bridge-cadence expectations
  - any segment-level voice overrides
  - any inherited non-default voice-direction controls
- Go/no-go: no go to Prompt 12 until the displayed package is explicitly approved.

### 12. Prompt 12: ElevenLabs synthesis
- Confirm `elevenlabs-input-review.md` matches the current locked package before generation starts.

---

## C) Fast Failure Recovery

If any stage fails:
1. Record failure stage + validator errors.
2. Repair only failed artifact(s), not whole chain.
3. Re-run just the failed validator/gate.
4. Resume at the same stage.

---

## D) Minimum Evidence Bundle (for closeout)

Collect and keep:
- `preflight-results.json`
- `operator-directives.md`
- `ingestion-evidence.md`
- fidelity receipts (G0-G4)
- `creative-directive.yaml` (if `EXPERIENCE_PROFILE` is set)
- `gary-dispatch-validation-result.json`
- `literal-visual-operator-packet.md` (if literal-visual slides exist)
- `authorized-storyboard.json`
- `variant-selection.json` (if `DOUBLE_DISPATCH: true`)
- `cluster-prompts.json`, `cluster-dispatch-plan.json`, `cluster-coherence-report.json` (if clustering enabled)
- `motion-designations.json` and `motion_plan.yaml` (if `MOTION_ENABLED: true`)
- `pass2-prep-receipt.json` and inspection-pack receipt (if Irene Pass 2 prep occurred)
- Pass 2 handoff validator output
- final stage receipts per prompt

---

## E) Operator Exit Criteria (Irene Pass 2 ready)

Run is considered successful up to Pass 2 when:
- Gate 1 approved
- Gate 2 approved
- If `EXPERIENCE_PROFILE` is set, Creative Directive resolved
- If `DOUBLE_DISPATCH: true`, winner selection is recorded and authorized
- If `MOTION_ENABLED: true`, Gate 2M and Motion Gate both passed
- Gary dispatch validator passes
- Pass 2 handoff validator passes
- G4 has no critical findings
- Operator directives recorded and honored throughout
