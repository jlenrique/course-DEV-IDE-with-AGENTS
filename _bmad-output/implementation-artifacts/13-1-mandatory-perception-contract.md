# Story 13.1: Mandatory Perception Contract for Irene Pass 2

**Epic:** 13 — Visual-Aware Irene Pass 2 Scripting
**Status:** done
**Sprint key:** `13-1-mandatory-perception-contract`
**Added:** 2026-04-05
**Validated:** 2026-04-05
**Depends on:** Epic 12 (soft). Hard dependency on sensory bridges skill (Epic 2A — complete).

## Story

As a content architect,
I want Irene's Pass 2 to require perception artifacts as first-class input,
So that every narration script is grounded in confirmed visual understanding of the slides.

## Acceptance Criteria

**Given** Irene Pass 2 is invoked with a context envelope
**When** activation begins
**Then** Irene validates `perception_artifacts` presence in the context envelope
**And** if absent, Irene invokes image sensory bridge on each slide PNG in `gary_slide_output` and generates `perception_artifacts` inline
**And** perception confirmation is logged per slide: "I see Slide N shows [description]. Confidence: HIGH/MEDIUM/LOW"
**And** LOW-confidence slides trigger automatic re-perception (one retry with different bridge parameters)
**And** if still LOW after retry, Irene flags to Marcus for decision (proceed with caveated narration or escalate to user)
**And** perception is confirmed before any narration writing begins

## Tasks / Subtasks

- [ ] Task 1: Update Irene SKILL.md Pass 2 contract (AC: all)
  - [ ] 1.1: Add mandatory `perception_artifacts` validation at Pass 2 entry
  - [ ] 1.2: Document inline generation fallback when perception absent
  - [ ] 1.3: Add perception confirmation output format requirement
  - [ ] 1.4: Add LOW-confidence retry and Marcus escalation behavior
- [ ] Task 2: Create `perception_contract.py` script (AC: 1-4)
  - [ ] 2.1: `validate_perception_presence(envelope)` — checks perception_artifacts in envelope
  - [ ] 2.2: `generate_inline_perception(gary_slide_output, gate, run_id)` — invokes image bridge per slide
  - [ ] 2.3: `retry_low_confidence(slide, perception_result)` — one retry with adjusted parameters
  - [ ] 2.4: `build_perception_confirmation(slide_num, perception_result)` — structured confirmation output
  - [ ] 2.5: `check_escalation_needed(perception_results)` — identifies persistent LOW slides for Marcus
- [ ] Task 3: Update existing validator (AC: 1-2)
  - [ ] 3.1: Verify `validate-irene-pass2-handoff.py` compatibility with inline-generated perception
  - [ ] 3.2: Update validator docstring to reflect Story 13.1 contract (mandatory, not just validated post-hoc)
- [ ] Task 4: Write tests (AC: all)
  - [ ] 4.1: Test perception present — passes validation, no inline generation
  - [ ] 4.2: Test perception absent — triggers inline generation via image bridge
  - [ ] 4.3: Test HIGH/MEDIUM confidence — proceeds without retry
  - [ ] 4.4: Test LOW confidence — triggers exactly one retry
  - [ ] 4.5: Test persistent LOW after retry — generates Marcus escalation payload
  - [ ] 4.6: Test perception confirmation output format matches protocol
  - [ ] 4.7: Test all perception confirmed before narration output (ordering invariant)
  - [ ] 4.8: Regression: existing `test-validate-irene-pass2-handoff.py` still passes
- [ ] Task 5: Update Irene Pass 2 references (AC: 3, 5)
  - [ ] 5.1: Update `template-narration-script.md` header to reference perception grounding
  - [ ] 5.2: Update Irene init.md if perception contract affects agent initialization

## Dev Notes

### Existing Infrastructure (DO NOT DUPLICATE)

- **`validate-irene-pass2-handoff.py`** (Story 11.3): Already requires both `gary_slide_output` and `perception_artifacts` as REQUIRED_PASS2_FIELDS. Runs *post*-Pass 2 to confirm completeness. Story 13.1 adds *pre*-narration enforcement *within* Irene's behavior itself. The two are complementary — do not merge or replace.
- **`bridge_utils.perceive()`**: Top-level dispatcher for all modalities. Supports run-scoped caching via `PerceptionCache`. Use this for inline generation — do not create a parallel image analysis path.
- **`png_to_agent.analyze_image()`**: Schema wrapper only — the LLM does actual vision analysis, then calls this to format the result into canonical perception schema. In automated/script context, callers pass pre-computed `extracted_text`, `layout_description`, `visual_elements` etc.
- **Perception cache**: `bridge_utils.perceive()` has `run_id` + `use_cache` params. Inline perception should use caching to avoid re-perceiving the same slide if retried or re-run.

