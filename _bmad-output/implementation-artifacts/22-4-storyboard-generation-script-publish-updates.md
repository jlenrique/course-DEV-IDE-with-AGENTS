# Story 22-4: Storyboard Generation Script & Publish Updates

**Epic:** 22 - Storyboard & Review Adaptation
**Status:** backlog
**Sprint key:** `22-4-storyboard-generation-script-publish-updates`
**Added:** 2026-04-12
**Depends on:** [22-1-storyboard-a-cluster-view.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/22-1-storyboard-a-cluster-view.md), [22-3-flat-play-sequential-preview-mode.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/22-3-flat-play-sequential-preview-mode.md)

## Story

As Marcus (orchestrator),
I want generate-storyboard.py to read cluster_id from the manifest and group slides accordingly, and the publish-to-GitHub-Pages routine to preserve cluster structure and flat-play mode,
So that both local generation and published snapshots support the full cluster review experience.

## Acceptance Criteria

**Given** generate-storyboard.py is invoked for a clustered presentation
**When** the script reads the segment manifest
**Then** the following generation and publish updates must work:

**AC-1: Cluster-Aware Generation**
- Script reads `cluster_id` from manifest to determine grouping
- Slides with non-null cluster_id grouped into cluster containers
- Slides with null cluster_id rendered as standalone (existing behavior)
- Generation handles mixed presentations (clustered + flat)

**AC-2: Storyboard A Generation**
- Cluster grouping, headers, collapsible containers (per 22-1)
- G2.5 coherence scores read from cluster coherence report and displayed
- Generation succeeds even if coherence report is missing (graceful degradation — no scores shown)

**AC-3: Storyboard B Generation**
- Cluster grouping with narration context (per 22-2)
- Flat-play toggle embedded in generated HTML (per 22-3)
- Generation succeeds even if narration is not yet available (Storyboard A mode only)

**AC-4: GitHub Pages Publish**
- Publish-to-GitHub-Pages snapshot preserves:
  - Cluster structure (collapsible groups)
  - Flat-play mode toggle and JavaScript
  - Coherence score badges
  - All CSS styling
- Published HTML is self-contained (no external CDN dependencies)

**AC-5: Both Storyboard Types**
- Both Storyboard A and B publish routines updated
- Single `generate-storyboard.py` handles both types via `--type a|b` flag (existing pattern)
- Cluster features only render when cluster data is present in manifest

## Tasks / Subtasks

- [ ] Task 1: Update generate-storyboard.py manifest reading
  - [ ] 1.1: Read cluster_id, cluster_role, cluster_position from manifest
  - [ ] 1.2: Group entries by cluster_id (null = standalone)
  - [ ] 1.3: Sort clusters per manifest order

- [ ] Task 2: Integrate 22-1/22-2/22-3 outputs into generation
  - [ ] 2.1: Cluster HTML templates for Storyboard A (collapsible, headers, coherence badges)
  - [ ] 2.2: Narration panel templates for Storyboard B (script, timing, intent)
  - [ ] 2.3: Flat-play toggle template with embedded JavaScript

- [ ] Task 3: Update publish routine
  - [ ] 3.1: Ensure GitHub Pages publish includes all CSS and JavaScript inline
  - [ ] 3.2: Verify collapsible elements work in published static HTML
  - [ ] 3.3: Verify flat-play toggle works in published static HTML

- [ ] Task 4: Graceful degradation
  - [ ] 4.1: Generate without coherence scores if report missing
  - [ ] 4.2: Generate Storyboard A only if narration not yet available
  - [ ] 4.3: Generate non-clustered storyboard if no cluster data in manifest

- [ ] Task 5: Testing
  - [ ] 5.1: Unit test: cluster grouping from manifest
  - [ ] 5.2: Unit test: graceful degradation (missing coherence report, missing narration)
  - [ ] 5.3: Integration test: full generate → publish cycle for clustered presentation
  - [ ] 5.4: Regression: non-clustered generation unchanged (34/34 existing tests pass)

## Dev Notes

### Key File

`skills/bmad-agent-marcus/scripts/generate-storyboard.py` — this is the integration point for all Epic 22 stories. 22-1, 22-2, and 22-3 define the features; this story wires them into the generation pipeline.

### Publish Approach

GitHub Pages serves static HTML. All JavaScript must be inline or bundled. No external CDN dependencies. The `<details>/<summary>` elements (22-1) are natively supported. The flat-play toggle (22-3) JavaScript must be embedded in a `<script>` tag within the HTML.

## References

- [generate-storyboard.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-marcus/scripts/generate-storyboard.py) — Storyboard generator
- [22-1-storyboard-a-cluster-view.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/22-1-storyboard-a-cluster-view.md) — Cluster view
- [22-3-flat-play-sequential-preview-mode.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/22-3-flat-play-sequential-preview-mode.md) — Flat-play mode
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 22.4 definition
