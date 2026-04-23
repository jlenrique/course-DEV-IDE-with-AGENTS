# Story 24-2: Descript Assembly Guide Enhancement

**Epic:** 24 - Assembly, Handoff & Regression Hardening
**Status:** done (2026-04-23: layered review complete, findings triaged, validation green)
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

- [x] Task 1: Implement cluster membership labeling
  - [x] 1.1: Generate HEAD/INTERSTITIAL/STANDALONE labels from manifest
  - [x] 1.2: Include cluster topic, interstitial type, isolation target in labels
  - [x] 1.3: Number interstitials within cluster (e.g., "2/3")

- [x] Task 2: Implement transition annotations
  - [x] 2.1: Detect within-cluster vs. between-cluster transitions from manifest sequence
  - [x] 2.2: Generate transition annotation text (cut vs. beat/pause)
  - [x] 2.3: Include bridge text content at cluster boundaries

- [x] Task 3: Implement audio treatment notes
  - [x] 3.1: Calculate expected audio duration per segment from word count at 150 WPM
  - [x] 3.2: Label each segment with VO type and expected duration
  - [x] 3.3: Confirm interstitials are VO, not silence

- [x] Task 4: Implement pacing guidance
  - [x] 4.1: Add within-cluster pacing note (tight, no pauses)
  - [x] 4.2: Add between-cluster pacing note (0.5-1.0s beat)
  - [x] 4.3: Add bridge pacing note (bridge audio covers transition)

- [x] Task 5: Testing
  - [x] 5.1: Unit test: cluster membership label generation
  - [x] 5.2: Unit test: transition annotation generation
  - [x] 5.3: Unit test: audio duration calculations
  - [x] 5.4: Regression: non-clustered guide unchanged

## Dev Agent Record

### Completion Notes

- Extended timeline row derivation to emit explicit operator-facing labels for head/interstitial/standalone segments, including interstitial numbering within each cluster.
- Added transition annotations and pacing guidance derived from manifest sequence state (`within-cluster`, `cluster-boundary`, `flat`) plus `bridge_type` handling.
- Added audio treatment guidance with fixed cluster bands (`10-16s`, `32-56s`, `15-20s`) and computed per-segment 150 WPM duration estimates from `narration_text`.
- Enhanced guide rendering with a cluster overview section that surfaces cluster-level `master_behavioral_intent`, plus boundary bridge text snippets for synthesis/forward-pull transitions.
- Hardened bridge guidance classification by normalizing `bridge_type` values to lowercase before applying boundary annotations and pacing rules.

### Review Gate (bmad-code-review)

- Blind Hunter: returned broad speculative risks; triaged as non-blocking or out-of-scope noise.
- Edge Case Hunter: surfaced one actionable hardening item (`bridge_type` case sensitivity); remediated with normalization + regression test.
- Acceptance Auditor: **PASS**, no acceptance-criteria violations.
- Disposition: 1 patch applied, remaining findings dismissed as non-actionable for this story.

### Validation

- `python -m pytest -q skills/compositor/scripts/tests/test_compositor_operations.py` → **17 passed**.
- `python -m ruff check skills/compositor/scripts/compositor_operations.py skills/compositor/scripts/tests/test_compositor_operations.py` → **all checks passed**.

## File List

- `skills/compositor/scripts/compositor_operations.py`
- `skills/compositor/scripts/tests/test_compositor_operations.py`
- `_bmad-output/implementation-artifacts/24-2-descript-assembly-guide-enhancement.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- 2026-04-23: Implemented Descript guide cluster labels, transition/audio annotations, pacing guidance, and 150-WPM estimates with regression coverage; promoted story to review.
- 2026-04-23: Completed layered code review, applied case-normalization hardening for `bridge_type`, and promoted story to done.

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
