# Story 20b.2: Cluster Plan Quality Gate (G1.5)

**Epic:** 20B - Irene Cluster Intelligence - Implementation
**Status:** review
**Sprint key:** `20b-2-cluster-plan-quality-gate-g1-5`
**Added:** 2026-04-11
**Validated:** 2026-04-11
**Depends on:** [20b-1-irene-pass1-cluster-planning-implementation.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20b-1-irene-pass1-cluster-planning-implementation.md), [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md)

## Story

As an operator,
I want a G1.5 quality gate between Irene Pass 1 and Gary dispatch,
So that I can review the cluster plan as a structural document and catch brief quality failures before committing Gamma API spend on a broken cluster architecture.

## Acceptance Criteria

**Given** Irene Pass 1 has produced a cluster plan with `cluster_density` ≠ none  
**When** Marcus reaches the G1.5 gate step in the production workflow  
**Then** Marcus must automatically run `validate-cluster-plan.py` against the segment manifest and report pass/fail before any operator review is presented

**And** if G1.5 validation fails, Marcus must block progression to Gary dispatch, surface the specific failing criteria, and prompt Irene to revise the cluster plan

**And** if G1.5 validation passes, Marcus must generate a human-readable **cluster plan review document** (`cluster-plan-review.md`) in the bundle directory containing:
- Per-cluster summary: topic, narrative arc, master behavioral intent, interstitial count
- Per-interstitial summary: type, isolation target, narration burden, cluster position
- G1.5 validation status (pass/fail per criterion)
- Operator decision prompt: approve to advance to Gary dispatch, or reject with revision notes

**And** the operator must explicitly approve the cluster plan review before Gary dispatch proceeds (operator HIL gate — not auto-advance)

**And** the G1.5 gate must be skipped entirely when `cluster_density: none` — non-clustered runs proceed directly from Prompt 5 to Prompt 6 unchanged

**And** a new prompt step `5B) Cluster Plan G1.5 Gate + Operator Review` must be added to the prompt pack (v4.1 and v4.2) for clustered runs, inserted between Prompt 5 and Prompt 6

**And** `marcus_prompt_harness.py` must dynamically insert step 5B into `STANDARD_STEP_HEADINGS` and `MOTION_STEP_HEADINGS` when the run is cluster-enabled (base tuples exclude 5B to avoid index shift)

**And** the cluster plan review document format must be defined as a reference template

## Tasks / Subtasks

- [x] Task 1: Create Marcus G1.5 gate script (AC: 1-2)
  - [x] 1.1: Created `skills/bmad-agent-marcus/scripts/run-g1.5-cluster-gate.py` — wraps `validate-cluster-plan.py`, reads `cluster_density` from run-constants, reads segment manifest from bundle, writes gate receipt
  - [x] 1.2: Gate receipt: `{bundle}/g1.5-cluster-gate-receipt.json` with `status`, `cluster_count`, `errors[]`, `timestamp`
  - [x] 1.3: On G1.5 fail: prints blocking summary with criterion IDs; exit 1; no review doc generated
  - [x] 1.4: On G1.5 pass: generates `cluster-plan-review.md` in bundle directory

- [x] Task 2: Define and implement cluster plan review document (AC: 3-4)
  - [x] 2.1: Created `skills/bmad-agent-marcus/references/template-cluster-plan-review.md`
  - [x] 2.2: Template includes: per-cluster section, per-interstitial table, G1.5 summary, operator decision block
  - [x] 2.3: `run-g1.5-cluster-gate.py` generates populated review doc from manifest data

- [x] Task 3: Add Prompt 5B to production prompt packs (AC: 5-6)
  - [x] 3.1: Added `5B) Cluster Plan G1.5 Gate + Operator Review` to v4.1 prompt pack between step 5 and step 6
  - [x] 3.2: Added same step to v4.2 prompt pack
  - [x] 3.3: Prompt 5B: runs `run-g1.5-cluster-gate.py`, displays review doc, halts for operator approval, blocks on fail

