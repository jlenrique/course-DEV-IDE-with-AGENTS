# Story 16.2: Shared Governance Enforcement Utilities

**Epic:** 16 — Bounded Autonomy Expansion
**Status:** backlog
**Sprint key:** `16-2-shared-governance-enforcement-utilities`
**Added:** 2026-04-06
**Depends on:** Existing governance contracts and lane matrix from Epic 4A. Can be implemented in parallel with Story 16.1.

## Summary

Build a shared Python module that validates governance constraints (`allowed_outputs`, `decision_scope`, `authority_chain`, required envelope fields) across all specialists, replacing duplicated governance prose enforcement with consistent, machine-checkable code. This does not replace specialist judgment — only enforces invariant boundaries.

## Goals

1. Shared `governance_validator.py` module with per-constraint validation functions.
2. Adoption across Marcus dispatch helpers, Gary, Irene, Vera, Quinn-R.
3. Consistent `scope_violation` output format.
4. Reduction of duplicated governance prose in agent SKILL.md files.
5. Machine-checkable scope violation detection.

## Existing Infrastructure To Build On

- `docs/lane-matrix.md` — authoritative cross-agent judgment ownership map (Story 4A-2)
- Agent SKILL.md governance blocks — `governance.allowed_outputs`, `governance.decision_scope.owned_dimensions`, `authority_chain`, `route_to` (defined per specialist in Stories 4A-1 through 4A-3)
- `skills/bmad-agent-marcus/references/envelope-governance-*.md` — envelope governance contracts
- `skills/bmad-agent-fidelity-assessor/references/envelope-governance-vera.md` — Vera envelope governance
- `scripts/utilities/ad_hoc_persistence_guard.py` — existing guard pattern (validates run_mode scope)
- `scripts/utilities/run_constants.py` — run-level configuration loading
- Baton authority contract from Story 4A-1 — specialist redirect vs standalone-consult

## Key Files

- `scripts/utilities/governance_validator.py` — new: shared governance validation module
- `docs/lane-matrix.md` — read: authoritative ownership source
- Agent SKILL.md files — update: reference shared validators instead of duplicating prose enforcement

## Acceptance Criteria

1. `governance_validator.py` provides:
   - `validate_allowed_outputs(agent_name, proposed_outputs)` — checks against agent's `governance.allowed_outputs`
   - `validate_decision_scope(agent_name, claimed_dimensions)` — checks owned vs. not-owned dimensions
   - `validate_authority_chain(envelope)` — confirms baton holder, route_to, delegation fields
   - `validate_required_envelope_fields(agent_name, envelope)` — per-specialist required field check
2. Governance definitions loaded from a YAML config derived from agent SKILL.md governance blocks (not hardcoded).
3. Scope violations produce consistent, machine-readable output: `{agent, violation_type, expected, actual, severity}`.
4. Shared module callable from Marcus dispatch helpers, Gary, Irene, Vera, Quinn-R execution contexts.
5. Agent SKILL.md governance prose can reference shared validators instead of re-implementing enforcement.
6. Does NOT replace specialist judgment — only enforces invariant governance boundaries.
7. Unit tests cover each validation function with pass/fail cases per specialist (Marcus, Gary, Irene, Vera, Quinn-R).
8. Integration test: simulated envelope with scope violation produces correct violation output.
