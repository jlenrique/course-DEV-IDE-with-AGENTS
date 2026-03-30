# Trial Prompt Pack v2: Marcus -> Irene Pass 2 Gate

Status:
- Superseded as default trial-run prompt pack by `docs/trial-run-prompts-to-irene-pass2-v3.md`.
- Retained for historical traceability and comparison.

Purpose: reduce ad-hoc recovery and reliably reach Irene Pass 2 handoff.

Operating style for this pack:
- Vera fidelity gates are internal validation receipts Marcus summarizes conversationally.
- User-facing explicit approvals stay minimal: Gate 1 and Gate 2.
- If a fidelity gate fails, Marcus reports the remediation path in plain language and pauses.

Use these prompts in order. Replace values in brackets once at the top and keep them constant through the run.

## Run constants (set once)

- RUN_ID: [C1-M1-PRES-ADHOC-YYYYMMDD]
- LESSON_SLUG: [c1-m1-topic-slug]
- BUNDLE_PATH: [course-content/staging/ad-hoc/source-bundles/<bundle-folder>]
- PRIMARY_SOURCE_FILE: [absolute path to primary PDF]
- OPTIONAL_CONTEXT_ASSETS: [comma-separated list]
- THEME_SELECTION: [approved theme key for standard slides]
- THEME_PARAMSET_KEY: [mapped parameter-set key for selected theme]

---

## 1) Activation and preflight contract gate

Marcus, before any work, return an activation receipt for RUN_ID [RUN_ID]:

1. Active agent identity and role.
2. Execution mode and quality preset.
3. Contracts/schemas you will enforce this run (Irene + Gary envelopes).
4. Required fields you will validate before specialist dispatch.
5. One refusal rule if contract-native delegation is violated.
6. Toolchain preflight status for Source Wrangler, sensory-bridges, Gamma auth, and Python interpreter.
7. Run these commands and report JSON result fields.
  - Runtime + toolchain gate (authoritative):
    - `py -3.13 -m scripts.utilities.app_session_readiness --with-preflight --format json`
    - Report: `overall_status`, failed/warned checks, and per-tool readiness summary (Source Wrangler pathway dependencies, sensory-bridges dependencies, Gamma auth/API, Python runtime).
    - Timeout: 30s max. If timeout occurs, treat as `fail`.
  - Python environment guardrail (supplemental):
    - `py -3.13 -m scripts.utilities.venv_health_check`
    - Report: `overall_status`, failed checks (if any), and `one_step_repair`.
    - Timeout: 30s max. If timeout occurs, treat as `fail`.
8. Write/update `[BUNDLE_PATH]/preflight-results.json` containing run_id, timestamp, and both command outputs.

Gate triage rules:
- `overall_status = pass` is required for both gates.
- Any `warn` or `fail` status in either gate blocks progression.
- If blocked, provide one-step repair guidance and stop.

If either authoritative preflight or venv guardrail is not `overall_status = pass`, stop immediately and ask for explicit approval before any ingestion or delegation.

Rules for this run:
- Contract-native delegation only.
- If required data is missing, ask one targeted clarification and stop.
- No ad-hoc helper scripts for production ingestion.
- Do not create new protocol docs.
- Fidelity gate criteria source of truth: `state/config/fidelity-contracts/` (including `_schema.yaml` and gate-specific contracts).

Wait for explicit GO.

---

## 2) Source authority map before ingestion

Marcus, produce source authority and ingestion map for RUN_ID [RUN_ID].

Primary source:
- [PRIMARY_SOURCE_FILE]

Optional context:
- [OPTIONAL_CONTEXT_ASSETS]

For each source, return:
- source_id
- source_type
- authority_level: primary, framing-only, excluded
- downstream_consumers_direct
- downstream_consumers_indirect
- extraction_pathway
- expected confidence
- known risks

Use the canonical row contract in `docs/workflow/trial-run-pass2-artifacts-contract.md`.

Policy:
- Use Source Wrangler official pathways only.
- No ad-hoc extraction scripts.

Stop and wait for approval.

---

## 3) Ingestion execution with evidence log

