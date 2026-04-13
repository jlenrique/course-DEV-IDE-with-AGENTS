# Story 22-1: Storyboard A Cluster View

**Epic:** 22 - Storyboard & Review Adaptation
**Status:** done
**Sprint key:** `22-1-storyboard-a-cluster-view`
**Added:** 2026-04-12
**Depends on:** [21-3-cluster-dispatch-sequencing.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/21-3-cluster-dispatch-sequencing.md), [21-4-cluster-coherence-validation.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/21-4-cluster-coherence-validation.md)

## Story

As an operator reviewing a clustered presentation,
I want Storyboard A to render clusters as collapsible visual groups with coherence indicators,
So that I can audit cluster structure, pacing, and visual coherence at a glance before advancing to narration.

## Acceptance Criteria

**Given** a clustered segment manifest with Gary dispatch results
**When** `generate-storyboard.py` renders Storyboard A
**Then** the following cluster view must be present:

**AC-1: Collapsible Cluster Groups**
- Clusters render as collapsible HTML groups
- Head slide is prominent (larger thumbnail, full metadata)
- Interstitials indented beneath the head with smaller thumbnails
- Cluster group is collapsible/expandable via click
- Default state: collapsed (pacing audit view)

**AC-2: Cluster Header Row**
- Each cluster group has a header row showing:
  - Topic label (from head slide's topic)
  - Cluster narrative arc (one-sentence emotional journey)
  - Interstitial count (e.g., "3 interstitials")
  - Interstitial types (e.g., "reveal, emphasis-shift, bridge-text")
  - Cluster coherence score from G2.5 (pass/warn/fail badge)

**AC-3: Collapsed View = Pacing Audit**
- When collapsed: cluster headers only, showing count + duration balance
- Allows operator to see overall presentation pacing at a glance
- Cluster count, estimated total duration per cluster, duration balance across clusters

**AC-4: Expanded View = Per-Slide QA**
- When expanded: head + interstitial thumbnails with full metadata per slide
- Per-interstitial G2.5 coherence indicator (green/yellow/red border)
- Slide-level metadata: interstitial_type, isolation_target, cluster_position

**AC-5: Visual Spacing**
- Inter-cluster gap visually distinct from within-cluster spacing
- Within-cluster: tight spacing (visual grouping)
- Between-cluster: prominent gap or divider line
- Non-clustered slides (cluster_id: null) render as standalone (existing behavior)

**AC-6: Backward Compatibility**
- Non-clustered presentations render identically to current Storyboard A (no cluster headers, no collapsing)
- Mixed presentations (some clustered, some flat) render both correctly

## Tasks / Subtasks

- [x] Task 1: Extend generate-storyboard.py for cluster grouping
  - [x] 1.1: Read cluster_id from segment manifest, group slides by cluster
  - [x] 1.2: Separate clustered slides from flat slides
  - [x] 1.3: Order clusters per manifest sequence

- [x] Task 2: Implement cluster header row
  - [x] 2.1: Extract topic label from head slide metadata
  - [x] 2.2: Display narrative_arc, interstitial count, types
  - [x] 2.3: Read G2.5 coherence scores and render as badge (pass=green, warn=yellow, fail=red)

- [x] Task 3: Implement collapsible groups
  - [x] 3.1: Add HTML/CSS collapsible container per cluster
  - [x] 3.2: Head slide always visible; interstitials in collapsible section
  - [x] 3.3: Default collapsed state; toggle on click
  - [x] 3.4: "Expand All" / "Collapse All" controls

- [x] Task 4: Implement per-slide QA view (expanded)
  - [x] 4.1: Render interstitial thumbnails indented below head
  - [x] 4.2: Per-interstitial coherence indicator (colored border from G2.5 score)
  - [x] 4.3: Show interstitial_type, isolation_target, cluster_position per slide

- [x] Task 5: Visual spacing and non-clustered handling
  - [x] 5.1: CSS for inter-cluster gap (prominent divider)
  - [x] 5.2: CSS for within-cluster spacing (tight grouping)
  - [x] 5.3: Non-clustered slides render standalone (existing behavior preserved)

- [x] Task 6: Testing
  - [x] 6.1: Unit test: cluster grouping from manifest (clustered + flat + mixed)
  - [x] 6.2: Visual test: generate Storyboard A from Storyboard A trial data, inspect HTML
  - [x] 6.3: Regression: non-clustered manifest produces identical output to current behavior

## Completion Notes

- Implemented in:
  - `skills/bmad-agent-marcus/scripts/generate-storyboard.py`
  - `skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py`
- Party Mode decisions upheld:
  - Flat `slides[]` and `rows[]` remain canonical.
  - Cluster metadata and `cluster_groups[]` are additive.
  - `--cluster-coherence-report` remains explicit opt-in.
- Verification evidence:
  - `python -m pytest skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py -q` -> `38 passed`
  - Included in consolidated Wave 1 rerun (2026-04-12) -> total `158 passed`

## Dev Notes

### Key File

`skills/bmad-agent-marcus/scripts/generate-storyboard.py` — the existing storyboard generator. This story extends it, not replaces it.

### G2.5 Data Source

Coherence scores come from the G2.5 gate output (21-4). If G2.5 hasn't run (e.g., non-clustered), coherence indicators are omitted. The storyboard reads scores from the cluster coherence report, not re-computes them.

### HTML/CSS Approach

Use native HTML `<details>/<summary>` elements for collapsible groups (no JavaScript dependency). Style with CSS for the visual distinction. GitHub Pages publish must preserve the interactive elements.

## References

- [generate-storyboard.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-marcus/scripts/generate-storyboard.py) — Existing storyboard generator
- [21-4-cluster-coherence-validation.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/21-4-cluster-coherence-validation.md) — G2.5 coherence scores
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 22.1 definition
