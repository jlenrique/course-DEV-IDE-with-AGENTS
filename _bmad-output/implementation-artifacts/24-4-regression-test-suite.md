# Story 24-4: Regression Test Suite

**Epic:** 24 - Assembly, Handoff & Regression Hardening
**Status:** backlog
**Sprint key:** `24-4-regression-test-suite`
**Added:** 2026-04-12
**Depends on:** [24-1-assembly-contract-hardening.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/24-1-assembly-contract-hardening.md), [24-3-elevenlabs-short-segment-handling.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/24-3-elevenlabs-short-segment-handling.md), [23-2-g4-gate-extension-for-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/23-2-g4-gate-extension-for-clusters.md)

## Story

As the quality system,
I want a comprehensive regression test suite that validates both flat and clustered presentations pass all validators end-to-end,
So that cluster features don't break non-clustered workflows and the full clustered pipeline produces a valid assembly bundle.

## Acceptance Criteria

**Given** the complete cluster feature set (Epics 19-24) is implemented
**When** the regression test suite runs
**Then** the following test categories must all pass:

**AC-1: Backward Compatibility — Non-Clustered Presentations**
- Non-clustered presentations pass ALL validators unchanged:
  - `validate-gary-dispatch-ready.py` accepts flat payloads
  - `validate-irene-pass2-handoff.py` accepts non-clustered segment entries
  - G2, G3, G4 gate contracts handle non-clustered payloads
  - Storyboard A/B generation produces identical output for non-clustered input
  - Assembly pipeline produces valid bundle for non-clustered input
- Existing production run (C1-M1) can be re-run without clusters as baseline

**AC-2: Cluster-Enabled End-to-End Validation**
- Cluster-enabled run produces valid assembly bundle end-to-end:
  - Irene Pass 1 → clustered segment manifest (G1.5 pass)
  - Gary dispatch → cluster PNGs (G2.5 pass)
  - Storyboard A → cluster view with coherence indicators
  - Irene Pass 2 → clustered narration (G4 pass including G4-16 through G4-19)
  - Storyboard B → cluster view with script context + flat-play mode
  - ElevenLabs → audio with cluster-aware buffers
  - Assembly → valid bundle with cluster-ordered assets

**AC-3: Validator Regression Tests**
- `validate-gary-dispatch-ready.py` accepts both flat and clustered payloads
- `validate-irene-pass2-handoff.py` accepts interstitial segment entries
- G1.5 (cluster plan) validates correctly
- G2.5 (cluster coherence) validates correctly
- G2, G3, G4 gate contracts handle cluster carve-outs correctly

**AC-4: Double-Dispatch + Non-Clustered**
- Double-dispatch still works for non-clustered presentations
- Double-dispatch disabled for interstitials only (cluster heads may double-dispatch)
- Mixed scenarios: some clusters + some flat slides + double-dispatch on flat slides

**AC-5: Fidelity Gate Contract Coverage**
- All fidelity contracts (G0-G5 + G1.5 + G2.5) have test coverage
- Each gate has at least: 1 pass case, 1 fail case, 1 edge case
- Cluster-specific criteria (G4-16 through G4-19) have dedicated test cases

**AC-6: Test Organization**
- Cluster regression tests organized in a dedicated test module or directory
- Tests clearly labeled: `test_cluster_*` prefix for cluster-specific, `test_regression_*` for backward compatibility
- All tests run in CI (no manual-trigger-only tests in regression suite)

## Tasks / Subtasks

- [ ] Task 1: Non-clustered regression tests
  - [ ] 1.1: Verify all existing validators pass with non-clustered payloads
  - [ ] 1.2: Verify storyboard generation produces identical output for non-clustered input
  - [ ] 1.3: Verify assembly pipeline produces valid bundle for non-clustered input
  - [ ] 1.4: Re-run C1-M1 non-clustered baseline (if feasible without API credits)

- [ ] Task 2: Cluster end-to-end tests
  - [ ] 2.1: Test full pipeline with Storyboard A trial data
  - [ ] 2.2: Validate each gate in sequence (G1.5 → G2.5 → G4)
  - [ ] 2.3: Validate assembly bundle structure and completeness
  - [ ] 2.4: Validate storyboard HTML generation (both views)

- [ ] Task 3: Validator-specific tests
  - [ ] 3.1: validate-gary-dispatch-ready.py: flat, clustered, mixed payloads
  - [ ] 3.2: validate-irene-pass2-handoff.py: flat, clustered, interstitial entries
  - [ ] 3.3: G1.5 cluster plan: pass, fail, edge cases
  - [ ] 3.4: G2.5 cluster coherence: pass, warn, fail cases
  - [ ] 3.5: G4-16 through G4-19: per-criterion pass and fail

- [ ] Task 4: Double-dispatch interaction tests
  - [ ] 4.1: Non-clustered double-dispatch works unchanged
  - [ ] 4.2: Clustered presentation with double-dispatch disabled for interstitials
  - [ ] 4.3: Mixed: some clusters + flat slides with double-dispatch on flat

- [ ] Task 5: Test organization and CI
  - [ ] 5.1: Create `tests/test_cluster_regression.py` for cluster-specific tests
  - [ ] 5.2: Create `tests/test_backward_compatibility.py` for non-clustered regression
  - [ ] 5.3: Verify all tests run in CI without API credit consumption (use fixtures)
  - [ ] 5.4: Document test fixtures and data requirements

## Dev Notes

### Scope Boundary

This is the capstone story for the cluster series. It validates the entire stack, not implementing new features. All other stories (19-* through 24-3) must be complete before this story can fully execute.

### Test Fixture Strategy

Use the Storyboard A trial data (`course-content/staging/storyboard-a-trial/`) as the cluster test fixture. For non-clustered baseline, use existing C1-M1 tracked run data. Do NOT consume API credits in automated regression — all tests use pre-generated fixtures.

### Risk: Test Maintenance

28 stories producing ~50+ test cases. Organize by concern (validator, gate, pipeline stage) not by story number. This prevents the test suite from becoming a chronological dump.

## References

- [validate-gary-dispatch-ready.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/scripts/utilities/validate-gary-dispatch-ready.py) — Gary validator
- [validate-irene-pass2-handoff.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/scripts/utilities/validate-irene-pass2-handoff.py) — Irene validator
- [storyboard-a-trial](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/course-content/staging/storyboard-a-trial/) — Cluster test fixtures
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 24.4 definition
