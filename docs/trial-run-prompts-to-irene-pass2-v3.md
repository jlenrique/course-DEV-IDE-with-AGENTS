# Trial Prompt Pack v3: Marcus -> Irene Pass 2 Gate

Status:
- Current default prompt pack for trial runs to Irene Pass 2.

Purpose: run a reliable, auditable trial from source ingestion through Irene Pass 2 with stronger fallback detail when output quality is uneven.

Design intent:
- Keep explicit user approvals minimal: Gate 1 and Gate 2.
- Keep Vera fidelity checks internal, but always return concise receipts.
- Use deterministic stop rules so weak outputs cannot drift downstream.
- Provide a detailed fallback path for each stage if the first response misses the sweet spot.

This v3 pack supersedes v2 for trial runs but keeps the same artifact and gate contracts.

Primary contract references:
- `docs/workflow/trial-run-pass2-artifacts-contract.md`
- `state/config/fidelity-contracts/` (G0-G4)

---

## Run Constants (set once)

- RUN_ID: C1-M1-PRES-ADHOC-20260330
- LESSON_SLUG: apc-c1m1-tejal-2026030-demo
- BUNDLE_PATH: course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-20260330-demo
- PRIMARY_SOURCE_FILE: C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS\course-content\courses\APC C1-M1 Tejal 2026-03-29.pdf
- OPTIONAL_CONTEXT_ASSETS: C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS\course-content\courses\APC Content Roadmap.jpg
- THEME_SELECTION: hil-2026-apc-nejal-A
- THEME_PARAMSET_KEY: hil-2026-apc-nejal-A

---

## 1) Activation + Preflight Contract Gate

Ask Marcus to return:
1. Active identity and role.
2. Execution mode and quality preset.
3. Contracts/schemas enforced this run.
4. Required fields checked before delegation.
5. One refusal rule for non-contract delegation.
6. Toolchain status (Source Wrangler, sensory bridges, Gamma auth/API, Python runtime).

Required commands:
- `py -3.13 -m scripts.utilities.app_session_readiness --with-preflight --format json`
- `py -3.13 -m scripts.utilities.venv_health_check`

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

---

## 2) Source Authority Map Before Ingestion

Require one row per source with:
- source_id
- source_type
- authority_level (primary|framing-only|excluded)
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

---

## 3) Ingestion Execution + Evidence Log

Require Source Wrangler official pathways only.

Required artifacts under bundle:
- `extracted.md`
- `metadata.json`
- `ingestion-evidence.md`

`ingestion-evidence.md` must include required columns/footer from the contract.

Confidence handling rule:
- If an official bridge or Source Wrangler extraction records source confidence inside `extracted.md`, inherit that confidence into `ingestion-evidence.md` unless you have explicit contrary evidence.
- A `high` confidence note with limited caveats (for example, minor wording variance on smallest labels) is cautionary, not blocking.

Confidence consistency validator:
- Run `py -3.13 skills/bmad-agent-marcus/scripts/validate-source-bundle-confidence.py --bundle-dir [BUNDLE_PATH]` after writing `extracted.md`, `metadata.json`, and `ingestion-evidence.md`.
- If the validator fails, stop and correct the confidence drift before continuing.

Fallback (detailed):
- If any planning-critical section confidence is medium/low:
  - produce anchor-level spot-check list
  - mark planning readiness as conditional/blocked
  - stop and request directed correction before continuing

---

## 4) Ingestion Quality Gate + Irene Packet

Require pass/fail by source on:
- completeness
- readability
- anchorability
- provenance quality
- planning usability
- fidelity usability

Precondition:
- Verify `preflight-results.json` exists and both preflight gates passed.

If all pass, create:
- `irene-packet.md` in required section order from contract.

Then run internal Vera G0 and return receipt:
- verdict: pass|warn|fail
- critical findings
- remediation target

Gate interpretation rule:
- Do not downgrade a source from `high` to `medium/low` in Prompt 4 unless the gate records explicit evidence for the downgrade.
- A `high` confidence source with non-blocking caveats can still pass planning usability and fidelity usability.
- If a Prompt 4 receipt is written to disk, re-run `py -3.13 skills/bmad-agent-marcus/scripts/validate-source-bundle-confidence.py --bundle-dir [BUNDLE_PATH] --receipt [BUNDLE_PATH]/ingestion-quality-gate-receipt.md` before finalizing the gate decision.

Fallback (detailed):
- If any dimension fails or G0 fails:
  - provide 2 remediation options
  - include precise source anchors affected
  - stop until corrected artifacts are produced and rechecked

---

## 5) Irene Pass 1 Structure + Gate 1 Fidelity

Marcus, proceed to Prompt 5 for the active trial run.

Use the active run context from this session, not the stale demo constants in the prompt pack header.

Active run context:
- RUN_ID: C1-M1-PRES-ADHOC-20260330B
- LESSON_SLUG: apc-c1m1-tejal-20260329
- BUNDLE_PATH: course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-20260329
- PRIMARY_SOURCE_FILE: - C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS\course-content\courses\APC C1-M1 Tejal 2026-03-29.pdf
- OPTIONAL_CONTEXT_ASSETS: C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS\course-content\courses\APC Content Roadmap.jpg
- THEME_SELECTION: hil-2026-apc-nejal-A
- THEME_PARAMSET_KEY: hil-2026-apc-nejal-A

Inputs for this step:
- Irene packet: irene-packet.md
- Source bundle: extracted.md
- Source metadata: metadata.json
- Prompt 4 receipt: ingestion-quality-gate-receipt.md

Requirements:

