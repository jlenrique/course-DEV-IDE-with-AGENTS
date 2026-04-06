# Production Prompt Pack v4.1: Narrated Deck Video Export

Status:
- Standard tracked/default prompt pack for the non-motion narrated workflow (`narrated-deck-video-export`).
- Sibling to the motion-enabled prompt pack, not superseded by it.
- Supersedes v3 (trial/ad-hoc era). v3 retained for historical traceability.

## Changelog

- **v4.1** — Added `DOUBLE_DISPATCH` run constant + conditional dispatch/selection logic in Prompts 1, 6, 7 (new 7B), 8 (Epic 12).

## Workflow Scope

Use this prompt pack when:
- the requested workflow is `narrated-deck-video-export`
- `motion_enabled` is false

Do not use this prompt pack when motion is enabled. For that case, use the motion-specific cousin prompt pack for `narrated-lesson-with-video-or-animation`.

Purpose: run a reliable, auditable production run from source ingestion through Irene Pass 2 with deterministic stop rules at every stage.

Design principles:
- All prompts are reusable templates. Run Constants (set once) is the single source of truth for per-run values.
- Explicit user approvals: Gate 1 and Gate 2 only.
- Vera fidelity checks are internal; Marcus returns concise receipts.
- Deterministic stop rules prevent weak outputs from drifting downstream.
- Detailed fallback paths for every stage when first response misses the mark.
- When `DOUBLE_DISPATCH` is true, an additional operator gate (Prompt 7B) appears between dispatch and narration for variant selection.
- `DOUBLE_DISPATCH` remains an inline branch inside this workflow, not a separate workflow family.

Execution mode: tracked/default (SQLite state tracking, production_runs table, run baton governance).

Primary contract references:
- `docs/workflow/trial-run-pass2-artifacts-contract.md`
- `state/config/fidelity-contracts/` (G0-G4)

---

## Run Constants (set once)

After acceptance, persist the same fields as **`run-constants.yaml`** in the bundle root so tooling can load them (`python -m scripts.utilities.run_constants --bundle-dir [BUNDLE_PATH]`). See `docs/workflow/trial-run-pass2-artifacts-contract.md` §1B.

- RUN_ID: [e.g., C1-M1-PRES-20260405]
- LESSON_SLUG: [e.g., apc-c1m1-tejal]
- BUNDLE_PATH: [e.g., course-content/staging/tracked/source-bundles/<bundle-folder>]
- PRIMARY_SOURCE_FILE: [absolute path to primary PDF or source document]
- OPTIONAL_CONTEXT_ASSETS: [comma-separated list of supplementary files, or "none"]
- THEME_SELECTION: [approved theme key for standard slides]
- THEME_PARAMSET_KEY: [mapped parameter-set key for selected theme]
- EXECUTION_MODE: tracked/default
- QUALITY_PRESET: [explore | draft | production | regulated]
- DOUBLE_DISPATCH: [true | false, default false]

---

## 1) Activation + Preflight Contract Gate

Marcus, return an activation receipt for RUN_ID [RUN_ID]:

1. Active agent identity and role.
2. Execution mode and quality preset.
3. Contracts/schemas enforced this run (Irene + Gary envelopes).
4. Required fields validated before specialist dispatch.
5. One refusal rule for non-contract delegation.
6. Toolchain preflight status (Source Wrangler, sensory bridges, Gamma auth/API, Python runtime).

Required commands:
- `py -3.13 -m scripts.utilities.app_session_readiness --with-preflight --format json`
- `py -3.13 -m scripts.utilities.venv_health_check`
- If `DOUBLE_DISPATCH: true`: run `check_double_dispatch_compatibility()` from preflight runner. Block on fail.

Required write:
- `[BUNDLE_PATH]/preflight-results.json` with run_id, timestamp, and both command outputs.

Gate rule:
- Both checks must be `overall_status = pass`.
- Any warn/fail blocks progression.

Fallback (detailed):
- If either command times out or warns/fails, require Marcus to produce:
  - exact failing checks
  - one-step repair command
  - re-run confirmation plan
- No ingestion/delegation until explicit GO after clean recheck.

Wait for explicit GO.

---

## 2) Source Authority Map Before Ingestion

Marcus, produce source authority and ingestion map for RUN_ID [RUN_ID].

Primary source:
- [PRIMARY_SOURCE_FILE]

