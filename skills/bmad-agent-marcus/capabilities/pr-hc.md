---
name: production-readiness-health-check
code: PR-HC
description: (STUB) Run a production session health check independent of preflight; full impl deferred to story 26-10.
script_module: scripts.marcus_capabilities.pr_hc
schema_path: skills/bmad-agent-marcus/capabilities/schemas/pr_hc.yaml
full_or_stub: stub
---

# PR-HC — Health Check (stub)

## When to invoke

**Currently stubbed.** Registered in the capability registry with pinned contracts and behavioral placeholder tests (`xfail`). Full implementation scheduled for **story 26-10 — Marcus production-readiness full-impl follow-up**, after the first clean trial restart reveals which gaps actually hurt.

Planned invocation triggers (post-26-10):

- Operator opens a production shift and wants a quick "is everything alive" check distinct from the fuller preflight suite.
- MCP outage suspected; need to ping the health surface of each API Marcus delegates to.
- Operator asks: "Marcus, is the system healthy?" / "Quick health check?"

## Inputs (planned)

- `context.run_id` (optional) — correlate to open run.
- `args.scope` (str, default `session`) — `session` | `workspace` | `fleet` (planned).

## Procedure (current stub)

1. Invocation in either `summarize` or `execute` mode returns a canonical `NOT_YET_IMPLEMENTED` envelope (`ReturnEnvelope` with `status: error`, `errors: [{code: NOT_YET_IMPLEMENTED, ...}]`). Stubs are operator-observable per AC-B.3 — invisible stubs hide breakage.

## Outputs (planned)

Structured health report. Deferred.

## Gates / checkpoints

Stub does not gate any workflow.

## Examples

```
Operator: Marcus, quick health check.
Marcus (PR-HC): Health-check capability is registered but not yet
                implemented. Scheduled for story 26-10. For now I can
                run the full preflight via PR-PF if you want a readiness
                signal.
```
