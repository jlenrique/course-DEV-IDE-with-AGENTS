# Story 23-2: G4 Gate Extension for Clusters

**Epic:** 23 - Irene Pass 2 Cluster-Aware Narration
**Status:** done
**Sprint key:** `23-2-g4-gate-extension-for-clusters`
**Added:** 2026-04-12
**Depends on:** [23-1-cluster-aware-dual-channel-grounding.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/23-1-cluster-aware-dual-channel-grounding.md), [19-3-fidelity-gate-contract-updates.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/19-3-fidelity-gate-contract-updates.md)

## Story

As the quality system (Vera / G4 gate),
I want four new cluster-specific G4 criteria that validate narration coherence, word budgets, concept scope, and arc integrity,
So that clustered narration meets the same rigor as non-clustered narration plus additional cluster-specific quality checks.

## Acceptance Criteria

**Given** a narration script for a clustered presentation
**When** the G4 Narration Script gate runs
**Then** the following new criteria must be evaluated in addition to existing G4-01 through G4-15:

**AC-1: G4-16 - Cluster Narration Coherence**
- For each cluster: do all interstitial segment narrations serve the cluster's master_behavioral_intent?
- Check: each interstitial segment's behavioral_intent is subordinate to the cluster master, using the cluster-level master derived from the head manifest row
- Fail: any interstitial behavioral_intent contradicts or diverges from master, or if the cluster master cannot be resolved from the manifest

**AC-2: G4-17 - Interstitial Word Budget**
- Head segments: word count within cluster_head_word_range [80, 140]
- Interstitial segments: word count within interstitial_word_range [25, 40]
- Tolerance: +/-5 words (to avoid failing on 79 or 141 word edge cases)
- Fail: any segment outside range + tolerance

**AC-3: G4-18 - No New Concepts in Interstitials**
- Interstitial narration must not introduce concepts absent from the head segment's source_ref scope
- Check: extract concept keywords from head narration; verify interstitial narration uses only those concepts (or subset)
- Fail: interstitial introduces a term/concept not present in head narration or head brief

**AC-4: G4-19 - Cluster Arc Integrity**
- The sequence establish -> tension -> develop -> resolve must form a coherent progression
- Check: positions assigned in canonical schema order, no gaps (e.g., establish -> resolve without a middle beat)
- Check: resolve narration echoes or callbacks to establish narration (semantic similarity)
- Fail: position sequence is disordered or resolve has no callback to establish

**AC-5: Existing G4 Criteria Compatibility**
- G4-01 through G4-15 apply per-segment as before
- Cluster-role-aware adjustments:
  - G4 word count checks use cluster-specific ranges (not global) for clustered segments
  - G4 bridge checks exempt within-cluster transitions (bridge_type: none is valid)
  - G4 spoken bridge enforcement skips within-cluster none bridges

**AC-6: G4 Contract Update**
- Update `state/config/fidelity-contracts/g4-narration-script.yaml` with G4-16 through G4-19
- Each new criterion has: id, description, severity (error), scope (cluster), check_type

## Tasks / Subtasks

- [x] Task 1: Implement G4-16 Cluster Narration Coherence
  - [x] 1.1: Extract master_behavioral_intent per cluster from manifest
  - [x] 1.2: Compare each interstitial behavioral_intent against master
  - [x] 1.3: Define subordination rules (which intents are compatible with which masters)
  - [x] 1.4: Report pass/fail per cluster with specific divergence details

- [x] Task 2: Implement G4-17 Interstitial Word Budget
  - [x] 2.1: Read cluster_head_word_range and interstitial_word_range from narration-script-parameters.yaml
  - [x] 2.2: Count words per segment in narration script
  - [x] 2.3: Apply +/-5 word tolerance
  - [x] 2.4: Report pass/fail per segment with actual vs. expected range

- [x] Task 3: Implement G4-18 No New Concepts
  - [x] 3.1: Extract concept keywords from head segment narration + brief
  - [x] 3.2: Check interstitial narration for terms not in head concept set
  - [x] 3.3: Allow common/generic words (articles, prepositions, etc.) - only flag domain terms
  - [x] 3.4: Report pass/fail per interstitial with the introduced concept flagged

- [x] Task 4: Implement G4-19 Cluster Arc Integrity
  - [x] 4.1: Verify position sequence (establish -> tension -> develop -> resolve) is ordered
  - [x] 4.2: Check for gaps (e.g., missing develop before tension)
  - [x] 4.3: Check resolve-to-establish callback (keyword overlap or semantic similarity)
  - [x] 4.4: Report pass/fail per cluster with specific integrity issues

- [x] Task 5: Update existing G4 criteria for cluster awareness
  - [x] 5.1: G4 word count checks use cluster-specific ranges for clustered segments
  - [x] 5.2: G4 bridge checks exempt within-cluster none bridges
  - [x] 5.3: Spoken bridge enforcement skips within-cluster transitions