Create irene-pass1.md with exact structure:
- executive summary
- slide plan table
- literal support plan
- risks and tradeoffs
- Gate 1 decision line
- 
Enforce hard constraints:
- exactly one mode per slide
- no mixed-mode labels
- full literal-visual spec card for each literal-visual slide

Before Gate 1 approval, run internal Vera gates:
- G1: lesson plan vs source bundle
- G2: slide brief vs lesson plan

If G1 or G2 fail:
include omission, invention, and alteration findings
include minimal patch targets in Irene output
rerun only the failed gate(s)
return one consolidated compact receipt

If G1 and G2 pass:
write irene-pass1.md under the active bundle directory
return a compact receipt with:
stage
status
artifacts_written
validator_results
gate_decision
next_action
Do not advance to Prompt 6 automatically.
Stop after producing irene-pass1.md and the compact receipt.

## 6) Gate 1 Approved -> Pre-Dispatch Package Build (No Send)

Prompt 6

Marcus, proceed to Prompt 6 for the active trial run.

Use the active run context from this session, not the stale demo constants in the prompt pack header.

Active run context:

RUN_ID: C1-M1-PRES-ADHOC-20260330B
LESSON_SLUG: apc-c1m1-tejal-20260329
BUNDLE_PATH: course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-20260329
PRIMARY_SOURCE_FILE: C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS\course-content\courses\APC C1-M1 Tejal 2026-03-29.pdf
OPTIONAL_CONTEXT_ASSETS: C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS\course-content\courses\APC Content Roadmap.jpg
THEME_SELECTION: hil-2026-apc-nejal-A
THEME_PARAMSET_KEY: hil-2026-apc-nejal-A
Precondition for this step:

Gate 1 must be approved for the active run.
Use the active Prompt 5 outputs, not any demo bundle.
Inputs for this step:

Source bundle: extracted.md
Irene packet: irene-packet.md
Irene Pass 1: course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-20260329/irene-pass1.md
Task:
Build the pre-dispatch package for Gary and stop before dispatch.

Required package sections:

claim-to-source fidelity matrix
literal candidate list and synthesis zones
final per-slide singular modes
creative + literal queue mapping
diagram card mapping
theme resolution block
all high-fidelity instructional graphics identified (minimum 2 in scope)
Gary envelope readiness check
Required machine artifacts to write under the active bundle:

g2-slide-brief.md
gary-slide-content.json
gary-fidelity-slides.json
gary-diagram-cards.json
gary-theme-resolution.json
gary-outbound-envelope.yaml
pre-dispatch-package-gary.md
Contract rules:

Follow trial-run-pass2-artifacts-contract.md exactly.
g2-slide-brief.md must be derived from irene-pass1.md and must not introduce new pedagogical content.
gary-slide-content.json must contain one content-bearing row per slide with fields: slide_number, content, source_ref.
Each slide must preserve exactly one mode: creative, literal-text, or literal-visual.
gary-fidelity-slides.json slide_number values must be unique and strictly increasing.
gary-diagram-cards.json must include only literal-visual cards that actually require hosted image handling.
gary-theme-resolution.json must freeze:
requested_theme_key
resolved_theme_key
resolved_parameter_set
mapping_source
mapping_version
user_confirmation
gary-outbound-envelope.yaml must carry forward theme_resolution and fidelity_per_slide unchanged from the machine artifacts.
If any artifact fails contract rules:

return contract violation list by file and field
regenerate only the failed artifact(s)
revalidate
stop and wait for approval
Return one compact receipt with:

stage
status
artifacts_written
validator_results
gate_decision
next_action
Do not dispatch to Gary in this step.
Stop after writing the pre-dispatch package and compact receipt.

## 7) Dispatch + Export + Sort Verification (Single Operation)

Dispatch only if all checks are true:
- diagram URLs validated as image content
- no unresolved literal-visual blockers
- envelope READY
- singular mode preserved
- theme selection confirmed and mapped
- resolved theme + parameter set carried in payload

Dispatch requirements:
- execute mixed-fidelity generation
- request exports and download
- non-null file_path for every output row
- normalize card order 1..N
- use a content-bearing slide payload for dispatch input; metadata-only fidelity payloads are invalid for production dispatch

Required outputs:
- `gary-dispatch-result.json`
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

Then run explicit HIL Gate 2 (user approval).

Fallback (detailed):
- If validator fails:
  - classify failure bucket: path completeness, source_ref completeness, sequence integrity, contract payload shape
  - include one repair path per bucket
  - rerun validator and include before/after receipts

---

## 8) Irene Pass 2 Handoff Gate

Proceed only if all are true:
- card sequence strictly ascending 1..N
- file_path populated for all cards
- source_ref present for all cards
- envelope + run log + dispatch result consistent
- theme-resolution artifact consistent with dispatch log

Delegate Irene Pass 2 with gary_slide_output as source-of-truth for order and visual paths.

Required outputs:
- `narration-script.md`
- `segment-manifest.yaml`

Required segment fields:
- id
- gary_card_number
- gary_slide_id
- visual_file
- narration_text
- duration_estimate_seconds
- source_ref

Run internal Vera G4 after Pass 2.
- If G4 critical: stop and remediate.
- If G4 non-critical: report and continue with explicit acknowledgment.

Fallback (detailed):
- If handoff fails validation:
  - output exact missing fields by segment id
  - patch manifest/script only where missing
  - rerun Pass 2 handoff validator and return clean receipt

---

## Mandatory Receipts Per Stage (compact)

Require Marcus to emit a compact receipt for each prompt:
- stage
- status (pass|warn|fail)
- artifacts_written
- validator_results
- gate_decision
- next_action

This keeps verbosity controlled while preserving enough detail to recover if quality drifts.
