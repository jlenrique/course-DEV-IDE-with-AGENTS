# Story 20a.1: Cluster Decision Criteria

**Epic:** 20A - Irene Cluster Intelligence - Design & Specification
**Status:** done
**Sprint key:** `20a-1-cluster-decision-criteria`
**Added:** 2026-04-11
**Validated:** 2026-04-11
**Depends on:** [interstitial-cluster-mvp-c1m1-storyboard-a.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/interstitial-cluster-mvp-c1m1-storyboard-a.md), [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md), Irene's existing pedagogical framework

## Story

As Irene,
I want an explicit decision framework for when a slide becomes a cluster head,
So that clustered presentations are driven by pedagogical need and visual logic rather than arbitrary expansion.

## Acceptance Criteria

**Given** the C1M1 Storyboard-A MVP requires exactly 3 meaningful clusters
**When** Irene evaluates a presentation for clustering
**Then** she must assess each candidate head slide against these criteria:

- concept density
- visual complexity
- pedagogical weight
- operator input

**And** each criterion must be defined in a way that is actionable during Pass 1, not just descriptive after the fact
**And** the resulting framework must help Irene distinguish:

- slides that should remain flat
- slides that deserve a single supporting interstitial
- slides that justify a fuller 2-3 interstitial cluster

**And** the framework must define how operator controls influence clustering without replacing Irene's judgment
**And** the design output must be documented in Irene's references for later implementation in 20b
**And** the C1M1 MVP context must be explicit: the immediate goal is selecting 3 clusters that create a beginning, middle, and end arc for Storyboard A review

## Tasks / Subtasks

- [x] Task 1: Define the decision criteria clearly (AC: 1-4)
  - [x] 1.1: Define `concept density` in terms of how many distinct explanatory beats a topic naturally contains
  - [x] 1.2: Define `visual complexity` in terms of whether the current slide would benefit from decomposition, isolation, or reduction
  - [x] 1.3: Define `pedagogical weight` in terms of concept centrality to the learning objective and learner burden if left undersupported
  - [x] 1.4: Define `operator input` as bounded override or preference, not sole authorship of cluster selection
- [x] Task 2: Produce a reusable decision framework reference for Irene (AC: 1-6)
  - [x] 2.1: Add a new reference document under `skills/bmad-agent-content-creator/references/`
  - [x] 2.2: Include pass/fail examples of likely cluster heads versus slides that should stay flat
  - [x] 2.3: Include explicit cues for when one interstitial is enough versus when 2-3 are justified
- [x] Task 3: Tie the framework to the C1M1 MVP (AC: 6)
  - [x] 3.1: Document that the first proof seeks exactly 3 clusters for beginning, middle, and end
  - [x] 3.2: Note that the initial stop point is Storyboard A, so criteria should optimize for visual proof before narration concerns
- [x] Task 4: Update Irene-facing references (AC: 5-6)
  - [x] 4.1: Update [SKILL.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/SKILL.md) to reference the cluster decision framework in the future Pass 1 cluster-planning step
  - [x] 4.2: Cross-link to [delegation-protocol.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/delegation-protocol.md) only where the criteria need to shape future writer briefs

## Dev Notes

### Scope Boundary

This story defines **how Irene decides** which slides should cluster. It does not yet implement:

- manifest schema changes
- Gary dispatch contract changes
- cluster narrative arc metadata
- cluster density controls as a runtime config mechanism
- Pass 2 narration changes

Those are handled in adjacent stories.

### Existing Irene References To Reuse

- [pedagogical-framework.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/pedagogical-framework.md) already holds Bloom's, cognitive load, and sequencing guidance. The new cluster criteria should extend this logic rather than bypass it.
- [runtime-variability-framework.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/runtime-variability-framework.md) already frames how visual burden and concept density affect runtime. Reuse those ideas when defining what kinds of slides deserve decomposition into clusters.
- [delegation-protocol.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/delegation-protocol.md) already includes `Runtime Intent` and `Timing Rationale`; future cluster planning should complement, not duplicate, those fields.

### Decision Quality Guardrails

- A cluster candidate should have enough substance to support multiple explanatory beats.
- A visually dense slide is not automatically a cluster head; complexity must serve comprehension if decomposed.
- A concept may have high pedagogical weight even when the source slide is visually simple.
- Operator input can force or suppress clustering, but the framework should still state whether that override is pedagogically natural or compensatory.
- The framework must help avoid decorative interstitials. If a supporting slide does not change learner understanding, it likely does not belong.

### C1M1 MVP Guidance

The immediate use case is not generic. It is the C1M1 three-cluster Storyboard-A MVP. The reference should therefore help Irene answer:

- Which 3 moments in C1M1 deserve cluster treatment?
- Why those 3, rather than any other 3?
- What makes each chosen moment suitable for a beginning, middle, or end role in the overall presentation?

### Previous Story Intelligence

- [13-2-visual-reference-injection.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/13-2-visual-reference-injection.md) and [13-3-segment-manifest-visual-references.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/13-3-segment-manifest-visual-references.md) show the recent pattern: new Irene behavior should be documented first in references and SKILL guidance before it is enforced in downstream tooling.
- [14-1-motion-workflow-design.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/14-1-motion-workflow-design.md) is the precedent for design-first stories where the primary deliverable is a clear workflow/design contract.

## Testing Requirements

- This is primarily a design/reference story, so verification is document and contract review rather than a large automated suite.
- If any code or validation hooks are touched while wiring Irene references, run the targeted tests through the repo venv.

## Project Structure Notes

- Likely new reference file:
  - `skills/bmad-agent-content-creator/references/cluster-decision-criteria.md`
- Likely modified files:
  - [SKILL.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/SKILL.md)
  - [pedagogical-framework.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/pedagogical-framework.md) or a new adjacent reference

## References

- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md)
- [interstitial-cluster-mvp-c1m1-storyboard-a.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/interstitial-cluster-mvp-c1m1-storyboard-a.md)
- [SKILL.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/SKILL.md)
- [pedagogical-framework.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/pedagogical-framework.md)
- [runtime-variability-framework.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/runtime-variability-framework.md)

## Dev Agent Record

### Debug Log

- 2026-04-11: Started implementation of 20a-1
- 2026-04-11: Created cluster-decision-criteria.md reference document with four criteria, decision framework, examples, and C1M1 MVP context
- 2026-04-11: Updated Irene SKILL.md to include CD capability in internal capabilities table
- 2026-04-11: Marked all tasks complete

### Completion Notes

Successfully defined the cluster decision criteria framework for Irene, including actionable definitions for concept density, visual complexity, pedagogical weight, and operator input. Created comprehensive reference document with examples and C1M1 MVP guidance. Updated Irene's capabilities to include cluster decision criteria.

### File List

- skills/bmad-agent-content-creator/references/cluster-decision-criteria.md (new)
- skills/bmad-agent-content-creator/SKILL.md (modified)

### Change Log

- feat: add cluster decision criteria framework for Irene (2026-04-11)

### Review Findings

- [x] [Review][Patch] YAML parse failure in sprint-status.yaml — indentation mismatch on two story keys [sprint-status.yaml:263,267]
- [x] [Review][Patch] Story 20a-1 status mismatch — created missing story tracking file with completion record

## Status

done

## Completion Status

Ultimate context engine analysis completed - design guidance created for Irene's first cluster-planning decision story.