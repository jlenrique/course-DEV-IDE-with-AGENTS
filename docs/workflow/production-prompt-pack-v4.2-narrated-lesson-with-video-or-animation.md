# Production Prompt Pack v4.2: Marcus Motion-Enabled Narrated Workflow

Status:
- Cousin to `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md`, not a replacement.
- Intended for tracked/default runs that include Epic 14 motion controls.
- `DOUBLE_DISPATCH` remains an inline branch inside this workflow rather than requiring its own separate prompt pack.

## Why This Is A Separate Prompt Pack

Motion changes the control plane enough to warrant its own prompts document:
- a new HIL checkpoint exists after slide approval (`Gate 2M`)
- Marcus must persist and route a run-scoped `motion_plan.yaml`
- non-static slides must pass motion generation/import and Motion Gate before Irene Pass 2
- Irene Pass 2 becomes motion-aware and fail-closed on incomplete motion coverage

By contrast, double-dispatch is a bounded branch inside the Gary stage:
- Gary produces A/B variants
- Marcus captures per-slide selections
- the selected winner deck then rejoins the normal path

That makes motion a separate workflow doc, and `DOUBLE_DISPATCH` a conditional branch inside it.

## Changelog

- **v4.2** - Added Epic 14 motion controls (`motion_enabled`, Gate 2M, motion generation/import, Motion Gate, motion-aware Irene Pass 2) while preserving the Epic 12 `DOUBLE_DISPATCH` branch inside the same document.

Purpose: run a reliable, auditable production run from source ingestion through Irene Pass 2 for a narrated deck that includes optional per-slide motion and may also use double-dispatch to choose the best treatment per screen.

Design principles:
- Use one workflow doc for all motion-enabled narrated runs.
- Treat `motion_enabled` as the authoritative workflow switch.
- Treat `DOUBLE_DISPATCH` as a local branch in slide generation and selection, not a separate workflow family.
- Bind Gate 2M to the authorized winner deck only, never unresolved A/B pairs.
- Keep explicit stop rules at every human gate.

Execution mode: tracked/default.

Primary contract references:
- `docs/workflow/trial-run-pass2-artifacts-contract.md`
- `state/config/fidelity-contracts/`
- `_bmad-output/planning-artifacts/motion-enhanced-workflow-design.md`

---

## Run Constants (set once)

Persist accepted values as `run-constants.yaml` in the bundle root.

- RUN_ID: [e.g., C1-M1-PRES-20260405]
- LESSON_SLUG: [e.g., apc-c1m1-tejal]
- BUNDLE_PATH: [e.g., course-content/staging/tracked/source-bundles/<bundle-folder>]
- PRIMARY_SOURCE_FILE: [absolute path to primary PDF or source document]
- OPTIONAL_CONTEXT_ASSETS: [comma-separated list of supplementary files, or "none"]
- THEME_SELECTION: [approved theme key for slides]
- THEME_PARAMSET_KEY: [mapped parameter-set key for selected theme]
- EXECUTION_MODE: tracked/default
- QUALITY_PRESET: [explore | draft | production | regulated]
- REQUESTED_CONTENT_TYPE: narrated-lesson-with-video-or-animation
- MOTION_ENABLED: true
- MOTION_BUDGET_MAX_CREDITS: [positive number]
- MOTION_BUDGET_MODEL_PREFERENCE: [std | pro]
- DOUBLE_DISPATCH: [true | false]

Operator rule:
- Do not change run constants mid-run.
- `MOTION_ENABLED: true` requires an explicit positive budget.
- `DOUBLE_DISPATCH` changes only the Gary selection branch, not the rest of the workflow.

---

## 1) Activation + Preflight Contract Gate

Marcus, return an activation receipt for RUN_ID [RUN_ID]:

1. Active agent identity and role.
2. Execution mode and quality preset.
3. Requested content type and effective workflow template.
4. Contracts/schemas enforced this run.
5. Required fields validated before specialist dispatch.
6. Motion + double-dispatch readiness summary.

