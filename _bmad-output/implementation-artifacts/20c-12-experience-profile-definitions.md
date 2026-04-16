# Story 20c-12: Experience Profile Definitions

**Epic:** 20c - Cluster Intelligence + Creative Control
**Status:** done
**Sprint key:** `20c-12-experience-profile-definitions`
**Added:** 2026-04-14
**Validated:** 2026-04-15
**Depends on:** [20c-8-assembly-timing-parameters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20c-8-assembly-timing-parameters.md), [20c-9-narration-parameter-expansion.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20c-9-narration-parameter-expansion.md), [20c-10-creative-director-agent.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20c-10-creative-director-agent.md)

## Story

As the Wave 2B profile registry,
I want canonical `visual-led` and `text-led` targets defined in `experience-profiles.yaml`,
So that creative-directive validation and later resolver/runtime work share one profile source of truth.

## Acceptance Criteria

1. `state/config/experience-profiles.yaml` defines exactly two bootstrap profiles: `visual-led` and `text-led`.
2. Each profile defines normalized `slide_mode_proportions`.
3. Each profile defines a complete `narration_profile_controls` map aligned to the creative-directive contract.
4. Validator and tests enforce parity between profile definitions and creative-directive payloads.

## Review Findings

- [x] [Review][Patch] Bootstrap experience profiles only carried a partial narration-control map, so profile parity checks could not enforce the full expanded Wave 2B narration contract.

## Implementation Summary

- The profile registry still defines the same two proof-of-concept profiles.
- Formal review made the profile targets explicit for the full narration control surface while preserving the existing differentiated controls and defaulting the remaining knobs conservatively.
- Creative-directive validation and resolver tests now read the richer profile targets as the canonical parity source.

## Validation Evidence

- `.\.venv\Scripts\python.exe -m pytest tests/test_experience_profiles.py tests/test_creative_directive_validator.py tests/test_creative_directive_schema.py tests/test_sprint_status_yaml.py -q`

## File List

- `state/config/experience-profiles.yaml`
- `state/config/schemas/creative-directive.schema.json`
- `state/config/schemas/creative-directive.schema.yaml`
- `scripts/utilities/creative_directive_validator.py`
- `tests/test_experience_profiles.py`
- `tests/test_creative_directive_validator.py`
- `tests/test_creative_directive_schema.py`

## Adversarial Review (BMAD)

### Blind Hunter
- **Shared finding (Creative Director contract path):** Same as 20c-11 — `schema_version` const was not enforced in `creative_directive_validator.py` until re-review.
- **Remediation:** Validator now requires `schema_version == "1.0"` (string); see `tests/test_creative_directive_validator.py` additions. Profile YAML definitions unchanged; parity tests still authoritative for AC1–4.

### Edge Case Hunter
- Wrong `schema_version` on a directive claiming profile parity now fails before parity compare.

### Acceptance Auditor
- AC1–4 satisfied; AC4 (validator parity) aligned with stricter directive gate.

Review closed: 2026-04-15 (BMAD re-review; validator remediation shared with 20c-11).

## BMAD tracking closure

**Framework:** Per `sprint-status.yaml` — **`done`** = ACs met + verification green + layered BMAD review complete + sprint key `done`.

| Check | State |
|-------|--------|
| ACs | Met (`experience-profiles.yaml` + profile/CD parity) |
| Verification | **Validation Evidence**; hardened `validate_creative_directive` |
| **`sprint-status.yaml`** | **`20c-12-experience-profile-definitions`: `done`** (reconciled 2026-04-15) |
