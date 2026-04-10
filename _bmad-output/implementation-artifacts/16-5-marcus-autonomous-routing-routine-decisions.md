# Story 16.5: Marcus Autonomous Routing for Routine Decisions

**Epic:** 16 — Bounded Autonomy Expansion
**Status:** backlog
**Sprint key:** `16-5-marcus-autonomous-routing-routine-decisions`
**Added:** 2026-04-06
**Depends on:** Story 16.1 (autonomy framework with decision classifications). Story 16.2 (shared governance validators ensure autonomous actions stay in-lane).

## Summary

Implement Marcus's ability to handle routine, low-risk decisions autonomously based on the autonomy framework classifications. For `confirm-unless-routine` decisions, Marcus proceeds automatically when context matches prior-approved patterns and notifies the operator. For `auto-with-audit` decisions, Marcus proceeds silently with audit trail. Operator can override, and the `regulated` preset disables all autonomy.

## Goals

1. Marcus reads autonomy framework to adjust checkpoint behavior.
2. Pattern matching for `confirm-unless-routine` decisions.
3. Audit logging for all autonomous decisions.
4. Operator override (in-run and persistent).
5. Retrospective integration: downstream failures after auto-decisions trigger reclassification.
6. Disabled entirely for `regulated` preset.

## Existing Infrastructure To Build On

- `state/config/autonomy-framework.yaml` (Story 16.1) — decision classifications
- `scripts/utilities/autonomy_framework.py` (Story 16.1) — classification query functions
- `scripts/utilities/governance_validator.py` (Story 16.2) — ensures autonomous actions respect governance
- `skills/bmad-agent-marcus/SKILL.md` — orchestrator checkpoint choreography
- `skills/bmad-agent-marcus/references/run-baton-authority.md` — baton authority contract (Story 4A-1)
- `skills/production-coordination/` — stage management and gate coordination
- Run preset system: `explore`, `draft`, `production`, `regulated`
- `scripts/utilities/learning_event_capture.py` (Story 15.1) — auto-decision events captured
- `scripts/utilities/run_retrospective.py` (Story 15.2) — auto-decision failure flagging

## Key Files

- `skills/bmad-agent-marcus/references/autonomy-protocol.md` — new: Marcus reference for autonomous behavior
- `scripts/utilities/autonomy_framework.py` (Story 16.1) — update: add pattern-matching helpers
- Run directory `{run_dir}/autonomy-log.yaml` — new: per-run log of all autonomous decisions

## Acceptance Criteria

1. `confirm-unless-routine`: Marcus proceeds automatically if current context matches a prior-approved pattern (same gate, same artifact type, same quality outcome in N prior runs). Operator notified: "Auto-approved Gate 1 — matches pattern from runs X, Y, Z."
2. `auto-with-audit`: Marcus proceeds automatically and logs decision to audit trail without interrupting the operator.
3. `always-confirm`: Marcus pauses and requests explicit operator confirmation (unchanged behavior).
4. Per-run autonomy log at `{run_dir}/autonomy-log.yaml` tracks: `{decision_point, classification, action_taken, pattern_cited, timestamp}`.
5. Operator override: "stop auto-approving [gate/decision]" during a run downgrades that decision to `always-confirm` for the remainder of the run.
6. Retrospective integration: if an auto-approved decision leads to a downstream failure, the retrospective (Story 15.2) flags it for reclassification in the autonomy framework.
7. Autonomy fully disabled when `run_preset: regulated` — all decisions treated as `always-confirm`.
8. Marcus autonomy protocol documented in new reference file.
9. Learning events (Story 15.1) capture auto-decision events with `event_type: auto_approved`.
10. Unit tests: pattern matching, classification lookup, operator override, regulated-preset bypass, audit log format.
