# Story 12.4: Winner Forwarding & Provenance Archive

**Epic:** 12 — Double-Dispatch Gamma Slide Selection
**Status:** backlog
**Sprint key:** `12-4-winner-forwarding-provenance-archive`
**Added:** 2026-04-05
**Depends on:** Story 12.3 (selection storyboard)

## Summary

Selected winners are promoted into the canonical `gary_slide_output` array for downstream consumption. Rejected variants are archived with full provenance. Irene sees only clean, confirmed slides.

## Goals

1. Promote selected slides to canonical `gary_slide_output` with `selected: true`.
2. Archive rejected variants with full metadata.
3. Generate `perception_artifacts` only for winning slides.
4. Ensure Irene's context envelope has no variant distinction.

## Key Files

- `skills/gamma-api-mastery/scripts/gamma_operations.py` — winner promotion logic
- `skills/bmad-agent-content-creator/SKILL.md` — Irene envelope contract (no change expected)
- Run directory structure: `{run_dir}/archived_variants/`

## Acceptance Criteria

1. After selection confirmation, `gary_slide_output` contains only winner slides with `selected: true`.
2. Rejected variants moved to `{run_dir}/archived_variants/` with full metadata.
3. Context envelope for Irene Pass 2 contains only selected slides — no variant A/B distinction visible to Irene.
4. `perception_artifacts` generated only for winning slides (no wasted sensory bridge calls on rejected variants).
5. Archive includes: variant PNGs, quality scores, selection metadata, timestamps.
6. Storyboard archive section shows selection history for audit trail.

## Party Mode Consensus (2026-04-05)

- Irene receives only winners — losing variants are archived, not forwarded.
- This keeps Irene's cognitive load focused on scripting for confirmed visuals.