Required commands:
- `py -3.13 -m scripts.utilities.app_session_readiness --with-preflight --motion-enabled --json-only`
- `py -3.13 -m scripts.utilities.venv_health_check`
- `py -3.13 skills/pre-flight-check/scripts/preflight_runner.py --motion-enabled`
- If `DOUBLE_DISPATCH: true`, also require double-dispatch compatibility confirmation from preflight runner before proceeding.

Required write:
- `[BUNDLE_PATH]/preflight-results.json`

Gate rule:
- All checks must pass.
- Any warn/fail blocks progression.

Wait for explicit GO.

---

## 2) Source Authority Map Before Ingestion

Marcus, produce source authority and ingestion map for RUN_ID [RUN_ID].

Primary source:
- [PRIMARY_SOURCE_FILE]

Optional context:
- [OPTIONAL_CONTEXT_ASSETS]

For each source, return:
- source_id
- source_type
- authority_level
- downstream_consumers_direct
- downstream_consumers_indirect
- extraction_pathway
- expected_confidence
- known_risks

Stop and wait for approval.

---

## 2A) Operator Directives (Mandatory)

Poll timing policy (hard requirement):
- Start a poll timer when Prompt 2A is issued.
- Enforce a hard 3-minute reply hold from poll start before any submission can be accepted.
- Auto-close the poll exactly 15 minutes after poll start if a complete submission is not received.
- Submissions before the 3-minute mark are invalid and must be re-polled.
- If the poll auto-closes, keep ingestion blocked and require a new Prompt 2A poll.

Marcus, capture operator directives for RUN_ID [RUN_ID].

Record exactly:
- focus_directives
- exclusion_directives
- special_treatment_directives

If none, record:
- "No operator directives - process all source content at default authority levels."

Required write:
- `[BUNDLE_PATH]/operator-directives.md`

Stop and wait for operator confirmation.

---

## 3) Ingestion Execution + Evidence Log

Marcus, execute ingestion for RUN_ID [RUN_ID] using Source Wrangler official pathways only.

Inputs:
- source authority map
- operator directives

Required artifacts:
- `[BUNDLE_PATH]/extracted.md`
- `[BUNDLE_PATH]/metadata.json`
- `[BUNDLE_PATH]/ingestion-evidence.md`

Required validator:
- `py -3.13 -m scripts.utilities.validate_source_bundle_confidence --bundle-dir [BUNDLE_PATH]`

Fallback:
- If any planning-critical area is medium/low confidence, stop for targeted remediation before Prompt 4.

---

## 4) Ingestion Quality Gate + Irene Packet

Marcus, run ingestion quality gate for RUN_ID [RUN_ID].

Required checks:
- completeness
- readability
- anchorability
- provenance quality
- planning usability
- fidelity usability

If all pass, create:
- `[BUNDLE_PATH]/irene-packet.md`

Then run Vera G0 and return a compact receipt.

Stop if any dimension or G0 fails.

---

## 5) Irene Pass 1 Structure + Gate 1 Fidelity

Marcus, delegate Irene Pass 1 for RUN_ID [RUN_ID].

Inputs:
- Irene packet
- source bundle
- source metadata
- operator directives
- ingestion quality receipt

Required output:
- `[BUNDLE_PATH]/irene-pass1.md`

Before Gate 1 approval, run:
- Vera G1
- Vera G2
- Quinn-R quality G2

Hard constraints:
- Exactly one mode per slide: creative, literal-text, or literal-visual.
- No slides planned from excluded content.
- Literal-visual slides must carry complete spec cards.

Stop after Gate 1 review and approval.

---

## 6) Gate 1 Approved -> Pre-Dispatch Package Build (No Send)

Marcus, after Gate 1 approval, build Gary's pre-dispatch package and stop before dispatch.

Required machine artifacts:
- `[BUNDLE_PATH]/g2-slide-brief.md`
- `[BUNDLE_PATH]/gary-slide-content.json`
- `[BUNDLE_PATH]/gary-fidelity-slides.json`
- `[BUNDLE_PATH]/gary-diagram-cards.json`
- `[BUNDLE_PATH]/gary-theme-resolution.json`
- `[BUNDLE_PATH]/gary-outbound-envelope.yaml`
- `[BUNDLE_PATH]/pre-dispatch-package-gary.md`

