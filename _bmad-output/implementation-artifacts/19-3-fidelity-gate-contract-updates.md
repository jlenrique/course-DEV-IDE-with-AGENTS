# Story 19-3: Fidelity Gate Contract Updates

**Epic:** 19 - Cluster Schema & Manifest Foundation
**Status:** done
**Sprint key:** `19-3-fidelity-gate-contract-updates`
**Added:** 2026-04-11
**Validated:** 2026-04-11
**Depends on:** [19-2-gary-dispatch-contract-extensions.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/19-2-gary-dispatch-contract-extensions.md)

## Story

As Vera and Marcus,
I want the G2 and G3 fidelity contracts to understand cluster-aware slide plans,
So that clustered Storyboard A runs are evaluated correctly without breaking existing flat workflows.

## Acceptance Criteria

**Given** clustered presentations introduce `cluster_role`, `cluster_interstitial_count`, and inherited interstitial behavior  
**When** G2 evaluates slide briefs  
**Then** `cluster_role == interstitial` is exempt from standalone LO traceability (`G2-01`) and standalone fidelity classification (`G2-03`) because interstitials inherit from the cluster head

**And** `G3-01` uses a cluster-aware counting rule that works for both clustered-only and mixed clustered+flat decks  
**And** the canonical fidelity contracts in `state/config/fidelity-contracts/` are updated without breaking flat-run semantics  
**And** Vera's gate evaluation protocol mirrors the cluster-aware G2/G3 contract behavior  
**And** fidelity contract validation passes after the updates

## Tasks / Subtasks

- [x] Task 1: Update G2 cluster-aware carve-outs
  - [x] 1.1: Amend `G2-01` to exempt interstitials from standalone LO traceability
  - [x] 1.2: Amend `G2-03` to exempt interstitials from standalone fidelity classification
  - [x] 1.3: Preserve flat-run behavior when cluster metadata is absent

- [x] Task 2: Update G3 count semantics
  - [x] 2.1: Replace raw brief-count logic with effective renderable-count language
  - [x] 2.2: Include flat slides, cluster heads, and declared interstitial expansion in the formula
  - [x] 2.3: Preserve backward compatibility for non-clustered briefs

- [x] Task 3: Align protocol and validation artifacts
  - [x] 3.1: Update Vera's gate evaluation protocol to mirror the new G2/G3 contract wording
  - [x] 3.2: Add regression tests pinning the cluster carve-outs and effective-count rule
  - [x] 3.3: Run fidelity contract validation end to end

## Dev Notes

### Scope Boundary

This story updates **fidelity contract definitions and protocol wording only**. It does not yet harden runtime validators such as `validate-gary-dispatch-ready.py`; that belongs to Story 19-4.

### Consensus Decision

The planning artifact's original shorthand for `G3-01` — `count(heads) + sum(cluster_interstitial_counts)` — is only correct for fully clustered decks.  
For mixed clustered + flat decks, the contract must count:

```text
count(generated_slides) ==
count(slide_brief.slides where cluster_role in (null, head)) +
sum(cluster_interstitial_count for each cluster head)
```

That consensus was confirmed during implementation review with the BMad roundtable.

## File List

- _bmad-output/implementation-artifacts/19-3-fidelity-gate-contract-updates.md (new)
- state/config/fidelity-contracts/g2-slide-brief.yaml (modified)
- state/config/fidelity-contracts/g3-generated-slides.yaml (modified)
- state/config/fidelity-contracts/g1.5-cluster-plan.yaml (modified - schema conformance repair surfaced during validation)
- skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md (modified)
- skills/bmad-agent-marcus/scripts/tests/test_cluster_fidelity_contracts.py (new)

## Dev Agent Record

### Debug Log

- 2026-04-11: Updated `g2-slide-brief.yaml` to exempt interstitials from standalone G2-01 and G2-03 evaluation
- 2026-04-11: Updated `g3-generated-slides.yaml` to use an effective renderable-count rule that includes flat slides and cluster expansion
- 2026-04-11: Updated Vera's gate evaluation protocol to mirror the cluster-aware contract wording
- 2026-04-11: Added targeted regression coverage for G2/G3 cluster carve-outs
- 2026-04-11: Repaired preexisting `g1.5-cluster-plan.yaml` schema drift so repo-wide contract validation passes

### Completion Notes List

- ✅ G2 now treats interstitials as inherited-from-head for LO traceability and fidelity classification
- ✅ G3 count semantics now work for clustered-only, mixed clustered+flat, and legacy flat decks
- ✅ Vera protocol text mirrors the live contract behavior
- ✅ `scripts/validate_fidelity_contracts.py` now passes across all live contracts

## Status

review

## Completion Status

Story 19-3 implemented and ready for adversarial review.