Marcus, execute ingestion now using Source Wrangler official pathways only.

For each source return an evidence row with:
- source_id
- pathway_used
- extraction_status
- coverage_metric
- confidence
- bundle_location
- provenance_summary
- planning_readiness

Then write/update these artifacts under [BUNDLE_PATH]:
- extracted.md
- metadata.json
- ingestion-evidence.md

`ingestion-evidence.md` must follow the required columns and footer block in `docs/workflow/trial-run-pass2-artifacts-contract.md`.

Confidence handling rule:
- If an official bridge or Source Wrangler extraction records source confidence inside `extracted.md`, inherit that confidence into `ingestion-evidence.md` unless explicit contrary evidence is recorded.
- A `high` confidence note with limited caveats is cautionary, not blocking.

Confidence consistency validator:
- Run `py -3.13 skills/bmad-agent-marcus/scripts/validate-source-bundle-confidence.py --bundle-dir [BUNDLE_PATH]` after writing the bundle artifacts.
- If the validator fails, stop and correct the confidence drift before continuing.

If confidence is medium/low on any planning-critical section, list exact anchors for spot-check and stop.

---

## 4) Ingestion quality gate and Irene packet construction

Marcus, run ingestion quality gate and return pass/fail per source on:
- completeness
- readability
- anchorability
- provenance quality
- planning usability
- fidelity usability

Before evaluating ingestion quality, verify `[BUNDLE_PATH]/preflight-results.json` exists and contains PASS for both preflight gates from Prompt 1.
If missing or non-pass, stop and report the exact blocking check(s).

If any fail: provide 2 remediation options and stop.

If all pass: prepare Irene packet optimized for concise, engaging deck quality:
- normalized concept map
- CLO-ranked opportunities
- conflict/ambiguity notes
- source anchors for every recommendation

Write/update:
- irene-packet.md

`irene-packet.md` must follow the required section order in `docs/workflow/trial-run-pass2-artifacts-contract.md`.

Before moving to Irene Pass 1, run internal Vera G0 (source-bundle fidelity) using the canonical G0 contract and return:
- verdict: pass/warn/fail
- critical findings (if any)

Do not downgrade a source from `high` to `medium/low` at this gate without explicit evidence. A `high` confidence source with non-blocking caveats may still pass planning usability and fidelity usability.

If a Prompt 4 receipt is written to disk, re-run `py -3.13 skills/bmad-agent-marcus/scripts/validate-source-bundle-confidence.py --bundle-dir [BUNDLE_PATH] --receipt [BUNDLE_PATH]/ingestion-quality-gate-receipt.md` before finalizing the gate.
- remediation target (if blocked)

If G0 is fail: stop and remediate before continuing.

---

## 5) Irene Pass 1 output structure and literal spec strictness

Marcus, require Irene Pass 1 output in this exact structure:
- executive summary
- slide plan table
- literal support plan
- risks and tradeoffs
- Gate 1 decision line

Hard constraints:
- Exactly one mode per slide: creative, literal-text, literal-visual.
- No mixed-mode labels.
- For every literal-visual slide include a full spec card with:
  - graphic_id
  - slide_number
  - CLO served
  - exact labels/claims to preserve
  - source anchors
  - chart/diagram structure
  - prohibited embellishments
  - acceptance checks

Write/update:
- irene-pass1.md

Before Gate 1 approval, run internal Vera gate checks in order:
- G1: lesson plan vs source bundle
- G2: slide brief vs lesson plan

Return a single fidelity receipt with per-gate verdicts and blocking findings.
If either G1 or G2 fails, stop and remediate before any Gate 1 approval.

---

## 6) Gate 1 approved -> pre-dispatch package build (no send yet)

Marcus, after Gate 1 approval, build Gary pre-dispatch package and stop before dispatch.

Required package sections:
- claim-to-source fidelity matrix
- literal candidate list and synthesis zones
- final per-slide singular modes
- two-queue mapping: creative queue + literal queue
- diagram card mapping
- theme resolution block:
  - requested theme key
  - resolved parameter-set key
  - mapping source/version used
  - mismatch handling decision (stop/ask user)