Double-dispatch behavior:
- If `DOUBLE_DISPATCH: true`, `gary-outbound-envelope.yaml` must carry `dispatch_count: 2`.
- Variant B artifacts use `-B` suffix where applicable.

Stop if any artifact fails contract rules.

---

## 6B) Literal-Visual Operator Build + Confirmation

Marcus, before Prompt 7, run the mandatory literal-visual operator checkpoint.

Required write:
- `[BUNDLE_PATH]/literal-visual-operator-packet.md`

Gate rule:
- Prompt 7 is blocked until all required literal-visual assets are operator-ready.

---

## 7) Gary Dispatch + Export + Sort Verification

Marcus, dispatch Gary only if all checks are true:
- no unresolved literal-visual blockers
- envelope READY
- singular mode preserved
- theme mapping frozen
- requested content is content-bearing and dispatch-ready

Dispatch behavior:
- If `DOUBLE_DISPATCH: false`, run one Gary dispatch cycle.
- If `DOUBLE_DISPATCH: true`, run variant A and variant B for every eligible slide position.

Required outputs:
- `[BUNDLE_PATH]/gary-dispatch-result.json`
- `[BUNDLE_PATH]/gary-dispatch-run-log.json`
- If `DOUBLE_DISPATCH: true`: `[BUNDLE_PATH]/gary-dispatch-result-B.json`
- If `DOUBLE_DISPATCH: true`: `[BUNDLE_PATH]/gary-dispatch-run-log-B.json`
- `gamma-export/...`
- If `DOUBLE_DISPATCH: true`: `gamma-export-B/...`

Required validation:
- Vera G3 on every dispatch set produced
- `py -3.13 skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py --payload [BUNDLE_PATH]/gary-dispatch-result.json`
- If `DOUBLE_DISPATCH: true`, run the same validator against `[BUNDLE_PATH]/gary-dispatch-result-B.json`

Required write:
- `[BUNDLE_PATH]/gary-dispatch-validation-result.json`
- If `DOUBLE_DISPATCH: true`: `[BUNDLE_PATH]/gary-dispatch-validation-result-B.json`

Stop on any validator or G3 failure.

---

## 7B) Variant Selection Gate (Double-Dispatch Only)

> Skip this prompt when `DOUBLE_DISPATCH` is false.

Marcus, run per-slide variant selection for RUN_ID [RUN_ID].

Preconditions:
- Both variant sets exist and passed G3.
- All file paths are valid.

Required operator task:
- Review paired A/B variants per slide.
- Select the stronger treatment for each slide position.

Required write:
- `[BUNDLE_PATH]/variant-selection.json`

Gate rule:
- No downstream progression until every slide has exactly one selected variant.
- Deferred slides block progression.

Fallback:
- If one side failed, auto-select the surviving side and record that fallback explicitly.

---

## 7C) Storyboard A + Gate 2 Approval + Winner Authorization

Marcus, build the pre-Irene review storyboard for the winner deck and obtain Gate 2 approval.

Storyboard inputs:
- If `DOUBLE_DISPATCH: false`, use `[BUNDLE_PATH]/gary-dispatch-result.json`
- If `DOUBLE_DISPATCH: true`, use `storyboard/storyboard.json` plus `[BUNDLE_PATH]/variant-selection.json` for winner collapse

Required behavior:
- Generate `storyboard/storyboard.json` and `storyboard/index.html`
- Present the slide review summary and the reviewer-friendly HTML storyboard surface (ordered thumbnails, script/script-notes panels, orientation/provenance metadata, related-assets section)
- Obtain explicit Gate 2 approval on the selected winner deck

Required write:
- `[BUNDLE_PATH]/authorized-storyboard.json`

Authorization command:

```powershell
python skills/bmad-agent-marcus/scripts/write-authorized-storyboard.py `
  --manifest [BUNDLE_PATH]/storyboard/storyboard.json `
  --run-id [RUN_ID] `
  --output [BUNDLE_PATH]/authorized-storyboard.json `
  [--selections [BUNDLE_PATH]/variant-selection.json]
```