Optional context:
- [OPTIONAL_CONTEXT_ASSETS]

For each source, return one row with:
- source_id
- source_type
- authority_level (primary | framing-only | excluded)
- downstream_consumers_direct
- downstream_consumers_indirect
- extraction_pathway
- expected_confidence
- known_risks

Contract:
- Must follow `docs/workflow/trial-run-pass2-artifacts-contract.md`.

Fallback (detailed):
- If source authority is ambiguous, require a split decision table:
  - include/exclude decision
  - confidence reason
  - downstream risk if wrong
- Stop for user confirmation before ingestion.

Stop and wait for approval.

---

## 2A) Operator Directives (Custom Source Instructions)

**This step is mandatory.** Ingestion (Prompt 3) cannot proceed without either explicit directives or an explicit "no special directives" acknowledgment from the operator.

Poll timing policy (hard requirement):
- Start a poll timer when Prompt 2A is issued.
- Enforce a hard 3-minute reply hold from poll start before any submission can be accepted.
- Auto-close the poll exactly 15 minutes after poll start if a complete submission is not received.
- Submissions before the 3-minute mark are invalid and must be re-polled.
- If the poll auto-closes, keep ingestion blocked and require a new Prompt 2A poll.

Marcus, record the operator's source-processing directives for RUN_ID [RUN_ID].

The operator will provide directives in three categories. For each, record exactly what is stated:

**Focus directives** — sections, topics, or content to emphasize:
- [e.g., "Focus on Section 3: Learning Outcomes and the case study in Chapter 5"]
- [e.g., "The table on page 12 is the primary data for slide content"]

**Exclusion directives** — content to ignore or deprioritize:
- [e.g., "Ignore Appendix B (instructor notes, not student-facing)"]
- [e.g., "Skip the bibliography and references section"]

**Special treatment directives** — content requiring non-default handling:
- [e.g., "Treat the infographic on page 8 as a literal-visual candidate"]
- [e.g., "The acronym list on page 2 should feed the pronunciation dictionary, not slide content"]
- [e.g., "Diagram on page 14 must be preserved exactly as-is (source-crop, no rebranding)"]

If the operator has no special directives, record: "No operator directives — process all source content at default authority levels."

Required write:
- `[BUNDLE_PATH]/operator-directives.md` with:
  - run_id
  - timestamp
  - poll_started_utc
  - reply_eligible_utc (poll_started_utc + 3 minutes)
  - poll_close_utc (poll_started_utc + 15 minutes)
  - poll_status (open | closed-timeout | submitted)
  - operator (from session)
  - focus_directives (list)
  - exclusion_directives (list)
  - special_treatment_directives (list)
  - or the explicit "no directives" acknowledgment

Governance rules:
- Operator directives bind Source Wrangler during ingestion and Irene during planning.
- Exclusion directives are provenance records: Vera G0 must not flag excluded content as an omission if the exclusion is recorded here.
- Focus directives are emphasis signals, not exclusion of unmentioned content.
- Special treatment directives override default fidelity classification for the specified content only.
- This artifact becomes a first-class input alongside `extracted.md` for downstream agents.

Stop and wait for operator to provide directives (or confirm "no special directives").

---

## 3) Ingestion Execution + Evidence Log

Marcus, execute ingestion for RUN_ID [RUN_ID] using Source Wrangler official pathways only.

Inputs for this step:
- Source authority map from Prompt 2
- Operator directives from Prompt 2A: `[BUNDLE_PATH]/operator-directives.md`

Apply operator directives during extraction:
- Honor exclusion directives: excluded sections are extracted but tagged `excluded` in provenance, not fed to planning.
- Honor focus directives: prioritize extraction depth and coverage for focused sections.
- Honor special treatment directives: tag affected content with the operator's specified handling.

For each source, return an evidence row with:
- source_id
- pathway_used
- extraction_status
- coverage_metric
- confidence
- bundle_location
- provenance_summary
- planning_readiness
- operator_directive_applied (yes/no, with directive reference if yes)

Required artifacts under [BUNDLE_PATH]:
- `extracted.md`
- `metadata.json`
- `ingestion-evidence.md`

`ingestion-evidence.md` must follow required columns and footer block from `docs/workflow/trial-run-pass2-artifacts-contract.md`.

