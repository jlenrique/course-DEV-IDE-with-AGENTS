# Story 23-1: Cluster-Aware Dual-Channel Grounding

**Epic:** 23 - Irene Pass 2 Cluster-Aware Narration
**Status:** backlog
**Sprint key:** `23-1-cluster-aware-dual-channel-grounding`
**Added:** 2026-04-12
**Depends on:** [20b-3-narration-script-parameters-extension-for-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20b-3-narration-script-parameters-extension-for-clusters.md), [21-3-cluster-dispatch-sequencing.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/21-3-cluster-dispatch-sequencing.md)

> **When this story ships:** Remove the `pass2_mode: structural-coherence-check` scope limitation from `docs/workflow/operator-script-v4.2-irene-ab-loop.md` (3 locations: Pass 2 section header, Prompt 5C.4 HIL guidance, sprint-status.yaml plan header). Pass 2 becomes a first-class refinement target in A/B trials.

## Story

As Irene (Pass 2),
I want to perceive each slide in a cluster and write narration calibrated to the head/interstitial split,
So that head segments get full explanatory narration while interstitial segments get brief, visual-complementary narration that presumes the slide carries 70% of the meaning.

## Acceptance Criteria

**Given** Irene Pass 2 receives a clustered segment manifest with generated PNGs
**When** Irene writes narration for a cluster
**Then** the following dual-channel rules must be enforced:

**AC-1: Head Segment Narration (Establish Position)**
- Fuller narration: 80-140 words (per cluster_head_word_range)
- Establishes the topic, plants the hook
- Standard dual-channel grounding: narration complements the visual
- Visual references per existing perception protocol (Epic 13)

**AC-2: Interstitial Segment Narration (Develop/Tension/Resolve)**
- Shorter narration: 25-40 words (per interstitial_word_range)
- Focused on the interstitial's isolation_target
- Presumes the visual carries 70% of the meaning — narration adds the remaining 30%
- No new concepts introduced (narration scope limited to head segment's source_ref)

**AC-3: Within-Cluster Transitions**
- Default: `bridge_type: none` — no spoken bridge (visual cut is sufficient)
- Exception: `tension` position may use `bridge_type: pivot` with an explicit tonal shift word (e.g., "but", "however", "yet")
- Irene must suppress bridge generation for within-cluster transitions unless cluster_position == tension

**AC-4: Cluster-Boundary Transitions**
- `bridge_type: cluster_boundary` — one sentence synthesis of what the cluster covered + one sentence forward pull to next topic
- Duration target: 15-20 seconds (37-50 words at 150 WPM)
- Bridge fires at cluster seams (not by slide count or time interval)

**AC-5: Behavioral Intent Subordination**
- Per-segment behavioral_intent must serve the cluster's master_behavioral_intent
- Irene cannot assign a behavioral_intent that contradicts or diverges from the cluster master
- Intent vocabulary remains the same; constraint is subordination, not restriction

**AC-6: Perception of All Cluster Members**
- Irene perceives each slide (head and interstitial) via sensory bridge before writing narration
- Perception data includes: dominant visuals, text content, layout, color palette
- Interstitial narration references the perceived isolation_target specifically

## Tasks / Subtasks

- [ ] Task 1: Extend Irene Pass 2 for cluster awareness
  - [ ] 1.1: Detect clustered segments in manifest (cluster_id not null)
  - [ ] 1.2: Read cluster parameters from narration-script-parameters.yaml (20b-3 output)
  - [ ] 1.3: Group segments by cluster_id for sequential processing

- [ ] Task 2: Implement head segment narration
  - [ ] 2.1: Apply cluster_head_word_range [80, 140] for head segments
  - [ ] 2.2: Standard perception + dual-channel grounding (existing Epic 13 flow)
  - [ ] 2.3: Set behavioral_intent as master_behavioral_intent for the cluster

- [ ] Task 3: Implement interstitial segment narration
  - [ ] 3.1: Apply interstitial_word_range [25, 40] for interstitial segments
  - [ ] 3.2: Focus narration on isolation_target from perception
  - [ ] 3.3: Enforce no-new-concepts rule (scope limited to head's source_ref)
  - [ ] 3.4: Set behavioral_intent subordinate to master

- [ ] Task 4: Implement bridge handling
  - [ ] 4.1: Suppress bridges within clusters (bridge_type: none)
  - [ ] 4.2: Allow pivot bridge for tension position only
  - [ ] 4.3: Generate cluster_boundary bridge at cluster seams (synthesis + forward pull)
  - [ ] 4.4: Apply bridge cadence override (bridges at cluster seams, not by count/time)

- [ ] Task 5: Testing
  - [ ] 5.1: Unit test: head narration within 80-140 word range
  - [ ] 5.2: Unit test: interstitial narration within 25-40 word range
  - [ ] 5.3: Unit test: no spoken bridge within cluster (non-tension)
  - [ ] 5.4: Unit test: cluster_boundary bridge at cluster seams
  - [ ] 5.5: Unit test: behavioral_intent subordination check
  - [ ] 5.6: Regression: non-clustered narration unchanged

## Dev Notes

### Scope Boundary

This story implements the narration writing rules. G4 gate extension is 23-2. Bridge cadence parameter changes are in 20b-3 (prerequisite). This story consumes the parameters and produces the narration.

### Key Dependency

This story requires 20b-3 (narration parameters) to be complete. Without cluster-specific word ranges and bridge policies in the YAML, Irene has no calibration data.

### Irene Is LLM-Driven

Irene's narration is produced by the LLM during Pass 2, not by Python scripts. The Python layer validates the output (G4 gate). This story defines the behavioral contract Irene must follow; the G4 gate (23-2) enforces it.

## References

- [20b-3-narration-script-parameters-extension-for-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20b-3-narration-script-parameters-extension-for-clusters.md) — Parameter infrastructure
- [13-2-visual-reference-injection.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/13-2-visual-reference-injection.md) — Existing perception/grounding
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 23.1 definition