- [x] Task 4: Update marcus_prompt_harness.py (AC: 7)
  - [x] 4.1: Added `CLUSTER_GATE_STEP_HEADING` constant — 5B excluded from positional index tuples by design (adding to tuples shifts all subsequent indices and breaks step 8 heading lookup)
  - [x] 4.2: Design decision documented inline in harness with rationale
  - [x] 4.3: Tests updated to assert 5B is in prompt packs (not in positional tuples)

- [x] Task 5: Tests (AC: 1-2, 7)
  - [x] 5.1: 10 tests for `run-g1.5-cluster-gate.py`: pass/fail/skip cases, receipt contents, review doc presence, CLI exit codes
  - [x] 5.2: 5 tests for harness: constant value, 5B not in tuples, both prompt packs contain 5B
  - [x] 5.3: Non-clustered run (cluster_density: none) → skip, no receipt, no review doc, exit 0

## Dev Notes

### What 20b-1 Already Delivered

**Do not re-implement these** — they exist and are tested:
- `skills/bmad-agent-marcus/scripts/validate-cluster-plan.py` — G1.5 validator with 13 criteria
- `state/config/fidelity-contracts/g1.5-cluster-plan.yaml` — fidelity contract
- `ALLOWED_CLUSTER_DENSITIES` and `cluster_density` field in `scripts/utilities/run_constants.py`

This story wraps those deliverables into a Marcus-callable gate with HIL review.

### Prompt Pack Gate Pattern (Existing Model)

The existing Gate 1 pattern at Prompt 5 (`5) Irene Pass 1 Structure + Gate 1 Fidelity`) is the model to follow. From the prompt pack:

```
Before Gate 1 approval, run internal Vera gates in order:
- G1: lesson plan vs source bundle
- G2: slide brief vs lesson plan

Return a single fidelity receipt with per-gate verdicts and blocking findings.
If G1 or G2 fail: surface specific failing criteria, block progression.
If G1 and G2 pass: return compact receipt with: stage, status, artifacts_written, validator_results, gate_decision, next_action
```

Prompt 5B follows this exact pattern for G1.5. The receipt format `{bundle}/g1.5-cluster-gate-receipt.json` mirrors the existing pattern of `preflight-results.json` and ingestion quality gate receipt.

### Prompt 5B Insertion Point

Current prompt pack order (clustered runs):
```
Prompt 5  → Irene Pass 1 + G1/G2 gates
Prompt 5B → [NEW] G1.5 Cluster Plan Gate + Operator Review ← insert here
Prompt 6  → Gate 1 Approved → Pre-Dispatch Package Build
```

Non-clustered runs skip 5B entirely. The prompt must include a conditional:
```
[CLUSTER_DENSITY ≠ none: run G1.5 gate and halt for operator review]
[CLUSTER_DENSITY = none: skip this step, proceed directly to Prompt 6]
```

### run-g1.5-cluster-gate.py Design

```
Usage: python run-g1.5-cluster-gate.py --bundle-dir <path> [--manifest <path>] [--json]
```

1. Load run-constants.yaml from bundle dir → get `cluster_density`
2. If `cluster_density` is None or `"none"` → print "SKIP: non-clustered run" and exit 0
3. Discover segment manifest: `{bundle}/segment-manifest.yaml` (default path)
4. Run `validate_cluster_plan(manifest_dict)` (import from validate-cluster-plan.py)
5. Write `{bundle}/g1.5-cluster-gate-receipt.json`
6. If fail: print blocking summary, exit 1
7. If pass: generate `{bundle}/cluster-plan-review.md` from manifest data, exit 0

The script must **import** `validate_cluster_plan` from `validate-cluster-plan.py` — do not duplicate logic. Use `importlib.util` (same pattern as `test_validate_cluster_plan.py`).

### cluster-plan-review.md Format

```markdown
# Cluster Plan Review — RUN_ID [run_id]

G1.5 Status: PASS (13/13 criteria)
Cluster count: N ([cluster_density] target)
Generated: [timestamp]

---

## Cluster [cluster_id]: [narrative_arc]

**Master behavioral intent:** [master_behavioral_intent]
**Interstitial count:** [cluster_interstitial_count]

| Position | Type | Isolation Target | Narration Burden |
|----------|------|-----------------|-----------------|
| establish (head) | — | — | — |
| [position] | [interstitial_type] | [isolation_target] | [narration_burden] |
...

---

## Operator Decision

[ ] APPROVE — advance to Gary dispatch
[ ] REJECT — return to Irene with revision notes: ________________
```

