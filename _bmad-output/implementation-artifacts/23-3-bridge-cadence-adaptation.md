# Story 23-3: Bridge Cadence Adaptation

**Epic:** 23 - Irene Pass 2 Cluster-Aware Narration
**Status:** backlog
**Sprint key:** `23-3-bridge-cadence-adaptation`
**Added:** 2026-04-12
**Depends on:** [20b-3-narration-script-parameters-extension-for-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20b-3-narration-script-parameters-extension-for-clusters.md), [23-1-cluster-aware-dual-channel-grounding.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/23-1-cluster-aware-dual-channel-grounding.md)

## Story

As the bridge cadence system,
I want to fire bridges at cluster seams rather than by arbitrary slide-count or time-interval when clusters are present,
So that the narration flow respects the cluster structure — no jarring bridges mid-cluster, and reliable synthesis bridges at cluster boundaries.

## Acceptance Criteria

**Given** a clustered presentation with cluster_bridge_cadence_override: true
**When** the bridge cadence logic determines where to place bridges
**Then** the following cadence rules must apply:

**AC-1: Cluster-Seam Bridge Firing**
- Bridges fire at cluster boundaries (between the last interstitial of one cluster and the head of the next)
- `bridge_type: cluster_boundary` satisfies the bridge cadence requirement
- Within-cluster slides do NOT trigger bridge cadence (bridge_type: none is exempt)

**AC-2: Existing Cadence as Upper Bound**
- `require_intro_or_outro_every_minutes: 3.0` and `require_intro_or_outro_every_slides: 5` still apply as upper bounds
- If no cluster boundary occurs within 5 slides or 3.0 minutes, a bridge fires anyway (fallback to existing behavior)
- Cluster_boundary bridges reset the cadence counter

**AC-3: Spoken Bridge Enforcement**
- `spoken_bridge_policy.enforcement` applies to `cluster_boundary` bridge_type
- Within-cluster `bridge_type: none` is exempt from spoken bridge enforcement
- When enforcement is `warn` or `error`, only cluster_boundary bridges are checked for spoken cue phrases

**AC-4: Bridge Type Vocabulary Extension**
- Add `cluster_boundary` to `accepted_bridge_types` in runtime_variability.bridge_cadence
- Existing types (intro, outro, both) unchanged
- Validators accept cluster_boundary as valid bridge_type

**AC-5: Non-Clustered Fallback**
- When cluster_bridge_cadence_override is false or cluster_id is null for all segments, existing cadence logic applies unchanged
- Mixed presentations: clustered segments use cluster cadence, flat segments use existing cadence

## Tasks / Subtasks

- [ ] Task 1: Update bridge cadence logic
  - [ ] 1.1: Detect cluster_bridge_cadence_override from narration-script-parameters.yaml
  - [ ] 1.2: When override is true, fire bridges at cluster boundaries only
  - [ ] 1.3: Implement upper-bound fallback (5 slides / 3.0 minutes without a bridge)
  - [ ] 1.4: Reset cadence counter when cluster_boundary bridge fires

- [ ] Task 2: Update spoken bridge enforcement
  - [ ] 2.1: Exempt within-cluster bridge_type: none from spoken bridge checks
  - [ ] 2.2: Apply enforcement (warn/error) only to cluster_boundary bridges
  - [ ] 2.3: Check cluster_boundary bridges for intro/outro phrase patterns

- [ ] Task 3: Extend bridge type vocabulary
  - [ ] 3.1: Add cluster_boundary to accepted_bridge_types
  - [ ] 3.2: Update validators to accept cluster_boundary as valid
  - [ ] 3.3: Update G4 bridge checks to recognize cluster_boundary

- [ ] Task 4: Testing
  - [ ] 4.1: Unit test: bridges fire at cluster seams (not mid-cluster)
  - [ ] 4.2: Unit test: upper-bound fallback fires after 5 slides without boundary
  - [ ] 4.3: Unit test: within-cluster none exempt from enforcement
  - [ ] 4.4: Unit test: cluster_boundary bridge has spoken cue phrases
  - [ ] 4.5: Regression: non-clustered cadence unchanged

## Dev Notes

### Scope Boundary

This story modifies bridge cadence logic only. The parameter infrastructure is 20b-3. The narration writing is 23-1. The G4 validation is 23-2. This story ensures bridges fire at the right places.

### Key Files

- `state/config/narration-script-parameters.yaml` — cadence parameters (modified by 20b-3)
- Bridge cadence logic in Irene Pass 2 / validation scripts
- G4 bridge validation criteria

## References

- [20b-3-narration-script-parameters-extension-for-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20b-3-narration-script-parameters-extension-for-clusters.md) — Parameter source
- [narration-script-parameters.yaml](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/state/config/narration-script-parameters.yaml) — Current cadence config
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 23.3 definition
