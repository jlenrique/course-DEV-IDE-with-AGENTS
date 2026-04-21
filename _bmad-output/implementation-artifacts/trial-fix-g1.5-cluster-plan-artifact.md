# Story: G1.5 Gate — Accept `cluster-plan.yaml` as Pass 1 Artifact Fallback

**Status:** ready-for-dev
**Type:** fix-in-flight
**Points:** 1
**Branch:** `trial/2026-04-19` (direct — no sub-branch)
**Gate mode:** single-gate (`bmad-code-review` before done)
**Created:** 2026-04-19 — party-mode consensus (Winston, Amelia, Murat, John)
**Blocks:** Trial `C1-M1-PRES-20260419B` resume at §05B

---

## TL;DR

The G1.5 Cluster Plan Gate (`run-g1.5-cluster-gate.py`) requires `segment-manifest.yaml` — a Pass 2 artifact — but fires pre-Gary (before Pass 2 runs). It always exits code 1 "segment manifest not found." Fix: add a `cluster-plan.yaml` fallback that Irene Pass 1 can emit with structural fields only. Update the runner's file probe order and add `mode: structural | full` to the validator.

---

## Story

As the **trial operator**,
I want **the G1.5 cluster plan gate to accept a lightweight `cluster-plan.yaml` emitted by Irene Pass 1**,
So that **the gate validates cluster structure before Gary dispatch without requiring the full Pass 2 segment manifest**.

---

## Background

`run_gate()` at line 190 of `skills/bmad-agent-marcus/scripts/run-g1.5-cluster-gate.py` does:

```python
mpath = manifest_path or (bundle_dir / MANIFEST_FILENAME)  # MANIFEST_FILENAME = "segment-manifest.yaml"
if not mpath.is_file():
    raise FileNotFoundError(f"Segment manifest not found: {mpath}")
```

`segment-manifest.yaml` is produced by Irene Pass 2 — after Gary runs. §05B fires between §05 (Pass 1) and §06 (Gary). The gate always fails on a live trial because the manifest doesn't exist yet.

Irene Pass 1 already knows everything the G1.5 validator needs: cluster assignments, cluster roles, arcs, slide IDs. It just doesn't serialize them to YAML.

**Gary field contract (confirmed from `skills/bmad-agent-gamma/SKILL.md` and `context-envelope-schema.md`):**
Gary consumes `cluster_id`, `cluster_role`, `parent_slide_id`, `narrative_arc`, `interstitial_count` — all structural Pass 1 fields. Gary does NOT consume `isolation_target`, `narration_burden`, `master_behavioral_intent`, `develop_type` (those are narration/Pass 2 concerns).

---

## Acceptance Criteria

### AC-1: `cluster-plan.yaml` schema
`cluster-plan.yaml` uses the **same top-level mapping contract** as `segment-manifest.yaml`:
```yaml
cluster_density: default          # string — matches run-constants value
segments:
  - slide_id: S01
    cluster_id: null              # null for singletons
    cluster_role: null            # null | head | interstitial
    cluster_position: null        # null | establish | tension | develop | resolve
    parent_slide_id: null         # null for heads and singletons
    interstitial_type: null       # null for heads/singletons
    isolation_target: null        # null in Pass 1 — narration concern
    narrative_arc: null           # string for heads; null for interstitials/singletons
    develop_type: null            # null in Pass 1 — narration concern
    master_behavioral_intent: null # null in Pass 1 — narration concern
    cluster_interstitial_count: 0  # int for heads; 0 for others
    double_dispatch_eligible: false
    narration_burden: null        # null in Pass 1 — narration concern
```
**Do NOT invent a different schema.** The validator reads `manifest.get("segments", [])` and `manifest.get("cluster_density")` — reusing the same contract means zero validator schema changes.

### AC-2: Runner fallback probe order
In `run_gate()` (line 190–192 of `run-g1.5-cluster-gate.py`), replace the hard `FileNotFoundError` with fallback probe:

```python
CLUSTER_PLAN_FILENAME = "cluster-plan.yaml"   # add as module constant

# Replace lines 190–192:
mpath = manifest_path or (bundle_dir / MANIFEST_FILENAME)
if not mpath.is_file():
    mpath = bundle_dir / CLUSTER_PLAN_FILENAME   # probe cluster-plan.yaml second
if not mpath.is_file():
    raise FileNotFoundError(
        f"Neither {MANIFEST_FILENAME} nor {CLUSTER_PLAN_FILENAME} found in {bundle_dir}"
    )
```

