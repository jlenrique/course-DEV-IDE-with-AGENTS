# Story 12.2: Parallel Fidelity & Quality Review for Variant Pairs

**Epic:** 12 — Double-Dispatch Gamma Slide Selection
**Status:** backlog
**Sprint key:** `12-2-parallel-fidelity-quality-review`
**Added:** 2026-04-05
**Depends on:** Story 12.1 (dual-dispatch infrastructure)

## Summary

Both slide variants pass independently through Vera fidelity assessment and Quinn-R quality review before the user sees them. This ensures the selection storyboard presents pre-qualified options.

## Goals

1. Extend Vera G2-G3 to run independently on each variant.
2. Extend Quinn-R scoring to evaluate each variant against the slide brief.
3. Attach paired quality scores to each variant record.
4. Flag pairs where both variants fail fidelity thresholds.

## Key Files

- `skills/bmad-agent-fidelity-assessor/SKILL.md` — Vera G2-G3 variant handling
- `skills/bmad-agent-quality-reviewer/SKILL.md` — Quinn-R variant scoring
- `skills/gamma-api-mastery/scripts/gamma_operations.py` — variant record structure

## Acceptance Criteria

1. Vera runs G2-G3 fidelity checks on each variant independently.
2. Quinn-R scores each variant independently against the slide brief.
3. Quality scores attached to each variant record: `{variant, vera_score, quinn_score, findings[]}`.
4. Variants that fail fidelity thresholds are flagged but still presented (user may override).
5. If both variants fail, the pair is flagged as "needs re-dispatch or manual intervention."
6. No new fidelity gates introduced — existing G2-G3 logic extended, not duplicated.
