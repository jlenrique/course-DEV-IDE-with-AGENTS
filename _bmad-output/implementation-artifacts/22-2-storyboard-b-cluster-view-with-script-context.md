# Story 22-2: Storyboard B Cluster View with Script Context

**Epic:** 22 - Storyboard & Review Adaptation
**Status:** backlog
**Sprint key:** `22-2-storyboard-b-cluster-view-with-script-context`
**Added:** 2026-04-12
**Depends on:** [22-1-storyboard-a-cluster-view.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/22-1-storyboard-a-cluster-view.md), [23-1-cluster-aware-dual-channel-grounding.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/23-1-cluster-aware-dual-channel-grounding.md)

> **Note on Dependency:** Although Epic 22 and 23 are parallel at the epic level, this specific story (22-2) depends on 23-1's narration output to display script context. 22-1, 22-3, and 22-4 do NOT depend on Epic 23.

## Story

As an operator reviewing narration quality for a clustered presentation,
I want Storyboard B to show cluster-grouped slides with narration scripts, timing summaries, and behavioral intent,
So that I can review how narration flows within and between clusters before assembly.

## Acceptance Criteria

**Given** a clustered presentation with Irene Pass 2 narration complete
**When** `generate-storyboard.py` renders Storyboard B
**Then** the following cluster view with script context must be present:

**AC-1: Cluster Grouping (Inherited from 22-1)**
- Same collapsible cluster groups as Storyboard A
- Head slide prominent, interstitials indented beneath

**AC-2: Per-Segment Narration Script**
- Each slide (head and interstitial) shows its narration text
- Head segments: full narration (80-140 words)
- Interstitial segments: shorter narration (25-40 words)
- Word count displayed per segment

**AC-3: Cluster Timing Summary**
- Per-cluster timing summary in cluster header:
  - Total cluster duration (sum of all segment durations)
  - Per-segment duration breakdown
  - Duration at 150 WPM target speaking rate

**AC-4: Behavioral Intent Display**
- Cluster-level: `master_behavioral_intent` shown in cluster header
- Segment-level: per-segment `behavioral_intent` shown alongside narration
- Visual indicator when segment intent doesn't align with master (mismatch flag)

**AC-5: Transition Visualization**
- Within-cluster transitions: subtle divider (visual cut, bridge_type: none)
- Cluster-boundary transitions: prominent divider with bridge text shown
- Bridge type label displayed at each transition point

**AC-6: Timing Metadata**
- Per-segment metadata shown: timing_role, content_density, cluster_position
- Voice-direction defaults in cluster header (existing behavior, cluster-extended)

## Tasks / Subtasks

- [ ] Task 1: Extend Storyboard B with cluster grouping
  - [ ] 1.1: Inherit cluster grouping from 22-1 implementation
  - [ ] 1.2: Add narration script panel per slide within cluster groups

- [ ] Task 2: Implement narration display
  - [ ] 2.1: Render narration text per segment with word count badge
  - [ ] 2.2: Differentiate head narration (full) from interstitial narration (short) visually
  - [ ] 2.3: Highlight bridge text at cluster boundaries

- [ ] Task 3: Implement timing summary
  - [ ] 3.1: Calculate per-cluster total duration from segment word counts at 150 WPM
  - [ ] 3.2: Display per-segment duration breakdown in expanded view
  - [ ] 3.3: Add timing summary to cluster header in collapsed view

- [ ] Task 4: Implement behavioral intent display
  - [ ] 4.1: Show master_behavioral_intent in cluster header
  - [ ] 4.2: Show per-segment behavioral_intent alongside narration
  - [ ] 4.3: Flag mismatches between segment intent and master intent

- [ ] Task 5: Implement transition visualization
  - [ ] 5.1: Subtle divider for within-cluster transitions (bridge_type: none)
  - [ ] 5.2: Prominent divider for cluster-boundary transitions (bridge_type: cluster_boundary)
  - [ ] 5.3: Display bridge type label at transition points

- [ ] Task 6: Testing
  - [ ] 6.1: Unit test: narration text rendering per segment type
  - [ ] 6.2: Unit test: timing calculations at 150 WPM
  - [ ] 6.3: Visual test: generate Storyboard B from trial data with narration
  - [ ] 6.4: Regression: non-clustered Storyboard B unchanged

## Dev Notes

### Dependency Nuance

This is the one story in Epic 22 that has a cross-epic dependency on Epic 23 (narration output). The other 22-* stories are purely visual/structural and can proceed in parallel with Epic 23.

### Scope Boundary

This story adds narration context to the cluster view. The flat-play preview mode (22-3) is a separate story. This story shows the editorial/production view; 22-3 shows the student view.

## References

- [22-1-storyboard-a-cluster-view.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/22-1-storyboard-a-cluster-view.md) — Cluster grouping base
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 22.2 definition
