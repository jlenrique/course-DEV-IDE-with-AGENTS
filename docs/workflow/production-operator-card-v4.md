# Production Run Operator Card (v4)

Use this card during tracked/production runs to Irene Pass 2.

Primary prompt pack:
- `docs/workflow/production-prompt-pack-v4.1.md`

Contracts and validators:
- `docs/workflow/trial-run-pass2-artifacts-contract.md`
- `skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py`
- `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`
- `skills/bmad-agent-marcus/scripts/validate-source-bundle-confidence.py` (loads `run-constants.yaml` when present)
- `python -m scripts.utilities.run_constants --bundle-dir <bundle>` (optional path verification: `--verify-paths`)

Session launcher:
- `docs/workflow/production-session-launcher.md`

VS Code users: use the same production session launcher prompt. VS Code tasks for preflight are defined in `.vscode/tasks.json` (`APP: Session Readiness + Preflight`).

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

Operator rule:
- Do not change run constants mid-run.
- Execution mode must be tracked/default for production runs.
- Persist accepted constants as **`run-constants.yaml`** in the bundle root (contract §1B); use `app_session_readiness --bundle-dir ...` during shift open if you want an automated alignment check.

---

## B) Gate Checklist (go/no-go)

### 1. Prompt 1: Preflight
- Run:
  - `py -3.13 -m scripts.utilities.app_session_readiness --with-preflight --format json`
  - `py -3.13 -m scripts.utilities.venv_health_check`
- Require both `overall_status = pass`.
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

### 5. Prompt 5: Irene Pass 1 + G1/G2
- Confirm one mode per slide.
- Confirm literal-visual spec cards are complete.
- Confirm operator directives are reflected in slide plan.
- Run/record G1 and G2 receipts.
- Go/no-go: no go until Gate 1 approval.

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
- Literal-visual dispatch uses **single-attempt template + composite fallback**:
  - `literal_visual_source: template` = Gamma rendered (best case)
  - `literal_visual_source: composite-preintegration` = local PNG composited
  - `literal_visual_source: composite-download` = URL downloaded and composited
  - All three produce valid 2400×1350 slide PNGs
- If composite fallback fired, verify the center-crop framing is acceptable for the specific image.
- Run G3.
- Run strict validator:
  - `py -3.13 skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py --payload [BUNDLE_PATH]/gary-dispatch-result.json`
- Save validator output:
  - `gary-dispatch-validation-result.json`
- Confirm Storyboard A artifacts and approval:
  - `storyboard/storyboard.json`
  - `storyboard/index.html`
  - `authorized-storyboard.json`
- Go/no-go: no go if validator `status=fail` or G3 fail.
- Then explicit Gate 2 approval.

### 7B. Prompt 7B: Variant Selection (double-dispatch only)
- **Skip if `DOUBLE_DISPATCH` is false.**
- Confirm paired-thumbnail selection storyboard presented to operator.
- Confirm per-slide A/B selection recorded in `variant-selection.json`.
- Confirm operator confirmation flag is set.
- Go/no-go: no go until all slides have a selected variant and operator confirms.

### 8. Prompt 8: Irene Pass 2 handoff
- Confirm preconditions:
  - order 1..N, file_path present, source_ref present, perception_artifacts aligned, artifacts consistent
- Delegate Irene Pass 2.
- Validate handoff envelope:
  - `py -3.13 skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py --envelope [BUNDLE_PATH]/pass2-envelope.json`
- Run G4.
- Go/no-go: no go downstream if G4 critical findings.
- Regenerate Storyboard B (slide + script context) and get explicit approval before downstream audio/script finalization.

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
- `gary-dispatch-validation-result.json`
- `literal-visual-operator-packet.md` (if literal-visual slides exist)
- `authorized-storyboard.json`
- Pass 2 handoff validator output
- final stage receipts per prompt

---

## E) Operator Exit Criteria (Irene Pass 2 ready)

Run is considered successful up to Pass 2 when:
- Gate 1 approved
- Gate 2 approved
- Gary dispatch validator passes
- Pass 2 handoff validator passes
- G4 has no critical findings
- Operator directives recorded and honored throughout
