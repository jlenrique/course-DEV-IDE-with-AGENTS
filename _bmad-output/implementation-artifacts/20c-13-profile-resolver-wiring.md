# Story 20c-13: Profile Resolver Wiring

**Epic:** 20c — Cluster Intelligence + Creative Control
**Status:** done
**Branch:** `DEV/slides-redesign`
**Dependencies:** 20c-12 (experience profiles defined), 20c-3 (static density configs, soft)

## Purpose

Wire a profile resolver so that selecting an experience profile name (e.g., `"visual-led"`) deterministically resolves to canonical `slide_mode_proportions` and `narration_profile_controls` values. Marcus calls the resolver during run setup. Resolved `slide_mode_proportions` merge into `RunConstants`. Resolved `narration_profile_controls` are returned separately for Marcus to pack into the delegation envelope for Irene.

## Architectural Invariant: Marcus as Single Point of Contact

The APP's #1 principle is that the HIL operator interacts exclusively through Marcus. This story deliberately opens a SPOC gap: the resolver exists but no prompt pack triggers it yet. **This gap is tracked and closed by 20c-14.** See the SPOC gap ledger in `_bmad-output/planning-artifacts/epics-interstitial-clusters.md`.

## Key Files

### Files to MODIFY

| File | What to change |
|------|---------------|
| `scripts/utilities/run_constants.py` | Add `resolve_experience_profile()` function; add `experience_profile: str | None = None` field to `RunConstants` dataclass; add profile validation to `parse_run_constants()` |
| `tests/test_run_constants.py` | Add resolver tests, backwards-compat tests, contract tests |
| `tests/test_experience_profiles.py` | Add contract test: all profile names accepted by `parse_run_constants()` |

### Files to READ (source of truth, do NOT modify)

| File | Why |
|------|-----|
| `state/config/experience-profiles.yaml` | The sole source of truth for profile definitions. Resolver reads this at runtime. |
| `state/config/parameter-registry-schema.yaml` | Ownership model — `slide_mode_proportions` belongs to run-constants family (Marcus), `narration_profile_controls` belongs to narration-time family (Irene + narration contracts) |
| `scripts/utilities/creative_directive_validator.py` | Already enforces profile parity (lines 122-138). Resolver must agree with this validator on the source of truth. Both read `experience-profiles.yaml`. |
| `docs/parameter-directory.md` | Master parameter reference. Understand family boundaries before coding. |
| `skills/bmad-agent-cd/SKILL.md` | CD agent scaffold. CD output feeds the resolver. Resolver does NOT call CD. |

### Files for context (skim for understanding)

| File | Why |
|------|-----|
| `_bmad-output/planning-artifacts/epics-interstitial-clusters.md` | Full story definition with all 7 constraints and 8 ACs (search for "Story 20c-13") |
| `state/config/narration-script-parameters.yaml` | Narration-time parameters that the `narration_profile_controls` map to. Irene consumes these through Marcus's envelope. |
| `state/config/schemas/creative-directive.schema.yaml` | Schema that the creative directive validator checks against |

## Implementation Constraints (Party Mode Consensus 2026-04-14)

These are non-negotiable architectural decisions from the review team:

1. **Resolver is a pure function in `run_constants.py`** — not a CLI, not a service, not a separate module. It lives alongside `parse_run_constants()` because it feeds INTO that validation path.

2. **Resolver output merges into the raw dict BEFORE `parse_run_constants()` is called** — the `RunConstants` dataclass is frozen; you cannot mutate after construction. The caller merges `slide_mode_proportions` into the raw dict, then calls `parse_run_constants()`.

3. **`experience_profile` is `Optional[str] = None` on `RunConstants`** — existing bundles that lack the field must continue to parse without error. Backwards compatibility is non-negotiable.

4. **`narration_profile_controls` do NOT land on `RunConstants`** — they belong to the narration-time parameter family (different owner). The resolver returns them alongside `slide_mode_proportions` but Marcus unpacks them into the delegation envelope for Irene. `RunConstants` is for run-identity and execution-mode parameters only.

5. **Unknown profile rejection raises `RunConstantsError` at resolve time** — the error must say "unknown experience profile" not "invalid slide_mode_proportions." Error locality matters for operator-facing diagnostics through Marcus.

6. **Resolver reads `experience-profiles.yaml` as sole source of truth** — no hardcoded profile values. The YAML is the single definition; everything derives from it at runtime.

7. **Irene must never import or reference `experience-profiles.yaml` directly** — controls arrive only via envelope. A static analysis test must enforce this.

## Function Signature

