# Story 23-2: G4 Gate Extension for Clusters

**Epic:** 23 - Irene Pass 2 Cluster-Aware Narration
**Status:** backlog
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

**AC-1: G4-16 — Cluster Narration Coherence**
- For each cluster: do all interstitial segment narrations serve the cluster's master_behavioral_intent?
- Check: each interstitial segment's behavioral_intent is subordinate to the cluster master
- Fail: any interstitial behavioral_intent contradicts or diverges from master

**AC-2: G4-17 — Interstitial Word Budget**
- Head segments: word count within cluster_head_word_range [80, 140]
- Interstitial segments: word count within interstitial_word_range [25, 40]
- Tolerance: ±5 words (to avoid failing on 79 or 141 word edge cases)
- Fail: any segment outside range + tolerance

**AC-3: G4-18 — No New Concepts in Interstitials**
- Interstitial narration must not introduce concepts absent from the head segment's source_ref scope
- Check: extract concept keywords from head narration; verify interstitial narration uses only those concepts (or subset)
- Fail: interstitial introduces a term/concept not present in head narration or head brief

**AC-4: G4-19 — Cluster Arc Integrity**
- The sequence establish → develop → tension → resolve must form a coherent progression
- Check: positions assigned in order, no gaps (e.g., establish → resolve without develop)
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

- [ ] Task 1: Implement G4-16 Cluster Narration Coherence
  - [ ] 1.1: Extract master_behavioral_intent per cluster from manifest
  - [ ] 1.2: Compare each interstitial behavioral_intent against master
  - [ ] 1.3: Define subordination rules (which intents are compatible with which masters)
  - [ ] 1.4: Report pass/fail per cluster with specific divergence details

- [ ] Task 2: Implement G4-17 Interstitial Word Budget
  - [ ] 2.1: Read cluster_head_word_range and interstitial_word_range from narration-script-parameters.yaml
  - [ ] 2.2: Count words per segment in narration script
  - [ ] 2.3: Apply ±5 word tolerance
  - [ ] 2.4: Report pass/fail per segment with actual vs. expected range

- [ ] Task 3: Implement G4-18 No New Concepts
  - [ ] 3.1: Extract concept keywords from head segment narration + brief
  - [ ] 3.2: Check interstitial narration for terms not in head concept set
  - [ ] 3.3: Allow common/generic words (articles, prepositions, etc.) — only flag domain terms
  - [ ] 3.4: Report pass/fail per interstitial with the introduced concept flagged

- [ ] Task 4: Implement G4-19 Cluster Arc Integrity
  - [ ] 4.1: Verify position sequence (establish → develop → tension → resolve) is ordered
  - [ ] 4.2: Check for gaps (e.g., missing develop before tension)
  - [ ] 4.3: Check resolve-to-establish callback (keyword overlap or semantic similarity)
  - [ ] 4.4: Report pass/fail per cluster with specific integrity issues

- [ ] Task 5: Update existing G4 criteria for cluster awareness
  - [ ] 5.1: G4 word count checks use cluster-specific ranges for clustered segments
  - [ ] 5.2: G4 bridge checks exempt within-cluster none bridges
  - [ ] 5.3: Spoken bridge enforcement skips within-cluster transitions

- [ ] Task 6: Update G4 fidelity contract
  - [ ] 6.1: Add G4-16, G4-17, G4-18, G4-19 to g4-narration-script.yaml
  - [ ] 6.2: Document scope, severity, and check_type for each

- [ ] Task 7: Testing
  - [ ] 7.1: Unit test per new criterion (pass, warn, fail cases)
  - [ ] 7.2: Unit test: existing G4-01 through G4-15 pass unchanged for non-clustered
  - [ ] 7.3: Unit test: cluster-aware adjustments to existing criteria
  - [ ] 7.4: Integration test: full G4 gate on clustered narration script

## Dev Notes

### G4-18 Complexity

"No new concepts" is the hardest criterion to implement reliably. Keyword extraction from narration text is inherently imprecise. Start with a simple approach: extract nouns/noun phrases from head narration, check interstitial narration for nouns not in that set. Refine with domain-specific term lists if false positives are high.

### Scope Boundary

This story implements the G4 gate extensions. The narration writing itself is 23-1. This story validates 23-1's output.

## References

- [g4-narration-script.yaml](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/state/config/fidelity-contracts/g4-narration-script.yaml) — Current G4 contract
- [23-1-cluster-aware-dual-channel-grounding.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/23-1-cluster-aware-dual-channel-grounding.md) — Narration rules
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 23.2 definition
