# Story 13.3: Segment Manifest Visual Reference Enrichment & Downstream QA

**Epic:** 13 — Visual-Aware Irene Pass 2 Scripting
**Status:** backlog
**Sprint key:** `13-3-segment-manifest-visual-references`
**Added:** 2026-04-05
**Depends on:** Story 13.2 (visual reference injection)

## Summary

Each segment in the manifest gains structured `visual_references` linking narration cues to perceived visual elements, enabling downstream fidelity verification by Vera G4 and Quinn-R.

## Goals

1. Extend segment manifest schema with `visual_references[]` per segment.
2. Enable Vera G4 to validate narration-to-visual alignment.
3. Enable Quinn-R to flag narration referencing non-existent visual elements.
4. Update Compositor assembly guide with visual reference cues.

## Key Files

- `skills/bmad-agent-content-creator/references/template-segment-manifest.md` — manifest schema
- `skills/bmad-agent-fidelity-assessor/SKILL.md` — Vera G4 extension
- `skills/bmad-agent-quality-reviewer/SKILL.md` — Quinn-R visual reference validation
- `skills/compositor/SKILL.md` — assembly guide visual reference cues

## Acceptance Criteria

1. Each segment gains `visual_references: [{element, location_on_slide, narration_cue, perception_source}]`.
2. `element` identifies what is referenced (e.g., "comparison timeline").
3. `location_on_slide` provides spatial description (e.g., "left panel").
4. `narration_cue` contains the exact narration phrase that references it.
5. `perception_source` references the perception artifact entry.
6. Vera G4 (narration vs slides) extended to validate visual references correspond to perceived elements.
7. Quinn-R can flag narration referencing visual elements not found in perception artifacts.
8. Compositor assembly guide includes visual reference cues for human assemblers.
