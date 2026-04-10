# Story 15.4: Synergy Scorecard

**Epic:** 15 — Learning & Compound Intelligence
**Status:** backlog
**Sprint key:** `15-4-synergy-scorecard`
**Added:** 2026-04-06
**Depends on:** Story 15.1 (learning events as data source). Multiple tracked runs recommended for meaningful scoring.

## Summary

Build a synergy scorecard that measures handoff quality across the core pipeline by analyzing learning event data from completed runs. The scorecard operationalizes the concept of cross-agent synergy from the APP optimization audit into a repeatable measurement instrument.

## Goals

1. Score each core handoff on five quality dimensions.
2. Cover the seven core pipeline handoffs.
3. Support on-demand generation and trend comparison.
4. Integration with retrospective and Marcus run planning.

## Existing Infrastructure To Build On

- `scripts/utilities/learning_event_capture.py` (Story 15.1) — learning event data
- `scripts/utilities/run_retrospective.py` (Story 15.2) — retrospective findings feed scorecard
- `_bmad-output/implementation-artifacts/app-optimization-map-and-baseline-audit-2026-04-05.md` — synergy audit framework (Section C)
- `docs/lane-matrix.md` — handoff ownership map
- `skills/app-maturity-audit/` — existing maturity audit skill pattern (four-pillar protocol)
- `reports/` — existing report output directory pattern

## Key Files

- `scripts/utilities/synergy_scorecard.py` — new: scorecard generator
- `reports/synergy/scorecard-{date}.md` — new: generated scorecard reports
- `state/config/synergy-scorecard-config.yaml` — new: handoff definitions and scoring weights

## Acceptance Criteria

1. Scorecard scores each handoff on: completeness rate, downstream usability rate, first-pass acceptance, correction locality (near-source = good, 2-3 stages later = bad), repeated friction signatures.
2. Seven handoffs scored: Marcus→Irene, Irene→Gary, Gary→Irene Pass 2, Irene→Vera, Vera→Quinn-R, Quinn-R→Marcus/Human, manifest→compositor.
3. Scoring derives from learning event data across one or more specified runs.
4. Report saved to `reports/synergy/scorecard-{date}.md` with per-handoff scores and an aggregate synergy health indicator.
5. Trend comparison supported: when multiple scorecards exist, the report shows improvement/regression per handoff.
6. Callable on-demand via `python -m scripts.utilities.synergy_scorecard --runs <run_ids>` or as part of retrospective.
7. Marcus can reference scorecard when planning subsequent runs (read synergy health for weak handoff awareness).
8. Scorecard configuration in `state/config/synergy-scorecard-config.yaml` defines handoff names, scoring weights, and threshold levels (healthy/warning/critical).
9. Unit tests: scoring calculation, trend comparison, report formatting.