### marcus_prompt_harness.py Update

Current `STANDARD_STEP_HEADINGS` ends after step 8. Step 5B must be inserted in sequence position after `"5) Irene Pass 1 Structure + Gate 1 Fidelity"`. The harness uses these headings to validate prompt packs and generate step outputs — ordering matters.

After inserting 5B, verify that any existing harness tests that assert `len(STANDARD_STEP_HEADINGS) == N` are updated to `N+1`. Check `tests/test_marcus_prompt_harness.py` (if it exists) before modifying.

### Skip Behavior for Non-Clustered Runs

`cluster_density: none` (or absent from run-constants) → gate is a no-op:
- No receipt written
- No review document generated
- Marcus proceeds directly to Prompt 6
- Prompt 5B text must make this conditional explicit to the operator

### Previous Story Intelligence

- 20b-1 confirmed: Irene is LLM-driven; the Python layer handles config loading and validation
- The G1.5 validator uses `cluster_role is None` (not `cluster_id is None`) to identify flat segments — this design decision matters when parsing manifests in the gate script
- Pattern for importing validate-cluster-plan.py: use `importlib.util.spec_from_file_location` (same as `test_validate_cluster_plan.py` line 34-38)

## Testing Requirements

- Unit tests for `run-g1.5-cluster-gate.py`: pass/fail/skip cases
- Regression: non-clustered run produces no artifacts and exits 0
- Harness heading count test: if one exists, update for the new step
- Run full suite via `python -m pytest tests/ skills/bmad-agent-marcus/scripts/tests/ -q`

## Project Structure Notes

- **New files:**
  - `skills/bmad-agent-marcus/scripts/run-g1.5-cluster-gate.py`
  - `skills/bmad-agent-marcus/scripts/tests/test_run_g1.5_cluster_gate.py`
  - `skills/bmad-agent-marcus/references/template-cluster-plan-review.md`
- **Modified files:**
  - `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md`
  - `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
  - `scripts/utilities/marcus_prompt_harness.py`

## References

- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 20b.2 definition
- [20b-1-irene-pass1-cluster-planning-implementation.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20b-1-irene-pass1-cluster-planning-implementation.md) — G1.5 validator delivered here
- [validate-cluster-plan.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-marcus/scripts/validate-cluster-plan.py) — validator to wrap
- [g1.5-cluster-plan.yaml](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/state/config/fidelity-contracts/g1.5-cluster-plan.yaml) — fidelity contract
- [production-prompt-pack-v4.1-narrated-deck-video-export.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md) — Gate 1 pattern to follow; step 5B insertion point
- [marcus_prompt_harness.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/scripts/utilities/marcus_prompt_harness.py) — step headings to update

## File List

- skills/bmad-agent-marcus/scripts/run-g1.5-cluster-gate.py (new)
- skills/bmad-agent-marcus/scripts/tests/test_run_g1.5_cluster_gate.py (new)
- skills/bmad-agent-marcus/references/template-cluster-plan-review.md (new)
- docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md (modified)
- docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md (modified)
- scripts/utilities/marcus_prompt_harness.py (modified)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6[1m]

### Debug Log

### Debug Log

- 2026-04-11: 5B cannot be in STANDARD/MOTION_STEP_HEADINGS tuples — positional indexing breaks step 8 heading; pivoted to CLUSTER_GATE_STEP_HEADING constant + prompt pack tests

### Completion Notes List

- ✅ Task 1: run-g1.5-cluster-gate.py — wraps validator, skip/pass/fail logic, receipt + review doc generation
- ✅ Task 2: template-cluster-plan-review.md — operator HIL review document format
- ✅ Task 3: Prompt 5B added to both v4.1 and v4.2 prompt packs
- ✅ Task 4: CLUSTER_GATE_STEP_HEADING constant added to harness with design rationale
- ✅ Task 5: 15 new tests (10 gate script + 5 harness); 464 total passing

### File List

## Status

review

## Completion Status

Ultimate context engine analysis completed — comprehensive developer guide created for G1.5 Cluster Plan Quality Gate wiring story.
