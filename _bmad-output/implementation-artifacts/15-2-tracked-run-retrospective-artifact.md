# Story 15.2: Tracked-Run Retrospective Artifact

**Epic:** 15 — Learning & Compound Intelligence
**Status:** backlog
**Sprint key:** `15-2-tracked-run-retrospective-artifact`
**Added:** 2026-04-06
**Depends on:** Story 15.1 (learning event capture — retrospective reads from the per-run learning ledger).

## Summary

Build an automated post-run retrospective generator that analyzes learning events from a completed tracked run and produces a structured retrospective artifact. The retrospective identifies successes, failures, root causes, corrections, and per-specialist learning recommendations. It also classifies each finding as a deterministic policy candidate, specialist guidance, or one-off note.

## Goals

1. Automated retrospective from learning event data.
2. Success/failure/correction analysis with origin tracing.
3. Per-specialist learning recommendations.
4. Finding classification: deterministic policy vs. specialist calibration vs. one-off.
5. Retrospective template for consistency.
6. Integration into Marcus's run reporting.

## Existing Infrastructure To Build On

- `scripts/utilities/learning_event_capture.py` (Story 15.1) — learning event ledger as primary input
- Production intelligence reporting from Story 4-4 — existing run report structure
- `skills/production-coordination/` — run lifecycle, stage tracking
- `skills/bmad-agent-marcus/` — run reporting references, end-of-run protocol
- Existing retrospective patterns in sprint planning (epic retrospectives in sprint-status.yaml)
- `_bmad-output/implementation-artifacts/epic-12-13-retro-2026-04-05.md` — retrospective format example

## Key Files

- `scripts/utilities/run_retrospective.py` — new: retrospective generator
- `state/config/retrospective-template.md` — new: template for consistent structure
- Run directory `{run_dir}/retrospective.md` — new: per-run retrospective output
- `skills/bmad-agent-marcus/` — update: reference retrospective generation in end-of-run protocol

## Acceptance Criteria

1. Retrospective generator reads `{run_dir}/learning-events.yaml` and produces `{run_dir}/retrospective.md`.
2. Retrospective contains:
   - successes: first-pass approvals, clean handoffs (grouped by gate)
   - failures: revisions, waivers, circuit breaks (grouped by gate and specialist)
   - origin tracing: per failure, where it originated vs. where detected
   - corrections: what fixed each issue
   - per-specialist learning recommendations: what each agent should learn from this run
   - finding classification: deterministic policy candidate / specialist guidance / one-off note
3. Retrospective template at `state/config/retrospective-template.md` defines section structure.
4. Marcus references retrospective in the run's final report (production intelligence reporting integration).
5. Retrospective can be generated on-demand for any completed run with a learning event ledger.
6. Unit tests: retrospective generation from synthetic event data, origin tracing accuracy, classification logic.
