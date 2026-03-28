# Fidelity Assessor — Access Boundaries

## Read Access

- Entire project repository (for artifact verification)
- `state/config/fidelity-contracts/` — L1 deterministic contracts
- `skills/sensory-bridges/` — perception bridge scripts and references
- `course-content/` — production artifacts under evaluation
- `docs/fidelity-gate-map.md` — gate definitions, role matrix, operating policy
- `docs/app-design-principles.md` — Three-Layer Model, Hourglass, design principles
- `docs/source-ref-grammar.md` — provenance resolution rules
- `skills/bmad-agent-content-creator/references/` — template schemas (slide brief, lesson plan)
- `skills/bmad-agent-gamma/references/` — context envelope schema
- `{project-root}/_bmad/memory/fidelity-assessor-sidecar/` — own memory

## Write Access

- `{project-root}/_bmad/memory/fidelity-assessor-sidecar/` — own memory only

## Deny Zones

- `.env` — credentials
- `scripts/api_clients/` — API client source code
- `course-content/` (write) — verification only, never modify production artifacts
- Other agents' memory sidecars (write)
- `resources/style-bible/` (write) — brand reference, read-only
- `.cursor-plugin/` — plugin configuration
- `tests/` (write) — test files
- `state/config/fidelity-contracts/` (write) — contracts are human-authored and version-controlled
- `state/runtime/` (write) — Vera does not write to SQLite; state tracking is Marcus's responsibility
