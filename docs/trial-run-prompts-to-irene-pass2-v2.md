# Trial Prompt Pack v2: Marcus -> Irene Pass 2 Gate

Purpose: reduce ad-hoc recovery and reliably reach Irene Pass 2 handoff.

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
7. Run this command and report JSON result fields: `overall_status`, failed checks (if any), and `one_step_repair`.
  - `py -3.13 -m scripts.utilities.venv_health_check`

If `overall_status` is `fail`, stop immediately and ask for explicit approval before any ingestion or delegation.

Rules for this run:
- Contract-native delegation only.
- If required data is missing, ask one targeted clarification and stop.
- No ad-hoc helper scripts for production ingestion.
- Do not create new protocol docs.

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
- downstream_consumers: Irene, Gary, Vera, Quinn-R
- extraction_pathway
- expected confidence
- known risks

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

If any fail: provide 2 remediation options and stop.

If all pass: prepare Irene packet optimized for concise, engaging deck quality:
- normalized concept map
- CLO-ranked opportunities
- conflict/ambiguity notes
- source anchors for every recommendation

Write/update:
- irene-packet.md

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
- exactly 2 high-fidelity instructional graphics in scope
- required Gary envelope readiness check

Required machine artifacts under [BUNDLE_PATH]:
- g2-slide-brief.md
- gary-fidelity-slides.json
- gary-diagram-cards.json
- gary-theme-resolution.json
- gary-outbound-envelope.yaml
- pre-dispatch-package-gary.md

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
- card_number
- slide_id
- visual file_path
- narration
- duration estimate
- source_ref

If any handoff requirement is missing, stop and report exact missing fields.
