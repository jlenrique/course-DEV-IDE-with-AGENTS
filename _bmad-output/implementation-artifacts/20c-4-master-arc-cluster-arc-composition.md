# Story 20c-4: Master Arc / Cluster Arc Composition

**Epic:** 20c - Cluster Intelligence Expansion & Iteration
**Status:** ready-for-dev
**Sprint key:** `20c-4-master-arc-cluster-arc-composition`
**Added:** 2026-04-12
**Depends on:** [20c-2-content-aware-template-selection-logic.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20c-2-content-aware-template-selection-logic.md), [20a-3-cluster-narrative-arc-schema.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-3-cluster-narrative-arc-schema.md)

## Story

As Irene,
I want explicit composition rules for how the presentation's master narrative arc interweaves with individual cluster arcs,
So that the overall presentation feels like one coherent story with well-paced chapters, not a sequence of disconnected cluster mini-arcs.

## Context

Currently Irene sets a `narrative_arc` per cluster and a `master_behavioral_intent`. But there's no explicit model for how clusters compose into the presentation's larger narrative. A presentation with 5 clusters each running establish→develop→tension→resolve can feel repetitive — every cluster has the same emotional shape. The master arc should modulate how individual clusters play their role in the bigger story.

## Acceptance Criteria

**AC-1: Presentation Master Arc Definition**
Irene defines a master arc for the entire presentation:
- **Opening act** (first 20-25%): Orient, establish stakes, plant the hook
- **Development** (middle 50-60%): Build complexity, introduce tensions, layer evidence
- **Resolution** (final 20-25%): Synthesize, land meaning, call to action
- The master arc maps to Sophia's framework at the presentation level

**AC-2: Cluster Role Within Master Arc**
Each cluster has a role in the master arc, distinct from its internal positions:
- `arc_role: foundation` — early presentation, establishes concepts (pairs with deep-dive, framework-expose templates)
- `arc_role: escalation` — builds complexity, introduces tensions (pairs with contrast-pair, evidence-build)
- `arc_role: pivot` — major perspective shift or surprise (pairs with narrative-pivot)
- `arc_role: culmination` — peaks of insight or emotional weight (pairs with emotional-arc, zoom-and-return)
- `arc_role: landing` — synthesis and resolution (pairs with data-walkthrough for final evidence, or deep-dive for final framework)
- `arc_role: transition` — connecting tissue between major clusters (quick-punch, cognitive-reset)

**AC-3: Composition Rules**
- No two consecutive clusters should have the same arc_role (except transition)
- The master arc should have identifiable rising action: foundation → escalation → culmination → landing
- Cluster internal arcs should vary: not every cluster needs establish→develop→tension→resolve. Some can be establish→develop→resolve (no tension). Some can be establish→tension→resolve (skipping develop for impact)
- Transition clusters (quick-punch, cognitive-reset) serve as pacing between heavier clusters

**AC-4: Stitching Quality**
- Cluster-boundary bridges (from 23-1) should reflect the master arc progression, not just summarize the prior cluster
- Bridge content should signal the master arc movement: "We've established the foundation. Now let's see where it gets complicated."
- Bridge style varies by arc transition: foundation→escalation gets a "but..." bridge; escalation→culmination gets a "which brings us to..." bridge

**AC-5: Operator Visualization**
- The cluster plan presented to the operator includes:
  - Master arc with cluster placements marked
  - Per-cluster: arc_role + internal template + narrative_arc
  - Pacing visualization: cluster depths mapped across the presentation timeline
  - Stitching preview: bridge intentions at each cluster boundary

## Tasks / Subtasks

- [ ] Task 1: Define master arc framework
  - [ ] 1.1: Define presentation-level arc structure (opening/development/resolution)
  - [ ] 1.2: Define arc_role vocabulary and assignment rules
  - [ ] 1.3: Define composition rules (sequencing, variety, pacing)

- [ ] Task 2: Implement arc-aware cluster planning
  - [ ] 2.1: Assign arc_role to each cluster based on position and content
  - [ ] 2.2: Vary internal cluster arc patterns based on arc_role
  - [ ] 2.3: Enforce composition rules (no consecutive same arc_role, rising action)

- [ ] Task 3: Implement stitching intelligence
  - [ ] 3.1: Define bridge style per arc transition type
  - [ ] 3.2: Generate bridge content that reflects master arc movement
  - [ ] 3.3: Integrate with 23-1 cluster-boundary bridge generation

- [ ] Task 4: Implement operator visualization
  - [ ] 4.1: Add master arc overlay to cluster plan output
  - [ ] 4.2: Add pacing timeline visualization
  - [ ] 4.3: Add bridge intention preview at each boundary

- [ ] Task 5: Testing and iteration
  - [ ] 5.1: Run against C1-M1 — evaluate master arc coherence
  - [ ] 5.2: Compare with/without arc composition — does it feel more intentional?
  - [ ] 5.3: Validate bridge stitching reflects arc progression

## Dev Notes

### This Is the Heart of Presentation Design

This story is where APP moves from "slides with interstitials" to "designed presentations with narrative structure." The cluster template library (20c-1) provides the building blocks; the selection logic (20c-2) picks them; this story composes them into a coherent whole.

### Sophia Connection

Sophia's storytelling framework (orient → complicate → illuminate → resolve) currently applies per-cluster. This story lifts it to the presentation level. Sophia may need to be consulted — either through her existing framework references or potentially as a specialty agent (see 20c-5).

## References

- [cluster-narrative-arc-schema.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/cluster-narrative-arc-schema.md)
- [pedagogical-framework.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/pedagogical-framework.md)
- [spoken-bridging-language.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/spoken-bridging-language.md)
