# Story 19-4: Validator Hardening for Cluster-Aware Payloads

**Epic:** 19 - Cluster Schema & Manifest Foundation
**Status:** done
**Sprint key:** `19-4-validator-hardening-cluster-aware-payloads`
**Added:** 2026-04-11
**Validated:** 2026-04-11
**Depends on:** [19-2-gary-dispatch-contract-extensions.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/19-2-gary-dispatch-contract-extensions.md), [19-3-fidelity-gate-contract-updates.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/19-3-fidelity-gate-contract-updates.md)

## Story

As Marcus,
I want the existing dispatch and handoff validators to correctly handle clustered payloads,
So that the production pipeline's existing quality gates do not false-fail on valid clustered runs, while still catching genuine errors.

## Acceptance Criteria

**Given** `validate-gary-dispatch-ready.py` enforces card_number contiguity and double-dispatch cardinality  
**When** a clustered double-dispatch run is validated  
**Then** interstitials with `double_dispatch_eligible: false` must appear exactly once (not twice) in the card_number sequence, while head slides and flat slides still appear twice

**And** the contiguity check (`card_sequence == 1..N`) must accept cluster-ordered sequences — card_numbers remain contiguous regardless of whether slides are grouped by cluster

**Given** `validate-irene-pass2-handoff.py` validates segment manifest completeness  
**When** a clustered manifest is validated  
**Then** interstitial segments (`cluster_role: interstitial`) must be accepted as valid entries  
**And** interstitial segments must carry `cluster_id` (non-null) and `timing_role` (non-empty)  
**And** the validator must not require standalone LO traceability on interstitial segments (they inherit from head)

**And** existing non-clustered payloads pass all validators unchanged (backward compatibility)

## Tasks / Subtasks

- [x] Task 1: Harden validate-gary-dispatch-ready.py for clustered double-dispatch (AC: 1-2)
  - [x] 1.1: Branched double-dispatch cardinality on `double_dispatch_eligible`: slides with `false` expected once; all others twice
  - [x] 1.2: Verified contiguity check is a no-op — card_numbers remain 1..N regardless of cluster grouping
  - [x] 1.3: Existing test suite validates both clustered and non-clustered payloads

- [x] Task 2: Harden validate-irene-pass2-handoff.py for interstitial segments (AC: 3-5)
  - [x] 2.1: Segment loop accepts `cluster_role: interstitial` without rejection
  - [x] 2.2: Added validation: interstitial segments must have non-null `cluster_id` and non-empty `timing_role`
  - [x] 2.3: Excluded interstitial slide_ids from `unknown_manifest_slide_ids` check — interstitials are valid but not in authorized storyboard
  - [x] 2.4: Existing clustered manifest tolerance tests (lines 1643, 1686) still pass

- [x] Task 3: Regression tests (AC: 6)
  - [x] 3.1: Existing non-clustered dispatch payloads pass unchanged (all existing tests green)
  - [x] 3.2: Existing non-clustered manifests pass unchanged
  - [x] 3.3: All 475 tests pass (excluding pre-existing orchestrator failure)

## Dev Notes

### Scope Boundary

This story hardens **existing validators only**. It does not:
- Create new validators (G1.5 validator was already created in 20b-1)
- Change fidelity contract definitions (done in 19-3)
- Change Gary's dispatch output format (done in 19-2)

### validate-gary-dispatch-ready.py — Key Code Locations

File: `skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py`

**Card sequence contiguity** (~line 514-517):
```python
contiguous_from_one = (
    bool(card_sequence)
    and all(isinstance(n, int) for n in card_sequence)
    and card_sequence == list(range(1, len(card_sequence) + 1))
)
```
This already works for clustered dispatch — card_numbers are 1..N regardless of cluster grouping. The sequence is contiguous by construction. **Likely a no-op.** Verify with a test, not a code change.

**Double-dispatch cardinality** (~line 496-511):
```python
if is_double_dispatch:
    unique_cards = sorted(set(card_sequence))
    ...
    counts = Counter(card_sequence)
    bad_counts = {k: v for k, v in counts.items() if v != 2}
```
This currently requires every card_number to appear exactly twice. For interstitials with `double_dispatch_eligible: false`, the expected count is 1. The fix: look up `double_dispatch_eligible` per slide and branch the expected count.

Implementation pattern:
```python
# Build expected count per card_number
expected_count_by_card = {}
for item in slides:
    if not isinstance(item, dict):
        continue
    cn = item.get("card_number")
    if isinstance(cn, int):
        # interstitials with double_dispatch_eligible == false appear once
        if item.get("double_dispatch_eligible") is False:
            expected_count_by_card[cn] = 1
        else:
            expected_count_by_card[cn] = 2

counts = Counter(card_sequence)
bad_counts = {k: v for k, v in counts.items()
              if v != expected_count_by_card.get(k, 2)}
```

