---
name: pre-flight-check
description: "Verify all MCPs, APIs, and tool capabilities before production runs. Generates a comprehensive readiness report with per-tool status and resolution guidance."
---

# Pre-Flight Check

## Purpose

Validates that the collaborative intelligence tool ecosystem is operational before starting content production. Checks MCP connectivity, API authentication, and tool availability, then produces a readiness report classifying each tool.

## When to Use

- Before starting a production run
- When the master orchestrator receives "run pre-flight check" or "are all tools ready?"
- After environment changes (new API keys, updated MCP config)
- Periodically to detect tool capability changes

## Invocation

### Manual (agent chat)

Ask the agent: "Run pre-flight check" or "Check system readiness"

### Programmatic (Python)

```bash
.venv/Scripts/python -m skills.pre-flight-check.scripts.preflight_runner
```

### Future: Session Hook

The `hooks/scripts/session-start.mjs` placeholder will be wired to invoke pre-flight through the master orchestrator in Story 2.5.

## What It Checks

| Check Type | Tools | Method |
|---|---|---|
| **MCP Config** | Gamma, Canvas LMS, Notion | Verify `.mcp.json` / `.cursor/mcp.json` entries are present and well-formed |
| **API Heartbeat** | All Tier 1-2 tools | Run `scripts/heartbeat_check.mjs` for read-only connectivity probes |
| **Targeted Smoke** | ElevenLabs, Qualtrics | Run focused smoke scripts for deeper API validation |
| **Notion API** | Notion | Direct Python API call to `/v1/users/me` to verify integration token |
| **Local FS** | Box Drive | Verify `BOX_DRIVE_PATH` exists, is a directory, and is readable |
| **Config Presence** | Kling, Panopto | Verify API keys are set in `.env` |
| **Static Classification** | Vyond, CourseArc, Articulate | Report as manual-only (no API to test) |
| **Blocker Reporting** | Canva | Report known MCP blockers with workaround guidance |
| **Ref MCP** | Documentation/Research | Verify Ref MCP responds (`ref_search_documentation` callable) — required by tech-spec-wrangler |
| **Doc Sources** | All specialist agents | Scan for `doc-sources.yaml` in each mastery skill's `references/`; flag stale `last_refreshed` dates |

## Output

A structured readiness report with four classification tiers:
- **MCP-ready** — MCP configured and API heartbeat passed
- **API-ready** — API connectivity verified (MCP not available or deferred)
- **Manual-only** — No programmatic access; agent provides specifications, user executes
- **Blocked/deferred** — Known issue preventing connectivity; resolution guidance provided

## References

For detailed diagnostic procedures, see:
- `references/diagnostic-procedures.md` — Step-by-step troubleshooting per tool
- `references/check-strategy-matrix.md` — When to use MCP check vs API smoke vs config check
- `references/tool-doc-scanning.md` — Patterns for scanning tool docs for capability changes via Ref MCP
