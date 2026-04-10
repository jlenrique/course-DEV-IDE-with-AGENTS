# Story 12.3: Selection Storyboard

**Epic:** 12 — Double-Dispatch Gamma Slide Selection
**Status:** backlog
**Sprint key:** `12-3-selection-storyboard`
**Added:** 2026-04-05
**Depends on:** Story 12.2 (parallel fidelity review)

## Summary

Extend the storyboard run-view to present side-by-side variant comparisons with quality scores, enabling the user to select the winning slide per position. Includes a full-deck sequential preview for visual flow verification after individual selections.

## Goals

1. Side-by-side comparison layout for variant pairs at legible scale.
2. Quality scores (Vera + Quinn-R) visible per variant.
3. Selection tracking with running tally and confirmation gate.
4. Full-deck sequential preview of chosen slides in presentation order.

## Key Files

- `skills/gamma-api-mastery/scripts/generate_storyboard.py` — storyboard generator extension
- `skills/gamma-api-mastery/scripts/write_authorized_storyboard.py` — authorization extension
- SB.1 storyboard infrastructure (manifest, HTML projection)

## Acceptance Criteria

1. Paired variants (A/B) displayed side-by-side per slide position at legible scale.
2. Quality scores (Vera + Quinn-R) visible per variant.
3. User selects exactly one winner per position (all positions must be selected before confirmation).
4. Running tally shows selection progress ("Selected: 7/12").
5. After all selections, a full-deck sequential preview shows chosen slides in presentation order for visual flow check.
6. User can revise selections during preview before final confirmation.
7. Selection metadata persisted: `{slide_id, selected_variant, rejected_variant, selection_timestamp}`.

## Party Mode Consensus (2026-04-05)

- Full-deck preview is the key feature — visual flow between consecutive slides matters.
- Preview shows slides at legible scale in presentation order, not thumbnails.
- Exactly one winner per position, no "keep both."