Confidence handling rule:
- If an official bridge or Source Wrangler extraction records source confidence inside `extracted.md`, inherit that confidence into `ingestion-evidence.md` unless explicit contrary evidence is recorded.
- A `high` confidence note with limited caveats is cautionary, not blocking.

Confidence consistency validator:
- Run `py -3.13 -m scripts.utilities.validate_source_bundle_confidence --bundle-dir [BUNDLE_PATH]` after writing bundle artifacts.
- If the validator fails, stop and correct the confidence drift before continuing.

Fallback (detailed):
- If any planning-critical section confidence is medium/low:
  - produce anchor-level spot-check list
  - mark planning readiness as conditional/blocked
  - stop and request directed correction before continuing

---

## 4) Ingestion Quality Gate + Irene Packet

Marcus, run ingestion quality gate for RUN_ID [RUN_ID] and return pass/fail per source on:
- completeness
- readability
- anchorability
- provenance quality
- planning usability
- fidelity usability

Precondition:
- Verify `[BUNDLE_PATH]/preflight-results.json` exists and both preflight gates passed.

If any fail: provide 2 remediation options and stop.

If all pass, create:
- `[BUNDLE_PATH]/irene-packet.md` in required section order from contract.

The Irene packet must incorporate operator directives:
- Focus directives inform CLO-ranked opportunities and recommendation emphasis.
- Exclusion directives are surfaced as "operator-excluded zones" so Irene does not plan content from them.
- Special treatment directives are passed through as fidelity-sensitive zone annotations.

Then run internal Vera G0 and return receipt:
- verdict: pass | warn | fail
- critical findings
- remediation target

Gate interpretation rules:
- Do not downgrade a source from `high` to `medium/low` unless the gate records explicit evidence.
- A `high` confidence source with non-blocking caveats can still pass planning usability and fidelity usability.
- Vera G0 must respect operator exclusion directives: content excluded by directive is not an omission.
- If a receipt is written, re-run `py -3.13 -m scripts.utilities.validate_source_bundle_confidence --bundle-dir [BUNDLE_PATH] --receipt [BUNDLE_PATH]/ingestion-quality-gate-receipt.md` before finalizing.

Fallback (detailed):
- If any dimension fails or G0 fails:
  - provide 2 remediation options
  - include precise source anchors affected
  - stop until corrected artifacts are produced and rechecked

---

## 5) Irene Pass 1 Structure + Gate 1 Fidelity

Marcus, delegate Irene Pass 1 for RUN_ID [RUN_ID].

Inputs for this step:
- Irene packet: `[BUNDLE_PATH]/irene-packet.md`
- Source bundle: `[BUNDLE_PATH]/extracted.md`
- Source metadata: `[BUNDLE_PATH]/metadata.json`
- Operator directives: `[BUNDLE_PATH]/operator-directives.md`
- Ingestion quality gate receipt: `[BUNDLE_PATH]/ingestion-quality-gate-receipt.md`

Require Irene Pass 1 output in this exact structure:
- executive summary
- slide plan table
- literal support plan
- risks and tradeoffs
- Gate 1 decision line

Hard constraints:
- Exactly one mode per slide: creative, literal-text, literal-visual.
- No mixed-mode labels.
- Operator focus directives are reflected in slide emphasis and CLO prioritization.
- Operator exclusion directives are respected: no slides planned from excluded content.
- Operator special treatment directives override default fidelity classification where specified.
- For every literal-visual slide, include a full spec card with:
  - graphic_id
  - slide_number
  - CLO served
  - exact labels/claims to preserve
  - source anchors
  - chart/diagram structure
  - prohibited embellishments
  - acceptance checks

Required write:
- `[BUNDLE_PATH]/irene-pass1.md`

Before Gate 1 approval, run internal Vera gates in order:
- G1: lesson plan vs source bundle
- G2: slide brief vs lesson plan

Return a single fidelity receipt with per-gate verdicts and blocking findings.

If G1 or G2 fail:
- include omission, invention, and alteration findings
- include minimal patch targets in Irene output
- rerun only the failed gate(s)
- return one consolidated compact receipt

If G1 and G2 pass:
- return compact receipt with: stage, status, artifacts_written, validator_results, gate_decision, next_action

Do not advance to Prompt 6 automatically. Stop after producing `irene-pass1.md` and the compact receipt.

---

