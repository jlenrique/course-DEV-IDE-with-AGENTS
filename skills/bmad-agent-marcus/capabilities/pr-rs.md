---
name: production-readiness-run-selection
code: PR-RS
description: (STUB) Determine whether a session is opening a new run or continuing one, and reconcile DB state; full impl deferred to story 26-10.
script_module: scripts.marcus_capabilities.pr_rs
schema_path: skills/bmad-agent-marcus/capabilities/schemas/pr_rs.yaml
full_or_stub: stub
---

# PR-RS — Run Selection (stub)

## When to invoke

**Currently stubbed.** Registered with pinned contracts; full implementation in **story 26-10**.

Planned invocation triggers (post-26-10):

- Operator opens a session and state/runtime SQLite has multiple rows in non-terminal status — which run is active? Marcus needs to help reconcile.
- Operator asks: "Are we starting a new run or continuing 20260415?" / "What's the active run?"
- A prior session left an orphaned stage (started, never completed/failed). The operator may want to cancel or resume.

This capability previously happened ad-hoc — at trial open on 2026-04-17, Marcus manually cancelled `C1-M1-PRES-20260409` and activated `C1-M1-PRES-20260415` inside the trial runbook. PR-RS formalizes that pattern.

## Inputs (planned)

- `args.action` (str, default `inspect`) — `inspect` | `start_new` | `continue` | `cancel_orphans`.
- `args.run_id` (str, optional) — target when `action != inspect`.

## Procedure (current stub)

1. Invocation in either mode returns canonical `NOT_YET_IMPLEMENTED` envelope. Stubs are operator-observable per AC-B.3.

## Outputs (planned)

Structured run-state inventory + proposed reconciliation plan. Deferred.

## Gates / checkpoints

Stub does not gate any workflow.

## Examples

```
Operator: Are we starting a new run or continuing?
Marcus (PR-RS): Run-selection capability is registered but not yet
                implemented. Scheduled for story 26-10. For now I can
                read state/runtime/ manually if you want me to walk
                through active runs — just ask.
```
