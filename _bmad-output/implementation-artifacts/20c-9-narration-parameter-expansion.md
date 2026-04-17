# Story 20c-9: Narration Parameter Expansion

**Epic:** 20c - Cluster Intelligence + Creative Control
**Status:** done
**Sprint key:** `20c-9-narration-parameter-expansion`
**Added:** 2026-04-14
**Validated:** 2026-04-15
**Depends on:** [20c-7-parameter-audit-registry-schema.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20c-7-parameter-audit-registry-schema.md)

## Story

As Irene and the narration-control contract layer,
I want the expanded `narration_profile_controls` set validated consistently across config, registry, and Creative Director contract seams,
So that Wave 2B creative-control tuning is explicit, enum-safe, and forwardable through Marcus-owned envelopes.

## Acceptance Criteria

1. `state/config/narration-script-parameters.yaml` defines the expanded `narration_profile_controls` set with enum-safe defaults.
2. `state/config/parameter-registry-schema.yaml` includes every expanded narration profile control key.
3. Creative-directive schema and validator enforce the same narration control shape instead of collapsing back to a smaller subset.
4. Tests prove the expanded controls are structurally valid and contract-aligned.

## Review Findings

- [x] [Review][Patch] Creative-directive contract only enforced 3 of the 11 expanded narration profile controls, so the Wave 2B CD seam could not actually validate the full 20c-9 control surface.

## Implementation Summary

- `state/config/narration-script-parameters.yaml` remains the narration-time source of truth for the 11 control keys.
- `state/config/parameter-registry-schema.yaml` already registered the full expanded control set.
- Formal review patched the Creative Director contract seam so the JSON schema, YAML companion schema, validator, tests, and bootstrap profile targets now agree on the same 11-key `narration_profile_controls` shape.

## Validation Evidence

- `.\.venv\Scripts\python.exe -m pytest tests/test_creative_directive_validator.py tests/test_creative_directive_schema.py tests/test_experience_profiles.py tests/test_parameter_registry_schema.py skills/bmad-agent-marcus/scripts/tests/test-narration-config-schemas.py tests/test_sprint_status_yaml.py -q`

## File List

- `state/config/narration-script-parameters.yaml`
- `state/config/parameter-registry-schema.yaml`
- `state/config/schemas/creative-directive.schema.json`
- `state/config/schemas/creative-directive.schema.yaml`
- `state/config/experience-profiles.yaml`
- `scripts/utilities/creative_directive_validator.py`
- `tests/test_creative_directive_validator.py`
- `tests/test_creative_directive_schema.py`
- `tests/test_experience_profiles.py`
- `skills/bmad-agent-marcus/scripts/tests/test-narration-config-schemas.py`

## Adversarial Review (BMAD)

### Blind Hunter
- **Shared finding:** Expanded narration keys were enforced, but `schema_version` **const** on the creative-directive contract was not enforced at runtime (same gap as 20c-11).
- **Remediation:** `validate_creative_directive` now requires `schema_version` to be exactly `"1.0"`; regression tests added in `tests/test_creative_directive_validator.py`.

### Edge Case Hunter
- Directive payloads with invalid `schema_version` types/values rejected regardless of narration key completeness.

### Acceptance Auditor
- AC1–4 satisfied; AC3–4 contract alignment improved via `schema_version` gate consistent with JSON Schema.

Review closed: 2026-04-15 (BMAD re-review; validator remediation).

## BMAD tracking closure

**Framework:** Per `sprint-status.yaml` — **`done`** = ACs met + agreed verification green + layered BMAD review complete + sprint key `done`.

| Check | State |
|-------|--------|
| ACs | Met (expanded `narration_profile_controls` contract aligned) |
| Verification | Commands in **Validation Evidence**; `validate_creative_directive` includes `schema_version` const remediation |
| **`sprint-status.yaml`** | **`20c-9-narration-parameter-expansion`: `done`** (reconciled 2026-04-15) |

