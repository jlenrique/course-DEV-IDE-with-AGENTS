# Story 16.4: Contract Linting & Drift Protection

**Epic:** 16 — Bounded Autonomy Expansion
**Status:** backlog
**Sprint key:** `16-4-contract-linting-drift-protection`
**Added:** 2026-04-06
**Depends on:** Existing fidelity contracts, structural-walk manifests, and schema files. Can parallel with Stories 16.1-16.3.

## Summary

Create a repeatable contract-validation routine that detects structural drift in YAML contracts, schemas, template references, perception modality references, and gate/lane definitions. The linter runs on-demand, during pre-merge checks, and as part of APP maturity audits.

## Goals

1. Contract structure validation against canonical schema.
2. Schema field consistency checks across related contracts.
3. Template reference resolution validation.
4. Perception modality reference validation against sensory bridges.
5. Gate name and ownership consistency with lane matrix.
6. CLI interface and integration with maturity audit.

## Existing Infrastructure To Build On

- `state/config/structural-walk/standard.yaml` and `motion.yaml` — structural-walk manifests (document integrity checks)
- `scripts/utilities/structural_walk.py` — existing manifest-driven validation engine (pattern to follow)
- `state/config/fidelity-contracts/` or equivalent — fidelity contract YAML files
- `docs/lane-matrix.md` — gate ownership definitions
- `skills/sensory-bridges/SKILL.md` — perception modality definitions
- `skills/app-maturity-audit/` — existing maturity audit skill (integration point)
- Agent SKILL.md `references/` directories — template references in contracts

## Key Files

- `scripts/utilities/contract_lint.py` — new: contract validation engine
- `state/config/contract-lint-rules.yaml` — new: extensible lint rule definitions
- `reports/contract-lint/lint-{date}.md` — new: lint report output

## Acceptance Criteria

1. Contract structure validation: fidelity contract YAML files validate against canonical field schema.
2. Schema consistency: related contracts (e.g., G2 and G3 fidelity contracts) share expected common fields without divergence.
3. Template resolution: all `template:` or `reference:` fields in contracts resolve to existing files in the repo.
4. Perception validation: perception modality references in contracts match capabilities defined in sensory bridges skill.
5. Gate/lane consistency: gate names in contracts match `docs/lane-matrix.md` definitions; ownership claims are consistent.
6. CLI: `python -m scripts.utilities.contract_lint` with `--fix-suggestions` for auto-fixable issues.
7. Output structured: `{file, rule_id, issue_type, severity, description, suggested_fix}`.
8. Zero-finding run produces clean bill of health report.
9. Lint rules extensible: new rules addable via `state/config/contract-lint-rules.yaml` without code changes.
10. Integration: callable from maturity audit skill and hookable into pre-merge checks.
11. Unit tests: each rule type with valid and invalid contract samples.