```python
EXPERIENCE_PROFILES_PATH = Path("state/config/experience-profiles.yaml")

def resolve_experience_profile(
    profile_name: str,
    *,
    profiles_path: Path = EXPERIENCE_PROFILES_PATH,
) -> dict[str, Any]:
    """Resolve a named experience profile to its canonical parameter values.

    Returns a dict with two keys:
        - "slide_mode_proportions": dict mapping mode keys to float proportions
        - "narration_profile_controls": dict of narration control settings

    The caller is responsible for:
        - Merging "slide_mode_proportions" into the raw run-constants dict
        - Packing "narration_profile_controls" into the delegation envelope

    Raises RunConstantsError if profile_name is not found or YAML is malformed.
    """
```

## Data Flow Diagram

```
experience-profiles.yaml  (sole source of truth)
         |
         v
resolve_experience_profile("visual-led")
         |
         ├─> slide_mode_proportions ──> merge into raw dict ──> parse_run_constants() ──> RunConstants.slide_mode_proportions
         |                                                                                RunConstants.experience_profile = "visual-led"
         └─> narration_profile_controls ──> Marcus packs into delegation envelope ──> Irene Pass 2
```

## Acceptance Criteria

1. `resolve_experience_profile(name)` returns `slide_mode_proportions` + `narration_profile_controls` for known profiles
2. Unknown profile name raises `RunConstantsError`
3. Resolved `slide_mode_proportions` round-trips through `parse_run_constants()` without mutation
4. `experience_profile` field on `RunConstants`: absent defaults to `None` (backwards compat), present validates against known profiles
5. Contract test: every profile name in `experience-profiles.yaml` is accepted by `parse_run_constants()`
6. Static analysis test: no file in `skills/bmad-agent-content-creator/` or downstream agent directories contains direct references to `experience-profiles`
7. Integration test: profile name -> resolver -> merge into raw dict -> `parse_run_constants()` -> success
8. All existing tests remain green (229+ baseline)

## Test Cases (10 minimum)

1. Visual-led resolves to expected proportions and controls (exact match against YAML)
2. Text-led resolves correctly (different values, same shape)
3. Unknown profile name raises `RunConstantsError`
4. Resolved `slide_mode_proportions` round-trips through `parse_run_constants()` without mutation
5. `experience_profile=None` on `RunConstants` — backwards compat with `_MINIMAL_RAW` dict
6. `experience_profile` set to valid string populates the field on dataclass
7. `experience_profile` set to unknown string raises `RunConstantsError` during parse
8. Resolver output keys match `SLIDE_MODE_KEYS` exactly (no drift between resolver and validator)
9. Resolver with custom `profiles_path` pointing to malformed YAML raises `RunConstantsError`
10. Resolver narration controls include the three required keys (`narrator_source_authority`, `slide_content_density`, `elaboration_budget`)

### Contract and static analysis tests

11. Every profile name in `experience-profiles.yaml` is accepted by `parse_run_constants()`
12. No downstream agent directory contains an import or read of `experience-profiles` (grep-based static analysis)
13. Integration: profile name -> resolve -> merge into raw dict -> `parse_run_constants()` -> assert success and field values match

## Current Experience Profiles (from `state/config/experience-profiles.yaml`)

```yaml
profiles:
  visual-led:
    slide_mode_proportions:
      literal-text: 0.15
      literal-visual: 0.25
      creative: 0.60
    narration_profile_controls:
      narrator_source_authority: source-grounded
      slide_content_density: adaptive
      elaboration_budget: medium

  text-led:
    slide_mode_proportions:
      literal-text: 0.60
      literal-visual: 0.25
      creative: 0.15
    narration_profile_controls:
      narrator_source_authority: slide-led
      slide_content_density: dense
      elaboration_budget: low
```

## Existing Code Patterns to Follow

- `_parse_slide_mode_proportions()` in `run_constants.py` — the validation function the resolver's output must pass through
- `ALLOWED_CLUSTER_DENSITIES` / `cluster_density` field pattern — follow this same pattern for `experience_profile` (optional enum field, `None` when absent)
- `_MINIMAL_RAW` dict in `test_run_constants.py` — the backwards-compat baseline that must continue to work
- `creative_directive_validator.py` lines 122-138 — the profile parity enforcement that must agree with the resolver on source of truth

## What NOT to Do

- Do NOT add `narration_profile_controls` to the `RunConstants` dataclass (wrong parameter family)
- Do NOT create a separate module — the resolver lives in `run_constants.py`
- Do NOT create a CLI entry point for the resolver
- Do NOT hardcode profile values — always read from YAML
- Do NOT modify `experience-profiles.yaml`, `creative_directive_validator.py`, or `narration-script-parameters.yaml`
- Do NOT update prompt packs or Marcus references — that's 20c-14
- Do NOT add the `experience_profile` field to `docs/parameter-directory.md` — that update is part of story closeout, not resolver implementation

## Validation Command

