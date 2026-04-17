# Story 23-3: Bridge Cadence Adaptation

**Epic:** 23 - Irene Pass 2 Cluster-Aware Narration
**Status:** done
**Sprint key:** `23-3-bridge-cadence-adaptation`
**Added:** 2026-04-12
**Depends on:** [20b-3-narration-script-parameters-extension-for-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20b-3-narration-script-parameters-extension-for-clusters.md), [23-1-cluster-aware-dual-channel-grounding.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/23-1-cluster-aware-dual-channel-grounding.md)

## Story

As the bridge cadence system,
I want to fire bridges at cluster seams rather than by arbitrary slide-count or time-interval when clusters are present,
So that the narration flow respects the cluster structure - no jarring bridges mid-cluster, and reliable synthesis bridges at cluster boundaries.

## Acceptance Criteria

**Given** a clustered presentation with cluster_bridge_cadence_override: true
**When** the bridge cadence logic determines where to place bridges
**Then** the following cadence rules must apply:

**AC-1: Cluster-Seam Bridge Firing**
- Bridges fire at cluster boundaries (between the last interstitial of one cluster and the head of the next)
- `bridge_type: cluster_boundary` satisfies the bridge cadence requirement
- Within-cluster slides do NOT trigger bridge cadence (`bridge_type: none` is exempt)

**AC-2: Existing Cadence as Upper Bound**
- `require_intro_or_outro_every_minutes: 3.0` and `require_intro_or_outro_every_slides: 5` still apply as upper bounds
- If no cluster boundary occurs within 5 slides or 3.0 minutes, a bridge fires anyway (fallback to existing behavior)
- `cluster_boundary` bridges reset the cadence counter

**AC-3: Spoken Bridge Enforcement**
- `spoken_bridge_policy.enforcement` applies to `cluster_boundary` bridge_type
- Within-cluster `bridge_type: none` is exempt from spoken bridge enforcement
- When enforcement is `warn` or `error`, only `cluster_boundary` bridges are checked for spoken cue phrases

**AC-4: Bridge Type Vocabulary Extension**
- Add `cluster_boundary` to `accepted_bridge_types` in `runtime_variability.bridge_cadence`
- Existing types (`intro`, `outro`, `both`) unchanged
- Validators accept `cluster_boundary` as valid `bridge_type`

**AC-5: Non-Clustered Fallback**
- When `cluster_bridge_cadence_override` is false or `cluster_id` is null for all segments, existing cadence logic applies unchanged
- Mixed presentations: clustered segments use cluster cadence, flat segments use existing cadence

## Tasks / Subtasks

- [x] Task 1: Update bridge cadence logic
  - [x] 1.1: Detect `cluster_bridge_cadence_override` from `narration-script-parameters.yaml`
  - [x] 1.2: When override is true, fire bridges at cluster boundaries only
  - [x] 1.3: Implement upper-bound fallback (5 slides / 3.0 minutes without a bridge)
  - [x] 1.4: Reset cadence counter when `cluster_boundary` bridge fires

- [x] Task 2: Update spoken bridge enforcement
  - [x] 2.1: Exempt within-cluster `bridge_type: none` from spoken bridge checks
  - [x] 2.2: Apply enforcement (`warn`/`error`) only to `cluster_boundary` bridges for clustered records
  - [x] 2.3: Check `cluster_boundary` bridges for intro/outro phrase patterns

- [x] Task 3: Extend bridge type vocabulary
  - [x] 3.1: Confirm `cluster_boundary` remains in accepted bridge types
  - [x] 3.2: Keep validators accepting `cluster_boundary` as valid
  - [x] 3.3: Preserve the cluster-aware G4 bridge checks added by 23-2

- [x] Task 4: Testing
  - [x] 4.1: Unit test: bridges fire at cluster seams (not mid-cluster)
  - [x] 4.2: Unit test: upper-bound fallback fires after 5 slides without boundary
  - [x] 4.3: Unit test: within-cluster none exempt from enforcement
  - [x] 4.4: Unit test: `cluster_boundary` bridge has spoken cue phrases
  - [x] 4.5: Regression: non-clustered cadence unchanged

