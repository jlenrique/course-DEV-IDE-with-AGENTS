# Story 20c.15: Parent Slide Count Architecture + Profile-Aware Estimator

Status: done

## Story

As a **production operator (via Marcus)**,
I want the slide count and runtime polling step to operate in terms of **parent slide count** (head slides only) and **target runtime**, with the estimator deriving all expansion parameters from the active experience profile,
so that interstitial cluster counts, word budgets, and per-slide timing are system-derived rather than manually configured, and the feasibility triangle is validated before locking.

## Background & Design Consensus

This story implements the consensus from two rounds of BMAD Party Mode design discussion (2026-04-15), involving Winston (Architect), Caravaggio (Presentation Expert), Murat (Test Architect), and John (PM).

### Core Design Decisions

1. **`parent_slide_count` replaces `locked_slide_count`** — The operator thinks in terms of head (parent) slides. Interstitials are system-derived from the experience profile's `cluster_expansion` block.
2. **Two operator inputs only** — `parent_slide_count` + `target_total_runtime_minutes`. Everything else is derived.
3. **Expansion factor lives in the profile** — Each experience profile carries a `cluster_expansion` block with `avg_interstitials_per_cluster`, `interstitial_range`, `singleton_ratio`, and profile-specific word budgets.
4. **Feasibility triangle** — `parent_count × (1 + avg_interstitials × (1 - singleton_ratio)) × avg_slide_seconds ≤ target_runtime_seconds`. Must PASS before lock.
5. **Profile-specific word budgets** — Visual-led gets tighter word ranges (head: 60-100, interstitial: 15-30) than text-led (head: 80-140, interstitial: 25-40).

### Divergent Spec Resolutions

| Point | Winston | Caravaggio | Resolution |
|-------|---------|------------|------------|
| Expansion measure | `expansion_factor: 2.5` | `avg_interstitials_per_cluster: 1.5` | **Caravaggio** — more granular, profile-specific |
| Cluster depth range | `[1, 4]` | `interstitial_range: [0, 3]` | **Caravaggio** — allows 0 (singletons handled by `singleton_ratio`) |
| Interstitial word range (visual-led) | `[20, 35]` | `[15, 30]` | **Caravaggio** — tighter for visual-led |
| Estimator advisory | Not proposed | `parents_per_minute` per profile | **Caravaggio** — useful for system recommendation |

## Acceptance Criteria

### AC-1: Experience profiles carry cluster expansion

Given `state/config/experience-profiles.yaml` with `schema_version: "1.1"`,
When the file is loaded,
Then each profile contains a `cluster_expansion` block with:
- `avg_interstitials_per_cluster` (float)
- `interstitial_range` (2-element list [min, max])
- `singleton_ratio` (float, 0.0-1.0)
- `cluster_head_word_range` (2-element list [min, max])
- `interstitial_word_range` (2-element list [min, max])
- `estimator_advisory.parents_per_minute` (float)

### AC-2: Estimator is profile-aware

Given `scripts/utilities/slide_count_runtime_estimator.py`,
When called with `(extracted_md_path, parent_slide_count, target_runtime_minutes, experience_profile)`,
Then it:
- Loads the active profile from `experience-profiles.yaml`
- Derives `estimated_total_slides` from `parent_slide_count × (1 + avg_interstitials × (1 - singleton_ratio))`
- Runs the feasibility triangle check
- Returns a result dict with `parent_slide_count`, `estimated_total_slides`, `target_total_runtime_minutes`, `feasibility` (PASS/WARN/BLOCK), `avg_slide_seconds` (derived), `profile_used`, and `word_budgets`
- No longer hardcodes 45s avg, 0.5 variability, or conflicting mode proportions

### AC-3: Operator polling simplified

Given `scripts/utilities/operator_polling.py`,
When the operator poll runs,
Then it:
- Polls for only `parent_slide_count` and `target_total_runtime_minutes`
- Pre-fills system recommendations from the estimator
- Removed: `slide_runtime_average_seconds`, `slide_runtime_variability_scale`, `slide_mode_proportions` overrides
- Loops until feasibility PASS before returning locked values
- `check_runtime_feasibility()` uses the profile-aware feasibility triangle

### AC-4: Prompt 4.5 updated

