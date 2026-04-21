# Prompt Pack v4.2 Run Constants Schema Drift — Backlog Story Stub

**Opened:** 2026-04-17 (surfaced during APC C1-M1 Tejal trial Prompt 1 execution)
**Status:** backlog
**Severity:** Medium (documentation-vs-code drift; working-around path exists; new-operator trap)
**Owner routing:** Paige (tech writer) for doc repair; Winston (architect) if a dual-schema decision is entertained

## Problem

The v4.2 production prompt pack's "Run Constants" section (`docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` lines ~22-37) displays the run-constants fields UPPERCASE and flat:

```
- RUN_ID: C1-M1-PRES-...
- MOTION_BUDGET_MAX_CREDITS: 125
- MOTION_BUDGET_MODEL_PREFERENCE: pro
```

The validator (`scripts/utilities/run_constants.py:96-99`) performs case-sensitive `data.get("run_id")` and expects lowercase snake_case keys + nested `motion_budget:` block:

```yaml
run_id: C1-M1-PRES-...
motion_budget:
  max_credits: 125
  model_preference: pro
```

Prior working bundles (20260409, 20260406-motion) use the lowercase nested form — the canonical schema. The pack-doc uppercase presentation is presumably intended as operator-facing readability (looks like env vars) but is not marked as display-only, so an operator setting up from the pack alone follows the doc verbatim and hits validator fail at emit_preflight_receipt.

## Evidence

- Trial run 2026-04-17 Prompt 1 execution — Marcus halted when `emit_preflight_receipt.py` failed with "Missing or empty required string field: run_id"
- Prior runs succeeded because `run-constants.yaml` was copied from a prior bundle template rather than authored from the pack doc
- Runbook: `_bmad-output/implementation-artifacts/trial-run-c1m1-tejal-20260417.md` — "Marcus Prompt 1 execution: HALT on validator fail" section

## Options

**Option A (recommended): Fix the pack doc.** Rewrite the Run Constants section to show the canonical lowercase nested YAML form an operator should actually put in `run-constants.yaml`. Preserve operator ergonomics with a short comment per field if needed for clarity. Paige tech-writer task.

**Option B: Extend validator to accept uppercase.** Change `run_constants.py` to normalize keys before validation. Adds validator complexity; forks canonical schema across two accepted forms; doesn't close the doc-vs-code SSOT gap. Not recommended.

**Option C: Add a prominent "YAML key casing" note at the top of the Run Constants section** explaining that the uppercase display is for readability only and the file must use lowercase snake_case. Minimal change, preserves current doc aesthetics, closes the operator trap. Paige tech-writer task.

Recommend **Option A** outright, or **Option C** if the pack's readability-style is load-bearing for other reasons.

## Adjacent Audit Recommendation

Scribe flagged this for Audra's L1 catalog: a `format-capability-lockstep` check for **docs-vs-code schema**. Would compile schema claims from load-bearing docs (prompt packs, operator guides) and diff against validator schemas. Would have caught this before a trial run surfaced it.

Filed as a nested recommendation in `texas-visual-source-gap-backlog.md` (the same L1-drift check class covers both).

## Not In Scope

- Changing validator semantics (Option B withdrawn)
- Rewriting the pack's prose style (touch only the technical-schema presentation)

## Acceptance Hint (Draft for Story Open)

- Pack doc Run Constants section shows canonical lowercase nested YAML
- Validator unchanged (still case-sensitive lowercase-only)
- A fresh operator authoring `run-constants.yaml` from the pack alone → `emit_preflight_receipt.py` PASSES first try
