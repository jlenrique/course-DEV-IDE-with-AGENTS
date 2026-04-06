# Story 17.3: Inline Citation Injection Mode

**Epic:** 17 — Research & Reference Services
**Status:** backlog
**Sprint key:** `17-3-inline-citation-injection-mode`
**Added:** 2026-04-06
**Depends on:** Story 17.1 (triangulation service). Story 17.2 (related resources — shared theme extraction).

## Summary

Add a citation injection mode that enriches narration scripts or lesson notes with inline academic citations and an appended bibliography. Claims, statistics, and assertions in the text are identified, researched, and augmented with natural-language citations that preserve the author's voice. No fabricated citations — claims without credible research remain unchanged.

## Goals

1. Claim/assertion identification in source text.
2. Per-claim research via triangulation service.
3. Natural-language inline citation insertion that preserves voice and flow.
4. Appended bibliography/references section.
5. Configurable citation density: `light`, `moderate`, `thorough`.
6. Citation map for audit trail.

## Existing Infrastructure To Build On

- `scripts/utilities/research_triangulator.py` (Story 17.1) — research engine
- `scripts/utilities/related_resources.py` (Story 17.2) — theme extraction reuse
- `skills/bmad-agent-content-creator/` (Irene) — can invoke during Pass 2 narration scripting
- Editorial review skills (`bmad-editorial-review-prose`) — prose quality check after injection

## Key Files

- `scripts/utilities/citation_injector.py` — new: claim identification, research, injection, bibliography
- `state/config/run-constants.yaml` — `citation_mode: none | inline`, `citation_density: light | moderate | thorough`

## Acceptance Criteria

1. Claim identification finds: factual assertions, statistics, named theories, causal claims, comparative statements.
2. Each identified claim researched via triangulation service.
3. Matching citations inserted naturally (e.g., "(Smith et al., 2024)" or "Research from [University] confirms...") without disrupting text flow.
4. Bibliography/references section appended with full citation details (APA-style default).
5. Citation density configurable: `light` (key claims only), `moderate` (most substantive claims), `thorough` (all supportable assertions).
6. Claims with no credible research are left unchanged — zero fabricated citations.
7. Output includes citation map: `{claim_text, citation, reliability_score, source_api}` for audit.
8. Irene can invoke `inject_citations(text, density, config)` during Pass 2.
9. Injected text passes prose quality review without degradation.
10. Unit tests: claim identification accuracy, injection formatting, bibliography generation, no-fabrication guarantee.