- all high-fidelity instructional graphics identified in Irene's literal support plan, minimum 2 in scope
- required Gary envelope readiness check

Required machine artifacts under [BUNDLE_PATH]:
- g2-slide-brief.md
- gary-fidelity-slides.json
- gary-diagram-cards.json
- gary-theme-resolution.json
- gary-outbound-envelope.yaml
- pre-dispatch-package-gary.md

`g2-slide-brief.md` and `gary-fidelity-slides.json` must conform to `docs/workflow/trial-run-pass2-artifacts-contract.md`.
`g2-slide-brief.md` is a normalized derivative of `irene-pass1.md` and must not add new pedagogical claims.

Rules:
- gary-diagram-cards.json must use contract fields:
  - card_number
  - image_url
  - placement_note
  - required
- gary-theme-resolution.json must include:
  - requested_theme_key
  - resolved_theme_key
  - resolved_parameter_set
  - mapping_source
  - mapping_version
  - user_confirmation
- gary-outbound-envelope.yaml must include:
  - schema_version
  - exemplar_references
  - governance.allowed_outputs with gary_slide_output

Stop for approval.

---

## 7) Dispatch + export + sort verification (single operation)

Marcus, dispatch Gary only if all checks are true:
- diagram URLs validated and image content type confirmed
- no unresolved literal visual blockers
- envelope status READY
- singular mode per slide preserved
- theme selection confirmed by user and recorded
- selected theme mapped to valid parameter set
- resolved theme + parameter set included in outbound payload

Dispatch requirements:
- execute mixed-fidelity generation
- request export artifacts
- download artifacts
- produce non-null file_path for every gary_slide_output entry
- normalize ordering by card_number 1..N
- do not infer order from internal zip title cards

Required outputs under [BUNDLE_PATH]:
- gary-dispatch-result.json
- gary-dispatch-run-log.json
- gary-theme-resolution.json (carried forward unchanged from pre-dispatch)
- gamma-export/...

Return a concise execution receipt with:
- generation_ids
- calls_made
- card sequence
- count of non-null file_path entries
- resolved theme key + parameter-set key used

Before any Irene Pass 2 delegation, run internal Vera G3 (generated slides vs slide brief).
If G3 fails, stop and remediate before HIL Gate 2.

Before HIL Gate 2 approval, run strict Gary dispatch readiness validation via Marcus gate script:

`py -3.13 skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py --payload [BUNDLE_PATH]/gary-dispatch-result.json`

Validation must enforce:
- non-empty `file_path` and `source_ref` for every `gary_slide_output` row
- non-empty slide set (Gate 2 cannot review zero slides)
- contiguous `card_number` sequence `1..N`

If validation returns `status: fail`, report the exact `errors` list and stop for remediation.

Write/update:
- `[BUNDLE_PATH]/gary-dispatch-validation-result.json`

Then run explicit HIL Gate 2 review (user approval on Gary slides).
Only after explicit Gate 2 approval may Marcus proceed to Prompt 8.

---

## 8) Irene Pass 2 handoff gate

Marcus, if and only if all of these are true:
- card sequence strictly ascending 1..N
- file_path populated for all cards
- source_ref present for all cards
- envelope + run log + dispatch result mutually consistent
- theme-resolution artifact present and consistent with dispatch run log

Then prepare Irene Pass 2 handoff package and delegate Irene Pass 2.

Irene handoff must treat gary_slide_output as source-of-truth for order and visual paths.

Required Irene outputs:
- narration-script.md
- segment-manifest.yaml

Each segment in manifest must include:
- id
- gary_card_number
- gary_slide_id
- visual_file
- narration_text
- duration_estimate_seconds
- source_ref

If any handoff requirement is missing, stop and report exact missing fields.

After Irene returns Pass 2 outputs, run internal Vera G4 (narration script vs lesson plan + approved slides).
If G4 has critical findings, stop and remediate before downstream audio/video stages.
If G4 has non-critical findings, report them and proceed with explicit acknowledgment.