Given `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`,
When Prompt 4.5 is read,
Then:
- Field names are `parent_slide_count` and `target_total_runtime_minutes` (not `locked_slide_count`, `slide_runtime_average_seconds`, `slide_runtime_variability_scale`)
- The estimator call includes `--experience-profile [EXPERIENCE_PROFILE]`
- Feasibility gate language is present
- Derived fields listed as system-computed (not operator-polled)

### AC-5: Narration parameters carry profile override comment

Given `state/config/narration-script-parameters.yaml`,
When the cluster_narration section is read,
Then a comment notes that per-profile `cluster_expansion.cluster_head_word_range` / `interstitial_word_range` override these defaults when an experience profile is active.

### AC-6: G1.5 gate gains 3 new criteria

Given `state/config/fidelity-contracts/g1.5-cluster-plan.yaml`,
Then it contains:
- **G1.5-15** (Expansion compliance): realized interstitial count per cluster falls within the profile's `interstitial_range`
- **G1.5-16** (Cluster balance): singleton ratio across all clusters approximates the profile's `singleton_ratio` (±15%)
- **G1.5-17** (Runtime fit): `total_estimated_slides × avg_slide_seconds ≤ target_runtime_seconds` with ≤5% overshoot tolerance

### AC-7: G4 criteria updated

Given `state/config/fidelity-contracts/g4-narration-script.yaml`,
Then:
- **G4-10** description updated to reference `parent_slide_count` instead of `locked_slide_count`
- **G4-17** (Cluster word budget) updated: when an experience profile is active, word budget ranges come from the profile's `cluster_expansion` block, not the global `narration-script-parameters.yaml` defaults

### AC-8: Downstream consumers updated (field rename)

All files carrying `locked_slide_count` or `slide_runtime_average_seconds` or `slide_runtime_variability_scale` are updated to the new field names or have those fields removed where no longer applicable:

| File | Change |
|------|--------|
| `skills/bmad-agent-marcus/scripts/generate-storyboard.py` | Update `runtime_plan.get()` calls |
| `skills/bmad-agent-marcus/scripts/prepare-irene-pass2-handoff.py` | Update envelope packing |
| `skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py` | Update test fixtures + assertions |
| `skills/bmad-agent-marcus/scripts/tests/test_prepare_irene_pass2_handoff.py` | Update test fixtures + assertions |
| `docs/workflow/trial-run-pass2-artifacts-contract.md` | Update field names in contract spec |
| `skills/bmad-agent-content-creator/references/cluster-density-controls.md` | Update reference to `parent_slide_count` |
| `skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md` | Update G4-10 description |
| `scripts/utilities/run_constants.py` | Review `RunConstants` dataclass for field name updates |

### AC-9: Epic documentation updated

`_bmad-output/planning-artifacts/epics-interstitial-clusters.md` updated with a new story (20c-15) entry under Epic 20c documenting this work.

### AC-10: Existing tests pass

All existing tests remain green after field rename propagation. Any test fixture using old field names is updated.

### AC-11: E2E integration test covers full estimator→polling→handoff chain

Given the estimator, operator polling, and Irene Pass 2 handoff all use the new field names and profile-aware interface,
When a single end-to-end test runs the chain (estimator produces result → polling consumes it → handoff envelope packs it),
Then all field names, profile references, and derived values are consistent across the boundary and the downstream envelope contains `parent_slide_count`, `estimated_total_slides`, `avg_slide_seconds`, and `profile_used`.

### AC-12: Parameter directory cross-links updated

Given `docs/parameter-directory.md` is the canonical parameter reference,
When the new fields (`parent_slide_count`, `estimated_total_slides`, `avg_slide_seconds`) are introduced and old fields (`locked_slide_count`, `slide_runtime_average_seconds`, `slide_runtime_variability_scale`) are retired,
Then `parameter-directory.md` reflects the rename with updated entries, cross-links, and deprecation notes in a single audit pass.

### AC-13: Run-constants template carries new field names

Given run-constants templates (or template-generation logic) are used to seed new production runs,
When a new bundle is initialized,
Then the template carries `parent_slide_count` and `target_total_runtime_minutes` as the operator-input fields (not `locked_slide_count`), and derived fields are documented as system-computed.

## Tasks / Subtasks

### Task 1: Experience Profiles Schema Update (AC: 1)

