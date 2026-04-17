# Story 23-1: Cluster-Aware Dual-Channel Grounding

**Epic:** 23 - Irene Pass 2 Cluster-Aware Narration
**Status:** done
**Sprint key:** `23-1-cluster-aware-dual-channel-grounding`
**Added:** 2026-04-12
**Depends on:** [20b-3-narration-script-parameters-extension-for-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20b-3-narration-script-parameters-extension-for-clusters.md), [21-3-cluster-dispatch-sequencing.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/21-3-cluster-dispatch-sequencing.md)

> **Implemented in this story:** Removed the `pass2_mode: structural-coherence-check` scope limitation from `docs/workflow/operator-script-v4.2-irene-ab-loop.md`. Pass 2 is now documented as a first-class cluster-aware refinement signal rather than a structural-only placeholder.

## Story

As Irene (Pass 2),
I want to perceive each slide in a cluster and write narration calibrated to the head/interstitial split,
So that head segments get full explanatory narration while interstitial segments get brief, visual-complementary narration that presumes the slide carries 70% of the meaning.

## Acceptance Criteria

**Given** Irene Pass 2 receives a clustered segment manifest with generated PNGs
**When** Irene writes narration for a cluster
**Then** the following dual-channel rules must be enforced:

**AC-1: Head Segment Narration (Establish Position)**
- Fuller narration: 80-140 words (per cluster_head_word_range)
- Establishes the topic, plants the hook
- Standard dual-channel grounding: narration complements the visual
- Visual references per existing perception protocol (Epic 13)

**AC-2: Interstitial Segment Narration (Develop/Tension/Resolve)**
- Shorter narration: 25-40 words (per interstitial_word_range)
- Focused on the interstitial's isolation_target
- Presumes the visual carries 70% of the meaning - narration adds the remaining 30%
- No new concepts introduced (narration scope limited to head segment's source_ref)

**AC-3: Within-Cluster Transitions**
- Default: `bridge_type: none` - no spoken bridge (visual cut is sufficient)
- Exception: `tension` position may use `bridge_type: pivot` with an explicit tonal shift word (for example, "but", "however", "yet")
- Irene must suppress bridge generation for within-cluster transitions unless `cluster_position == tension`

**AC-4: Cluster-Boundary Transitions**
- `bridge_type: cluster_boundary` - one sentence synthesis of what the cluster covered plus one sentence forward pull to next topic
- Duration target: 15-20 seconds (37-50 words at 150 WPM)
- Bridge fires at cluster seams (not by slide count or time interval)

**AC-5: Behavioral Intent Subordination**
- Per-segment `behavioral_intent` must serve the cluster's `master_behavioral_intent`
- Irene cannot assign a `behavioral_intent` that contradicts or diverges from the cluster master
- Intent vocabulary remains the same; constraint is subordination, not restriction

**AC-6: Perception of All Cluster Members**
- Irene perceives each slide (head and interstitial) via sensory bridge before writing narration
- Perception data includes dominant visuals, text content, layout, and color palette
- Interstitial narration references the perceived `isolation_target` specifically

## Tasks / Subtasks

- [x] Task 1: Extend Irene Pass 2 for cluster awareness
  - [x] 1.1: Detect clustered segments in manifest (`cluster_id` not null)
  - [x] 1.2: Read cluster parameters from `narration-script-parameters.yaml` (20b-3 output)
  - [x] 1.3: Group segments by `cluster_id` for sequential processing

- [x] Task 2: Implement head segment narration
  - [x] 2.1: Apply `cluster_head_word_range [80, 140]` for head segments
  - [x] 2.2: Standard perception plus dual-channel grounding (existing Epic 13 flow)
  - [x] 2.3: Set `behavioral_intent` as `master_behavioral_intent` for the cluster

- [x] Task 3: Implement interstitial segment narration
  - [x] 3.1: Apply `interstitial_word_range [25, 40]` for interstitial segments
  - [x] 3.2: Focus narration on `isolation_target` from perception
  - [x] 3.3: Enforce no-new-concepts rule (scope limited to head `source_ref`)
  - [x] 3.4: Set `behavioral_intent` subordinate to master

- [x] Task 4: Implement bridge handling
  - [x] 4.1: Suppress bridges within clusters (`bridge_type: none`)
  - [x] 4.2: Allow `bridge_type: pivot` for tension position only
  - [x] 4.3: Generate `cluster_boundary` bridge at cluster seams (synthesis plus forward pull)
  - [x] 4.4: Apply bridge cadence override (bridges at cluster seams, not by count/time)

- [x] Task 5: Testing
  - [x] 5.1: Unit test: head narration within 80-140 word range
  - [x] 5.2: Unit test: interstitial narration within 25-40 word range
  - [x] 5.3: Unit test: no spoken bridge within cluster (non-tension)
  - [x] 5.4: Unit test: cluster_boundary bridge at cluster seams
  - [x] 5.5: Unit test: behavioral_intent subordination check
  - [x] 5.6: Regression: non-clustered narration unchanged

## Dev Notes

### Scope Boundary

This story implements the narration writing rules. G4 gate extension is 23-2. Bridge cadence parameter changes are in 20b-3 (prerequisite). This story consumes the parameters and produces the narration contract.

### Key Dependency

This story requires 20b-3 (narration parameters) to be complete. Without cluster-specific word ranges and bridge policies in the YAML, Irene has no calibration data.

### Irene Is LLM-Driven

Irene's narration is produced by the LLM during Pass 2, not by Python scripts. The Python layer validates the output (G4 gate). This story defines the behavioral contract Irene must follow; the deterministic G4 extension remains 23-2.

## References

- [20b-3-narration-script-parameters-extension-for-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20b-3-narration-script-parameters-extension-for-clusters.md) - Parameter infrastructure
- [13-2-visual-reference-injection.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/13-2-visual-reference-injection.md) - Existing perception and grounding
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) - Story 23.1 definition

