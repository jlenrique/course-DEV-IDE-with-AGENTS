# Story 13.2: Visual Reference Injection in Narration Scripts

**Epic:** 13 — Visual-Aware Irene Pass 2 Scripting
**Status:** done
**Sprint key:** `13-2-visual-reference-injection`
**Added:** 2026-04-05
**Validated:** 2026-04-05
**Depends on:** Story 13.1 (mandatory perception contract — done)

## Story

As a content architect,
I want narration scripts to explicitly reference specific visual elements on each slide,
So that learners are guided through the visuals rather than hearing generic commentary.

## Acceptance Criteria

**Given** confirmed `perception_artifacts` exist for all slides (Story 13.1 contract)
**When** Irene writes narration for a slide
**Then** `narration-script-parameters.yaml` parameter `visual_references_per_slide: int` (default: 2) controls reference count
**And** narration includes exactly `visual_references_per_slide` explicit references to perceived visual elements (±1 tolerance)
**And** references are natural language integrated into narration flow ("As you can see in the comparison chart on the right..." not "Reference 1: comparison chart")
**And** each reference is grounded in a specific element from `perception_artifacts` — traceable
**And** references complement (not duplicate) slide content — narrate the insight, reference the visual
**And** narration script template is updated with `visual_references[]` metadata per segment
**And** unit tests validate reference count compliance and traceability to perception artifacts

## Tasks / Subtasks

- [ ] Task 1: Add `visual_references_per_slide` to narration-script-parameters.yaml (AC: 1)
  - [ ] 1.1: Add parameter in `visual_narration` section (default: 2, tolerance: 1)
- [ ] Task 2: Create `visual_reference_injector.py` script (AC: 2-5)
  - [ ] 2.1: `extract_visual_references(perception_artifact, count)` — selects best visual elements from perception
  - [ ] 2.2: `validate_reference_count(references, target, tolerance)` — checks ±1 compliance
  - [ ] 2.3: `build_visual_reference_metadata(references, perception_source)` — structured metadata per reference
  - [ ] 2.4: `validate_references_traceable(references, perception_artifacts)` — traceability check
- [ ] Task 3: Update narration script template (AC: 6)
  - [ ] 3.1: Add `visual_references[]` metadata field per segment in template
- [ ] Task 4: Update Irene SKILL.md (AC: all)
  - [ ] 4.1: Reference visual_reference_injector in Pass 2 Step 2 (narration writing)
  - [ ] 4.2: Add VR capability code to capabilities table
- [ ] Task 5: Write tests (AC: 7)
  - [ ] 5.1: Test reference extraction from perception with varying element counts
  - [ ] 5.2: Test count compliance (exact, +1, -1, out-of-tolerance)
  - [ ] 5.3: Test traceability — every reference maps to a perception element
  - [ ] 5.4: Test metadata structure matches expected schema
  - [ ] 5.5: Test with zero visual elements (empty perception)
  - [ ] 5.6: Test parameter loading from narration-script-parameters.yaml

## Dev Notes

### Existing Infrastructure (DO NOT DUPLICATE)

- **`narration-script-parameters.yaml`** section 3 (`visual_narration`) already has `deictic_references: moderate` and `description_depth: identify`. Add `visual_references_per_slide` and `tolerance` here — do NOT add to `run-constants.yaml` (Party Mode consensus: narration style param, not pipeline config).
- **`perception_contract.py`** (Story 13.1): Provides perception artifacts with `visual_elements[]` containing `{type, description, position}` per element. These are the source for reference extraction.
- **`template-narration-script.md`**: Already has per-segment structure with `[SEGMENT: seg-XX]` markers. Add `visual_references[]` metadata alongside existing `Stage Directions` block.
- **`template-segment-manifest.md`**: Story 13.3 will add `visual_references[]` to manifest. This story only needs narration template changes.

### Visual Reference Design

References should feel like a good lecturer pointing at the screen:
- "As you can see in the comparison chart on the right..." (GOOD — natural, deictic)
- "Notice how the timeline on the left spans three decades..." (GOOD — guides attention)
- "Reference 1: comparison chart" (BAD — annotation, not narration)
- "The slide shows a chart" (BAD — describes slide structure, not content insight)

Each reference must:
1. Name a specific visual element from `perception_artifacts[].visual_elements[]`
2. Include its spatial context (position from perception: "on the right", "in the center")
3. Narrate an insight about it, not just identify it

### Parameter Location

```yaml
# In narration-script-parameters.yaml, section 3 (visual_narration):
visual_narration:
  deictic_references: moderate
  description_depth: identify
  visual_silence_permitted: true
  visual_references_per_slide: 2     # NEW (Story 13.2)
  visual_references_tolerance: 1     # NEW (Story 13.2)
```

### Cross-Story Context

- Story 13.3 will add `visual_references[]` to the segment manifest schema for downstream QA.
- Vera G4 extension (Story 13.3) will validate references correspond to perceived elements.
- The `visual_references[]` metadata this story produces becomes input for 13.3.

### Project Structure Notes

- New script: `skills/bmad-agent-content-creator/scripts/visual_reference_injector.py`
- New test: `skills/bmad-agent-content-creator/scripts/tests/test_visual_reference_injector.py`
- Modified: `state/config/narration-script-parameters.yaml` (section 3)
- Modified: `skills/bmad-agent-content-creator/references/template-narration-script.md`
- Modified: `skills/bmad-agent-content-creator/SKILL.md`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 13, Story 13.2]
- [Source: state/config/narration-script-parameters.yaml#visual_narration]
- [Source: skills/bmad-agent-content-creator/scripts/perception_contract.py]
- [Source: skills/bmad-agent-content-creator/references/template-narration-script.md]
- [Source: skills/sensory-bridges/references/perception-schema.md#Image response fields]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (1M context)

### Debug Log References

### Completion Notes List

- Party Mode consensus: `visual_references_per_slide` goes in `narration-script-parameters.yaml` (not `run-constants.yaml`)
- Code review: 1 edge case caught and fixed (non-dict artifact in traceability check), clean review after fix
- 28 new tests + 39 Story 13.1 tests + 243 main suite all passing

### File List

- skills/bmad-agent-content-creator/scripts/visual_reference_injector.py (NEW)
- skills/bmad-agent-content-creator/scripts/tests/test_visual_reference_injector.py (NEW)
- state/config/narration-script-parameters.yaml (MODIFIED — visual_references_per_slide, tolerance)
- skills/bmad-agent-content-creator/references/template-narration-script.md (MODIFIED — visual_references[] metadata)
- skills/bmad-agent-content-creator/SKILL.md (MODIFIED — VR capability, Step 2 references)
- skills/bmad-agent-content-creator/scripts/tests/conftest.py (MODIFIED — register new module)
