# Epic 26: BMB Sanctum Migration

**Status:** in-progress
**Created:** 2026-04-17
**Driver:** Bring all custom agents from the old Anthropic/Claude pattern (dense SKILL.md + stub `*-sidecar/`) onto the BMAD Module Builder (bmb) sanctum pattern released March 2026.

## Why This Is Its Own Epic

Party-mode consensus (2026-04-17, Winston / Amelia / Murat / John / Paige) concluded this work is a distinct Job-to-be-Done from Epic 25 (Texas Runner). Same verb ("agent migration"), different success metric: **BMB conformance coverage % across the agent fleet**, not runtime reliability of a single agent. Stapling 15+ stories onto a closed epic muddies the burndown.

Previously scoped into Epic 15 (Learning & Compound Intelligence) as a side effect; pulled forward now because the old pattern is blocking clean Party / LangGraph orchestration substrate.

## Scope

**In scope:**
- Migrate 15 remaining old-pattern agents (Marcus, Irene, Dan, Gary, Kira, Vera, Quinn-R, Aria, Audra, Cora, Enrique, Kim, Mike, Mira, Tamara, Vyx — final count after audit).
- Bring **Desmond** from halfway-conformant to canonical by replacing its hardcoded `init_desmond_sanctum.py` with the shared scaffold (tracked as a grace story, not a pilot).
- Texas remains canonical reference; explicit drift reconciliation handled in a follow-up story (not blocking Epic 26).

**Out of scope:**
- Runtime wiring of the migrated agents into LangGraph graphs (that's Epic 15 / Epic 16 work).
- Rewriting agent behavior or logic — migration is **structural**, not semantic.
- Renaming or moving `skills/<agent>/scripts/` or `skills/<agent>/references/` — those are cemented by 100+ external references per agent.

## Story Tiering (Party-Mode Consensus)

| Tier | Agents | Rationale |
|------|--------|-----------|
| **Pilot (26-1)** | Marcus | Orchestrator lynchpin; validates the pattern on the hardest case. User mandate. |
| **Tier 1 (high risk)** | Irene (26-2) | Highest iteration churn in the fleet (memory-flagged); if pattern survives Irene, it survives anything. |
| **Tier 2 (medium)** | Dan (26-3), Gary, Kira, Vera, Quinn-R | Specialist agents with documented integration contracts. |
| **Tier 3 (batch candidates)** | Remaining 9-10 sidecar-only agents | Mostly self-contained; eligible for small-batch stories once the pattern is proven. |

## Shared Artifacts

All located at [_bmad-output/implementation-artifacts/epic-26/_shared/](./epic-26/_shared/):

- [acceptance-criteria.md](./epic-26/_shared/acceptance-criteria.md) — the AC spine every per-agent story references.
- [runbook.md](./epic-26/_shared/runbook.md) — step-by-step migration procedure.
- [migration-worksheet-TEMPLATE.md](./epic-26/_shared/migration-worksheet-TEMPLATE.md) — per-agent worksheet; each migration produces a filled copy.
- [downstream-reference-map-marcus.md](./epic-26/_shared/downstream-reference-map-marcus.md) — Marcus-specific grep inventory (pre-work for 26-1).

## Stories

| Story | Agent | Status |
|-------|-------|--------|
| 26-1 | Marcus | in-progress |
| 26-2 | Irene | planned |
| 26-3 | Dan | planned |
| 26-4..N | Remaining agents | planned (batched by tier) |

## Acceptance Criteria for Epic Closure

- All 15 Tier 1-3 agents migrated to BMB-conformant form (AC from shared spine met per agent).
- Texas drift reconciled (separate story filed).
- Desmond brought to canonical via generic scaffold.
- No regressions in `tests/` or the contract validator (`.venv/Scripts/python scripts/validate_fidelity_contracts.py` clean).
- Structural walks remain 3/3 READY.
- Legacy `*-sidecar/` directories deprecated with pointers to new sanctums (not removed until Epic 27 cleanup).

## Risk Register (Party-Mode Flagged)

| Risk | Owner | Mitigation |
|------|-------|-----------|
| Pilot-debt: Marcus scaffold shape locks in for 16 downstream migrations | Winston | Freeze scaffold API v0.1 before Marcus; don't iterate shape mid-pilot. |
| Texas byte-identical regression (generic script must match Texas's current sanctum) | Amelia | Test: `test_texas_sanctum_byte_identical` in `tests/migration/`. |
| Orphaned references when extracting doctrine from dense SKILL.md | Paige | Migration worksheet mandates a grep-before-commit pass. |
| "Temporarily-still-in-SKILL.md" content drift | Paige | Every chunk routes to exactly one home; worksheet records destination. |
| Sanctum read-order ambiguity during transition (embedded vs file) | Murat | Negative test: Marcus fails loudly if sanctum missing. |
| Downstream SKILL.md section reference map not enumerated before Marcus migrates | Murat | Pre-work: `downstream-reference-map-marcus.md`. |
| Marcus↔Texas delegation contract reference breakage | Murat | Marcus-specific handshake AC in 26-1 (not all migrations pay this cost). |
