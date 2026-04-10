# Story 17.1: Research Service Foundation & API Integration

**Epic:** 17 — Research & Reference Services
**Status:** backlog
**Sprint key:** `17-1-research-service-foundation-api-integration`
**Added:** 2026-04-06
**Depends on:** Consensus and Scite.ai API credentials in `.env`. Follows `BaseAPIClient` pattern from `scripts/api_clients/base_client.py`.

## Summary

Build API clients for Consensus and Scite.ai following the established `BaseAPIClient` pattern (constructor, auth headers, retry, pagination, error handling). Add a triangulation module that cross-validates findings from both sources, producing a canonical result format with composite reliability scores.

## Goals

1. `scripts/api_clients/consensus_client.py` — search, filter, retrieve paper metadata and key findings.
2. `scripts/api_clients/scite_client.py` — search, DOI lookup, citation context (supporting/contrasting/mentioning), smart citation counts.
3. `scripts/utilities/research_triangulator.py` — cross-validate findings, score reliability, flag contradictions.
4. Extend pre-flight check (`skills/pre-flight-check/`) to verify Consensus and Scite.ai connectivity.
5. Canonical result format for downstream consumers.

## Existing Infrastructure To Build On

- `scripts/api_clients/base_client.py` — BaseAPIClient with `_request()`, retry, pagination, auth headers
- 10 existing API clients following this pattern (gamma, elevenlabs, canvas, qualtrics, notion, kling, panopto, botpress, wondercraft, canva placeholder)
- `scripts/utilities/env_loader.py` — `.env` loading for API keys
- `skills/pre-flight-check/` — connectivity verification pattern (add Consensus + Scite.ai checks)
- `docs/admin-guide.md` — API key documentation template

## Key Files

- `scripts/api_clients/consensus_client.py` — new
- `scripts/api_clients/scite_client.py` — new
- `scripts/utilities/research_triangulator.py` — new
- `skills/pre-flight-check/SKILL.md` — update connectivity checks
- `.env` — `CONSENSUS_API_KEY`, `SCITE_API_KEY`
- `docs/admin-guide.md` — credential documentation update
- `resources/tool-inventory/tool-access-matrix.md` — add Consensus and Scite.ai entries

## Acceptance Criteria

1. `ConsensusClient(BaseAPIClient)` provides: `search(query, filters)`, `get_paper(paper_id)`, `get_findings(query, max_results, recency_years)`.
2. `SciteClient(BaseAPIClient)` provides: `search(query)`, `get_by_doi(doi)`, `get_citation_contexts(paper_id)`, `get_smart_citations(doi)`.
3. Both clients follow `BaseAPIClient` constructor pattern: `base_url`, API key from `.env`, standard headers, retry config.
4. `research_triangulator.py` provides `triangulate(consensus_results, scite_results)` returning canonical format: `{query, findings[], reliability_scores, contradictions[], metadata}`.
5. Triangulation scoring: papers found in both sources score higher; contradictory citation contexts flagged; recency, citation count, and journal quality contribute to composite reliability score.
6. Pre-flight check extended: `CONSENSUS_API_KEY` and `SCITE_API_KEY` presence, API heartbeat calls.
7. Unit tests cover each client with mocked responses.
8. Unit tests cover triangulation logic with synthetic data (agreement, disagreement, partial overlap scenarios).
9. Live integration tests (behind `--run-live` flag) validate real API connectivity.
10. Tool access matrix updated with Consensus (Tier 2: API Only) and Scite.ai (Tier 2: API Only).