## 6) Gate 1 Approved -> Pre-Dispatch Package Build (No Send)

Marcus, after Gate 1 approval, build Gary pre-dispatch package for RUN_ID [RUN_ID] and stop before dispatch.

Inputs for this step:
- Source bundle: `[BUNDLE_PATH]/extracted.md`
- Irene packet: `[BUNDLE_PATH]/irene-packet.md`
- Irene Pass 1: `[BUNDLE_PATH]/irene-pass1.md`
- Operator directives: `[BUNDLE_PATH]/operator-directives.md`

Required package sections:
- claim-to-source fidelity matrix
- literal candidate list and synthesis zones
- final per-slide singular modes
- creative + literal queue mapping
- diagram card mapping
- theme resolution block:
  - requested_theme_key
  - resolved_theme_key
  - resolved_parameter_set
  - mapping_source
  - mapping_version
  - user_confirmation
- all high-fidelity instructional graphics identified (minimum 2 in scope)
- Gary envelope readiness check

Required machine artifacts under [BUNDLE_PATH]:
- `g2-slide-brief.md`
- `gary-slide-content.json`
- `gary-fidelity-slides.json`
- `gary-diagram-cards.json`
- `gary-theme-resolution.json`
- `gary-outbound-envelope.yaml`
- `pre-dispatch-package-gary.md`

Double-dispatch behavior:
- When `DOUBLE_DISPATCH: true`, `gary-outbound-envelope.yaml` must carry `dispatch_count: 2`.
- Artifact filenames for the second dispatch variant gain a `-B` suffix (e.g., `gary-dispatch-result-B.json`).
- The primary dispatch artifacts retain their canonical names (no suffix).

Contract rules:
- Follow `docs/workflow/trial-run-pass2-artifacts-contract.md` exactly.
- `g2-slide-brief.md` must be derived from `irene-pass1.md` and must not introduce new pedagogical content.
- `gary-slide-content.json` must contain one content-bearing row per slide with fields: slide_number, content, source_ref.
- Literal-visual policy: for literal-visual slides, `gary-slide-content.json.slides[].content` must be image URL only (no explanatory/support text on-slide; move that text to narration/script).
- Each slide must preserve exactly one mode: creative, literal-text, or literal-visual.
- `gary-fidelity-slides.json` slide_number values must be unique and strictly increasing.
- `gary-diagram-cards.json` must include only literal-visual cards that require image handling.
- For tracked/default runs, diagram cards may carry local `preintegration_png_path` values for APP-managed Git-host staging at dispatch time.
- `gary-theme-resolution.json` must freeze the theme mapping handshake fields.
- `gary-outbound-envelope.yaml` must carry forward theme_resolution and fidelity_per_slide unchanged from the machine artifacts.

If any artifact fails contract rules:
- return contract violation list by file and field
- regenerate only the failed artifact(s)
- revalidate
- stop and wait for approval

Return one compact receipt with: stage, status, artifacts_written, validator_results, gate_decision, next_action.

Do not dispatch to Gary in this step.

---

## 6B) Literal-Visual Operator Build + Confirmation (Mandatory Before Dispatch)

Marcus, before Prompt 7, run a mandatory literal-visual operator checkpoint for RUN_ID [RUN_ID].

Inputs for this step:
- Irene Pass 1: `[BUNDLE_PATH]/irene-pass1.md`
- Pre-dispatch package: `[BUNDLE_PATH]/pre-dispatch-package-gary.md`
- Diagram cards: `[BUNDLE_PATH]/gary-diagram-cards.json`
- Source bundle: `[BUNDLE_PATH]/extracted.md`

Required behavior:
- Produce a user-facing list of all slides flagged `literal-visual`.
- For each listed slide, provide an operator build packet with:
  - slide_number
  - graphic_id (from Irene literal-visual spec card)
  - source anchors and extracted context needed to recreate the visual faithfully
  - Irene constraints (labels/claims to preserve, prohibited embellishments, acceptance checks)
  - expected local preintegration path (`preintegration_png_path`) from diagram cards
- Ask the operator to confirm each asset is created in Gamma and downloaded locally as PNG.

Required write:
- `[BUNDLE_PATH]/literal-visual-operator-packet.md` containing the full per-slide packet and checklist.

Gate rule:
- Prompt 7 is blocked until all required literal-visual cards are marked operator-ready.
- If any required card is missing local PNG evidence, return blockers and stop.

