# Story 24-3: ElevenLabs Short Segment Handling

**Epic:** 24 - Assembly, Handoff & Regression Hardening
**Status:** backlog
**Sprint key:** `24-3-elevenlabs-short-segment-handling`
**Added:** 2026-04-12
**Depends on:** [23-1-cluster-aware-dual-channel-grounding.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/23-1-cluster-aware-dual-channel-grounding.md)

## Story

As the ElevenLabs audio pipeline,
I want to handle 10-16 second interstitial audio segments with reduced buffers and validated quality,
So that short interstitial audio segments maintain the same quality as longer head segments while preserving tight within-cluster pacing.

## Acceptance Criteria

**Given** ElevenLabs receives narration text for interstitial segments (25-40 words, 10-16 seconds)
**When** audio is generated
**Then** the following short-segment handling must apply:

**AC-1: Quality Validation for Short Segments**
- Validate that ElevenLabs handles 10-16 second segments without degradation
- Check: no clipping, no truncation, no excessive silence padding
- Check: pronunciation quality comparable to longer segments
- Minimum segment length: 25 words (enforced by G4-17, but validated here too)

**AC-2: Within-Cluster Reduced Buffer**
- Within-cluster segments use reduced buffer: 0.5s lead-in + 0.5s tail (vs. standard 1.5s)
- Reduced buffer maintains tight within-cluster flow (no perceptible gap)
- Buffer reduction applies to both head and interstitial segments within a cluster

**AC-3: Between-Cluster Standard Buffer**
- Between-cluster segments retain standard buffer (1.5s lead-in + 1.5s tail)
- Cluster-boundary bridge segments use standard buffer
- Non-clustered segments use standard buffer (existing behavior)

**AC-4: Per-Segment Buffer Override**
- Update `elevenlabs_operations.py` to accept per-segment buffer overrides
- Buffer determined by `cluster_role` and position in sequence:
  - Within-cluster: reduced buffer (0.5s + 0.5s)
  - Cluster boundary: standard buffer (1.5s + 1.5s)
  - Non-clustered: standard buffer (1.5s + 1.5s)
- Override keyed to cluster metadata from manifest

**AC-5: Backward Compatibility**
- Non-clustered presentations use standard buffer everywhere (existing behavior)
- No change to ElevenLabs API call parameters beyond buffer timing
- Existing audio generation tests pass unchanged

## Tasks / Subtasks

- [ ] Task 1: Validate short segment quality
  - [ ] 1.1: Generate test audio for 25-word, 30-word, and 40-word segments
  - [ ] 1.2: Check for clipping, truncation, silence padding artifacts
  - [ ] 1.3: Compare pronunciation quality against longer (95-word) baseline
  - [ ] 1.4: Document minimum viable segment length for ElevenLabs

- [ ] Task 2: Implement per-segment buffer override
  - [ ] 2.1: Add buffer_override parameter to elevenlabs_operations.py generation function
  - [ ] 2.2: Read cluster_role from manifest to determine buffer tier
  - [ ] 2.3: Apply reduced buffer (0.5s + 0.5s) for within-cluster segments
  - [ ] 2.4: Apply standard buffer (1.5s + 1.5s) for between-cluster and non-clustered segments

- [ ] Task 3: Implement buffer stitching logic
  - [ ] 3.1: When concatenating audio segments, use the appropriate buffer between segments
  - [ ] 3.2: Within-cluster: minimal gap (0.5s tail + 0.5s lead-in = 1.0s total gap)
  - [ ] 3.3: Between-cluster: standard gap (1.5s tail + 1.5s lead-in = 3.0s total gap)

- [ ] Task 4: Testing
  - [ ] 4.1: Unit test: buffer override applied correctly per cluster_role
  - [ ] 4.2: Unit test: non-clustered segments use standard buffer
  - [ ] 4.3: Integration test: generate short audio segment via ElevenLabs API (credit-consuming, manual trigger)
  - [ ] 4.4: Regression: existing ElevenLabs tests pass unchanged

## Dev Notes

### Key File

`scripts/api_clients/elevenlabs_operations.py` — the audio generation pipeline. This story adds buffer override parameters to the generation function.

### Risk: ElevenLabs Minimum Duration

ElevenLabs may have minimum audio duration requirements or quality degradation below a certain length. The 25-word / 10-second floor should be safe, but validate empirically in Task 1 before committing to the buffer strategy.

### Scope Boundary

This story handles audio generation quality and timing. Assembly guide annotations are 24-2. The assembly pipeline contract is 24-1.

## References

- [elevenlabs_operations.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/scripts/api_clients/elevenlabs_operations.py) — Audio pipeline
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 24.3 definition
