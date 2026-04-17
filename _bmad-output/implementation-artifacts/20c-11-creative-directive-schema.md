# Story 20c-11: Creative Directive Schema

**Epic:** 20c - Cluster Intelligence + Creative Control
**Status:** done
**Sprint key:** `20c-11-creative-directive-schema`
**Added:** 2026-04-14
**Validated:** 2026-04-15
**Depends on:** [20c-10-creative-director-agent.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20c-10-creative-director-agent.md)

## Story

As the Creative Director contract layer,
I want machine-readable and human-readable creative-directive schemas backed by runtime validation,
So that non-conforming directives are rejected before they can drift into Marcus-owned runtime plumbing.

## Acceptance Criteria

1. JSON and YAML creative-directive schema artifacts exist and remain aligned.
2. Required top-level fields include `schema_version`, `experience_profile`, `slide_mode_proportions`, `narration_profile_controls`, and `creative_rationale`.
3. Schema validation enforces the canonical slide-mode key set and the full narration-profile control contract used by Wave 2B.
4. Runtime validation rejects malformed directives and profile-parity drift.

## Review Findings

- [x] [Review][Patch] Creative-directive schema only modeled a 3-key narration control subset, so malformed directives could still satisfy the schema while dropping most of the expanded Wave 2B narration controls.

## Implementation Summary

- The creative-directive JSON and YAML schemas remain the canonical contract pair for CD outputs.
- Formal review expanded both schemas to the full 11-key narration control shape and aligned the validator/tests with that stricter contract.
- Runtime validation continues to reject top-level drift, enum violations, and profile-target mismatches.

## Validation Evidence

- `.\.venv\Scripts\python.exe -m pytest tests/test_creative_directive_validator.py tests/test_creative_directive_schema.py tests/test_sprint_status_yaml.py -q`

## File List

- `state/config/schemas/creative-directive.schema.json`
- `state/config/schemas/creative-directive.schema.yaml`
- `skills/bmad-agent-cd/references/creative-directive-contract.md`
- `scripts/utilities/creative_directive_validator.py`
- `tests/test_creative_directive_validator.py`
- `tests/test_creative_directive_schema.py`

## Adversarial Review (BMAD)

### Blind Hunter
- **Finding:** Runtime validator enforced required keys but not JSON Schema `schema_version` **const** (`"1.0"`). Payloads with `"schema_version": "2.0"` or numeric `1` could pass when profile fields matched targets—violating AC3 (full schema contract).
- **Remediation:** `scripts/utilities/creative_directive_validator.py` now rejects any `schema_version` other than the string `"1.0"`. Added `tests/test_creative_directive_validator.py::test_validate_creative_directive_fails_wrong_schema_version_string` and `::test_validate_creative_directive_fails_non_string_schema_version`.

### Edge Case Hunter
- Non-string and wrong-version `schema_version` values are explicit validation failures (no silent acceptance).

### Acceptance Auditor
- AC1–4 satisfied; AC3 strengthened: contract parity with `creative-directive.schema.json` includes `schema_version` const.

Review closed: 2026-04-15 (BMAD re-review; remediation merged).

## BMAD tracking closure

**Framework:** Per `sprint-status.yaml` — **`done`** = ACs met + verification green + layered BMAD review complete + sprint key `done`.

| Check | State |
|-------|--------|
| ACs | Met (schemas + runtime validation; `schema_version` const enforced in code) |
| Verification | **Validation Evidence** + `tests/test_creative_directive_validator.py` (incl. schema_version tests) |
| **`sprint-status.yaml`** | **`20c-11-creative-directive-schema`: `done`** (reconciled 2026-04-15) |