Fallback (detailed):
- If packet fields are incomplete for any slide, regenerate only missing rows and revalidate packet completeness.
- If operator marks any card as not-ready, keep dispatch blocked and return only unresolved card numbers + required next action.

Return one compact receipt with: stage, status, artifacts_written, validator_results, gate_decision, next_action.

---

## 7) Dispatch + Export + Sort Verification (Single Operation)

Marcus, dispatch Gary for RUN_ID [RUN_ID] only if all checks are true:
- diagram inputs are dispatch-ready: tracked/default mode provides local preintegration PNGs plus `site_repo_url` for managed staging, or HTTPS image URLs validate as image content
- no unresolved literal-visual blockers
- envelope READY
- singular mode preserved
- theme selection confirmed and mapped
- resolved theme + parameter set carried in payload

Double-dispatch behavior:
- If `DOUBLE_DISPATCH: true`, Gary dispatches **twice** per slide (variant A and variant B) using different theme or parameter configurations as specified in the envelope.
- Both dispatch cycles must complete and produce valid exports before proceeding.
- Write variant-B outputs with `-B` suffix: `gary-dispatch-result-B.json`, `gary-dispatch-run-log-B.json`, `gamma-export-B/...`.
- Run Vera G3 on **both** variant sets independently before proceeding to Prompt 7B.

Dispatch requirements:
- execute mixed-fidelity generation
- before publish/dispatch side effects, return a short pre-dispatch report listing literal-visual cards, local PNG paths, and target `site_repo_url`, then require explicit operator confirmation to proceed
- if local preintegration literal-visual assets are present, supply `site_repo_url` and require `literal_visual_publish.preintegration_ready=true` before Gate 2 review
- request exports and download
- non-null file_path for every output row
- normalize card order 1..N
- use a content-bearing slide payload for dispatch input; metadata-only fidelity payloads are invalid for production dispatch
- enforce literal-visual image-only payloads at dispatch input: literal-visual content entries are URL-only and must not include supporting prose

### Literal-visual dispatch behavior

Literal-visual slides use a **best-effort template → composite fallback** strategy:

1. **Single template attempt** (`_MAX_TEMPLATE_RETRIES = 1`): The Gamma template API dispatches with an anti-fade prompt ("at full opacity, not as background, not faded"). Gamma's AI classifies images as "accent" (cropped) or "background" (full-bleed) based on visual content — this classification is not controllable via the API (see `developers.gamma.app`).

2. **Fill validation**: `validate_visual_fill()` checks the exported PNG using edge-band sampling and content variance detection (`content_stddev`). Blank slides (stddev < 5) and faded slides (stddev < 25) are rejected.

3. **Composite fallback**: On validation failure, `_composite_full_bleed()` produces a deterministic 2400×1350 center-cropped slide from the preintegration PNG or, when no local PNG exists, by downloading from the hosted URL. Output flows through the same pipeline as template-generated slides.

4. **Provenance**: Each literal-visual output record includes `literal_visual_source` tracking how the slide was produced: `template` (Gamma rendered), `composite-preintegration` (local PNG composited), or `composite-download` (URL downloaded and composited).

**API constraints** (validated 2026-04-05 against `developers.gamma.app`):
- Template endpoint rejects `imageOptions.source` (HTTP 400). Template `g_gior6s13mvpk8ms` uses image source: `placeholder`.
- Images optimized for background classification (dense, photographic, minimal whitespace) render most reliably. See `skills/gamma-api-mastery/references/literal-visual-image-optimization.md`.

Required outputs under [BUNDLE_PATH]:
- `gary-dispatch-result.json` (includes `literal_visual_source` per slide)
- `gary-dispatch-run-log.json`
- `gary-theme-resolution.json` (unchanged carry-forward)
- `gamma-export/...`

Run internal Vera G3 before Gate 2.

Mandatory technical gate before Gate 2 approval:
- `py -3.13 skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py --payload [BUNDLE_PATH]/gary-dispatch-result.json`

If validator `status: fail`:
- report exact `errors`
- stop and remediate before user review

Required write:
- `[BUNDLE_PATH]/gary-dispatch-validation-result.json`