- [ ] 1.1 Bump `schema_version` from `"1.0"` to `"1.1"` in `state/config/experience-profiles.yaml`
- [ ] 1.2 Add `cluster_expansion` block to `visual-led` profile:
  ```yaml
  cluster_expansion:
    avg_interstitials_per_cluster: 1.5
    interstitial_range: [0, 3]
    singleton_ratio: 0.30
    cluster_head_word_range: [60, 100]
    interstitial_word_range: [15, 30]
    estimator_advisory:
      parents_per_minute: 1.5
  ```
- [ ] 1.3 Add `cluster_expansion` block to `text-led` profile:
  ```yaml
  cluster_expansion:
    avg_interstitials_per_cluster: 3.0
    interstitial_range: [1, 5]
    singleton_ratio: 0.10
    cluster_head_word_range: [80, 140]
    interstitial_word_range: [25, 40]
    estimator_advisory:
      parents_per_minute: 0.95
  ```

### Task 2: Estimator Rewrite (AC: 2)

- [ ] 2.1 Replace `analyze_content_for_slides()` with `estimate_and_validate()` accepting `(extracted_md_path, parent_slide_count, target_runtime_minutes, experience_profile)`
- [ ] 2.2 Load profile from `experience-profiles.yaml` using `experience_profile` key
- [ ] 2.3 Derive `estimated_total_slides` = `parent_slide_count × (1 + avg_interstitials × (1 - singleton_ratio))`
- [ ] 2.4 Derive `avg_slide_seconds` = `(target_runtime_minutes × 60) / estimated_total_slides`
- [ ] 2.5 Implement feasibility triangle: PASS (all 5 conditions), WARN (marginal), BLOCK (any hard fail)
  - Condition 1: `estimated_total_slides × avg_slide_seconds ≤ target_runtime_seconds` (≤5% overshoot = WARN, >5% = BLOCK)
  - Condition 2: `avg_slide_seconds ≥ 8` (minimum viable slide duration)
  - Condition 3: `avg_slide_seconds ≤ 90` (maximum before attention drops)
  - Condition 4: `parent_slide_count ≥ 1`
  - Condition 5: `target_runtime_minutes ≥ 0.5`
