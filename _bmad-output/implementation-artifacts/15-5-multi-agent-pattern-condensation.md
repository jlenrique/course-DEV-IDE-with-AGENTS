# Story 15.5: Multi-Agent Pattern Condensation

**Epic:** 15 — Learning & Compound Intelligence
**Status:** backlog
**Sprint key:** `15-5-multi-agent-pattern-condensation`
**Added:** 2026-04-06
**Depends on:** Story 15.3 (feedback routing populates sidecars with structured entries that condensation processes).

## Summary

Build a periodic condensation process that distills accumulated sidecar patterns across all agents into high-signal summaries, identifies contradictions and duplicates, and highlights candidates for promotion to deterministic policy. Prevents sidecar sprawl and memory fragmentation.

## Goals

1. Per-specialist condensation summaries.
2. Cross-agent contradiction and duplication detection.
3. Policy-promotion candidate identification.
4. Append-only safety: original chronology preserved.
5. Condensation cadence guidance.

## Existing Infrastructure To Build On

- `_bmad/memory/*/patterns.md` — 15 agent sidecars with pattern entries (varying population levels)
- `_bmad/memory/*/chronology.md` — session history entries
- `_bmad/memory/*/access-boundaries.md` — scope control
- `_bmad/memory/*/index.md` — sidecar context summaries
- Feedback routing (Story 15.3) — structured entries routed to sidecars
- `skills/app-maturity-audit/` — existing audit pattern (periodic assessment with structured output)
- `state/config/feedback-routing-rules.yaml` (Story 15.3) — routing rules that inform cross-agent analysis

## Key Files

- `scripts/utilities/pattern_condensation.py` — new: condensation engine
- `_bmad/memory/*/condensation-{date}.md` — new: per-specialist condensation output
- `reports/condensation/condensation-{date}.md` — new: cross-agent condensation summary

## Acceptance Criteria

1. Condensation reads all `patterns.md` entries across specified sidecars.
2. Per-specialist output includes: top recurring success patterns, top recurring failure patterns, patterns for deterministic policy promotion, patterns for specialist calibration retention, patterns to archive as one-off.
3. Cross-agent analysis identifies: contradictory lessons (e.g., Irene patterns that conflict with Gary patterns), duplicated learnings in multiple sidecars.
4. Policy-promotion section highlights candidates for hardening into deterministic validators or contracts.
5. Output written to `{sidecar}/condensation-{date}.md` per specialist and `reports/condensation/condensation-{date}.md` for cross-agent summary.
6. Original `chronology.md` and `patterns.md` entries are never deleted (append-only archive preserved).
7. Callable via `python -m scripts.utilities.pattern_condensation` with optional `--agents` filter.
8. Condensation recommended cadence: after every 3-5 tracked runs, or when sidecar patterns.md exceeds a configurable size threshold.
9. Unit tests: pattern grouping, contradiction detection, duplication detection, policy-promotion identification.
