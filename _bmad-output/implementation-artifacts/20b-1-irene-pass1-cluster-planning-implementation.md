# Story 20b-1: Irene Pass 1 Cluster Planning Implementation

**Epic:** 20b - Irene Cluster Intelligence - Implementation
**Status:** done
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

- [x] Task 1: Extend Irene Pass 1 cluster evaluation logic
  - [x] 1.1: Read cluster_density from run-constants.yaml — extended RunConstants dataclass + parse_run_constants() in scripts/utilities/run_constants.py
  - [x] 1.2: Parse special_treatment_directives for cluster overrides — documented in CP capability (SKILL.md); Irene reads operator-directives.md during Pass 1
  - [x] 1.3: Implement decision criteria scoring — CP capability loads cluster-decision-criteria.md; Irene applies scoring during LLM Pass 1
  - [x] 1.4: Apply operator overrides — CP capability loads cluster-density-controls.md; force/suppress syntax documented and loaded

- [x] Task 2: Implement cluster planning algorithm
  - [x] 2.1: Select cluster heads — CP capability loads all four references; Irene selects per density target + overrides
  - [x] 2.2: Assign cluster positions — cluster-narrative-arc-schema.md defines establish/develop/tension/resolve mapping
  - [x] 2.3: Set develop sub-types — cluster-narrative-arc-schema.md defines deepen/reframe/exemplify with non-redundancy rule
  - [x] 2.4: Determine cluster_interstitial_count — cluster-density-controls.md defines 1/2/3 heuristic

- [x] Task 3: Generate interstitial briefs
  - [x] 3.1: Select interstitial_type — canonical 5-type vocabulary in interstitial-brief-specification.md
  - [x] 3.2: Define isolation_target — specification standard requires reference to actual head content
  - [x] 3.3: Specify visual_register_constraint — specification standard requires named elements
  - [x] 3.4: Set content_scope — minimal/focused/reduced per specification standard
  - [x] 3.5: Calculate narration_burden — low/medium/high per corrected field semantics (visual 70%/narration 30% target)

- [x] Task 4: Assign cluster narrative arcs
  - [x] 4.1: Generate one-sentence emotional journey — cluster-narrative-arc-schema.md "From [start] to [end] through [mechanism]"
  - [x] 4.2: Set master_behavioral_intent — cluster-narrative-arc-schema.md defines vocabulary and subordination rules
  - [x] 4.3: Ensure segment behavioral_intents serve master — subordination rule documented in cluster-narrative-arc-schema.md

- [x] Task 5: Update bridge planning for clusters
  - [x] 5.1: Fire bridges at cluster boundaries — cluster-density-controls.md documents bridge cadence override
  - [x] 5.2: Set within-cluster bridge_type: none — documented in cluster-narrative-arc-schema.md and epics spec
  - [x] 5.3: Set cluster-boundary bridge_type: synthesis_plus_forward_pull — documented in epics spec

- [x] Task 6: Populate segment manifest cluster fields
  - [x] 6.1: Add cluster metadata — template-segment-manifest.md already has all cluster fields (from 19-1)
  - [x] 6.2: Set double_dispatch_eligible: false for interstitials — enforced by G1.5-08 in validate-cluster-plan.py
  - [x] 6.3: Validate cluster structure — G1.5-01 checks parent_slide_id references; G1.5-11 checks position completeness

 - [x] Task 7: Implement G1.5 quality gate
   - [x] 7.1: Validate cluster plan meets specification standard — validate-cluster-plan.py with 13 criteria
   - [x] 7.2: Check brief quality — G1.5-02 (type vocab), G1.5-03 (isolation_target), G1.5-04 (narration_burden)
   - [x] 7.3: Verify cluster arc coherence — G1.5-05 (narrative_arc), G1.5-13 (master_behavioral_intent), G1.5-06/07 (develop_type)
   - [x] 7.4: Confirm density target respected — G1.5-10 (cluster count within density range)

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

- _bmad-output/implementation-artifacts/20b-1-irene-pass1-cluster-planning-implementation.md (modified — this file)
- scripts/utilities/run_constants.py (modified — added cluster_density field + ALLOWED_CLUSTER_DENSITIES)
- tests/test_run_constants.py (modified — 5 new cluster_density tests)
- tests/test_sprint_status_yaml.py (modified — updated expected status for 20b-1)
- skills/bmad-agent-content-creator/SKILL.md (modified — added CP capability, updated Pass 1 description)
- skills/bmad-agent-marcus/scripts/validate-cluster-plan.py (new — G1.5 quality gate validator, 13 criteria)
- skills/bmad-agent-marcus/scripts/tests/test_validate_cluster_plan.py (new — 26 tests for G1.5 validator)
- state/config/fidelity-contracts/g1.5-cluster-plan.yaml (new — G1.5 fidelity contract)

## Change Log

- feat: implement Irene Pass 1 cluster planning — run_constants cluster_density, G1.5 validator, CP capability (2026-04-11)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6[1m]

### Debug Log

- 2026-04-11: Confirmed Irene is LLM-driven; Python layer = run_constants + G1.5 validator
- 2026-04-11: Orchestrator test pre-existing failure (ModuleNotFoundError) — not caused by this story
- 2026-04-11: Fixed flat-segment detection in G1.5 validator: use cluster_role is None, not cluster_id is None

### Completion Notes List

- ✅ Task 1.1: Extended RunConstants with cluster_density (none|sparse|default|rich); validation in parse_run_constants(); 5 new tests passing
- ✅ Tasks 1.2–6: Added CP (cluster planning) capability to Irene SKILL.md; loads all four cluster references; updated Pass 1 description
- ✅ Task 7: Created validate-cluster-plan.py with 13 G1.5 criteria; 26 tests passing; created g1.5-cluster-plan.yaml fidelity contract
- ✅ Added G1.5-13 (master_behavioral_intent on heads) and hardened G1.5-09 (actual count vs declared); fidelity contract updated to 13 criteria; 3 new tests added
- ✅ All 450 tests pass (excluding pre-existing orchestrator failure)
- ✅ sprint-status regression test updated to reflect in-progress state; story status aligned

### File List

## Status

review

## Completion Status

Story 20b-1 ready for development — Irene Pass 1 cluster planning implementation planned and documented.
