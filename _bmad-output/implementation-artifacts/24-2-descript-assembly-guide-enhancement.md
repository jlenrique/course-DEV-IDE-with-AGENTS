# Story 24-2: Descript Assembly Guide Enhancement

**Epic:** 24 - Assembly, Handoff & Regression Hardening
**Status:** backlog
**Sprint key:** `24-2-descript-assembly-guide-enhancement`
**Added:** 2026-04-12
**Depends on:** [24-1-assembly-contract-hardening.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/24-1-assembly-contract-hardening.md)

## Story

As Desmond (Descript operator agent),
I want the assembly guide to label each slide with cluster membership, role, and transition annotations,
So that the human operator in Descript knows exactly which slides form a cluster, what transitions to use within vs. between clusters, and how to treat interstitial audio segments.

## Acceptance Criteria

**Given** the assembly guide is generated for a clustered presentation
**When** Desmond or a human operator reads the guide in Descript
**Then** the following annotations must be present:

**AC-1: Cluster Membership Labels**
- Each slide labeled with cluster membership and role:
  - Head: `[HEAD — Cluster 3: "Cognitive Load Theory"]`
  - Interstitial: `[INTERSTITIAL 2/3 — emphasis-shift: "working memory"]`
- Non-clustered slides: `[STANDALONE]`

**AC-2: Transition Annotations**
- Within-cluster transitions: `[TRANSITION: cut — no effect]`
- Between-cluster transitions: `[TRANSITION: beat/pause — brief black or fade]`
- Bridge text shown at cluster boundaries with the synthesis + forward pull content

**AC-3: Audio Treatment Notes**
- Per interstitial: `[AUDIO: VO segment, 10-16s]` — confirm this is voice-over, not silence
- Per head: `[AUDIO: VO segment, 32-56s]`
- Cluster boundary: `[AUDIO: bridge VO, 15-20s]`

**AC-4: Behavioral Intent and Bridge Context**
- Per-segment behavioral_intent shown alongside audio treatment
- Per-segment bridge_type shown for transition guidance
- Cluster-level master_behavioral_intent shown in cluster header

**AC-5: Pacing Guidance**
- Within-cluster: "maintain tight pacing — no pauses between slides"
- Between-cluster: "insert 0.5-1.0s beat between clusters for cognitive reset"
- Cluster-boundary bridge: "bridge audio covers the transition — no additional pause needed"

## Tasks / Subtasks

- [ ] Task 1: Implement cluster membership labeling
  - [ ] 1.1: Generate HEAD/INTERSTITIAL/STANDALONE labels from manifest
  - [ ] 1.2: Include cluster topic, interstitial type, isolation target in labels
  - [ ] 1.3: Number interstitials within cluster (e.g., "2/3")

- [ ] Task 2: Implement transition annotations
  - [ ] 2.1: Detect within-cluster vs. between-cluster transitions from manifest sequence
  - [ ] 2.2: Generate transition annotation text (cut vs. beat/pause)
  - [ ] 2.3: Include bridge text content at cluster boundaries

- [ ] Task 3: Implement audio treatment notes
  - [ ] 3.1: Calculate expected audio duration per segment from word count at 150 WPM
  - [ ] 3.2: Label each segment with VO type and expected duration
  - [ ] 3.3: Confirm interstitials are VO, not silence

- [ ] Task 4: Implement pacing guidance
  - [ ] 4.1: Add within-cluster pacing note (tight, no pauses)
  - [ ] 4.2: Add between-cluster pacing note (0.5-1.0s beat)
  - [ ] 4.3: Add bridge pacing note (bridge audio covers transition)

- [ ] Task 5: Testing
  - [ ] 5.1: Unit test: cluster membership label generation
  - [ ] 5.2: Unit test: transition annotation generation
  - [ ] 5.3: Unit test: audio duration calculations
  - [ ] 5.4: Regression: non-clustered guide unchanged

## Dev Notes

### Scope Boundary

This story enhances the Descript assembly guide. The assembly contract is 24-1. ElevenLabs audio handling is 24-3. This story is the operator-facing documentation layer.

### Key Files

- `skills/compositor/` — Assembly guide generation templates
- `skills/bmad-agent-desmond/` — Desmond agent (consumes the guide)

## References

- [24-1-assembly-contract-hardening.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/24-1-assembly-contract-hardening.md) — Assembly contract
- [compositor skill](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/compositor/) — Guide templates
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 24.2 definition