- [x] Task 6: Update G4 fidelity contract
  - [x] 6.1: Add G4-16, G4-17, G4-18, G4-19 to g4-narration-script.yaml
  - [x] 6.2: Document scope, severity, and check_type for each

- [x] Task 7: Testing
  - [x] 7.1: Unit test per new criterion (pass, warn, fail cases)
  - [x] 7.2: Unit test: existing G4-01 through G4-15 pass unchanged for non-clustered
  - [x] 7.3: Unit test: cluster-aware adjustments to existing criteria
  - [x] 7.4: Integration test: full G4 gate on clustered narration script

## Dev Notes

### G4-18 Complexity

"No new concepts" is the hardest criterion to implement reliably. Keyword extraction from narration text is inherently imprecise. Start with a simple approach: extract nouns/noun phrases from head narration, check interstitial narration for nouns not in that set. Refine with domain-specific term lists if false positives are high.

### Scope Boundary

This story implements the G4 gate extensions. The narration writing itself is 23-1. This story validates 23-1's output.

## References

- [g4-narration-script.yaml](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/state/config/fidelity-contracts/g4-narration-script.yaml) - Current G4 contract
- [23-1-cluster-aware-dual-channel-grounding.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/23-1-cluster-aware-dual-channel-grounding.md) - Narration rules
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) - Story 23.2 definition

## Dev Agent Record

### Implementation Plan

- Extend the deterministic Pass 2 validator with explicit cluster-level G4 evidence rather than creating a separate cluster gate implementation path.
- Reconcile G4 numbering across the contract and Vera protocol first, so the repo has one canonical meaning for `G4-16..19`.
- Use simple, testable heuristics for concept-scope and arc-callback checks, then validate them against both new focused cluster tests and the existing Pass 2 regression suite.

### Debug Log

- 2026-04-15: Marked `23-2` in progress after `23-1` formal review closure and loaded the current G4 contract, Vera protocol, and Pass 2 validator surface.
- 2026-04-15: Reconciled an existing numbering drift where Vera protocol had a stray `G4-16` spoken-bridge note while the formal contract still ended at `G4-15`.
- 2026-04-15: Extended `validate-irene-pass2-handoff.py` with cluster-level outputs for behavioral-intent coherence, +/-5 cluster word-budget tolerance, head-scope concept checks, and arc-integrity validation.
- 2026-04-15: Implemented simple source-ref-assisted concept extraction and canonical cluster-position ordering based on the authoritative 20a-3 cluster narrative arc schema.
- 2026-04-15: Added focused validator and contract tests, then reconciled older cluster fixtures so they continued testing their original criterion instead of failing accidentally on the new cluster-arc checks.

### Completion Notes

- Added `G4-16` through `G4-19` to the G4 contract with explicit `scope: cluster` and `check_type` metadata, and mirrored the same criteria in Vera's gate-evaluation protocol.
- `validate-irene-pass2-handoff.py` now reports cluster-specific findings for behavioral-intent subordination, cluster word budgets with +/-5 tolerance, interstitial new-concept detection against head scope, and cluster arc-integrity failures.
- Preserved existing runtime-policy behavior: cluster word-budget findings remain auditable warnings in advisory mode and hard failures in strict mode.
- Formal review remediation closed three findings before final approval:
  - G4-16 now derives the cluster master from the head row instead of silently bypassing interstitial checks when the per-interstitial field is blank.
  - The story's AC-4 wording now matches the authoritative cluster arc schema order: `establish -> tension -> develop -> resolve`.
  - Contract tests now assert `severity` and `description` for `G4-16..19`, not just presence/scope/check type.
- Validation passed:
  - `.\.venv\Scripts\python.exe -m pytest -q skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py skills/bmad-agent-marcus/scripts/tests/test-narration-config-schemas.py tests/test_cluster_aware_pass2_contract_docs.py tests/test_parameter_registry_schema.py`
  - Result: `151 passed`
- Full regression passed:
  - `.\.venv\Scripts\python.exe -m pytest -q`
  - Result: `693 passed, 1 skipped, 27 deselected`
- Tracker validation passed:
  - `.\.venv\Scripts\python.exe -m pytest -q tests/test_sprint_status_yaml.py`
  - `.\.venv\Scripts\python.exe -m scripts.utilities.progress_map --no-latest-file`
  - Result: sprint-status green; progress map reported `Sources: STRUCTURALLY CLEAN`

## File List

- `_bmad-output/implementation-artifacts/23-2-g4-gate-extension-for-clusters.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `state/config/fidelity-contracts/g4-narration-script.yaml`
- `skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md`
- `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`
- `skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py`
- `skills/bmad-agent-marcus/scripts/tests/test-narration-config-schemas.py`

## Change Log

- 2026-04-15: Implemented the cluster-aware G4 extension for Pass 2, reconciled the `G4-16..19` contract/protocol numbering, added focused cluster-gate heuristics and tests, and advanced the story to review.
- 2026-04-15: Formal BMAD review completed clean after closing interstitial master-derivation, AC/order alignment, and AC-6 contract-test coverage findings; story moved to done.