When `--manifest` is supplied explicitly, that path wins unconditionally (existing behavior preserved).

### AC-3: `source_artifact` in receipt
Add `source_artifact` (optional, with default `None`) to the receipt written at lines 208–216:

```python
receipt: dict[str, Any] = {
    "status": "pass" if result["passed"] else "fail",
    "cluster_count": len(cluster_ids),
    "cluster_density": cluster_density,
    "errors": result["errors"],
    "timestamp": timestamp,
    "source_artifact": mpath.name,   # "cluster-plan.yaml" or "segment-manifest.yaml"
}
```

Old receipts without `source_artifact` must remain parseable (field is additive — no breaking change).

### AC-4: `validate_cluster_plan()` mode parameter
Add `mode: str = "full"` to `validate_cluster_plan()` in `validate-cluster-plan.py`. In `"structural"` mode, skip checks for narration-time fields that will be null in Pass 1:

Fields to skip in structural mode: `isolation_target`, `narration_burden`, `master_behavioral_intent`, `develop_type`

Fields to check in structural mode: `cluster_id`, `cluster_role`, `cluster_position`, `parent_slide_id`, `interstitial_type`, `narrative_arc`, `cluster_interstitial_count`, `double_dispatch_eligible`

The runner selects mode based on which artifact was resolved:
- `cluster-plan.yaml` → `validate_cluster_plan(manifest, mode="structural")`
- `segment-manifest.yaml` → `validate_cluster_plan(manifest, mode="full")` (existing behavior)

### AC-5: Gate runs against live bundle
`PYTHONPATH=. .venv/Scripts/python.exe skills/bmad-agent-marcus/scripts/run-g1.5-cluster-gate.py --bundle-dir "course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion"` exits code 0 (pass) or 1 (fail on content — not on missing file) after `cluster-plan.yaml` is present.

### AC-6: `cluster-plan-review.md` parseable from minimal artifact
`_build_review_doc()` renders `—` placeholders for absent narration fields (`isolation_target`, `narration_burden`). Test that when built from a minimal `cluster-plan.yaml`, the review doc file is written and is valid markdown (no exceptions, no empty file).

### AC-7: Gary field contract confirmed in story
`cluster-plan.yaml` carries: `cluster_id`, `cluster_role`, `parent_slide_id`, `narrative_arc`, `cluster_interstitial_count`. These are the **only** cluster fields Gary's context envelope schema consumes. Confirmed from `skills/bmad-agent-gamma/references/context-envelope-schema.md` lines 63, 66, 86, 88, 170–181. Dev agent: read that file before implementation to confirm no fields were missed.

### AC-8: Backward compat — existing segment-manifest.yaml path unbroken
All 12 existing tests in `test_run_g1_5_cluster_gate.py` pass without modification. Tests that write `segment-manifest.yaml` continue to use the preferred (non-fallback) path.

### AC-9: Murat's five traps addressed
1. **Receipt field drift** — `source_artifact` is optional with default `None` (AC-3 above) ✓
2. **Validator mode coupling** — explicit `mode` param, default `"full"` (AC-4 above) ✓
3. **G1.5-08 `double_dispatch_eligible`** — explicitly include in structural mode checks (not skipped); `cluster-plan.yaml` must populate this field (default `false` for all interstitials) ✓
4. **`_build_review_doc` with minimal artifact** — narration fields render as `—`; add parseable-output test (AC-6 above) ✓
5. **`cluster_density` injection** — existing injection path (lines 196–197) unchanged; `cluster-plan.yaml` may omit `cluster_density` and it will be injected from run-constants ✓

### AC-10: Deferred inventory updated
Add to `_bmad-output/planning-artifacts/deferred-inventory.md` §Named-But-Not-Filed Follow-Ons:
> "Converge `cluster-plan.yaml` and `segment-manifest.yaml` to single pre-Gary artifact shape — currently two files, two schemas, one gate. Named by party-mode 2026-04-19."

### AC-11: Cora hook exits 0
Run `PYTHONPATH=. .venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` and confirm exit 0 after all changes. If `steps[05B]` in `state/config/pipeline-manifest.yaml` is updated to document `cluster-plan.yaml` in an `emits` field (optional but recommended), treat as Tier-1 prose change — regenerate pack and confirm L1 passes.

---

## Test Matrix (K-floor 1.3–1.5×, target 10–12 new/updated tests)

### New tests in `test_run_g1_5_cluster_gate.py`

