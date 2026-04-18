---
name: production-readiness-preflight
code: PR-PF
description: Run the production preflight check against the session's run-constants; surface PASS/FAIL for operator before firing Prompt 1.
script_module: scripts.marcus_capabilities.pr_pf
schema_path: skills/bmad-agent-marcus/capabilities/schemas/pr_pf.yaml
full_or_stub: full
---

# PR-PF — Preflight

## When to invoke

Offer this capability whenever:

- The operator is about to fire **Prompt 1** on a trial or tracked production run.
- The operator returns from a break and is unsure whether preflight still passes (config drift, MCP outage).
- A prior gate flagged a readiness concern the operator wants to confirm cleared.

The operator can also ask directly: "Marcus, run preflight" / "Can you verify readiness?".

## Inputs

From invocation context:

- `context.run_id` (optional) — correlates to the run journal if a tracked run is open.
- `context.bundle_path` (optional) — enables `bundle_run_constants` validation against the frozen bundle instead of workspace defaults.

From invocation args (`Invocation.args`):

- `with_preflight` (bool, default true) — if false, readiness check only; preflight suite skipped.
- `json_only` (bool, default true) — underlying runner uses JSON output.

## Procedure

1. **Summarize mode.** Report what would be checked: readiness scope, preflight scope, target bundle, recent receipt status if known. No side-effects.
2. **Execute mode.** Invoke `python -m scripts.utilities.app_session_readiness --with-preflight [--json-only] [--bundle-dir <path>]` as a subprocess. Parse JSON output. Populate `ReturnEnvelope.result` with the readiness report and `landing_point` with bundle + manifest + sha256 pointers.
3. **On subprocess non-zero exit,** set `status: error` and populate `errors[]` with a code `PREFLIGHT_FAILED` entry carrying the underlying runner's summary. Do **not** let the exception cross the Marcus boundary (AC-C.3).

## Outputs / artifacts

- Structured `ReturnEnvelope` with `status, result, landing_point, errors, telemetry`.
- No filesystem writes from this capability itself — the underlying runner emits receipts to its canonical location.

## Gates / checkpoints

- This capability **replaces** the "Initialization Instructions" pre-prompt checklist operators used to run manually. Marcus now offers it at the natural landing point; operator approves via verbose posture.

## Examples

```
Marcus: I'll run preflight against the current session. Default bundle:
        apc-c1m1-tejal-20260418-motion (from run-constants.yaml).
        Last receipt: PASSED (2026-04-17 20:14).
        Recommendation: run it — we shipped scaffold v0.2 fixes since the
        last receipt and I'd like to re-verify.
        Proceed?
Operator: yes
Marcus: [invokes PR-PF in execute mode; reports PASS / FAIL with structured detail]
```