## Dev Notes

### Scope Boundary

This story modifies bridge cadence logic only. The parameter infrastructure is 20b-3. The narration writing is 23-1. The G4 validation is 23-2. This story ensures bridges fire at the right places.

### Key Files

- `state/config/narration-script-parameters.yaml` - cadence parameters (modified by 20b-3)
- Bridge cadence logic in Irene Pass 2 / validation scripts
- G4 bridge validation criteria

## References

- [20b-3-narration-script-parameters-extension-for-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20b-3-narration-script-parameters-extension-for-clusters.md) - parameter source
- [narration-script-parameters.yaml](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/state/config/narration-script-parameters.yaml) - current cadence config
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) - story 23.3 definition

## Dev Agent Record

### Implementation Plan

- Keep the implementation boundary inside the deterministic Pass 2 validator and its regression suite unless the code inspection reveals a conflicting upstream cadence enforcement path.
- Tighten clustered cadence so cluster seams prefer `bridge_type: cluster_boundary`, while slide/minute caps remain upper-bound fallback logic rather than the primary scheduling rule.
- Preserve non-clustered behavior and mixed clustered/flat compatibility, then validate with focused cadence tests before full regression and formal review.

### Debug Log

- 2026-04-15: Marked `23-3` in progress after `23-2` formal review closure and loaded the current cadence config, Pass 2 validator, and existing cadence/cluster tests.
- 2026-04-15: Reused the BMAD party-mode review panel to confirm the implementation boundary should stay validator-scoped and to identify the highest-risk cadence regressions before editing.
- 2026-04-15: Tightened seam detection so only true cluster-to-cluster transitions count as `cluster_boundary` opportunities, added `cluster_role` to ordered slide records, and normalized accepted bridge types to lowercase.
- 2026-04-15: Split cadence satisfaction from bridge vocabulary so clustered interstitial `pivot` beats no longer satisfy cadence debt and clustered spoken-cue enforcement only checks `cluster_boundary`.
- 2026-04-15: Closed a formal review finding by requiring `fallback_due=True` before clustered non-seam `intro`/`outro`/`both` bridges can satisfy cadence, then added a regression proving clustered heads cannot reset cadence early.
- 2026-04-15: Closed a second formal review finding by adding an aggregated-record regression showing a real seam still passes when a same-slide flat record is normalized ahead of the clustered head.

### Completion Notes

- `validate-irene-pass2-handoff.py` now treats cluster seams as direct cluster-to-cluster transitions only, preventing flat-to-cluster and cluster-to-flat edges from being misread as seam obligations.
- Clustered cadence now resets on `cluster_boundary` seams or on generic fallback bridges only when the upper bound is already due; `pivot` no longer clears cadence debt.
- Clustered spoken bridge enforcement is now limited to `cluster_boundary` records, while flat/non-clustered narration keeps the earlier intro/outro/both spoken-cue checks.
- Formal BMAD review completed clean after two remediations:
  - Clustered heads can no longer clear cadence debt early with `intro`/`outro`/`both`.
  - Seam detection is now covered against an aggregated same-slide record layout that could otherwise have hidden a true boundary.
- Validation passed:
  - `.\.venv\Scripts\python.exe -m pytest -q skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py skills/bmad-agent-marcus/scripts/tests/test-narration-config-schemas.py tests/test_cluster_aware_pass2_contract_docs.py`
  - Result: `149 passed`
- Full regression passed:
  - `.\.venv\Scripts\python.exe -m pytest -q`
  - Result: `700 passed, 1 skipped, 27 deselected`

## File List

- `_bmad-output/implementation-artifacts/23-3-bridge-cadence-adaptation.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `next-session-start-here.md`
- `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`
- `skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py`

## Change Log

- 2026-04-15: Story moved to in-progress for disciplined BMAD implementation.
- 2026-04-15: Implemented cluster-aware bridge cadence adaptation, added focused clustered cadence regressions, completed formal BMAD review clean, and moved the story to done.