| # | Test name | What it covers |
|---|---|---|
| 1 | `test_fallback_to_cluster_plan_when_manifest_absent` | Mode A happy path: `cluster-plan.yaml` present, no `segment-manifest.yaml` → exit 0, receipt written, `source_artifact: cluster-plan.yaml` |
| 2 | `test_cluster_plan_invalid_fields_fails` | Mode A failure: `cluster-plan.yaml` present with invalid structural fields → exit 1, clean error, receipt `status: fail` |
| 3 | `test_cluster_plan_density_none_skips` | Mode A skip: `cluster-plan.yaml` present, `cluster_density: none` → gate skips |
| 4 | `test_cluster_plan_density_absent_skips` | Mode A skip: `cluster-plan.yaml` present, no `cluster_density` key → injected from run-constants; if none → skip |
| 5 | `test_both_files_present_cluster_plan_wins` | Mode C priority: both files present → `cluster-plan.yaml` wins; `source_artifact: cluster-plan.yaml` in receipt |
| 6 | `test_neither_file_present_raises` | Mode C error: neither file → `FileNotFoundError` message cites both filenames |
| 7 | `test_malformed_cluster_plan_yaml_exits_1` | Mode C edge: malformed YAML in `cluster-plan.yaml` → clean exit 1, no partial receipt |
| 8 | `test_review_doc_parseable_from_minimal_cluster_plan` | AC-6: `_build_review_doc` from minimal `cluster-plan.yaml` → file written, valid markdown, no exception |
| 9 | `test_source_artifact_in_receipt` | AC-3: receipt contains `source_artifact` field when cluster-plan used |
| 10 | `test_segment_manifest_source_artifact_present` | AC-8 regression: existing segment-manifest path sets `source_artifact: segment-manifest.yaml` |

### New tests in `test_validate_cluster_plan.py`

| # | Test name | What it covers |
|---|---|---|
| 11 | `test_structural_mode_passes_with_null_narration_fields` | AC-4: minimal `cluster-plan.yaml` with null isolation_target/narration_burden/master_behavioral_intent/develop_type → `passed: True` in structural mode |
| 12 | `test_full_mode_fails_on_null_narration_fields` | AC-4 boundary: same minimal dict in full mode → validation errors on narration fields |

---

## Implementation Notes

### File locations
- `skills/bmad-agent-marcus/scripts/run-g1.5-cluster-gate.py` — lines 48, 190–216
- `skills/bmad-agent-marcus/scripts/validate-cluster-plan.py` — `validate_cluster_plan()` signature
- `skills/bmad-agent-marcus/scripts/tests/test_run_g1_5_cluster_gate.py` — add 10 tests
- `skills/bmad-agent-marcus/scripts/tests/test_validate_cluster_plan.py` — add 2 tests
- `_bmad-output/planning-artifacts/deferred-inventory.md` — add follow-on entry
- `state/config/pipeline-manifest.yaml` — optional Tier-1 prose update to `steps[05B]`

### Do NOT touch
- `segment-manifest.yaml` schema — no changes
- Existing 12 `test_run_g1_5_cluster_gate.py` tests — must pass unmodified
- Existing 26 `test_validate_cluster_plan.py` tests — must pass unmodified (new `mode` param defaults to `"full"`)
- `state/config/pipeline-manifest.yaml` block_mode_trigger_paths — runner script is not in this list; no Cora hook on gate script changes

### `cluster-plan.yaml` for current trial bundle
After implementation, generate `cluster-plan.yaml` for the live bundle `apc-c1m1-tejal-20260419b-motion` from `irene-pass1.md`. The plan has 14 slides: 2 singletons (S01, S12) and 5 cluster-head+interstitial groups. Cluster density is `default` (3–5 clusters). Pass the gate and confirm receipt + review doc are written before resuming the trial.

### Existing code pattern to follow
`validate-cluster-plan.py` already uses `frozenset` constants for valid field values and a consistent `errors: list[str]` return pattern. Follow the same pattern for any new checks added to structural mode.

---

## Definition of Done

- [ ] All 12 existing `test_run_g1_5_cluster_gate.py` tests pass
- [ ] All 26 existing `test_validate_cluster_plan.py` tests pass
- [ ] All 12 new tests (10 runner + 2 validator) pass
- [ ] Live bundle gate runs without FileNotFoundError
- [ ] `g1.5-cluster-gate-receipt.json` written with `source_artifact` field
- [ ] `cluster-plan-review.md` written and parseable
- [ ] `deferred-inventory.md` updated with convergence follow-on
- [ ] `bmad-code-review` single-gate passes
- [ ] Cora hook (check_pipeline_manifest_lockstep.py) exits 0
