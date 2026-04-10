# Story 12.5: Marcus Run Mode Integration for Double-Dispatch

**Epic:** 12 — Double-Dispatch Gamma Slide Selection
**Status:** backlog
**Sprint key:** `12-5-marcus-double-dispatch-integration`
**Added:** 2026-04-05
**Depends on:** Stories 12.1–12.4

## Summary

Wire double-dispatch into Marcus's run orchestration and run-constants.yaml parameter management. Marcus adjusts the workflow when double-dispatch is active: Gary dispatches 2x, parallel review, selection storyboard gate, then Irene Pass 2.

## Goals

1. Marcus recognizes `double_dispatch: true` and adjusts workflow accordingly.
2. Run progress reporting reflects 2x generation timing.
3. Cost estimates account for 2x Gamma credits.
4. Pre-flight check validates double-dispatch compatibility.
5. Ad-hoc mode supports double-dispatch.

## Key Files

- `skills/bmad-agent-marcus/SKILL.md` — workflow variant logic
- `skills/bmad-agent-marcus/references/` — workflow management, delegation references
- `skills/production-coordination/` — run mode, cost estimation
- `skills/pre-flight-check/` — double-dispatch compatibility check

## Acceptance Criteria

1. Marcus recognizes `double_dispatch: true` in run-constants and adjusts workflow: Gary 2x → parallel review → selection storyboard gate → Irene Pass 2.
2. Run progress reporting accounts for dual-dispatch timing (estimated 2x generation time).
3. Run cost estimate reflects 2x Gamma credits when double-dispatch is active.
4. Pre-flight check validates double-dispatch compatibility (sufficient API credits, template supports re-dispatch).
5. Ad-hoc mode supports double-dispatch (same flag, same workflow).
