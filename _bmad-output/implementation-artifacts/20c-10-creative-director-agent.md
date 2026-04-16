# Story 20c-10: Creative Director Agent

**Epic:** 20c - Cluster Intelligence + Creative Control
**Status:** done
**Sprint key:** `20c-10-creative-director-agent`
**Added:** 2026-04-14
**Validated:** 2026-04-15
**Depends on:** [20c-7-parameter-audit-registry-schema.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20c-7-parameter-audit-registry-schema.md), [20c-9-narration-parameter-expansion.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20c-9-narration-parameter-expansion.md)

## Story

As Marcus-led creative orchestration,
I want a contract-first Creative Director scaffold with an enforceable output contract and validator path,
So that downstream creative-control work uses a deterministic, reviewable directive seam rather than ad-hoc profile payloads.

## Acceptance Criteria

1. `skills/bmad-agent-cd/SKILL.md` declares the CD purpose, output contract, and guardrails.
2. CD output is validated through `scripts/utilities/creative_directive_validator.py`.
3. The validator is safe to call from normal repo tooling paths rather than depending on the caller's current working directory.
4. CD contract references remain consistent with the creative-directive schema artifacts.

## Review Findings

- [x] [Review][Patch] `creative_directive_validator.py` resolved schema/profile files relative to the process working directory, making the CD validation path brittle outside repo-root execution.

## Implementation Summary

- The CD scaffold remains contract-first and Marcus-mediated.
- Formal review hardened the validator to anchor its schema/profile lookups to the repository root, matching the already-reviewed `run_constants.py` pattern.
- The CD contract references and tests now exercise the hardened validator path.

## Validation Evidence

- `.\.venv\Scripts\python.exe -m pytest tests/test_creative_directive_validator.py tests/test_creative_directive_schema.py tests/test_sprint_status_yaml.py -q`

## File List

- `skills/bmad-agent-cd/SKILL.md`
- `skills/bmad-agent-cd/references/creative-directive-contract.md`
- `scripts/utilities/creative_directive_validator.py`
- `tests/test_creative_directive_validator.py`
- `tests/test_creative_directive_schema.py`

## Adversarial Review (BMAD)

### Blind Hunter
- **Shared finding:** CD output is checked via `validate_creative_directive` (AC2). Prior validator gap: `schema_version` const not enforced (see 20c-11).
- **Remediation:** `creative_directive_validator.py` + tests updated so validated directives cannot claim wrong `schema_version` while passing.

### Edge Case Hunter
- Non-string / wrong-version `schema_version` on synthetic CD payloads now fail validation explicitly.

### Acceptance Auditor
- AC1–4 satisfied; AC2–3 strengthened by const enforcement on the repo-anchored validator path.

Review closed: 2026-04-15 (BMAD re-review; validator remediation).

## BMAD tracking closure

**Framework:** Per `sprint-status.yaml` — **`done`** = ACs met + verification green + layered BMAD review complete + sprint key `done`.

| Check | State |
|-------|--------|
| ACs | Met (CD scaffold + repo-anchored validator path) |
| Verification | **Validation Evidence**; shared `schema_version` const gate with 20c-11 |
| **`sprint-status.yaml`** | **`20c-10-creative-director-agent`: `done`** (reconciled 2026-04-15) |