- [ ] 2.6 Return result dict with: `parent_slide_count`, `estimated_total_slides`, `target_total_runtime_minutes`, `avg_slide_seconds`, `feasibility` (PASS/WARN/BLOCK), `feasibility_details`, `profile_used`, `word_budgets` (from profile), `analysis` (content analysis), `recommendation` (system-recommended parent count from `word_count / (wpm × 60 / parents_per_minute)`)
- [ ] 2.7 Keep backward-compatible `analyze_content_for_slides()` as a thin wrapper that calls `estimate_and_validate()` with default profile, for any callers not yet updated
- [ ] 2.8 Update CLI `main()` to accept `--parent-slides`, `--target-runtime`, `--experience-profile` args
- [ ] 2.9 Remove hardcoded 45s avg, 0.5 variability, 150 WPM (use profile's `estimator_advisory.parents_per_minute` and narration_density.target_wpm from narration-script-parameters.yaml)

### Task 3: Operator Polling Rewrite (AC: 3)

- [ ] 3.1 Simplify `poll_operator_for_runtime_params()` to poll only `parent_slide_count` and `target_total_runtime_minutes`
- [ ] 3.2 Pre-fill system recommendations from estimator's `recommendation` field
- [ ] 3.3 Remove choices 4 (override avg runtime), 5 (override variability), 6 (override proportions) — these are now profile-derived
- [ ] 3.4 Rewrite `check_runtime_feasibility()` to call the estimator's feasibility triangle
- [ ] 3.5 Loop on BLOCK: if feasibility fails, show the failure reason and re-poll
- [ ] 3.6 Return dict with `parent_slide_count`, `target_total_runtime_minutes` (operator-confirmed), plus all derived values from estimator
- [ ] 3.7 Update range validation: `parent_slide_count` 1-50 (not 1-20), `target_total_runtime_minutes` 0.5-60 (not 1-30)

### Task 4: Prompt 4.5 Update (AC: 4)

- [ ] 4.1 Update Prompt 4.5 section header and body in `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- [ ] 4.2 Replace `locked_slide_count` with `parent_slide_count` in Required locking
- [ ] 4.3 Remove `slide_runtime_average_seconds` and `slide_runtime_variability_scale` from Required locking
- [ ] 4.4 Add derived fields note: `estimated_total_slides`, `avg_slide_seconds`, `feasibility_result` (system-computed, persisted for audit)
- [ ] 4.5 Update estimator call to include `--experience-profile [EXPERIENCE_PROFILE]`
- [ ] 4.6 Add feasibility gate: "If feasibility is BLOCK, re-poll. If WARN, surface warning and require explicit operator acknowledgment."
- [ ] 4.7 Add changelog entry `2026-04-15e`

### Task 5: Narration Parameters Comment (AC: 5)

- [ ] 5.1 Add comment to `cluster_narration` section in `state/config/narration-script-parameters.yaml` noting profile overrides

### Task 6: G1.5 Gate Criteria (AC: 6)

- [ ] 6.1 Add G1.5-15 (expansion compliance) to `state/config/fidelity-contracts/g1.5-cluster-plan.yaml`
- [ ] 6.2 Add G1.5-16 (cluster balance / singleton ratio) 
- [ ] 6.3 Add G1.5-17 (runtime fit)

### Task 7: G4 Gate Criteria (AC: 7)

- [ ] 7.1 Update G4-10 description in `state/config/fidelity-contracts/g4-narration-script.yaml` to reference `parent_slide_count`
- [ ] 7.2 Update G4-17 description to note profile-derived word budgets when experience profile is active

### Task 8: Field Rename Propagation (AC: 8)

- [ ] 8.1 `generate-storyboard.py` — update `runtime_plan.get("slide_runtime_average_seconds")` (line ~2262) and `runtime_plan.get("slide_runtime_variability_scale")` (line ~2269). Replace with profile-derived equivalents or remove if no longer consumed by storyboard.
- [ ] 8.2 `prepare-irene-pass2-handoff.py` — update envelope `runtime_plan` dict (lines ~139-142): replace `locked_slide_count` → `parent_slide_count`, remove `slide_runtime_average_seconds` and `slide_runtime_variability_scale`, add `estimated_total_slides` and `avg_slide_seconds`
- [ ] 8.3 `test_generate_storyboard.py` — update all test fixtures using old field names (lines ~566, 567, 621, 1160, 1161, 1332)
- [ ] 8.4 `test_prepare_irene_pass2_handoff.py` — update test fixtures (lines ~129-132) and assertions (line ~198)
- [ ] 8.5 `trial-run-pass2-artifacts-contract.md` — update field name list (lines ~328-331)
- [ ] 8.6 `cluster-density-controls.md` — update `locked_slide_count` reference (line ~132)
- [ ] 8.7 `gate-evaluation-protocol.md` — update G4-10 field names (line ~154)
- [ ] 8.8 `run_constants.py` — review `RunConstants` dataclass; if `locked_slide_count` is a field, rename to `parent_slide_count`; assess whether `slide_runtime_average_seconds` / `slide_runtime_variability_scale` should be removed or replaced

### Task 9: Epic Documentation (AC: 9)

- [ ] 9.1 Add Story 20c-15 entry to `_bmad-output/planning-artifacts/epics-interstitial-clusters.md` under Epic 20c

### Task 10: Test Verification (AC: 10, 11)

- [ ] 10.1 Run full test suite to confirm all existing tests pass after field rename propagation
- [ ] 10.2 Fix any test failures caused by the rename
- [ ] 10.3 Add feasibility triangle unit tests (E2):
  - PASS case: all 5 conditions satisfied
  - WARN case: ≤5% runtime overshoot (Condition 1 marginal)
  - BLOCK case: >5% overshoot
  - BLOCK case: `avg_slide_seconds < 8` (Condition 2)
  - BLOCK case: `avg_slide_seconds > 90` (Condition 3)
  - BLOCK case: `parent_slide_count = 0` (Condition 4)
  - BLOCK case: `target_runtime_minutes < 0.5` (Condition 5)
  - Edge: `singleton_ratio = 0.0` → maximum expansion, verify estimated_total_slides
  - Edge: `singleton_ratio = 1.0` → no expansion, estimated_total_slides = parent_slide_count
  - Edge: very short runtime (30s) → verify BLOCK triggers
- [ ] 10.4 Add profile resolution edge-case tests (E3):
  - Profile key not found in experience-profiles.yaml → `RunConstantsError`
  - Malformed YAML (invalid syntax) → graceful error
  - Profile exists but `cluster_expansion` block missing → `RunConstantsError` with clear message
  - Schema version mismatch (e.g. loading "1.0" profile without `cluster_expansion`) → error or fallback documented
- [ ] 10.5 Add backward compatibility wrapper test (E4):
  - `analyze_content_for_slides()` callable without `experience_profile` argument
  - Returns a valid result dict using a default profile
  - Does not raise when called with legacy signature
- [ ] 10.6 Add operator WARN→ACK→PASS cycle test (E5):
  - Simulate feasibility returning WARN → verify polling surfaces warning
  - Simulate operator ACK after WARN → verify lock proceeds
  - Simulate feasibility returning BLOCK → verify re-poll loop (no lock)
- [ ] 10.7 Add E2E integration test (E1):
  - Wire estimator → polling → handoff envelope in a single test
  - Assert `parent_slide_count`, `estimated_total_slides`, `avg_slide_seconds`, `profile_used` flow through all boundaries
  - Assert old field names (`locked_slide_count`, `slide_runtime_average_seconds`, `slide_runtime_variability_scale`) do NOT appear in the final envelope

### Task 11: Parameter Directory Cross-Link Audit (AC: 12)

- [ ] 11.1 Audit `docs/parameter-directory.md` for all references to `locked_slide_count`, `slide_runtime_average_seconds`, `slide_runtime_variability_scale`
- [ ] 11.2 Add entries for `parent_slide_count`, `estimated_total_slides`, `avg_slide_seconds` with correct owners, consumers, and cross-links
- [ ] 11.3 Mark old field entries as deprecated with pointer to replacement fields

### Task 12: Run-Constants Template Update (AC: 13)

- [ ] 12.1 Locate run-constants template(s) or template-generation logic
- [ ] 12.2 Replace `locked_slide_count` with `parent_slide_count` in template
- [ ] 12.3 Ensure `estimated_total_slides` and `avg_slide_seconds` are documented as system-computed (not operator-input) in template comments

## Dev Notes

### Execution Order (Critical Path)

1. **Task 1** (experience-profiles.yaml) — foundation, everything depends on this schema
2. **Task 2** (estimator rewrite) — depends on Task 1 schema
3. **Task 3** (operator polling) — depends on Task 2 interface
4. **Task 4** (Prompt 4.5) — depends on Task 2+3 interface
5. **Task 5** (narration params comment) — independent, safe anytime
6. **Task 6** (G1.5 criteria) — depends on Task 1 schema
7. **Task 7** (G4 criteria) — independent of code changes
8. **Task 8** (field rename propagation) — the widest blast radius, do after estimator is stable
9. **Task 9** (epic docs) — anytime
10. **Task 10** (test verification + new test cases) — final gate, must be last. Includes E1-E5 enhancements.
11. **Task 11** (parameter-directory.md audit) — after Task 8 field renames are stable
12. **Task 12** (run-constants template) — after Task 8 field renames are stable

### Architecture Constraints

- **Profile YAML is sole source of truth** — estimator reads from `experience-profiles.yaml`, never hardcodes
- **Backward compatibility** — `analyze_content_for_slides()` must remain callable for any legacy paths
- **Resolver invariant (Story 20c-13)** — the profile resolver is a pure function in `run_constants.py`. This story does NOT change the resolver; it adds a new consumer (the estimator) that reads the same profile YAML
- **SPOC invariant** — operator interacts with Marcus only. The estimator runs behind Marcus; operator never calls it directly
- **No Irene direct reads** — Irene gets word budgets via the delegation envelope, not by reading `experience-profiles.yaml` (constraint from 20c-13)

### Files to Touch (Complete List)

| # | Path | Change Type |
|---|------|-------------|
| 1 | `state/config/experience-profiles.yaml` | MODIFY — add `cluster_expansion`, bump schema |
| 2 | `scripts/utilities/slide_count_runtime_estimator.py` | REWRITE — profile-aware estimator |
| 3 | `scripts/utilities/operator_polling.py` | REWRITE — simplified 2-input poll |
| 4 | `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` | MODIFY — Prompt 4.5 + changelog |
| 5 | `state/config/narration-script-parameters.yaml` | MODIFY — add comment |
| 6 | `state/config/fidelity-contracts/g1.5-cluster-plan.yaml` | MODIFY — add 3 criteria |
| 7 | `state/config/fidelity-contracts/g4-narration-script.yaml` | MODIFY — update 2 criteria |
| 8 | `skills/bmad-agent-marcus/scripts/generate-storyboard.py` | MODIFY — field rename |
| 9 | `skills/bmad-agent-marcus/scripts/prepare-irene-pass2-handoff.py` | MODIFY — field rename |
| 10 | `skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py` | MODIFY — fixture rename |
| 11 | `skills/bmad-agent-marcus/scripts/tests/test_prepare_irene_pass2_handoff.py` | MODIFY — fixture rename |
| 12 | `docs/workflow/trial-run-pass2-artifacts-contract.md` | MODIFY — field rename |
| 13 | `skills/bmad-agent-content-creator/references/cluster-density-controls.md` | MODIFY — field rename |
| 14 | `skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md` | MODIFY — field rename |
| 15 | `scripts/utilities/run_constants.py` | REVIEW — field rename if applicable |
| 16 | `_bmad-output/planning-artifacts/epics-interstitial-clusters.md` | MODIFY — add story entry |
| 17 | `docs/parameter-directory.md` | MODIFY — cross-link audit: add new fields, deprecate old |
| 18 | Run-constants template / template logic | MODIFY — carry `parent_slide_count`, remove `locked_slide_count` |

### Cluster Expansion Values (Caravaggio Consensus)

**Visual-led profile:**
- avg_interstitials_per_cluster: 1.5
- interstitial_range: [0, 3]
- singleton_ratio: 0.30 (30% of parents have zero interstitials)
- cluster_head_word_range: [60, 100] (tighter than global default of [80, 140])
- interstitial_word_range: [15, 30] (tighter than global default of [25, 40])
- estimator_advisory.parents_per_minute: 1.5

**Text-led profile:**
- avg_interstitials_per_cluster: 3.0
- interstitial_range: [1, 5]
- singleton_ratio: 0.10 (almost all parents get clusters)
- cluster_head_word_range: [80, 140] (matches global default)
- interstitial_word_range: [25, 40] (matches global default)
- estimator_advisory.parents_per_minute: 0.95

**Design rationale (Caravaggio):** Visual-led ≠ "dwell on slides." It means the VO/sfx/music isn't reading from slides — narration is lighter, interstitials are shorter visual beats. Text-led narration reads more from slides as scripts/cue cards, so clusters are deeper and word budgets match the existing defaults.

### Feasibility Triangle (Murat Consensus)

Five conditions, all must PASS:
1. `estimated_total_slides × avg_slide_seconds ≤ target_runtime_seconds` (≤5% = WARN, >5% = BLOCK)
2. `avg_slide_seconds ≥ 8` (min viable duration)
3. `avg_slide_seconds ≤ 90` (max attention span)
4. `parent_slide_count ≥ 1`
5. `target_runtime_minutes ≥ 0.5`

If ANY condition is BLOCK → re-poll (do not lock).
If ANY condition is WARN with no BLOCK → surface warning, require operator ACK.

### Edge Cases (Murat)

| Edge Case | Resolution |
|-----------|------------|
| parent_slide_count = 0 | BLOCK — at least 1 parent required |
| target_runtime < 30s | BLOCK — below minimum viable |
| Profile not found | Raise `RunConstantsError` (consistent with 20c-13 resolver) |
| Singleton ratio = 1.0 | All parents are unclustered; estimated_total_slides = parent_slide_count |
| Singleton ratio = 0.0 | All parents get clusters; maximum expansion |
| Extreme parent count (>30) | WARN — unusual but permitted; surface advisory |

### Testing Standards

- Existing tests: 229+ baseline must remain green
- Field rename: every test fixture using old names must be updated
- New coverage needed (Tasks 10.3–10.7):
  - **Feasibility triangle**: 10+ cases covering all 5 conditions in PASS/WARN/BLOCK states, plus singleton_ratio boundary edges (0.0, 1.0)
  - **Profile resolution**: 4 negative cases (not found, malformed, missing cluster_expansion, version mismatch)
  - **Backward compat**: `analyze_content_for_slides()` legacy wrapper still callable without profile arg
  - **WARN→ACK→PASS cycle**: operator polling loop behavior on WARN vs BLOCK
  - **E2E chain**: single test wiring estimator → polling → handoff, asserting old field names are absent from final envelope
- No new test files required — update existing test fixtures and add cases to existing test modules

### Project Structure Notes

- `state/config/` — YAML config files (experience-profiles, narration-script-parameters, fidelity-contracts)
- `scripts/utilities/` — Python utility scripts (estimator, polling, run_constants)
- `skills/bmad-agent-marcus/scripts/` — Marcus agent scripts (storyboard, Irene handoff)
- `docs/workflow/` — Prompt packs and workflow contracts
- `_bmad-output/planning-artifacts/` — Epic/story planning docs

### Historical Artifact (Out of Scope)

- `_bmad-output/implementation-artifacts/20a-4-operator-cluster-density-controls.md` — Contains example YAML with `locked_slide_count: 15`. This is a historical story artifact, not an active contract. Do NOT update unless operator specifically requests it.

### References

- [Source: Party Mode Round 1 — 2026-04-15 design discussion transcript (session context)]
- [Source: Party Mode Round 2 — Winston, Caravaggio, Murat, research subagent consensus (session context)]
- [Source: `state/config/experience-profiles.yaml` — current schema v1.0]
- [Source: `scripts/utilities/slide_count_runtime_estimator.py` — current profile-unaware implementation]
- [Source: `_bmad-output/planning-artifacts/epics-interstitial-clusters.md` — Epic 20c charter]
- [Source: `state/config/fidelity-contracts/g1.5-cluster-plan.yaml` — current 13 criteria]
- [Source: `state/config/fidelity-contracts/g4-narration-script.yaml` — current 19 criteria]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (GitHub Copilot)

### Completion Notes List

1. All 12 implementation tasks completed in sequence.
2. 31 new tests in `tests/test_slide_count_estimator.py` — all GREEN.
3. 96 total tests across 4 test files — all GREEN (0 failures, 0 regressions).
4. BMAD Code Review completed (3-layer adversarial: Blind Hunter, Edge Case Hunter, Acceptance Auditor).
   - 10 findings total: 0 CRITICAL, 0 HIGH, 3 MEDIUM, 5 LOW, 2 informational.
   - 2 patches applied: (a) CLI flag mismatch in Prompt 4.5 (`--profile` → `--experience-profile`), (b) TODO comment on legacy fallback chain in `generate-storyboard.py`.
   - 8 findings dismissed with rationale (by-design, unreachable paths, over-engineering, project-controlled config).
   - 13 acceptance criteria validated: 12 PASS, 1 PARTIAL (AC-13 RunConstants — by architecture, runtime plan fields use raw dict access, not dataclass fields).
5. `RunConstants` dataclass confirmed NOT to have `locked_slide_count` — runtime plan fields consumed via raw YAML dict in `_load_runtime_plan()`. No rename needed in dataclass.
6. Backward compatibility preserved: `analyze_content_for_slides()` wrapper retained, `generate-storyboard.py` fallback chain for old field names.

### File List

**New files:**
- `tests/test_slide_count_estimator.py` — 31 tests across 8 test classes

**Modified files (17):**
- `state/config/experience-profiles.yaml` — schema 1.0→1.1, cluster_expansion blocks
- `scripts/utilities/slide_count_runtime_estimator.py` — full rewrite with estimate_and_validate()
- `scripts/utilities/operator_polling.py` — 2-input poll + feasibility delegation
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` — Prompt 4.5 rewrite + CLI flag fix
- `state/config/narration-script-parameters.yaml` — profile-override comment
- `state/config/fidelity-contracts/g1.5-cluster-plan.yaml` — G1.5-15, G1.5-16, G1.5-17
- `state/config/fidelity-contracts/g4-narration-script.yaml` — G4-10, G4-17 updated
- `docs/workflow/trial-run-pass2-artifacts-contract.md` — field renames in runtime_plan
- `skills/bmad-agent-content-creator/references/cluster-density-controls.md` — parent_slide_count ref
- `skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md` — G4-10 field list
- `skills/bmad-agent-marcus/scripts/prepare-irene-pass2-handoff.py` — _load_runtime_plan() new fields
- `skills/bmad-agent-marcus/scripts/tests/test_prepare_irene_pass2_handoff.py` — fixtures + assertions
- `skills/bmad-agent-marcus/scripts/generate-storyboard.py` — avg_slide_seconds fallback + TODO
- `tests/test_experience_profiles.py` — schema_version 1.0→1.1
- `docs/parameter-directory.md` — 4 new Family 1 entries
- `_bmad-output/planning-artifacts/epics-interstitial-clusters.md` — 20c-15 entry
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — 20c-15 → done