## Dev Agent Record

### Implementation Plan

- Treat 23-1 as a contract-hardening story, not a runtime refactor.
- Tighten Irene Pass 2 instructions and paired templates around cluster-aware narration behavior.
- Reconcile the operator workflow and status docs so Pass 2 is no longer described as structural-only.
- Add focused deterministic tests for the new contract surface, then move to review only if the tracker surface stays clean.

### Debug Log

- 2026-04-15: Ran disciplined BMAD startup for 23-1, reviewed scope with Party Mode architect/developer, and marked the story `in-progress`.
- 2026-04-15: Hardened Irene's Pass 2 contract for cluster-by-cluster processing, head/interstitial calibration, no-new-concepts boundaries, behavioral-intent subordination, and cluster seam handling.
- 2026-04-15: Aligned narration/manifest templates and narration-script parameters so `pivot` is an explicit accepted bridge type alongside `cluster_boundary`.
- 2026-04-15: Removed the obsolete `structural-coherence-check` limitation from the Irene A/B workflow doc and reconciled handoff/status docs.
- 2026-04-15: Added focused regression coverage and re-ran the progress map until source health was structurally clean.
- 2026-04-15: Closed late review findings by enforcing pivot-only tension bridges, pivot cue validation, master behavioral-intent subordination checks, bridge-type registry parity, and tracker reconciliation.

### Completion Notes

- Irene's `SKILL.md` now explicitly instructs clustered Pass 2 runs to process segments cluster-by-cluster, give head segments the fuller explanatory role, keep interstitials short and isolation-targeted, and prohibit new concepts beyond the head segment's source-backed scope.
- The narration and segment-manifest templates now expose cluster role/position context, require cluster-level behavioral-intent coherence, and document both `pivot` and `cluster_boundary` bridge types.
- `state/config/narration-script-parameters.yaml` now advertises `pivot` as an accepted bridge type, matching the existing tension-override contract already present in the validator logic.
- `docs/workflow/operator-script-v4.2-irene-ab-loop.md` now treats Pass 2 as `cluster-aware-refinement` rather than structural-only, so future trial loops can legitimately use cluster-aware narration as an evaluative signal.
- Focused validation passed:
  - `.\.venv\Scripts\python.exe -m pytest -q skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py skills/bmad-agent-marcus/scripts/tests/test-narration-config-schemas.py tests/test_cluster_aware_pass2_contract_docs.py tests/test_parameter_registry_schema.py tests/test_sprint_status_yaml.py`
  - Result: `147 passed`
- Progress map validation passed:
  - `.\.venv\Scripts\python.exe -m scripts.utilities.progress_map --no-latest-file`
  - Result: `Sources: ✓ STRUCTURALLY CLEAN`
- Party Mode review gate:
  - Amelia: `APPROVE`
  - Murat: `APPROVE`

## File List

