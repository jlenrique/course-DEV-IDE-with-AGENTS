# scite fixtures — provenance

**Story 27-2** (PDG-2 path B resolution): scite MCP tool shapes inferred from
`scite.ai/api-docs` + public MCP docs, 2026-04-18. Fixtures are synthetic JSON
mirroring the expected shape of each MCP tool response. First live run is the
moment-of-truth; any diff between synthetic and live becomes the scope for the
follow-on `27-2-live-cassette-refresh` story.

## Files

| File | Tool | Purpose |
|------|------|---------|
| `search_happy.json` | `search` | Topical query with 3 papers returned |
| `paper_metadata_happy.json` | `paper_metadata` | DOI lookup, full-text available |
| `paper_metadata_paywalled.json` | `paper_metadata` | DOI lookup, abstract-only degradation |
| `citation_context_happy.json` | `citation_contexts` | DOI with 10/10/10 smart-citation contexts across 3 classifications |
| `empty_search.json` | `search` | Query with zero matches |
| `auth_failure_401.json` | (any) | HTTP 401 body payload |
| `rate_limit_429.json` | (any) | HTTP 429 body payload |

Each fixture is the **JSON-RPC `result` payload only** — tests wrap via
`tests._helpers.mcp_fixtures.jsonrpc_response(result=...)`.