Gate rule:
- Motion planning and Irene Pass 2 must consume the authorized winner deck, not unresolved A/B variants.

---

## 7D) Gate 2M Motion Designation

Marcus, after `authorized-storyboard.json` exists and `MOTION_ENABLED: true`, present Gate 2M.

Required Marcus behavior before operator designation:
- Generate a per-slide recommendation for every authorized slide.
- Every recommendation must include:
  - recommended motion type
  - rationale
  - source anchor
  - confidence label
- Present the recommendation set as the starting point for operator review; the operator may override or add detail.

Required operator task:
- For each authorized slide, choose exactly one:
  - `static`
  - `video`
  - `animation`
- Add optional `motion_brief` for video slides
- Add optional `guidance_notes` for animation slides
- If you override Marcus's recommendation on any slide, add `override_reason`

Required writes:
- `[BUNDLE_PATH]/motion-designations.json`
- `[BUNDLE_PATH]/motion_plan.yaml`

Required commands:

```powershell
python skills/production-coordination/scripts/motion_plan.py build `
  --authorized-storyboard [BUNDLE_PATH]/authorized-storyboard.json `
  --output [BUNDLE_PATH]/motion_plan.yaml `
  --designations-output [BUNDLE_PATH]/motion-designations.json `
  --motion-enabled `
  --motion-budget-max-credits [MOTION_BUDGET_MAX_CREDITS] `
  --motion-budget-model-preference [MOTION_BUDGET_MODEL_PREFERENCE]
```

```powershell
python skills/production-coordination/scripts/motion_plan.py apply `
  --motion-plan [BUNDLE_PATH]/motion_plan.yaml `
  --designations [BUNDLE_PATH]/motion-designations.json `
  --output [BUNDLE_PATH]/motion_plan.yaml
```

Optional routing summary:

```powershell
python skills/production-coordination/scripts/motion_plan.py route `
  --motion-plan [BUNDLE_PATH]/motion_plan.yaml
```

Gate rules:
- Every authorized slide must have Gate 2M coverage.
- Recommendations must be presented for every authorized slide before operator selection.
- Unknown slide IDs or incomplete coverage block progression.

---

## 7E) Motion Generation / Import

Marcus, route non-static slides from `motion_plan.yaml` to their downstream handlers.

Routing rules:
- `static` slides remain unchanged.
- `video` slides route to Kling.
- `animation` slides route to manual animation guidance and import validation.

Required outcomes:
- video rows acquire generated MP4s plus credits consumed
- animation rows acquire imported approved files plus duration
- `motion_plan.yaml` is updated with concrete asset paths and statuses

Recommended authoritative command for `video` rows:

```powershell
python skills/production-coordination/scripts/run_motion_generation.py `
  --motion-plan [BUNDLE_PATH]/motion_plan.yaml `
  --slide-id [AUTHORIZED_SLIDE_ID]
```

Expected receipts per generated slide:
- run-scoped `.progress.json` receipt with `task_id` for resume/reconciliation
- run-scoped terminal `.json` receipt with provider status, local asset path, credits, and validation details
- production silence encoded as `requested_audio_mode: silent` with Kling native-audio field omitted from the API request

Fail-closed rules:
- One `pro -> std` downgrade is allowed per over-budget clip.
- If a clip still exceeds budget after downgrade, pause for operator action.
- No silent partial continuation.
- If a `.progress.json` receipt already exists for the same slide, resume polling that `task_id` instead of submitting a duplicate job.
- Patch `motion_plan.yaml` only after the downloaded MP4 passes local validation.

Stop before Irene Pass 2 until all non-static rows intended for this run have concrete assets or explicit operator resolution.

---

## 7F) Motion Gate

Marcus, run Motion Gate after motion generation/import is complete.

Required operator review:
- confirm generated/imported motion assets are acceptable
- confirm each non-static slide is either approved or intentionally reset to static
- confirm the exact approved asset path for each non-static slide before Irene Pass 2 handoff