Required HIL review (Storyboard A):
- Generate storyboard from `[BUNDLE_PATH]/gary-dispatch-result.json`.
- Present manifest-derived summary and obtain explicit Gate 2 approval.
- For literal-visual slides, note the `literal_visual_source` provenance in the storyboard so the operator knows which slides came from Gamma vs composite.
- Persist `[BUNDLE_PATH]/authorized-storyboard.json` (fail closed on overwrite).

Then run explicit HIL Gate 2 (user approval on Gary slides).

Fallback (detailed):
- If validator fails:
  - classify failure bucket: path completeness, source_ref completeness, sequence integrity, contract payload shape
  - include one repair path per bucket
  - rerun validator and include before/after receipts
- If literal-visual slides used composite fallback:
  - verify composite output is acceptable (center-crop may differ from intended framing)
  - operator may regenerate the source image with optimized attributes and re-dispatch

Only after explicit Gate 2 approval may Marcus proceed to Prompt 7B (if double-dispatch) or Prompt 8 (if single dispatch).

---

## 7B) Variant Selection Gate (Double-Dispatch Only)

> **This prompt is skipped when `DOUBLE_DISPATCH` is false.**

Marcus, run variant selection for RUN_ID [RUN_ID].

### Preconditions

- Both variant A and variant B dispatch results exist and passed Vera G3.
- Storyboard A (from Prompt 7) has been approved for the primary variant.
- Variant B exports are complete with valid file_paths.

### Selection storyboard

Generate a **paired-thumbnail selection storyboard**:
- For each slide, display variant A (left) and variant B (right) side by side.
- Include slide number, fidelity class, and `literal_visual_source` provenance for each variant.
- Provide a per-slide selection control (A or B) for the operator.

The operator reviews both variants per slide and selects the stronger treatment.

### Required write

- `[BUNDLE_PATH]/variant-selection.json` containing:
  - run_id
  - timestamp
  - per-slide entries: `{ slide_number, selected_variant: "A" | "B", reason (optional) }`
  - operator confirmation flag

### Gate rule

- Prompt 8 is blocked until `variant-selection.json` is written and operator confirmation is recorded.
- If operator requests re-dispatch for any slide, return to Prompt 7 for the specified slides only.

### Fallback (detailed)

- If variant B dispatch failed for some slides, present only variant A for those slides (auto-select A) and note the fallback in `variant-selection.json`.
- If operator cannot decide, allow "defer" per slide — deferred slides block Prompt 8 until resolved.

Return one compact receipt with: stage, status, artifacts_written, validator_results, gate_decision, next_action.

---

## 8) Irene Pass 2 — Dual-Channel Narration with Inline Perception

Marcus, delegate Irene Pass 2 for RUN_ID [RUN_ID].

### Pre-delegation checks

Proceed only if all are true:
- card sequence strictly ascending 1..N
- file_path populated for all cards
- source_ref present for all cards
- envelope + run log + dispatch result consistent
- theme-resolution artifact consistent with dispatch log
- if `literal_visual_publish` is present, treat as provenance only; narration grounds on approved local slide PNGs in `gary_slide_output`
- if `literal_visual_source` is present on any slide, note the provenance (`template`, `composite-preintegration`, or `composite-download`) — all three sources produce valid slide PNGs for narration grounding

### Delegation

Inputs for this step:
- Gary slide output: `[BUNDLE_PATH]/gary-dispatch-result.json`
- Source bundle: `[BUNDLE_PATH]/extracted.md`
- Operator directives: `[BUNDLE_PATH]/operator-directives.md`
- Irene Pass 1: `[BUNDLE_PATH]/irene-pass1.md`
- If `DOUBLE_DISPATCH: true`: variant selections from `[BUNDLE_PATH]/variant-selection.json`

Double-dispatch input resolution:
- When `DOUBLE_DISPATCH: true`, build a merged slide output by selecting per-slide from variant A (`gary-dispatch-result.json`) or variant B (`gary-dispatch-result-B.json`) according to `variant-selection.json`.
- The merged set becomes `gary_slide_output` for Irene.

Delegate Irene Pass 2 with `gary_slide_output`.
Use `gary_slide_output` as source-of-truth for order and visual paths.

Irene generates `perception_artifacts` inline during Pass 2:
- For each slide PNG, Irene reads the image and emits a perception artifact as a side-effect of writing the narration segment.
- Perception artifacts follow the canonical schema from `sensory-bridges/bridge_utils.py`.
- The `png_to_agent.py` bridge is a schema wrapper — the LLM agent does the actual visual reading.