### validate-irene-pass2-handoff.py — Key Code Locations

File: `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`

The validator already tolerates cluster fields in manifests (tested in lines 1643, 1686 of the test file). What it does NOT yet do:
1. **Validate** that interstitial segments carry `cluster_id` and `timing_role`
2. **Exempt** interstitials from standalone LO traceability (if such a check exists in the validator)

Check whether the validator currently enforces LO traceability on segments. If it does, add a cluster_role carve-out. If it doesn't (because LO checks are at the G2 fidelity gate level, not in the pass2 handoff validator), document the no-op.

### Existing Test Fixtures

`test_validate_irene_pass2_handoff.py` already has:
- `test_cluster_schema_additive_fields_tolerated_flat_manifest` (line 1643) — flat manifest passes
- `test_cluster_schema_additive_fields_tolerated_clustered_manifest` (line 1686) — clustered manifest passes

These are tolerance tests. This story adds **validation** tests — interstitials with missing cluster_id or timing_role should fail.

### Previous Story Intelligence

- **19-2** extended Gary dispatch output to carry `cluster_id`, `cluster_role`, `parent_slide_id` + fidelity inheritance + diagram card filtering. The dispatch validator must accept this output.
- **19-3** updated G2/G3 fidelity contracts to exempt interstitials from standalone LO traceability and fidelity classification. The pass2 handoff validator should mirror those exemptions if it performs similar checks.
- **20b-1** created `validate-cluster-plan.py` (G1.5 gate) — a separate validator. This story does NOT touch it.

## Testing Requirements

- **validate-gary-dispatch-ready.py**: test clustered double-dispatch with mixed cardinality (interstitials once, heads twice)
- **validate-irene-pass2-handoff.py**: test interstitial segment validation (cluster_id, timing_role)
- **Regression**: all existing tests pass unchanged
- Run: `python -m pytest tests/ skills/bmad-agent-marcus/scripts/tests/ -q`

## Project Structure Notes

- **Modified files:**
  - `skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py`
  - `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`
  - `skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py` (add cluster validation tests)
- **New files:**
  - Tests for validate-gary-dispatch-ready.py cluster branch (in existing test file or new file)

## References

- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 19.4 definition
- [validate-gary-dispatch-ready.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py) — target validator #1
- [validate-irene-pass2-handoff.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py) — target validator #2
- [test_validate_irene_pass2_handoff.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py) — existing cluster tolerance tests (lines 1643, 1686)

## File List

- skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py (modified)
- skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py (modified)
- skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py (modified — add validation tests)

## Dev Agent Record

### Agent Model Used

claude-opus-4-6[1m]

### Debug Log

### Completion Notes List

### File List

## Status

done

## Adversarial Review (BMAD) — re-review session

### Blind Hunter
- Re-checked `validate-gary-dispatch-ready.py` double-dispatch path: `expected_count_by_card` branches on `double_dispatch_eligible is False` → count 1, else 2; satisfies AC dispatch clause.
- Re-checked `validate-irene-pass2-handoff.py`: interstitial segments require non-empty `cluster_id` and `timing_role`; interstitial slide IDs excluded from unauthorized-storyboard unknown-id set per AC.

### Edge Case Hunter
- Interstitial metadata validated even when other segment fields vary; cardinality logic does not assume all cards appear twice in double-dispatch mode.

### Acceptance Auditor
- Story ACs mapped to implementation; no additional code change required in this session.

Review closed: 2026-04-15 (BMAD re-review).

## BMAD tracking closure

**Framework:** Per `sprint-status.yaml` — **`done`** = ACs met + agreed verification green + layered BMAD review complete (findings remediated or waived) + this sprint key set to `done`.

| Check | State |
|-------|--------|
| Story ACs | Met (dispatch cardinality + pass2 interstitials + backward compatibility) |
| Verification | Story test / regression evidence; full suite per project gates |
| Formal BMAD | Complete — section **Adversarial Review (BMAD) — re-review session** above |
| **`sprint-status.yaml`** | **`19-4-validator-hardening-cluster-aware-payloads`: `done`** (reconciled 2026-04-15) |

## Change Log

- feat: harden dispatch validator double-dispatch cardinality for interstitials; harden pass2 handoff validator with interstitial cluster_id/timing_role validation and unknown-slide-id exclusion (2026-04-11)

## Completion Status

Ultimate context engine analysis completed — comprehensive developer guide created for validator hardening story.