### Image Bridge Usage Pattern

The image bridge is NOT an automated image analyzer. The workflow is:
1. Agent (Irene) reads slide PNG via LLM vision capability
2. Agent extracts text, layout, visual elements from what it sees
3. Agent calls `analyze_image()` with those extracted values
4. `analyze_image()` wraps them in canonical perception schema
5. Result is a structured `perception_artifacts` entry

For Story 13.1, the "inline generation" path means Irene perceives each slide, formats via `analyze_image()`, and stores results in the envelope before writing narration.

### Confidence Rubric (Image Modality)

| Level | Criteria |
|-------|----------|
| **HIGH** | All text blocks extracted ≥95% confidence; layout unambiguous; all visual elements identifiable |
| **MEDIUM** | Text 80-95% OR layout ambiguous OR ≥1 element unidentifiable |
| **LOW** | Text <80% OR layout unparseable OR image corrupt/blank |

Gate thresholds: Production=HIGH, Ad-hoc=MEDIUM, Regulated=HIGH.

### Universal Perception Protocol (Five Steps)

All agents must follow: Receive → Perceive → Confirm → Proceed → Escalate. Perception confirmation must be visible output (not silent). See `skills/sensory-bridges/references/perception-protocol.md`.

### Confirmation Output Format

```yaml
perception_confirmation:
  artifact: "{file path}"
  modality: "image"
  confidence: "{HIGH|MEDIUM|LOW}"
  summary: "{what Irene perceived — 1-3 sentences}"
  gate: "G4"
  action: "{proceeding|escalating}"
```

### Party Mode Consensus (2026-04-05)

- LOW-confidence escalation goes to Marcus, not user — Marcus decides whether to proceed or escalate.
- This keeps the pipeline flowing without unnecessary user interruption.

### Cross-Story Context

Story 13.2 (Visual Reference Injection) depends on 13.1's perception artifacts being available and well-structured. The `visual_elements` list in perception output must be rich enough for 13.2 to extract specific visual references for narration. Design the inline perception to populate `visual_elements` thoroughly — each element with `type`, `description`, and `position`.

### Project Structure Notes

- New script: `skills/bmad-agent-content-creator/scripts/perception_contract.py`
- New test: `skills/bmad-agent-content-creator/scripts/tests/test_perception_contract.py`
- Modified: `skills/bmad-agent-content-creator/SKILL.md` (Pass 2 section, ~lines 89-96)
- Verified unchanged: `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`
- Verified unchanged: `skills/sensory-bridges/scripts/bridge_utils.py`
- Verified unchanged: `skills/sensory-bridges/scripts/png_to_agent.py`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 13, Story 13.1]
- [Source: skills/sensory-bridges/references/perception-protocol.md]
- [Source: skills/sensory-bridges/references/perception-schema.md]
- [Source: skills/sensory-bridges/references/confidence-rubric.md]
- [Source: skills/bmad-agent-content-creator/SKILL.md#Pass 2]
- [Source: skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py]
- [Source: _bmad-output/implementation-artifacts/11-3-irene-pass2-perception-grounding-enforcement.md]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (1M context)

### Debug Log References

### Completion Notes List

- Party Mode consensus: Option A (new script under Irene's skill dir, not extending Marcus validator or bridge_utils)
- Code review: 1 patch (type annotation), 5 dismissed. All ACs verified.
- 39 new tests + 11 existing validator tests regression-free + 243 main suite tests passing.

### File List

- skills/bmad-agent-content-creator/scripts/perception_contract.py (NEW)
- skills/bmad-agent-content-creator/scripts/tests/test_perception_contract.py (NEW)
- skills/bmad-agent-content-creator/scripts/tests/conftest.py (NEW)
- skills/bmad-agent-content-creator/scripts/__init__.py (NEW)
- skills/bmad-agent-content-creator/scripts/tests/__init__.py (NEW)
- skills/bmad-agent-content-creator/SKILL.md (MODIFIED — Pass 2 contract, PC capability)
- _bmad-output/implementation-artifacts/13-1-mandatory-perception-contract.md (MODIFIED)
- _bmad-output/implementation-artifacts/sprint-status.yaml (MODIFIED)
