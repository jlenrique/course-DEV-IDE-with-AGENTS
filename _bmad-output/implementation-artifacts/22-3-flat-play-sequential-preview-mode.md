# Story 22-3: Flat-Play Sequential Preview Mode

**Epic:** 22 - Storyboard & Review Adaptation
**Status:** backlog
**Sprint key:** `22-3-flat-play-sequential-preview-mode`
**Added:** 2026-04-12
**Depends on:** [22-1-storyboard-a-cluster-view.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/22-1-storyboard-a-cluster-view.md)

## Story

As an operator preparing a clustered presentation for assembly,
I want a "view as student" flat-play mode that shows slides in linear playback order without cluster grouping,
So that I can experience the pacing and flow as a student would, validating that the progressive disclosure feels natural in sequence.

## Acceptance Criteria

**Given** a Storyboard B with clustered presentation data
**When** the operator toggles to flat-play mode
**Then** the following preview must render:

**AC-1: Linear Slide Sequence**
- All slides displayed in flat manifest order (head, interstitial 1, interstitial 2, ..., next head, ...)
- No cluster grouping, indentation, or cluster headers
- Each slide shows: thumbnail, narration text, word count, estimated duration

**AC-2: Transition Indicators**
- Within-cluster transitions: subtle divider (thin line or minimal spacing)
- Cluster-boundary transitions: prominent divider (thicker line, background color change, or spacing)
- Transition type label: "within cluster" vs. "cluster boundary"
- Bridge text shown at cluster boundaries (synthesis + forward pull)

**AC-3: Toggle Control**
- Accessible from Storyboard B HTML via a toggle button/switch
- Toggle label: "Cluster View" (default) ↔ "Student View"
- Toggle preserves scroll position where possible
- Both views available in the same HTML file (no separate generation)

**AC-4: Pacing Visualization**
- Running time counter alongside each slide (cumulative duration)
- Duration bar or timeline showing relative time allocation per slide
- Visual highlight for slides with unusual duration (>2x or <0.5x average)

**AC-5: No Cluster Metadata in Student View**
- Hide: cluster_id, cluster_role, cluster_position, interstitial_type, isolation_target
- Show: slide topic/title, narration text, duration, behavioral_intent
- The student doesn't know about clusters — this view reflects their experience

## Tasks / Subtasks

- [ ] Task 1: Implement flat-play view renderer
  - [ ] 1.1: Flatten clustered manifest into linear slide sequence
  - [ ] 1.2: Render each slide with thumbnail + narration + duration
  - [ ] 1.3: Strip cluster metadata from display (hide, don't delete from data)

- [ ] Task 2: Implement transition indicators
  - [ ] 2.1: Detect within-cluster vs. cluster-boundary transitions from manifest
  - [ ] 2.2: Render subtle divider for within-cluster
  - [ ] 2.3: Render prominent divider for cluster-boundary with bridge text

- [ ] Task 3: Implement toggle control
  - [ ] 3.1: Add toggle button to Storyboard B HTML
  - [ ] 3.2: JavaScript to switch between cluster view and student view
  - [ ] 3.3: Preserve scroll position on toggle

- [ ] Task 4: Implement pacing visualization
  - [ ] 4.1: Calculate cumulative running time per slide
  - [ ] 4.2: Render running time counter alongside each slide
  - [ ] 4.3: Highlight slides with outlier duration

- [ ] Task 5: Testing
  - [ ] 5.1: Unit test: manifest flattening preserves order
  - [ ] 5.2: Unit test: transition type detection (within-cluster vs. boundary)
  - [ ] 5.3: Visual test: toggle between cluster and student views
  - [ ] 5.4: Regression: non-clustered presentation shows flat view only (no toggle needed)

## Dev Notes

### Spec Note

The spec explicitly states: "Flat-play mode is essential, not optional." This is how operators validate pacing before assembly.

### JavaScript Requirement

Unlike 22-1 (pure HTML/CSS with `<details>/<summary>`), this story requires JavaScript for the toggle. Keep it minimal — vanilla JS, no framework dependencies. The toggle swaps CSS display properties on two pre-rendered views.

### Scope Boundary

This story adds the student-perspective preview. It does NOT modify the cluster view (22-1) or add narration display (22-2). It reads the same data but presents it differently.

## References

- [22-1-storyboard-a-cluster-view.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/22-1-storyboard-a-cluster-view.md) — Cluster view base
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 22.3 definition