### Dual-channel grounding protocol

Irene writes each narration segment using two channels simultaneously:

1. **Slide channel** — what is visually on screen (perceived inline from the slide PNG).
2. **Source channel** — the extraction content anchored by `source_ref` for each slide, filtered by operator directives.

The balance between channels is governed by the slide's fidelity class, configured in:
- `state/config/narration-grounding-profiles.yaml` (per-fidelity channel balance)
- `state/config/narration-script-parameters.yaml` (script-wide style knobs)

Per-fidelity defaults:
- **creative** (`stance: explain-behind`): Source is primary. Narration teaches the content behind the atmospheric visual. Min 1 substantive source claim per segment.
- **literal-text** (`stance: read-along`): Slide is primary. Narration paraphrases visible text in conversational language. Source confirms accuracy.
- **literal-visual** (`stance: walk-through`): Slide is primary and image-only on-screen. Narration carries the explanatory/support text while walking through the visual, with at least 1 source-backed insight.

Script-level parameters (from narration-script-parameters.yaml):
- `narration_density` — target WPM and words-per-slide bounds
- `slide_echo` — verbatim | paraphrase | inspired (per-fidelity overridable)
- `visual_narration` — deictic references, description depth, visual silence policy
- `terminology_treatment` — inline glossing strategy and domain filter
- `pedagogical_bridging` — transition style between segments
- `engagement_stance` — narrator posture, direct address, rhetorical questions
- `source_depth` — how deep into extraction material per fidelity class
- `pronunciation_sensitivity` — flagging policy for ElevenLabs downstream

### Required outputs
- `[BUNDLE_PATH]/narration-script.md`
- `[BUNDLE_PATH]/segment-manifest.yaml`
- `[BUNDLE_PATH]/perception-artifacts.json` (emitted inline, one entry per slide)

### Required segment fields
- id
- gary_card_number
- gary_slide_id
- visual_file
- narration_text
- duration_estimate_seconds
- source_ref

### Post-Pass-2 completeness validation

After Irene completes Pass 2, run the handoff validator:
- `py -3.13 skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py --envelope [BUNDLE_PATH]/pass2-envelope.json`

This confirms:
- perception_artifacts present and aligned 1:1 with Gary slide_ids
- card sequence integrity preserved
- file_path and source_ref populated for all cards

If validator `status: fail`:
- output exact missing fields by segment id
- patch missing perception_artifacts or manifest fields
- rerun validator and return clean receipt

### Post-Pass-2 quality gate

Run internal Vera G4 after Pass 2.
- G4-01 through G4-06: existing deterministic + agentic checks.
- **G4-07 (Source depth utilization):** For creative slides, verify narration incorporates at least one substantive claim from source_ref anchors beyond what is visible on the slide PNG. Uses perception_artifacts as visual baseline.
- If G4 critical: stop and remediate.
- If G4 non-critical (including G4-07 high-severity): report and continue with explicit acknowledgment.
- If G4-07 fails, check `narration-grounding-profiles.yaml` alignment before re-delegating Irene — the failure may be a config issue, not a writing issue.

Required HIL review (Storyboard B, before audio/script finalization):
- Regenerate storyboard with script context using:
  - Gary payload: `[BUNDLE_PATH]/gary-dispatch-result.json`
  - Segment manifest: `[BUNDLE_PATH]/segment-manifest.yaml`
- Present manifest-derived summary for slide+script alignment review.
- Require explicit operator approval before downstream audio/script finalization (for example ElevenLabs generation).

Fallback (detailed):
- If handoff validator fails:
  - output exact missing fields by segment id
  - generate or attach missing perception_artifacts before re-delegation
  - patch manifest/script only where missing
  - rerun Pass 2 handoff validator and return clean receipt
- If Vera G4 fails on G4-07:
  - identify which creative slides lack source depth
  - show the source_ref anchor content vs. the narration text
  - redraft only the affected segments with `stance: explain-behind` reinforced

---

## Mandatory Receipts Per Stage (compact)

Require Marcus to emit a compact receipt for each prompt:
- stage
- status (pass | warn | fail)
- artifacts_written
- validator_results
- gate_decision
- next_action

This keeps verbosity controlled while preserving enough detail to recover if quality drifts.
