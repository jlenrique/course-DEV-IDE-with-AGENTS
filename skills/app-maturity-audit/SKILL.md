---
name: app-maturity-audit
description: Repeatable APP pipeline maturity audit against the Three-Layer Model, Hourglass Model, and Sensory Horizon principle. Use when the user says "audit APP maturity", "run maturity audit", or "check pipeline maturity".
---

# APP Maturity Audit

## Overview

This skill audits the Agentic Production Platform pipeline against the architectural principles defined in `docs/app-design-principles.md`. It produces a structured maturity report covering four pillars (L1 Contracts, L2 Evaluation, L3 Memory, Perception) across all production gates (G0–G6), a Leaky Neck report, a Sensory Horizon coverage assessment, cumulative drift summary, and a maturity delta against the previous audit.

Invocable by Marcus, by the user directly, or as part of a session startup protocol.

## On Activation

1. Load `docs/app-design-principles.md` for the Three-Layer Model, Hourglass, Leaky Neck, and Sensory Horizon definitions
2. Load `docs/fidelity-gate-map.md` for gate definitions and role matrix
3. Load all L1 contracts from `state/config/fidelity-contracts/g*.yaml`
4. Scan `skills/bmad-agent-fidelity-assessor/` for Vera's current gate coverage
5. Scan `skills/sensory-bridges/` for bridge modality coverage
6. Scan `_bmad/memory/` for active agent memory sidecars
7. Load the most recent previous audit from `_bmad-output/implementation-artifacts/fidelity-audit-*.md` for delta comparison
8. Follow the audit protocol in `./references/audit-protocol.md`

## Capabilities

| Capability | Description | Reference |
|------------|-------------|-----------|
| **Full Audit** | Complete four-pillar assessment across all gates with heat map, reports, and delta | `./references/audit-protocol.md` |
| **Quick Check** | Abbreviated check of a single gate or pillar — useful for post-change validation | `./references/audit-protocol.md` |

## Output

Audit results are written to `_bmad-output/implementation-artifacts/fidelity-audit-{date}.md` with the timestamp for historical comparison. The report follows the template in `./references/report-template.md`.
