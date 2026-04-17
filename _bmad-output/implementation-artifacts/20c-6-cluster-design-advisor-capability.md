# Story 20c-6: Cluster Design Advisor Capability

**Epic:** 20c - Cluster Intelligence Expansion & Iteration
**Status:** ready-for-dev
**Sprint key:** `20c-6-cluster-design-advisor-capability`
**Added:** 2026-04-12
**Depends on:** [20c-1-cluster-structure-template-library.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20c-1-cluster-structure-template-library.md), [20a-2-interstitial-brief-specification-standard.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-2-interstitial-brief-specification-standard.md)

## Story

As Irene (or as Pax delegating to a micro-level design capability),
I want a cluster design advisor that handles within-cluster decomposition — deciding exactly how to break a specific slide into interstitials given the selected template,
So that the interstitial brief quality is driven by deep analysis of the head slide's content structure, not generic brief templates.

## Context

Once Pax (or Irene) selects a template for a cluster (e.g., "deep-dive"), someone still needs to decide: what SPECIFIC aspects of this slide get surfaced in each interstitial? What's the isolation_target for the reveal? What gets simplified in the simplification? This micro-level design work is content-specific and requires understanding what's actually on the head slide.

This could be:
- A **capability within Irene's SKILL.md** (simplest, start here)
- A **capability within Pax's SKILL.md** (if Pax owns the full structural design)
- A **standalone agent** (if the decomposition logic becomes complex enough to justify its own context)

Start as a capability. Promote to agent if warranted by complexity.

## Acceptance Criteria

**AC-1: Content Decomposition Analysis**
Given a head slide brief and its selected cluster template, the advisor must:
- Identify all decomposable elements in the head (concepts, data points, visual elements, terminology)
- Rank elements by importance and visual decomposability
- Map the top N elements to the template's interstitial slots

**AC-2: Isolation Target Selection**
For each interstitial in the template sequence:
- Select the specific isolation_target from the head's decomposable elements
- Ensure isolation_targets are non-overlapping (each interstitial surfaces a different element)
- Ensure isolation_targets follow the template's narrative progression (establish → develop → tension → resolve)

**AC-3: Visual Register Determination**
For each interstitial:
- Determine what to REMOVE/SUPPRESS from the head (per 20a-2 specification)
- Specify the visual_register_constraint based on the interstitial_type
- Ensure the constraint is specific enough for Gary to execute (not "simplify the slide" but "remove the left panel, enlarge the right panel's key metric")

**AC-4: Content Scope Calibration**
For each interstitial:
- Set content_scope (1-2 sentences max of on-screen text)
- Calibrate narration_burden based on interstitial_type and content
- Ensure content_scope serves the isolation_target without introducing new concepts

**AC-5: Quality Self-Check**
Before outputting briefs, the advisor validates:
- Each brief is specific enough to pass G1.5 (isolation_target references actual head content)
- No brief says "continue the topic" or other vague language
- Isolation_targets cover the most important decomposable elements
- The brief sequence tells a coherent micro-story within the cluster

## Tasks / Subtasks

- [ ] Task 1: Implement content decomposition
  - [ ] 1.1: Parse head slide brief for decomposable elements
  - [ ] 1.2: Categorize elements (concept, data point, visual element, terminology, example)
  - [ ] 1.3: Rank by importance (LO-alignment, complexity, visual weight)
  - [ ] 1.4: Rank by decomposability (can this element stand alone as an interstitial?)

- [ ] Task 2: Implement isolation target mapping
  - [ ] 2.1: Map ranked elements to template interstitial slots
  - [ ] 2.2: Enforce non-overlap (each interstitial gets a distinct element)
  - [ ] 2.3: Respect template's narrative progression in element ordering

- [ ] Task 3: Implement visual register determination
  - [ ] 3.1: Generate specific visual_register_constraint per interstitial
  - [ ] 3.2: Use head brief's visual description to specify what to remove/suppress
  - [ ] 3.3: Cross-reference with Gary's constraint library (21-1) for type-specific rules

- [ ] Task 4: Implement quality self-check
  - [ ] 4.1: Validate brief specificity (no vague language)
  - [ ] 4.2: Validate isolation_target references actual head content
  - [ ] 4.3: Validate narrative coherence across the brief sequence

- [ ] Task 5: Integration and testing
  - [ ] 5.1: Integrate as Irene capability (or Pax capability)
  - [ ] 5.2: Run against C1-M1 slides — evaluate brief quality
  - [ ] 5.3: Compare advisor-generated briefs vs. ad-hoc Irene briefs from trial

## Dev Notes

### Start as Capability, Promote if Needed

Initial implementation: a reference document + prompt section in Irene's SKILL.md that guides decomposition. If the logic grows complex enough (e.g., different decomposition strategies per content type, visual analysis of head PNG for decomposition candidates), promote to standalone agent.

### Potential Agent Identity (if promoted)

| Field | Value |
|-------|-------|
| **name** | `bmad-agent-cluster-advisor` |
| **displayName** | Lens |
| **title** | Cluster Decomposition Specialist |
| **icon** | 🔍 |
| **role** | Analyzes slide content at the micro level and designs optimal interstitial decompositions |

Communication style: Precise, visual, detail-oriented. Speaks in terms of elements, focal points, visual weight, and isolation. Thinks like a photographer composing shots from a scene.

## References

- [interstitial-brief-specification.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/interstitial-brief-specification.md) — Brief quality bar
- [21-1-visual-design-constraint-library.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/21-1-visual-design-constraint-library.md) — Gary's type-specific constraints
