# Story 20b-1: Irene Pass 1 Cluster Planning Implementation

**Epic:** 20b - Irene Cluster Intelligence - Implementation
**Status:** ready-for-dev
**Sprint key:** `20b-1-irene-pass1-cluster-planning-implementation`
**Added:** 2026-04-11
**Validated:** 2026-04-11
**Depends on:** [20a-1-cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-1-cluster-decision-criteria.md), [20a-2-interstitial-brief-specification-standard.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-2-interstitial-brief-specification-standard.md), [20a-3-cluster-narrative-arc-schema.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-3-cluster-narrative-arc-schema.md), [20a-4-operator-cluster-density-controls.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-4-operator-cluster-density-controls.md)

## Story

As Irene,
I want to implement cluster planning in Pass 1,
So that I can produce clustered backbone with interstitial briefs that meet the specification standard.

## Acceptance Criteria

**Given** Irene Pass 1 receives lesson plan and slide brief input
**When** cluster_density is set (not none)
**Then** Irene produces clustered segment manifest with heads + interstitials

**And** cluster planning follows decision criteria (20a-1):
- Evaluates each slide against concept density, visual complexity, pedagogical weight
- Applies operator overrides from special_treatment_directives
- Respects cluster_density target (sparse 1-2, default 3-5, rich 6+)

**And** interstitial briefs meet specification standard (20a-2):
- Type: reveal | emphasis-shift | bridge-text | simplification | pace-reset
- Isolation_target references actual head content
- Visual_register_constraint specifies what to remove/suppress
- Content_scope ≤2 sentences
- Narration_burden targets visual 70%, narration 30%

**And** cluster narrative arcs follow schema (20a-3):
- One-sentence emotional journey per cluster
- Positions: establish (head) → develop/tension/resolve (interstitials)
- Develop sub-types: deepen | reframe | exemplify
- Master behavioral intent serves the cluster arc

**And** operator controls work (20a-4):
- cluster_density sets overall target
- Per-slide overrides via Prompt 2A special_treatment_directives
- cluster_interstitial_count per cluster (1-3, based on content complexity)

**And** output includes cluster metadata in segment manifest (19-1):
- cluster_id, cluster_role, cluster_position, develop_type, parent_slide_id
- interstitial_type, isolation_target, narrative_arc, master_behavioral_intent, cluster_interstitial_count
- double_dispatch_eligible (false for interstitials)

**And** bridge planning adapts for clusters:
- Bridges fire at cluster boundaries, not arbitrary intervals
- Within-cluster transitions: bridge_type: none (default), pivot allowed for tension
- Cluster-boundary bridges: synthesis_plus_forward_pull

**And** quality gate G1.5 validates cluster plan before Gary dispatch

## Tasks / Subtasks

- [ ] Task 1: Extend Irene Pass 1 cluster evaluation logic
  - [ ] 1.1: Read cluster_density from run-constants.yaml
  - [ ] 1.2: Parse special_treatment_directives for cluster overrides
  - [ ] 1.3: Implement decision criteria scoring (concept density, visual complexity, pedagogical weight)
  - [ ] 1.4: Apply operator overrides (force/suppress per slide)

- [ ] Task 2: Implement cluster planning algorithm
  - [ ] 2.1: Select cluster heads based on criteria + overrides + density target
  - [ ] 2.2: Assign cluster positions (establish/develop/tension/resolve)
  - [ ] 2.3: Set develop sub-types (deepen/reframe/exemplify)
  - [ ] 2.4: Determine cluster_interstitial_count per cluster (1-3 based on complexity)

- [ ] Task 3: Generate interstitial briefs
  - [ ] 3.1: Select interstitial_type per position (5 types vocabulary)
  - [ ] 3.2: Define isolation_target (reference actual head content)
  - [ ] 3.3: Specify visual_register_constraint (what to remove/suppress)
  - [ ] 3.4: Set content_scope (≤2 sentences)
  - [ ] 3.5: Calculate narration_burden (visual 70%/narration 30%)

