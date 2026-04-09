# Tool Access Matrix

This document catalogs all tools integrated into the course content production platform, classified by programmatic access tier.

## Tool Universe (Researched March 26, 2026)

17 tools classified by programmatic access. Full details in `resources/tool-inventory/tool-access-matrix.md`.

| Tier | Tools | Access |
|------|-------|--------|
| **Tier 1: API + MCP** | Gamma, ElevenLabs, Canvas LMS, Qualtrics, Canva, Notion | Platform capability: REST API and published MCP server |
| **Tier 2: API Only** | Botpress, Wondercraft, Kling, Panopto | REST API, no MCP server |
| **Tier 3: Limited API** | Descript, Midjourney, CapCut | Early access / third-party only |
| **Tier 4: Manual Only** | Vyond, CourseArc, Articulate (Storyline/Rise) | No usable programmatic access for this repo setup |
| **Local FS** | Box Drive | Local filesystem via desktop sync client, no API needed |

- **Live Cursor-verified MCP servers** in `.mcp.json` / `.cursor/mcp.json`: Gamma, Canvas LMS
- **API-verified but MCP-deferred platforms**: ElevenLabs, Qualtrics
- **Documented but currently deferred MCPs**: ElevenLabs (Cursor tool-name filtering), Canva (OAuth redirect rejection), Qualtrics (GitHub-only build step), Fetch (no usable surfaced tools in this setup), Brave Search (not enabled by default)
- **User-level MCPs** already available: Playwright (browser automation), Ref (doc search/reading)
- **API keys** documented in `docs/admin-guide.md`: Tier 1-3 tools with documentation links; values live in local `.env` only
- **Manual tools** require agent-guided workflows where agents provide specs and users execute in tool UI

## Implementation Status

- **Tier 1**: Full API + MCP integration (Gamma, ElevenLabs, Canvas, Qualtrics, Canva, Notion)
- **Tier 2**: API-only clients built (Botpress, Wondercraft, Kling, Panopto)
- **Tier 3**: Limited support (Descript, Midjourney, CapCut)
- **Tier 4**: Manual workflows (Vyond, CourseArc, Articulate)
- **Local FS**: Box Drive sync client

## Security Notes

- All API keys stored in local `.env` only (not committed)
- MCP servers configured for Cursor IDE integration
- Heartbeat checks validate connectivity pre-production