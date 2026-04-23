# Story 22-3: Flat-Play Sequential Preview Mode

**Epic:** 22 - Storyboard & Review Adaptation
**Status:** review
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

- [x] Task 1: Implement flat-play view renderer
  - [x] 1.1: Flatten clustered manifest into linear slide sequence
  - [x] 1.2: Render each slide with thumbnail + narration + duration
  - [x] 1.3: Strip cluster metadata from display (hide, don't delete from data)

- [x] Task 2: Implement transition indicators
  - [x] 2.1: Detect within-cluster vs. cluster-boundary transitions from manifest
  - [x] 2.2: Render subtle divider for within-cluster
  - [x] 2.3: Render prominent divider for cluster-boundary with bridge text

- [x] Task 3: Implement toggle control
  - [x] 3.1: Add toggle button to Storyboard B HTML
  - [x] 3.2: JavaScript to switch between cluster view and student view
  - [x] 3.3: Preserve scroll position on toggle

- [x] Task 4: Implement pacing visualization
  - [x] 4.1: Calculate cumulative running time per slide
  - [x] 4.2: Render running time counter alongside each slide
  - [x] 4.3: Highlight slides with outlier duration

- [x] Task 5: Testing
  - [x] 5.1: Unit test: manifest flattening preserves order
  - [x] 5.2: Unit test: transition type detection (within-cluster vs. boundary)
  - [x] 5.3: Visual test: toggle between cluster and student views
  - [x] 5.4: Regression: non-clustered presentation shows flat view only (no toggle needed)

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

## Dev Agent Record

### Implementation Plan

- Extend `generate-storyboard.py` with a flat-play student renderer only for clustered Storyboard B runs, while preserving existing non-clustered Storyboard B output as-is.
- Add deterministic helper functions for flatten ordering, transition classification, duration/cumulative-time math, and outlier detection.
- Add a JS view toggle that swaps pre-rendered cluster/student views in one HTML file and preserves scroll position.
- Expand `test_generate_storyboard.py` with unit coverage for flatten/transition helpers plus Storyboard B student-view visual assertions and non-clustered regression checks.

### Debug Log

- 2026-04-23: Loaded full story spec and Storyboard generator implementation/tests before coding.
- 2026-04-23: Implemented student-view rendering, transition markers, pacing track/cumulative timing, duration outlier highlighting, and Cluster View ↔ Student View toggle with scroll preservation.
- 2026-04-23: Added helper tests for order-preserving flatten and transition detection; updated Storyboard B tests for toggle/student-view output and non-clustered no-toggle regression.
- 2026-04-23: Ran targeted generator suites green after one compatibility adjustment to keep non-clustered Storyboard B in legacy flat layout.

### Completion Notes

- Storyboard B now supports a flat-play Student View for clustered presentations with:
  - linear manifest-order slide playback,
  - within-cluster vs. cluster-boundary transition indicators,
  - bridge text excerpts at cluster boundaries,
  - per-slide duration bar + cumulative running-time counters,
  - outlier highlighting for segments outside the `$0.5\times$` to `$2.0\times$` average duration band.
- Cluster view remains default and now toggles to student view in the same HTML document via vanilla JS controls.
- Non-clustered Storyboard B remains single-view (no toggle), preserving existing downstream behavior.
- Validation:
  - `pytest skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py`
  - `pytest skills/bmad-agent-marcus/scripts/tests/test_write_authorized_storyboard.py`
  - Result: `65 passed`, `0 failed`.

## File List

- `_bmad-output/implementation-artifacts/22-3-flat-play-sequential-preview-mode.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `skills/bmad-agent-marcus/scripts/generate-storyboard.py`
- `skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py`

## Change Log

- 2026-04-23: Implemented Storyboard B clustered student flat-play mode (toggle, transition markers, pacing visualization, outlier highlighting), added helper/test coverage, and moved story to `review`.
