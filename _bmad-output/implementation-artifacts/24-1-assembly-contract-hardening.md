# Story 24-1: Assembly Contract Hardening

**Epic:** 24 - Assembly, Handoff & Regression Hardening
**Status:** backlog
**Sprint key:** `24-1-assembly-contract-hardening`
**Added:** 2026-04-12
**Depends on:** [23-1-cluster-aware-dual-channel-grounding.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/23-1-cluster-aware-dual-channel-grounding.md), [21-3-cluster-dispatch-sequencing.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/21-3-cluster-dispatch-sequencing.md)

## Story

As the assembly pipeline (Compositor / Desmond),
I want the assembly contract to handle clustered presentations with correct slide-to-audio mapping and cluster-ordered asset management,
So that the assembly bundle preserves cluster sequence and correctly pairs shorter interstitial audio segments with their slides.

## Acceptance Criteria

**Given** an assembly bundle for a clustered presentation
**When** the assembly pipeline processes the bundle
**Then** the following contract rules must hold:

**AC-1: Manifest Order Is Authoritative**
- Assembly respects segment manifest order for all slides (heads and interstitials)
- No reordering, deduplication, or filtering based on cluster metadata
- Manifest order = presentation order = assembly order

**AC-2: Slide-Index-to-Audio Mapping**
- Each slide (head or interstitial) maps to exactly one audio segment
- Interstitial audio segments are shorter (10-16 seconds) — assembly handles short audio correctly
- No padding, silence insertion, or duration normalization at assembly level (that's 24-3)

**AC-3: Cluster-Ordered Asset Management**
- Assembly bundle preserves cluster structure: visuals sorted by cluster in the bundle directory
- Cluster directory structure: `cluster_{cluster_id}/head.png`, `cluster_{cluster_id}/interstitial_1.png`, etc.
- Or flat structure with cluster-encoded filenames (per 21-3 naming convention)
- Non-clustered slides in standard flat structure

**AC-4: sync-visuals Compositor Handling**
- `sync-visuals` compositor handles interstitial PNGs identically to head PNGs
- No special treatment based on cluster_role — a PNG is a PNG
- Cluster metadata is in the manifest, not in the asset pipeline

**AC-5: Assembly Guide Cluster Context**
- Assembly guide (for Desmond/Descript operator) includes cluster membership per slide
- Guide preserves behavioral_intent and bridge_type context
- Within-cluster transitions annotated (see 24-2 for full guide enhancement)

## Tasks / Subtasks

- [ ] Task 1: Update assembly manifest processing
  - [ ] 1.1: Verify manifest reader handles interstitial segment entries
  - [ ] 1.2: Verify slide-to-audio mapping works with shorter interstitial audio
  - [ ] 1.3: Verify manifest order is preserved through entire assembly chain

- [ ] Task 2: Update asset management
  - [ ] 2.1: Handle cluster-encoded PNG filenames from dispatch (21-3)
  - [ ] 2.2: Bundle directory structure supports cluster grouping
  - [ ] 2.3: sync-visuals treats interstitial PNGs identically to head PNGs

- [ ] Task 3: Update assembly guide generation
  - [ ] 3.1: Include cluster membership per slide in guide output
  - [ ] 3.2: Include behavioral_intent and bridge_type per segment
  - [ ] 3.3: Annotate within-cluster vs. cluster-boundary transitions

- [ ] Task 4: Testing
  - [ ] 4.1: Unit test: manifest processing with interstitial entries
  - [ ] 4.2: Unit test: slide-to-audio mapping with short audio segments
  - [ ] 4.3: Unit test: asset bundle directory structure
  - [ ] 4.4: Regression: non-clustered assembly unchanged

## Dev Notes

### Scope Boundary

This story hardens the assembly contract for cluster awareness. The full Descript guide enhancement is 24-2. ElevenLabs short segment handling is 24-3. Regression test suite is 24-4.

### Key Files

- `skills/compositor/` — Assembly guide generation
- `skills/bmad-agent-desmond/` — Descript operator agent
- Segment manifest reader in assembly pipeline

## References

- [compositor skill](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/compositor/) — Assembly guide
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 24.1 definition