- [ ] Task 4: Assign cluster narrative arcs
  - [ ] 4.1: Generate one-sentence emotional journey per cluster
  - [ ] 4.2: Set master_behavioral_intent for cluster
  - [ ] 4.3: Ensure segment behavioral_intents serve master intent

- [ ] Task 5: Update bridge planning for clusters
  - [ ] 5.1: Fire bridges at cluster boundaries (not slide/time count)
  - [ ] 5.2: Set within-cluster bridge_type: none (default), pivot for tension
  - [ ] 5.3: Set cluster-boundary bridge_type: synthesis_plus_forward_pull

- [ ] Task 6: Populate segment manifest cluster fields
  - [ ] 6.1: Add cluster metadata to all segment entries
  - [ ] 6.2: Set double_dispatch_eligible: false for interstitials
  - [ ] 6.3: Validate cluster structure (heads have interstitials, interstitials have parents)

- [ ] Task 7: Implement G1.5 quality gate
  - [ ] 7.1: Validate cluster plan meets specification standard
  - [ ] 7.2: Check brief quality (isolation_target references, narration_burden)
  - [ ] 7.3: Verify cluster arc coherence
  - [ ] 7.4: Confirm density target respected

## Dev Notes

### Scope Boundary

This story implements **Irene Pass 1 cluster planning only**. Does not include:

- Gary dispatch (Epic 21)
- Irene Pass 2 narration (Epic 23)
- Storyboard adaptation (Epic 22)
- Assembly/handoff (Epic 24)

Pure Irene Pass 1 extension — input lesson plan, output clustered segment manifest.

### Dependencies

All 20a design stories complete. 19-1 schema defined. No dependency on 19-2 (Gary contracts) — Irene writes her own output artifacts.

### Cluster Planning Algorithm

1. **Evaluate slides:** Score each against criteria, apply overrides
2. **Select heads:** Top-scoring slides that meet density target
3. **Plan clusters:** Assign positions, set interstitial count
4. **Generate briefs:** Per interstitial type vocabulary
5. **Assign arcs:** One-sentence journey per cluster
6. **Plan bridges:** Cluster-aware cadence
7. **Populate manifest:** Add cluster metadata

### Risk: Brief Quality

Interstitial briefs must be specific enough for Gamma to execute. If briefs are too vague, Epic 21 will fail. Quality gate G1.5 catches this.

### Testing

- Unit tests: Cluster evaluation logic, brief generation
- Integration tests: End-to-end Pass 1 with clustered output
- Regression tests: Non-clustered runs unchanged

## Project Structure Notes

- **Modified files:**
  - `skills/bmad-agent-content-creator/` — Irene Pass 1 logic
  - `scripts/` — Cluster planning scripts
  - `state/config/` — G1.5 quality gate

## References

- [20a-1-cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-1-cluster-decision-criteria.md) — Decision criteria
- [20a-2-interstitial-brief-specification-standard.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-2-interstitial-brief-specification-standard.md) — Brief standard
- [20a-3-cluster-narrative-arc-schema.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-3-cluster-narrative-arc-schema.md) — Arc schema
- [20a-4-operator-cluster-density-controls.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-4-operator-cluster-density-controls.md) — Operator controls
- [19-1-segment-manifest-cluster-schema-extension.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/19-1-segment-manifest-cluster-schema-extension.md) — Manifest schema
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 20b.1 definition

## File List

- _bmad-output/implementation-artifacts/20b-1-irene-pass1-cluster-planning-implementation.md (this file)
- skills/bmad-agent-content-creator/ (modified Irene logic)
- scripts/ (modified cluster planning)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6[1m]

### Debug Log

### Completion Notes List

- ✅ Story file created with AC, tasks, dev notes
- ✅ Dependencies and scope boundaries defined
- ✅ Algorithm and risks specified
- ✅ Testing approach outlined

### File List

## Status

ready-for-dev

## Completion Status

Story 20b-1 ready for development — Irene Pass 1 cluster planning implementation planned and documented.
