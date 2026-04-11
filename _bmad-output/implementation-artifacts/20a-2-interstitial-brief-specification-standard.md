# Story 20a.2: Interstitial Brief Specification Standard

**Epic:** 20A - Irene Cluster Intelligence - Design & Specification
**Status:** ready-for-dev
**Sprint key:** `20a-2-interstitial-brief-specification-standard`
**Added:** 2026-04-11
**Validated:** 2026-04-11
**Depends on:** [20a-1-cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-1-cluster-decision-criteria.md), [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md)

## Story

As Irene,
I want a strict specification for interstitial briefs sent to Gary,
So that Gamma receives constrained, coherent instructions that preserve head-slide lineage instead of drifting into decorative new slides.

## Acceptance Criteria

**Given** clustered slide production depends on Irene's brief quality  
**When** Irene defines an interstitial for Gary  
**Then** every interstitial brief must specify:

- `interstitial_type`
- `isolation_target`
- `visual_register_constraint`
- `content_scope`
- `narration_burden`
- `relationship_to_head`

**And** each field must have a clear quality bar and a failure mode example  
**And** `isolation_target` must point to actual content already present in the head brief or head slide concept  
**And** the specification must make explicit that interstitials remove, isolate, enlarge, or simplify head content rather than introduce new imagery or concepts  
**And** the brief standard must include examples of strong versus weak interstitial instructions  
**And** the standard must be documented in Irene's references and positioned as the contract that later implementation and Gary dispatch work must honor

## Tasks / Subtasks

- [ ] Task 1: Define the interstitial brief contract fields (AC: 1-4)
  - [ ] 1.1: Define each required field with acceptable value shapes and intent
  - [ ] 1.2: Explain how each field constrains Gamma toward continuity with the head slide
  - [ ] 1.3: Explain what makes a brief too vague to use
- [ ] Task 2: Create a reusable reference standard for Irene (AC: 2-6)
  - [ ] 2.1: Add a new reference document under `skills/bmad-agent-content-creator/references/`
  - [ ] 2.2: Include pass/fail examples for each supported interstitial type
  - [ ] 2.3: Include at least one C1M1-oriented example showing how a head slide becomes a constrained interstitial brief
- [ ] Task 3: Wire the standard into Irene's operating guidance (AC: 5-6)
  - [ ] 3.1: Update [SKILL.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/SKILL.md) so future cluster-planning steps reference the new standard
  - [ ] 3.2: Update [delegation-protocol.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/delegation-protocol.md) only where Gary-facing brief structure intersects with Irene's broader delegation logic

## Dev Notes

### Scope Boundary

This story defines the **brief quality standard**. It does not yet implement:

- Gamma prompt templates
- Gary dispatch sequencing
- automatic coherence scoring
- re-dispatch handling
- cluster-aware narration

Those belong to Epics 21 and 23.

### Required Brief Fields

Use the field set from the planning artifact verbatim:

- `interstitial_type`
- `isolation_target`
- `visual_register_constraint`
- `content_scope`
- `narration_burden`
- `relationship_to_head`

The standard should explain the expected behavior of each:

- `interstitial_type`: which visual move this interstitial is making
- `isolation_target`: the exact element or sub-concept being surfaced
- `visual_register_constraint`: what must be removed, suppressed, or deemphasized
- `content_scope`: the maximum on-screen content burden
- `narration_burden`: how much meaning the visual versus narration should carry
- `relationship_to_head`: whether this slide zooms, isolates, simplifies, reframes, or rests relative to the head

### Quality Guardrails

- Briefs like "continue the topic" or "show the same concept differently" should fail explicitly.
- Briefs should bias toward removing or isolating head content, not adding new iconography or fresh conceptual material.
- The standard should protect against Gamma overproduction by making constraints legible and concrete.
- The human reviewer should be able to inspect a brief and predict what visual simplification or emphasis change it is asking for.

### C1M1 MVP Context

This standard is being built for the first three-cluster C1M1 proof. That means the examples should be practical and presentation-oriented, not abstract. The best examples will show:

- why a specific C1M1 head slide deserves an interstitial
- what exact element should be isolated or simplified
- what should disappear from the frame
- why the resulting interstitial would help Storyboard A pacing

### Previous Story Intelligence

- [20a-1-cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-1-cluster-decision-criteria.md) decides **which** slides cluster.
- This story decides **how** those chosen clusters are expressed tightly enough for Gary to execute them.
- [delegation-protocol.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/delegation-protocol.md) already shows how Irene structures writer briefs. Reuse that discipline: explicit fields, explicit intent, explicit constraints.

## Testing Requirements

- This is a design/reference story; validation is primarily document quality and internal consistency.
- If any helper code or schema examples are added for validation, keep tests narrow and run them via the repo venv.

## Project Structure Notes

- Likely new reference file:
  - `skills/bmad-agent-content-creator/references/interstitial-brief-specification.md`
- Likely modified files:
  - [SKILL.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/SKILL.md)
  - [delegation-protocol.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/delegation-protocol.md)

## References

- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md)
- [20a-1-cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-1-cluster-decision-criteria.md)
- [SKILL.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/SKILL.md)
- [delegation-protocol.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/delegation-protocol.md)

## Completion Status

Ultimate context engine analysis completed - Gary-facing interstitial brief specification story is ready for development.
