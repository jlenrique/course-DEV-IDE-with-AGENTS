# Story 20b-3: Narration Script Parameters Extension for Clusters

**Epic:** 20b - Irene Cluster Intelligence - Implementation
**Status:** done
**Sprint key:** `20b-3-narration-script-parameters-extension-for-clusters`
**Added:** 2026-04-12
**Depends on:** [20b-1-irene-pass1-cluster-planning-implementation.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20b-1-irene-pass1-cluster-planning-implementation.md), [20a-3-cluster-narrative-arc-schema.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-3-cluster-narrative-arc-schema.md)

## Story

As Irene (Pass 2),
I want narration-script-parameters.yaml extended with cluster-specific word ranges, bridge policies, and cadence overrides,
So that when I write narration for clustered presentations, my word budgets, bridge decisions, and pacing rules are calibrated for the head/interstitial split rather than treating every segment identically.

## Acceptance Criteria

**Given** a clustered presentation enters Irene Pass 2
**When** Irene reads narration-script-parameters.yaml
**Then** the following cluster-specific parameters must be present and enforced:

**AC-1: Cluster Head Word Range**
- `cluster_head_word_range: [80, 140]` — heads get extended upper bound (vs. default mean_words_per_slide: 95)
- G4 validation must accept head segments within this range without flagging max_words_per_slide (220) as the relevant cap

**AC-2: Interstitial Word Range**
- `interstitial_word_range: [25, 40]` — lower bound raised from min_words_per_slide (25) to enforce a floor that prevents degenerate 5-word interstitials
- G4 validation flags interstitial segments outside this range

**AC-3: Within-Cluster Bridge Policy**
- `within_cluster_bridge_policy: none` — default; no spoken bridge within a cluster
- Exception: `pivot` allowed only for `tension` position (explicit override, not default)
- Irene must suppress bridge generation for within-cluster transitions unless cluster_position == tension

**AC-4: Cluster Boundary Bridge Style**
- `cluster_boundary_bridge_style: synthesis_plus_forward_pull` — one sentence synthesis of what the cluster covered + one sentence forward pull to next topic
- Duration target: 15-20 seconds (approx 37-50 words at 150 WPM)

**AC-5: Bridge Cadence Override**
- `cluster_bridge_cadence_override: true` — when clusters are present, bridges fire at cluster seams, not by `require_intro_or_outro_every_slides` (5) or `require_intro_or_outro_every_minutes` (3.0)
- Existing cadence settings still apply as upper bounds: if no cluster boundary occurs within 5 slides or 3 minutes, a bridge fires anyway
- `cluster_boundary` bridge_type satisfies the cadence requirement

**AC-6: Backward Compatibility**
- Non-clustered presentations ignore all cluster parameters (nullable/conditional)
- Existing narration-script-parameters.yaml consumers unaffected
- All existing G4 criteria (G4-01 through G4-15) pass unchanged for non-clustered runs

## Tasks / Subtasks

- [x] Task 1: Extend narration-script-parameters.yaml
  - [x] 1.1: Add `cluster_narration` section with cluster_head_word_range and interstitial_word_range
  - [x] 1.2: Add `within_cluster_bridge_policy` under pedagogical_bridging
  - [x] 1.3: Add `cluster_boundary_bridge_style` under pedagogical_bridging
  - [x] 1.4: Add `cluster_bridge_cadence_override` under runtime_variability.bridge_cadence
  - [x] 1.5: Bump schema_version to "1.1"

- [x] Task 2: Update parameter consumers
  - [x] 2.1: Ensure Irene Pass 2 reads cluster_narration section when cluster_id present in manifest
  - [x] 2.2: Update bridge generation logic to check cluster_bridge_cadence_override before applying slide-count/time-based cadence
  - [x] 2.3: Update bridge_type vocabulary to include `cluster_boundary` as accepted type

- [x] Task 3: Extend G4 validation for cluster parameters
  - [x] 3.1: G4 validator checks head segments against cluster_head_word_range (not global max)
  - [x] 3.2: G4 validator checks interstitial segments against interstitial_word_range
  - [x] 3.3: G4 validator accepts bridge_type: none within clusters (no spoken bridge enforcement)
  - [x] 3.4: G4 validator accepts bridge_type: cluster_boundary at cluster seams

- [x] Task 4: Regression testing
  - [x] 4.1: Non-clustered payloads pass G4 unchanged
  - [x] 4.2: Clustered payload with correct word ranges passes G4
  - [x] 4.3: Clustered payload with interstitial >40 words fails G4
  - [x] 4.4: Clustered payload with within-cluster bridge (non-tension) fails G4
  - [x] 4.5: Bridge cadence override correctly fires at cluster boundaries

## Completion Notes

- Implemented in:
  - `state/config/narration-script-parameters.yaml`
  - `state/config/fidelity-contracts/g4-narration-script.yaml`
  - `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`
  - `skills/bmad-agent-marcus/scripts/tests/test-narration-config-schemas.py`
  - `skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py`
- Consolidated Wave 1 verification rerun (2026-04-12):
  - `python -m pytest skills/bmad-agent-marcus/scripts/tests/test-narration-config-schemas.py skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py skills/bmad-agent-marcus/scripts/tests/test_interstitial_redispatch_protocol.py skills/bmad-agent-marcus/scripts/tests/test_run_interstitial_redispatch.py -q`
  - Result: `158 passed` (with existing unrelated `pytest_asyncio` deprecation warning)

## Dev Notes

### Scope Boundary

This story modifies `state/config/narration-script-parameters.yaml` and its consumers. Does NOT implement the actual narration writing (Epic 23) or assembly changes (Epic 24). Pure parameter infrastructure.

### Key File

`state/config/narration-script-parameters.yaml` — current schema_version "1.0", sections 1-9. Cluster parameters add to sections 1 (density), 5 (bridging), and 9 (runtime_variability).

### Risk: Parameter Conflicts

If `cluster_head_word_range[1]` (140) exceeds existing `max_words_per_slide` (220), no conflict. But if future density adjustments push head range higher, the global max becomes the binding constraint. Document the precedence rule: cluster-specific range applies first, global max is the hard ceiling.

## References

- [narration-script-parameters.yaml](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/state/config/narration-script-parameters.yaml) — Current parameter file
- [20b-1-irene-pass1-cluster-planning-implementation.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20b-1-irene-pass1-cluster-planning-implementation.md) — Cluster planning (sets manifest fields this story's parameters govern)
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 20b.3 definition