- `_bmad-output/implementation-artifacts/23-1-cluster-aware-dual-channel-grounding.md`
- `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `SESSION-HANDOFF.md`
- `docs/project-context.md`
- `docs/workflow/operator-script-v4.2-irene-ab-loop.md`
- `next-session-start-here.md`
- `skills/bmad-agent-content-creator/SKILL.md`
- `skills/bmad-agent-content-creator/references/template-narration-script.md`
- `skills/bmad-agent-content-creator/references/template-segment-manifest.md`
- `state/config/narration-script-parameters.yaml`
- `skills/bmad-agent-marcus/scripts/tests/test-narration-config-schemas.py`
- `skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py`
- `tests/test_cluster_aware_pass2_contract_docs.py`

## Change Log

- 2026-04-15: Completed the 23-1 contract-hardening pass for cluster-aware Irene Pass 2 behavior, closed the late review findings, and moved the story to `done` after focused validation.

### Review Findings

- [x] [Review][Patch] Enforce `pivot` as the only allowed non-`none` within-cluster bridge for `tension` interstitials [skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py:868]
- [x] [Review][Patch] Validate spoken-cue semantics for `bridge_type: pivot` so tonal-turn language is actually enforced [skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py:283]
- [x] [Review][Patch] Implement automated behavioral-intent subordination checks against `master_behavioral_intent` rather than only script/manifest parity [skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py:912]
- [x] [Review][Patch] Reconcile shared bridge-type references so `pivot` is included in `docs/parameter-directory.md` and `state/config/parameter-registry-schema.yaml` [docs/parameter-directory.md:107]
- [x] [Review][Patch] Align `bmm-workflow-status.yaml` wording with the actual post-review state so it no longer describes `23-1` as the active implementation slice [_bmad-output/implementation-artifacts/bmm-workflow-status.yaml:26]

## Adversarial Review (BMAD)

**Prior review evidence:** The **Review Findings** checklist above and the Party Mode gate (Amelia/Murat `APPROVE` in **Completion Notes**) record a narrower, implementation-focused pass before this formal BMAD closure.

### Blind Hunter

- **Contract surface locked:** `tests/test_cluster_aware_pass2_contract_docs.py` asserts Irene `SKILL.md`, narration template, segment-manifest template, and `operator-script-v4.2-irene-ab-loop.md` carry cluster-by-cluster processing, `pivot` / `cluster_boundary`, `master_behavioral_intent` subordination, and `cluster-aware-refinement` (with `structural-coherence-check` absent)—reducing silent doc drift.
- **Deterministic enforcement:** `validate-irene-pass2-handoff.py` implements post-review patches for pivot-only-on-tension, pivot cue patterns, `master_behavioral_intent` subordination, and bridge-type registry parity referenced in **Review Findings**; behavior is not SKILL-only.
- **Residual risk (accepted):** Word-range ACs in this story are **targets** for Irene; the **G4** layer (Story 23-2) applies tolerances and gate severity—this story’s AC table does not restate ±5 tolerance, by design.

### Edge Case Hunter

- **Mixed decks:** Validator paths preserve non-clustered segments; clustered records are keyed off `cluster_id` presence—empty or malformed `cluster_id` strings are treated as non-cluster for transition logic, which is consistent with “clustering optional” operation.
- **Perception / 70–30 split:** AC-6 and dual-channel grounding remain **LLM-execution** obligations; the harness validates manifest/narration contract and gates, not a replay of sensory-bridge inference.

### Acceptance Auditor

- **AC-1–AC-2:** Head/interstitial word ranges and roles are documented in SKILL + templates and parameterized via `narration-script-parameters.yaml` (prerequisite 20b-3).
- **AC-3:** Within-cluster bridge suppression and `pivot` exception for `tension` are enforced in validator + documented bridge vocabulary.
- **AC-4:** `cluster_boundary` seam behavior is specified; duration/word targets are **evaluative** in HIL guidance (full G4 numeric enforcement completed in 23-2).
- **AC-5:** `master_behavioral_intent` subordination is implemented in validator (post-review patch) rather than template prose alone.
- **AC-6:** Per-slide perception is prescribed in SKILL; deterministic validation covers structural contract, not re-invocation of perception.

Review closed: 2026-04-15 (BMAD re-review; first layered BMAD block for this story—prior checklist + Party Mode gate superseded for sprint tracking by this section).

## BMAD tracking closure

**Framework:** Per `sprint-status.yaml` — **`done`** = ACs met + agreed verification green + layered BMAD review complete + sprint key `done`.

| Check | State |
|-------|--------|
| ACs | Met (Irene Pass 2 cluster contract + operator workflow + templates) |
| Verification | **Completion Notes** commands; `tests/test_cluster_aware_pass2_contract_docs.py`; validator tests in **File List** |
| **`sprint-status.yaml`** | **`23-1-cluster-aware-dual-channel-grounding`: `done`** (reconciled 2026-04-15) |
| Formal BMAD | Complete — section **Adversarial Review (BMAD)** above |
