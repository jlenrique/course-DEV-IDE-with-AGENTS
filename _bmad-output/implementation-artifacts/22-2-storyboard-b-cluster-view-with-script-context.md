# Story 22-2: Storyboard B Cluster View with Script Context

**Epic:** 22 - Storyboard & Review Adaptation
**Status:** done
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

- [x] Task 1: Extend Storyboard B with cluster grouping
  - [x] 1.1: Inherit cluster grouping from 22-1 implementation
  - [x] 1.2: Add narration script panel per slide within cluster groups

- [x] Task 2: Implement narration display
  - [x] 2.1: Render narration text per segment with word count badge
  - [x] 2.2: Differentiate head narration (full) from interstitial narration (short) visually
  - [x] 2.3: Highlight bridge text at cluster boundaries

- [x] Task 3: Implement timing summary
  - [x] 3.1: Calculate per-cluster total duration from segment word counts at 150 WPM
  - [x] 3.2: Display per-segment duration breakdown in expanded view
  - [x] 3.3: Add timing summary to cluster header in collapsed view

- [x] Task 4: Implement behavioral intent display
  - [x] 4.1: Show master_behavioral_intent in cluster header
  - [x] 4.2: Show per-segment behavioral_intent alongside narration
  - [x] 4.3: Flag mismatches between segment intent and master intent

- [x] Task 5: Implement transition visualization
  - [x] 5.1: Subtle divider for within-cluster transitions (bridge_type: none)
  - [x] 5.2: Prominent divider for cluster-boundary transitions (bridge_type: cluster_boundary)
  - [x] 5.3: Display bridge type label at transition points

- [x] Task 6: Testing
  - [x] 6.1: Unit test: narration text rendering per segment type
  - [x] 6.2: Unit test: timing calculations at 150 WPM
  - [x] 6.3: Visual test: generate Storyboard B from trial data with narration
  - [x] 6.4: Regression: non-clustered Storyboard B unchanged

## Dev Notes

### Dependency Nuance

This is the one story in Epic 22 that has a cross-epic dependency on Epic 23 (narration output). The other 22-* stories are purely visual/structural and can proceed in parallel with Epic 23.

### Scope Boundary

This story adds narration context to the cluster view. The flat-play preview mode (22-3) is a separate story. This story shows the editorial/production view; 22-3 shows the student view.

## References

- [22-1-storyboard-a-cluster-view.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/22-1-storyboard-a-cluster-view.md) - Cluster grouping base
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) - Story 22.2 definition

## Dev Agent Record

### Implementation Plan

- Reuse the existing 22-1 cluster-group rendering path instead of inventing a second grouping model for Storyboard B.
- Extend the Storyboard B slide script panel with deterministic timing, intent, and transition metadata derived from the segment manifest so operators can inspect cluster behavior directly.
- Close the story only to `review` after targeted generator tests and one real rendered bundle pass both succeed.

### Debug Log

- 2026-04-15: Loaded BMAD dev-story workflow, project context, and the full 22-2 story artifact before resuming implementation.
- 2026-04-15: Completed the pending `generate-storyboard.py` Storyboard B cluster-view implementation by propagating `master_behavioral_intent`, computing 150-WPM timing summaries, surfacing per-segment script metadata, and rendering boundary vs. within-cluster transition treatments.
- 2026-04-15: Added focused `test_generate_storyboard.py` coverage for clustered Storyboard B script context and for flat Storyboard B regression behavior.
- 2026-04-15: Ran the targeted storyboard generator suite green, then generated a real Storyboard B smoke bundle from clustered narration data to verify the rendered bundle path end-to-end.

### Completion Notes

- Storyboard B now reuses the cluster-group shell from 22-1 while extending the clustered view with per-segment narration context: word counts, 150-WPM duration badges, timing role, density, cluster position, and segment behavioral intent.
- Cluster headers now surface `master_behavioral_intent`, aggregate cluster duration/word totals, mismatch counts, and voice-direction defaults so operators can assess cluster pacing and intent coherence before assembly.
- Cluster-boundary heads now render a prominent bridge divider with excerpted bridge text, while within-cluster interstitials render a lighter transition divider; segment/master intent mismatches are explicitly flagged in the script panel.
- Validation passed:
  - `.\.venv\Scripts\python.exe -m pytest skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py -q`
  - Result: `40 passed`
- Smoke generation passed:
  - `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/generate-storyboard.py generate --payload %TEMP%\\storyboard-b-22-2-smoke\\dispatch.json --out-dir %TEMP%\\storyboard-b-22-2-smoke\\out --asset-base %TEMP%\\storyboard-b-22-2-smoke --segment-manifest %TEMP%\\storyboard-b-22-2-smoke\\segment-manifest.yaml --pass2-envelope %TEMP%\\storyboard-b-22-2-smoke\\pass2-envelope.json --print-summary`
  - Output bundle: `%TEMP%\\storyboard-b-22-2-smoke\\out\\storyboard\\index.html`
  - Result: `Storyboard B summary: 3 slide(s)` with `pending_narration=0` and `slides_with_findings=0`

## File List

- `_bmad-output/implementation-artifacts/22-2-storyboard-b-cluster-view-with-script-context.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `skills/bmad-agent-marcus/scripts/generate-storyboard.py`
- `skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py`

## Change Log

- 2026-04-15: Completed Storyboard B cluster-view implementation, added focused clustered/flat regression coverage, verified the generator via targeted tests plus a rendered smoke bundle, and moved the story to `review`.
- 2026-04-15: Formal BMAD review completed clean with no findings; story closed to `done`.

## Adversarial Review (BMAD)

### Blind Hunter

- No implementation defects found in the 22-2 delta. The Storyboard B cluster view stays additive to the existing Storyboard A grouping path, and the new timing / intent / transition surfaces are derived from manifest fields already used elsewhere in the pipeline.

### Edge Case Hunter

- No unhandled branch or regression path found in the reviewed scope. The new tests cover clustered Storyboard B rendering and the flat non-clustered fallback, and the adjacent authorized-Storyboard path remains green.

### Acceptance Auditor

- AC-1 through AC-6 are satisfied by the current implementation:
  - clustered grouping is reused from 22-1
  - per-segment narration text, word counts, and visual differentiation are present
  - cluster timing summary and per-segment duration breakdown render at 150 WPM
  - `master_behavioral_intent`, segment intent, and mismatch signaling are surfaced
  - within-cluster vs. cluster-boundary transitions are visually distinct with bridge labeling
  - timing metadata plus voice-direction defaults remain visible in Storyboard B

Review closed: 2026-04-15 (formal BMAD review; clean, no findings).

## BMAD Tracking Closure

**Framework:** Per `sprint-status.yaml` — **`done`** = ACs met + agreed verification green + layered BMAD review complete + sprint key `done`.

| Check | State |
|-------|--------|
| ACs | Met |
| Verification | `test_generate_storyboard.py`, `test_write_authorized_storyboard.py`, smoke Storyboard B generation, `test_sprint_status_yaml.py` |
| `sprint-status.yaml` | `22-2-storyboard-b-cluster-view-with-script-context: done` |
| Formal BMAD | Complete — clean review, no findings |