Required state:
- every non-static row in `motion_plan.yaml` must be `approved`
- any reset-to-static row must be updated in `motion_plan.yaml` before Irene Pass 2

Gate rule:
- Irene Pass 2 is blocked until Motion Gate closes cleanly.

---

## 8) Irene Pass 2 - Motion-Aware Narration + Segment Manifest

Marcus, delegate Irene Pass 2 only after:
- Gate 2 approval completed
- `authorized-storyboard.json` exists
- `motion_plan.yaml` exists and fully covers the authorized winner deck
- all approved motion assets are present for non-static slides

Inputs:
- winner slide output derived from the authorized deck
- source bundle
- operator directives
- Irene Pass 1
- refreshed `[BUNDLE_PATH]/pass2-envelope.json`
- if `DOUBLE_DISPATCH: true`, `[BUNDLE_PATH]/variant-selection.json`
- if `MOTION_ENABLED: true`, `[BUNDLE_PATH]/motion_plan.yaml`

Required Marcus behavior before delegation:
- refresh or regenerate `[BUNDLE_PATH]/pass2-envelope.json` so it reflects the current authorized deck, current `motion_plan.yaml`, expected Pass 2 outputs, and any approved motion assets for this run
- if this is a rerun, archive or remove stale partial Pass 2 outputs before delegation so Irene writes fresh canonical artifacts at bundle root
- treat `authorized-storyboard.json` plus the approved local winner-slide PNGs as the slide identity source of truth; do not reuse prior storyboard review projections as execution inputs
- in motion runs, preserve the exact Motion Gate-approved asset path per non-static slide; do not re-decide motion inside Pass 2

Required outputs:
- `[BUNDLE_PATH]/narration-script.md`
- `[BUNDLE_PATH]/segment-manifest.yaml`
- `[BUNDLE_PATH]/perception-artifacts.json`
- if motion exists: motion perception confirmations aligned to non-static segments, written into `pass2-envelope.json` as `motion_perception_artifacts`

Required validation:
- `py -3.13 skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py --envelope [BUNDLE_PATH]/pass2-envelope.json`
- Vera G4

Validator expectations at this stage:
- every authorized slide must have at least one segment in `segment-manifest.yaml`
- every manifest segment must have non-empty `narration_text`
- every manifest segment must contain at least one non-empty `visual_references[].narration_cue` that is traceable to `perception-artifacts.json` and present in the segment narration text
- every non-static motion segment must remain bound to the approved `motion_plan.yaml` asset and have matching motion perception confirmation before handoff passes

Motion-specific rules:
- Irene must hydrate motion fields from `motion_plan.yaml`, not infer them from draft narration.
- Motion-enabled manifest hydration must fail closed on empty or partial plan coverage.
- Motion-enabled reruns must fail closed if `motion_plan.yaml` is not already in final Motion Gate-approved state.
- Non-static segments must pass motion perception confirmation before final handoff.
- If a segment's approved playback visual is a motion clip (`visual_mode: video`, `motion_type: video`), Irene should write motion-first narration: use the slide once for orientation if needed, then speak primarily to the visible action/change in the approved clip rather than continuing to narrate the static slide layout as if it were still on screen.

Rerun rule:
- If Prompt 8 is being re-run after a partial or invalid Pass 2 attempt, restart at Prompt 8 itself once Gate 2 and Motion Gate remain valid; do not jump ahead to Storyboard B from stale Pass 2 artifacts.

Required HIL review:
- Regenerate Storyboard B with script context before downstream audio finalization.

---

## Mandatory Receipts Per Stage

Require Marcus to emit a compact receipt for every prompt:
- stage
- status (pass | warn | fail)
- artifacts_written
- validator_results
- gate_decision
- next_action

---

## Scope Position

This prompt pack is the right home for motion-enabled narrated runs.

Documentation rule going forward:
- keep `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md` for the non-motion narrated workflow
- keep this doc for motion-enabled narrated workflow
- keep `DOUBLE_DISPATCH` as a conditional branch inside either doc rather than splitting it into separate single-dispatch and double-dispatch prompt packs
