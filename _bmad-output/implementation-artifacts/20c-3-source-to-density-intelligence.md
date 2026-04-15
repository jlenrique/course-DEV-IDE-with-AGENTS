# Story 20c-3: Static Density Configs

**Epic:** 20c - Cluster Intelligence Expansion & Iteration
**Status:** done
**Sprint key:** `20c-3-static-density-configs`
**Added:** 2026-04-12
**Depends on:** [20c-2-content-aware-template-selection-logic.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20c-2-content-aware-template-selection-logic.md), [20b-1-irene-pass1-cluster-planning-implementation.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20b-1-irene-pass1-cluster-planning-implementation.md)

## Story

As Marcus and downstream deterministic utilities,
I want two canonical static density configs aligned to the validated `visual-led` and `text-led` experience profiles,
So that profile choice deterministically influences cluster-density behavior without reopening the broader source-analysis engine.

## Context

This story was compressed during the 2026-04-14 Wave 2 replanning. The original broader "source-to-density intelligence" concept is out of scope for this slice.

For this story, `20c-14` is the upstream proof that experience-profile selection and envelope plumbing already work. `20c-3` now narrows to a deterministic bridge: profile-specific static density configs that can be consumed by the existing run-constants/profile flow and later used by cluster-planning/template-selection logic.

## Acceptance Criteria

**AC-1: Two Canonical Static Configs**
- Define exactly two static density configs for the current proof-of-concept profiles: `visual-led` and `text-led`.
- Each config is deterministic and version-controlled, not computed from source analysis at runtime.

**AC-2: Profile Alignment**
- Each density config aligns with the already-validated `slide_mode_proportions` for its matching experience profile.
- The implementation reuses the canonical profile-resolution path rather than introducing a second source of truth.

**AC-3: Run-Constants Integration**
- The selected density config is available through the existing run-constants/profile plumbing used by Marcus and downstream code.
- Unknown or inconsistent profile/density inputs fail clearly rather than silently drifting.

**AC-4: Minimal Scope Boundary**
- Do not implement the broader source-structure scoring engine, per-slide ranking, or budget-allocation logic in this story.
- Do not reopen `20c-13`/`20c-14` profile plumbing except as required to consume the already-proven contract.

**AC-5: Downstream Readiness**
- The static density output is shaped so later cluster-planning/template-selection work can consume it without another contract rewrite.
- Focus on the current two-profile proof path only; no generalized density engine is required.

**AC-6: Validation**
- Add focused tests that prove:
  - `visual-led` and `text-led` resolve to the expected static density config.
  - The integration preserves the already-validated profile behavior.
  - Invalid inputs fail with explicit errors.

## Tasks / Subtasks

- [x] Task 1: Define the static density contract
  - [x] 1.1: Decide the canonical shape for profile-specific density config data
  - [x] 1.2: Encode exactly two configs for `visual-led` and `text-led`
  - [x] 1.3: Document how the config relates to `slide_mode_proportions`

- [x] Task 2: Wire the config through the existing profile path
  - [x] 2.1: Reuse the current profile resolver / run-constants seam
  - [x] 2.2: Expose the resolved static density config to downstream callers
  - [x] 2.3: Fail clearly on unknown or inconsistent inputs

- [x] Task 3: Preserve scope hygiene
  - [x] 3.1: Keep the change bounded to the compressed static-config slice
  - [x] 3.2: Do not implement per-slide density intelligence in this story
  - [x] 3.3: Avoid reopening completed profile-plumbing contracts

- [x] Task 4: Validate the slice
  - [x] 4.1: Add focused unit coverage for both profiles
  - [x] 4.2: Add regression coverage around the profile/run-constants seam
  - [x] 4.3: Run the smallest relevant targeted test suite

### Review Findings

- [x] [Review][Patch] Marcus harness fails open on invalid profile/density bundles [scripts/utilities/marcus_prompt_harness.py:167]
- [x] [Review][Patch] Experience profile resolution depends on process working directory [scripts/utilities/run_constants.py:25]
- [x] [Review][Patch] Static density map duplicates the canonical profile source of truth [scripts/utilities/run_constants.py:30]

## Dev Notes

### Scope Compression Note

The canonical implementation scope for `20c-3` is the compressed Wave 2A version recorded in `next-session-start-here.md`, `sprint-status.yaml`, and `epics-interstitial-clusters.md`: two hardcoded density configs aligned to the current proof profiles.

### Backward Compatibility

Existing `cluster_density` validation may remain for legacy callers, but this story's new behavior should flow from experience-profile resolution for the `visual-led` / `text-led` proof path.

### Implementation Summary

- Added a canonical static resolver mapping in `scripts/utilities/run_constants.py`:
  - `visual-led -> default`
  - `text-led -> rich`
- Extended `resolve_experience_profile()` to return `cluster_density` alongside `slide_mode_proportions` and `narration_profile_controls`.
- Updated `parse_run_constants()` so `experience_profile` auto-populates `cluster_density` when omitted and rejects explicit mismatches when both values are present.
- Added focused contract coverage in:
  - `tests/test_run_constants.py`
  - `tests/test_experience_profiles.py`
  - `tests/test_marcus_prompt_harness.py`

### Validation Evidence

- `.\.venv\Scripts\python.exe -m pytest tests/test_run_constants.py tests/test_experience_profiles.py tests/test_marcus_prompt_harness.py -q`
- Result: `61 passed`
- `ReadLints` on changed files: no linter errors

### Out of Scope

- Source-material analysis
- Per-slide density recommendation engines
- Global density budget allocation heuristics
- Additional experience profiles beyond `visual-led` and `text-led`

## References

- [next-session-start-here.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/next-session-start-here.md) — Current session objective and compressed 20c-3 scope
- [sprint-status.yaml](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/sprint-status.yaml) — Current story status and Wave 2 sequencing
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Compressed 20c-3 definition
- [run_constants.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/scripts/utilities/run_constants.py) — Current profile/run-constants seam
- [experience-profiles.yaml](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/state/config/experience-profiles.yaml) — Canonical profile targets
