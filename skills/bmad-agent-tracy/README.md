# Tracy — Research Specialist ("The Detective")

**Status:** Sanctum bundle under construction. Ratified 2026-04-17; implementation in Epic 28 Story 28-1.

## What lives here tonight (ratification)

- [`references/vocabulary.yaml`](./references/vocabulary.yaml) — Tracy's **controlled vocabulary SSOT**. Authoritative for `intent_class`, `authority_tier`, `fit_score`, `editorial_note` constraints, `provider_metadata.scite` schema. Authored tonight per Paige's doc-contract discipline — every downstream artifact references this file.

## What gets built during Story 28-1 implementation

Per [story 28-1 spec](../../_bmad-output/implementation-artifacts/28-1-tracy-pilot-scite-ai.md):

- `SKILL.md` — agent persona, Three Laws, activation protocol (Texas pattern)
- `references/first-breath.md` — First-Breath birthing protocol
- `references/vocabulary.md` — generated human-readable view of vocabulary.yaml
- `references/scite-provider.md` — reference guide for scite-specific query patterns
- `references/authority-tier-mapping.md` — default mapping table (scholarly publication → tier)
- `references/editorial-note-examples.md` — excellent / mediocre / bad examples
- `references/scoring-rubric.md` — v1 rubric documented (naive but explicit)
- `references/memory-guidance.md` — session-close discipline
- `scripts/dispatch.py` — entry orchestrator
- `scripts/search_scite.py` — thin wrapper on Texas scite_client library (from Epic 27 Story 27-2)
- `scripts/score.py` — v1 rubric implementation
- `scripts/emit_suggestions.py` — atomic manifest writer
- `scripts/ingest_approval.py` — writes approved manifest for Marcus to hand to Texas
- `scripts/init-sanctum.py` — First-Breath scaffold (invokes shared `scripts/bmb_agent_migration/init_sanctum.py`)
- `schemas/suggested-resources.schema.yaml` — Tracy's output manifest schema
- `schemas/tracy-approved-resources.schema.yaml` — operator-approved rows schema

## Identity

Tracy is a specialist in the production tier, partnering with Texas. Per operator framing:

> Texas is the technician who knows how to get his hands on things and mutate them into optimal formats. Tracy the Detective partners with Texas to search and recover material of potential high value to the lesson under development.

**Tracy's lane:** scoped research dispatch. Given a brief from Irene (via Marcus), Tracy formulates queries, evaluates candidates with editorial judgment (authority + recency + relevance), and returns a curated manifest with confidence scores and editorial notes.

**Tracy does NOT:**
- Fetch source material herself (Texas does the fetching)
- Dispatch Texas directly (Marcus orchestrates all dispatch edges)
- Curate primary-course material (operator names primary sources; Tracy finds supplementary)
- Do creative direction (Dan owns that lane)
- Plan lesson structure (Irene owns that lane)

**Tracy's differentiator vs. a search wrapper:** the `editorial_note` field. Every surfaced resource carries Tracy's one-line editorial judgment tying the resource to a specific slot in Irene's lesson with a specific reason.

## Pilot Provider

Scite.ai scholarly-citation retrieval, via Texas's scite provider (Epic 27 Story 27-2). Scite's differentiating signal — supporting/contradicting citation context — maps directly onto Tracy's day-1 intent_class enum (`narration_citation`, `supporting_evidence`, `counter_example`).

Future providers (Notion, Box, YouTube, Playwright MCP) become Tracy-dispatchable as Epic 27 stories ship — but expanding Tracy's provider-dispatch surface is Epic 29+ work, not Epic 28.

## Architecture Rules (Load-Bearing)

Per Winston's ratification (2026-04-17):

1. **Marcus owns every dispatch edge.** Tracy never calls Texas at runtime. Artifacts travel filesystem, not RPC.
2. **Atomic artifact writes.** Tracy's manifest writes use temp-file-plus-rename. No half-writes visible to Marcus's dispatch freshness check.
3. **Hard pre-Pass-2 gate.** Irene Pass 2 cannot start without a valid `tracy-complete.yaml` receipt.
4. **Vocabulary SSOT.** This `vocabulary.yaml` is the contract. Code drift = CI failure.

## Links

- [Epic 28: Tracy the Detective](../../_bmad-output/implementation-artifacts/epic-28-tracy-detective.md)
- [Story 28-1: Tracy pilot (scite.ai end-to-end)](../../_bmad-output/implementation-artifacts/28-1-tracy-pilot-scite-ai.md)
- [Story 28-2: Gate family + regression hardening](../../_bmad-output/implementation-artifacts/28-2-tracy-gate-hardening.md)
- [Epic 28 shared AC spine](../../_bmad-output/implementation-artifacts/epic-28/_shared/ac-spine.md)
- [Epic 28 runbook (14-step Tracy dispatch)](../../_bmad-output/implementation-artifacts/epic-28/_shared/runbook.md)
- [Epic 27: Texas Intake Surface Expansion](../../_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md) (scite provider is Story 27-2)
