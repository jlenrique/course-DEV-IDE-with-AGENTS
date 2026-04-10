# Story 16.1: Autonomy Evidence Baseline & Decision Framework

**Epic:** 16 — Bounded Autonomy Expansion
**Status:** backlog
**Sprint key:** `16-1-autonomy-evidence-baseline-decision-framework`
**Added:** 2026-04-06
**Depends on:** Epic 15 (hard — learning events, retrospectives, and feedback routing provide the evidence base). At least 3-5 tracked runs recommended for meaningful classification.

## Summary

Build a structured framework for classifying production decision points as `always-confirm`, `confirm-unless-routine`, or `auto-with-audit` based on evidence from tracked runs. Each classification cites specific run evidence. Marcus reads the framework to adjust checkpoint behavior. The framework is a living document updated after each condensation cycle.

## Goals

1. Decision-point inventory across the production pipeline.
2. Three-tier classification: always-confirm, confirm-unless-routine, auto-with-audit.
3. Evidence-based classification (run IDs, approval rates, revision counts).
4. Marcus integration for adaptive checkpoint behavior.
5. Operator override and reclassification capability.
6. Review cadence tied to pattern condensation (Story 15.5).

## Existing Infrastructure To Build On

- `scripts/utilities/learning_event_capture.py` (Story 15.1) — gate decision data
- `scripts/utilities/run_retrospective.py` (Story 15.2) — per-run success/failure analysis
- `scripts/utilities/pattern_condensation.py` (Story 15.5) — periodic review trigger
- `skills/bmad-agent-marcus/` — checkpoint choreography, run baton authority (Story 4A-1)
- `docs/lane-matrix.md` — judgment ownership boundaries
- Existing run-preset system: `explore`, `draft`, `production`, `regulated` — autonomy disabled for `regulated`
- `skills/production-coordination/` — stage definitions and gate coordination

## Key Files

- `state/config/autonomy-framework.yaml` — new: decision-point classifications with evidence
- `scripts/utilities/autonomy_framework.py` — new: classification query, evidence aggregation, update functions
- `skills/bmad-agent-marcus/` — update: reference autonomy framework in checkpoint logic

## Acceptance Criteria

1. Decision-point inventory covers all HIL gates and key operator-confirmation points in the production pipeline.
2. Each decision point classified as: `always-confirm` (high-risk/high-cost), `confirm-unless-routine` (low-risk when pattern matches), `auto-with-audit` (consistently approved without revision).
3. Each classification cites evidence: `{run_ids[], approval_count, revision_count, waiver_count, last_failure_run}`.
4. Framework stored in `state/config/autonomy-framework.yaml`.
5. `autonomy_framework.py` provides: `classify_decision(gate, context)` → `{classification, evidence_summary, confidence}`.
6. Marcus can read the framework to decide whether to pause for confirmation or proceed autonomously.
7. Operator can manually reclassify any decision point at any time (override persisted in the YAML).
8. Framework reviewed and updated after each pattern condensation cycle.
9. Autonomy behavior disabled entirely when `run_preset: regulated`.
10. Unit tests: classification logic, evidence aggregation, operator override, regulated-preset bypass.
