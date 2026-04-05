# Story 13.3: Segment Manifest Visual Reference Enrichment & Downstream QA

**Epic:** 13 — Visual-Aware Irene Pass 2 Scripting
**Status:** done
**Sprint key:** `13-3-segment-manifest-visual-references`
**Added:** 2026-04-05
**Validated:** 2026-04-05
**Depends on:** Story 13.2 (visual reference injection — done)

## Story

As a quality reviewer,
I want each segment in the manifest to carry structured visual references linking narration cues to perceived visual elements,
So that downstream fidelity verification can confirm narration-to-visual alignment.

## Acceptance Criteria

**Given** Irene has produced narration with visual references (Story 13.2)
**When** the segment manifest is generated
**Then** each segment gains `visual_references: [{element, location_on_slide, narration_cue, perception_source}]`
**And** `element` identifies what is referenced (e.g., "comparison timeline")
**And** `location_on_slide` provides spatial description (e.g., "left panel")
**And** `narration_cue` contains the exact narration phrase that references it
**And** `perception_source` references the perception artifact entry
**And** Vera G4 (narration vs slides) is extended to validate visual references correspond to perceived elements
**And** Quinn-R can flag narration referencing visual elements not found in perception artifacts
**And** Compositor assembly guide includes visual reference cues for human assemblers

## Tasks / Subtasks

- [ ] Task 1: Update segment manifest template schema (AC: 1-5)
  - [ ] 1.1: Add `visual_references[]` field to segment schema
  - [ ] 1.2: Document each sub-field: element, location_on_slide, narration_cue, perception_source
- [ ] Task 2: Create `manifest_visual_enrichment.py` script (AC: 1-5)
  - [ ] 2.1: `enrich_segment_with_visual_references(segment, slide_injection_result)` — merges visual ref metadata into manifest segment
  - [ ] 2.2: `enrich_manifest(segments, injection_results)` — bulk enrichment
  - [ ] 2.3: `validate_manifest_visual_references(segments, perception_artifacts)` — traceability check at manifest level
- [ ] Task 3: Update Vera G4 reference (AC: 6)
  - [ ] 3.1: Add visual reference validation criteria to Vera's G4 gate reference
- [ ] Task 4: Update Quinn-R reference (AC: 7)
  - [ ] 4.1: Add visual reference flagging to Quinn-R's review checklist
- [ ] Task 5: Update Compositor reference (AC: 8)
  - [ ] 5.1: Add visual reference cues to assembly guide template
- [ ] Task 6: Write tests (AC: all)
  - [ ] 6.1: Test single segment enrichment with visual references
  - [ ] 6.2: Test bulk manifest enrichment
  - [ ] 6.3: Test traceability validation passes with valid data
  - [ ] 6.4: Test traceability validation fails with orphaned references
  - [ ] 6.5: Test manifest validation with missing narration_cue
  - [ ] 6.6: Regression: all existing tests still pass

## Dev Notes

### Existing Infrastructure

- **`visual_reference_injector.py`** (Story 13.2): Produces per-slide `visual_references[]` metadata with `element`, `element_type`, `location_on_slide`, `perception_source_slide_id`, `perception_element_index`. This story adds `narration_cue` (the exact phrase from narration) and packages into manifest segments.
- **`template-segment-manifest.md`**: Current schema has no `visual_references` field. Add it alongside existing segment fields.
- **Vera G4 gate**: Currently validates narration script vs lesson plan + slides. Extension adds: "visual references in manifest correspond to perceived visual elements."
- **Quinn-R review**: Currently checks quality metrics. Extension adds: "flag narration referencing visual elements not found in perception."
- **Compositor**: Currently generates Descript Assembly Guide. Extension adds: visual reference cues as assembly notes for human editors.

### Schema Extension

```yaml
# Added to each segment in manifest.yaml:
visual_references:
  - element: string          # what is referenced (e.g., "comparison timeline")
    location_on_slide: string # spatial description (e.g., "left panel")
    narration_cue: string    # exact phrase from narration that references this
    perception_source: string # perception artifact slide_id
```

### Project Structure Notes

- New script: `skills/bmad-agent-content-creator/scripts/manifest_visual_enrichment.py`
- New test: `skills/bmad-agent-content-creator/scripts/tests/test_manifest_visual_enrichment.py`
- Modified: `skills/bmad-agent-content-creator/references/template-segment-manifest.md`
- Modified: `skills/bmad-agent-fidelity-assessor/SKILL.md` (G4 extension)
- Modified: `skills/bmad-agent-quality-reviewer/SKILL.md` (visual reference flagging)
- Modified: `skills/compositor/SKILL.md` (assembly guide visual cues)

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 13, Story 13.3]
- [Source: skills/bmad-agent-content-creator/scripts/visual_reference_injector.py]
- [Source: skills/bmad-agent-content-creator/references/template-segment-manifest.md]
- [Source: skills/bmad-agent-fidelity-assessor/SKILL.md#G4]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (1M context)

### Debug Log References

### Completion Notes List

- Code review: clean. No patch findings. All ACs verified.
- 17 new tests + 67 existing Story 13.1/13.2 tests + 273 main+Marcus tests all passing (357 total)
- Downstream references updated: Vera G4 (G4-08), Quinn-R (VR capability), Compositor (assembly guide visual cues)

### File List

- skills/bmad-agent-content-creator/scripts/manifest_visual_enrichment.py (NEW)
- skills/bmad-agent-content-creator/scripts/tests/test_manifest_visual_enrichment.py (NEW)
- skills/bmad-agent-content-creator/references/template-segment-manifest.md (MODIFIED — visual_references[] schema)
- skills/bmad-agent-content-creator/references/template-narration-script.md (MODIFIED — visual_references metadata block)
- skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md (MODIFIED — G4-08 visual reference traceability)
- skills/bmad-agent-quality-reviewer/SKILL.md (MODIFIED — VR capability)
- skills/compositor/references/assembly-guide-format.md (MODIFIED — visual reference cues)
- skills/bmad-agent-content-creator/scripts/tests/conftest.py (MODIFIED — register new module)
