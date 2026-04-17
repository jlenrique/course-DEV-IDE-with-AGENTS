# Story 21-5: Interstitial Re-dispatch Protocol

**Epic:** 21 - Gary Cluster Dispatch - Gamma Interpretation
**Status:** done
**Sprint key:** `21-5-interstitial-re-dispatch-protocol`
**Added:** 2026-04-12
**Depends on:** [21-4-cluster-coherence-validation.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/21-4-cluster-coherence-validation.md), [21-2-cluster-aware-prompt-engineering.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/21-2-cluster-aware-prompt-engineering.md)

## Story

As Gary,
I want a targeted re-dispatch protocol for interstitials that fail coherence validation,
So that I can fix individual interstitials using perception data from the first pass rather than re-dispatching the entire cluster at full Gamma credit cost.

## Acceptance Criteria

**Given** G2.5 coherence validation has flagged one or more interstitials in a cluster
**When** the operator selects re-dispatch-interstitial for a specific interstitial
**Then** the following re-dispatch protocol must execute:

**AC-1: Targeted Re-dispatch**
- Only the failed interstitial re-dispatches (not the head, not passing interstitials)
- Re-dispatch prompt is tightened using head slide perception data from the G2.5 pass
- Perception-informed prompt additions: explicit color hex values, font family names, background treatment description extracted from head PNG

**AC-2: Partial Re-run Contract**
- Re-dispatch generates a new Gamma session for the single interstitial
- The re-dispatched interstitial uses the head slide's theme_id and style parameters
- New PNG replaces the failed one in the cluster's asset directory
- Cluster metadata updated to reflect re-dispatch (re_dispatch_count incremented)

**AC-3: Circuit Breaker**
- Max 2 re-dispatch attempts per interstitial (consistent with existing literal-visual retry pattern)
- After 2 failed re-dispatches, circuit breaker fires
- Operator chooses fallback:
  - `accept-as-is`: Use the best available version (original or re-dispatch)
  - `replace-with-pace-reset`: Swap the interstitial for a minimal pace-reset slide
  - `drop-from-cluster`: Remove interstitial, decrement cluster_interstitial_count

**AC-4: Cluster Integrity After Re-dispatch**
- After re-dispatch, re-run G2.5 coherence check on the replacement interstitial only (not full cluster)
- Update cluster coherence report with new scores
- If replacement passes, cluster proceeds
- If replacement fails and circuit breaker fires, operator fallback applies

**AC-5: Full Cluster Re-dispatch**
- If operator selects re-dispatch-cluster instead of re-dispatch-interstitial, the entire cluster re-dispatches as a new atomic unit (21-3 flow)
- Full cluster re-dispatch resets all interstitial re-dispatch counters

## Tasks / Subtasks

- [x] Task 1: Implement targeted re-dispatch
  - [x] 1.1: Extract perception data from G2.5 results for the head slide
  - [x] 1.2: Build tightened re-dispatch prompt (original prompt + perception constraints)
  - [x] 1.3: Dispatch single interstitial to Gamma API
  - [x] 1.4: Replace failed PNG with new PNG in asset directory

- [x] Task 2: Implement circuit breaker
  - [x] 2.1: Track re_dispatch_count per interstitial in cluster metadata
  - [x] 2.2: After 2 failures, present fallback options to operator
  - [x] 2.3: Implement accept-as-is (no change, mark as accepted-with-warning)
  - [x] 2.4: Implement replace-with-pace-reset (generate minimal pace-reset slide)
  - [x] 2.5: Implement drop-from-cluster (remove interstitial, update cluster_interstitial_count)

- [x] Task 3: Post-re-dispatch validation
  - [x] 3.1: Run G2.5 coherence on replacement interstitial vs. head
  - [x] 3.2: Update cluster coherence report
  - [x] 3.3: Route to next decision (proceed, re-dispatch again, or circuit breaker)

- [x] Task 4: Testing
  - [x] 4.1: Unit test: targeted re-dispatch prompt includes perception constraints
  - [x] 4.2: Unit test: circuit breaker fires after 2 attempts
  - [x] 4.3: Unit test: each fallback option (accept, replace, drop) produces valid cluster state
  - [x] 4.4: Unit test: full cluster re-dispatch resets counters
  - [x] 4.5: Integration test: re-dispatch → new PNG → G2.5 re-check (credit-consuming, manual trigger path implemented as explicit CLI)

## Completion Notes

- Implemented files:
  - `skills/bmad-agent-marcus/scripts/interstitial_redispatch_protocol.py`
  - `skills/bmad-agent-marcus/scripts/run-interstitial-redispatch.py`
  - `skills/bmad-agent-marcus/scripts/cluster_coherence_validation.py` (targeted `validate_interstitial_replacement`)
  - `skills/bmad-agent-marcus/scripts/tests/test_interstitial_redispatch_protocol.py`
  - `skills/bmad-agent-marcus/scripts/tests/test_run_interstitial_redispatch.py`
  - `skills/bmad-agent-marcus/scripts/tests/test_cluster_coherence_validation.py`
- Runtime guardrails:
  - Manual-only execution path (no auto-trigger in default flow)
  - Credit-consuming run requires `--execute` plus `--confirm-credit-spend YES`
  - Bundle-local metadata persistence only (no new global state)
- Verification evidence:
  - Protocol + wiring suites included in consolidated Wave 1 rerun (2026-04-12): `158 passed`

## Dev Notes

### Scope Boundary

This story handles re-dispatch execution. Coherence detection and scoring is 21-4. This story acts on 21-4's verdicts.

### Perception-Informed Prompting

The key differentiator from initial dispatch: re-dispatch prompts include concrete visual metadata (hex colors, font names, background descriptions) extracted from the head slide's perception data. This narrows Gamma's generative space significantly.

### Risk: Pace-Reset Generation

The "replace-with-pace-reset" fallback requires generating a minimal slide outside the cluster's Gamma session. This may use a simpler prompt template (icon + whitespace + head palette undertone). Ensure this template exists in the constraint library (21-1).

## References

- [21-4-cluster-coherence-validation.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/21-4-cluster-coherence-validation.md) — Coherence detection
- [21-2-cluster-aware-prompt-engineering.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/21-2-cluster-aware-prompt-engineering.md) — Prompt construction
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 21.5 definition
