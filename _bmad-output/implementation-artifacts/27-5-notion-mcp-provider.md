# Story 27-5: Notion MCP Provider

**Epic:** 27 — Texas Intake Surface Expansion
**Status:** ratified-stub
**Sprint key:** `27-5-notion-mcp-provider`
**Added:** 2026-04-17
**Points:** 3
**Depends on:** 27-2 (atomic-write + lockstep patterns).
**Blocks:** nothing.

## Story

As the Texas wrangler,
I want to fetch Notion page content via the Notion MCP server (auth already handled by the MCP layer) given a Notion page URL or page ID at directive time,
So that operator-owned Notion knowledge bases and Tracy-suggested Notion references become first-class Texas sources without the operator manually exporting pages to PDF first.

## Background

The 2026-04-17 Tejal trial hit a Notion authorization issue: "Notion fetch blocked — integration not granted to specific page." This proves the MCP pathway exists but page-scope authorization UX needs work. The existing `provider: notion` in Texas's current code is a legacy direct-API path; this story replaces or supplements it with an MCP-mediated path that leverages the already-loaded `mcp__claude_ai_Notion__*` and `mcp__notion__API-*` tool families.

MCP provides auth + page access + block traversal as primitives. This story wires Texas to invoke those MCP tools via the runtime harness and transform the response into Texas's canonical extraction shape.

## Acceptance Criteria (Stub Level)

- **AC-1:** `provider: notion_mcp` registered (distinct from legacy `notion`); legacy path deprecated with migration note in `transform-registry.md`.
- **AC-2:** Directive accepts Notion page URL or page ID; extracts page content including nested blocks (sub-pages optional via `include_children: true/false` flag).
- **AC-3:** Rich-text semantics preserved: headings render as markdown headings, code blocks as fenced code, databases as tables (with known-losses documented).
- **AC-4:** Auth failure (integration not granted to specific page) produces a clear FAILED outcome with actionable guidance: "Grant Notion integration access to this page — see [docs link]."
- **AC-5:** `provider_metadata.notion`: `page_id`, `last_edited_by`, `last_edited_time`, `database` (if page is a database entry), `parent_path`.
- **AC-6:** Cassette-backed tests via mocked MCP responses; integration test with a live fixture page gated behind env var.
- **AC-7:** Lockstep check passes. Epic 27 spine satisfied.
- **AC-8:** No pytest regressions.

## File Impact (Preliminary)

- `skills/bmad-agent-texas/scripts/providers/notion_mcp_provider.py` — new
- `skills/bmad-agent-texas/scripts/run_wrangler.py` — `notion_mcp` branch
- `skills/bmad-agent-texas/references/transform-registry.md` — add notion_mcp row, mark legacy `notion` deprecated
- `tests/test_notion_mcp_provider.py` — new
- `tests/cassettes/texas/notion_mcp/*.yaml` — cassette library
- Documentation: README section for the operator's Notion-integration grant flow (Sally UX input warranted at create-story time)

## Notes for Create-Story

- MCP invocation from a Python runner is non-trivial — the MCP layer is harness-owned. Decide at create-story: does the runner shell out to a node/TS harness, or does the harness invoke Texas with MCP results pre-fetched as directive inputs? This is a Winston architecture call.
- Legacy `notion` path removal is deferred to a follow-up story; this story adds the MCP path and marks the old one deprecated.

## Party Input Captured
- **John (PM, Round 3):** originally grouped with Box as "credentialed read-only fetchers" — separated here for architectural clarity (MCP vs. direct API).
- **Operator (Round 3 NN1):** Notion MCP provider is one of the committed new capabilities.