```bash
.venv\Scripts\python.exe -m pytest tests/test_run_constants.py tests/test_experience_profiles.py tests/test_sprint_status_yaml.py -q
```

All tests (existing + new) must pass before marking the story done.

## Tasks / Subtasks

- [x] Task 1: Add runtime resolver support in `run_constants.py`
  - [x] 1.1: Add `EXPERIENCE_PROFILES_PATH` and a shared YAML loader
  - [x] 1.2: Implement `resolve_experience_profile()` as a pure function
  - [x] 1.3: Return canonical `slide_mode_proportions` and `narration_profile_controls`

- [x] Task 2: Extend `RunConstants` parsing for profile-aware validation
  - [x] 2.1: Add optional `experience_profile` field to the frozen dataclass
  - [x] 2.2: Preserve backwards compatibility when the field is absent
  - [x] 2.3: Reject unknown profiles with `RunConstantsError`

- [x] Task 3: Add resolver and contract coverage
  - [x] 3.1: Add exact-match resolver tests for `visual-led` and `text-led`
  - [x] 3.2: Add malformed-YAML and unknown-profile negative tests
  - [x] 3.3: Add integration test for resolve -> merge -> `parse_run_constants()`

- [x] Task 4: Add profile contract and static-analysis guardrails
  - [x] 4.1: Verify every configured profile name is accepted by `parse_run_constants()`
  - [x] 4.2: Verify downstream skills do not reference `experience-profiles.yaml` directly
  - [x] 4.3: Run the story validation command successfully

## Dev Agent Record

### Implementation Plan

- Load profile targets from `state/config/experience-profiles.yaml` through a shared helper in `scripts/utilities/run_constants.py`.
- Validate profile-selected `slide_mode_proportions` through the existing `_parse_slide_mode_proportions()` path to avoid drift.
- Keep `narration_profile_controls` out of `RunConstants`; return them only from the resolver.
- Extend tests to cover resolver success, resolver failure, parse-time profile validation, contract acceptance, and static downstream isolation.

### Debug Log

- 2026-04-14: Added failing tests first for missing resolver/API surface and parse-time profile validation.
- 2026-04-14: Implemented `resolve_experience_profile()` plus shared YAML loading and parse-time `experience_profile` validation.
- 2026-04-14: Verified targeted test pack passes, including the sprint-status regression required for closeout.

### Completion Notes

- Added pure profile resolver support in `scripts/utilities/run_constants.py` with runtime loading from `state/config/experience-profiles.yaml`.
- Added optional `experience_profile` on `RunConstants` with backwards-compatible default `None` and unknown-profile rejection.
- Added resolver, contract, integration, malformed-input, and downstream static-analysis tests across `tests/test_run_constants.py` and `tests/test_experience_profiles.py`.

## File List

- `scripts/utilities/run_constants.py`
- `tests/test_run_constants.py`
- `tests/test_experience_profiles.py`
- `_bmad-output/implementation-artifacts/20c-13-profile-resolver-wiring.md`

## Change Log

- 2026-04-14: Implemented profile resolver wiring, parse-time experience-profile validation, and deterministic test coverage.

## SPOC Gap Note

This story opens a SPOC gap: the resolver exists but no prompt pack triggers it. Marcus can pass `experience_profile` in run-constants but isn't conversationally prompted to do so. This gap is deliberate and bounded — **closed by 20c-14** (prompt pack update + Marcus reference update + CD intake contract + E2E validation).

## Adversarial Review (BMAD)

### Blind Hunter
- Reviewed `resolve_experience_profile()` and `parse_run_constants()` paths: unknown profiles raise `RunConstantsError`; experience profile strings normalized with `.strip().lower()` consistently before lookup (matches YAML keys).
- No additional code defect found in this session. Downstream `creative_directive_validator` hardened separately (20c-11) for `schema_version` const—resolver and validator both read the same `experience-profiles.yaml` for values.

### Edge Case Hunter
- Malformed profiles YAML surfaces via `_load_experience_profiles` / resolver errors; empty profile name rejected.

### Acceptance Auditor
- AC1–8 verified against `tests/test_run_constants.py` and `tests/test_experience_profiles.py` (including static-analysis guard for direct `experience-profiles` references outside allowlisted skills).

Review closed: 2026-04-15 (BMAD re-review; no resolver code change required).

## BMAD tracking closure

**Framework:** Per `sprint-status.yaml` — **`done`** = ACs met + verification green + layered BMAD review complete + sprint key `done`.

| Check | State |
|-------|--------|
| ACs | Met (`resolve_experience_profile` + `parse_run_constants` + static guard) |
| Verification | `tests/test_run_constants.py`, `tests/test_experience_profiles.py` per story |
| **`sprint-status.yaml`** | **`20c-13-profile-resolver-wiring`: `done`** (reconciled 2026-04-15) |
