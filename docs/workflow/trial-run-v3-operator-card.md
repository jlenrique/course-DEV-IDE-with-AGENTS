# Trial Run v3 Operator Card (Initial Attempt)

Use this card during the first live trial run to Irene Pass 2.

Primary prompt pack:
- `docs/trial-run-prompts-to-irene-pass2-v3.md`

Contracts and validators:
- `docs/workflow/trial-run-pass2-artifacts-contract.md`
- `skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py`
- `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`

---

## A) Run Setup (once)

Set values:
- RUN_ID
- LESSON_SLUG
- BUNDLE_PATH
- PRIMARY_SOURCE_FILE
- OPTIONAL_CONTEXT_ASSETS
- THEME_SELECTION
- THEME_PARAMSET_KEY

Operator rule:
- Do not change run constants mid-run.

---

## B) Gate Checklist (go/no-go)

1. Prompt 1: Preflight
- Run:
  - `py -3.13 -m scripts.utilities.app_session_readiness --with-preflight --format json`
  - `py -3.13 -m scripts.utilities.venv_health_check`
- Require both `overall_status = pass`.
- Write `preflight-results.json`.
- Go/no-go: no go on any warn/fail.

2. Prompt 2: Source authority map
- Confirm direct/indirect consumer fields are present.
- Go/no-go: no go until approved.

3. Prompt 3: Ingestion evidence
- Confirm artifacts:
  - `extracted.md`, `metadata.json`, `ingestion-evidence.md`
- Go/no-go: no go if planning-critical confidence medium/low without spot-check approval.

4. Prompt 4: Ingestion quality + G0
- Confirm `preflight-results.json` pass state rechecked.
- Confirm `irene-packet.md` section order is valid.
- Run/record G0 receipt.
- Go/no-go: no go if any fail.

5. Prompt 5: Irene Pass 1 + G1/G2
- Confirm one mode per slide.
- Confirm literal-visual spec cards are complete.
- Run/record G1 and G2 receipts.
- Go/no-go: no go until Gate 1 approval.

6. Prompt 6: Pre-dispatch package
- Confirm required machine artifacts exist:
  - `g2-slide-brief.md`
  - `gary-fidelity-slides.json`
  - `gary-diagram-cards.json`
  - `gary-theme-resolution.json`
  - `gary-outbound-envelope.yaml`
  - `pre-dispatch-package-gary.md`
- Go/no-go: no go until approved.

7. Prompt 7: Dispatch + Gate 2
- Confirm outputs:
  - `gary-dispatch-result.json`
  - `gary-dispatch-run-log.json`
  - `gamma-export/...`
- Run G3.
- Run strict validator:
  - `py -3.13 skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py --payload [BUNDLE_PATH]/gary-dispatch-result.json`
- Save validator output:
  - `gary-dispatch-validation-result.json`
- Go/no-go: no go if validator `status=fail` or G3 fail.
- Then explicit Gate 2 approval.

8. Prompt 8: Irene Pass 2 handoff
- Confirm preconditions:
  - order 1..N, file_path present, source_ref present, artifacts consistent
- Delegate Irene Pass 2.
- Validate handoff envelope:
  - `py -3.13 skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py --envelope <pass2-envelope.json>`
- Run G4.
- Go/no-go: no go downstream if G4 critical findings.

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
- `ingestion-evidence.md`
- fidelity receipts (G0-G4)
- `gary-dispatch-validation-result.json`
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
