# First-Run Setup for Vera (Fidelity Assessor)

Welcome! Setting up the Fidelity Assessor workspace.

## Memory Location

Creating `{project-root}/_bmad/memory/fidelity-assessor-sidecar/` for persistent memory.

## Initial Structure

Creating:
- `index.md` — active assessment context, calibration summary, recurring fidelity patterns
- `patterns.md` — gate-specific patterns, fidelity class patterns, human calibration, medical sensitivity
- `chronology.md` — assessment history, circuit breaker events, human waivers, calibration events
- `access-boundaries.md` — read/write/deny zones for Vera

## Environment Check

Verify these paths exist and are accessible:
- `state/config/fidelity-contracts/` — L1 deterministic contracts (YAML per gate)
- `state/config/fidelity-contracts/_schema.yaml` — contract schema definition
- `docs/fidelity-gate-map.md` — gate definitions, role matrix, operating policy
- `docs/app-design-principles.md` — Three-Layer Model, Hourglass, Leaky Neck
- `docs/source-ref-grammar.md` — provenance resolution rules
- `skills/sensory-bridges/` — multimodal perception infrastructure

If any reference is missing, Vera operates in partial assessment mode — available criteria are evaluated, unavailable criteria are flagged as SKIPPED with the missing dependency noted.

## Ready

Setup complete! Vera is ready to verify fidelity at G0, G1, G2, and G3 gates.
