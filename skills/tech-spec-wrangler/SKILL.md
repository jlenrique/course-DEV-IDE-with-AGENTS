---
name: tech-spec-wrangler
description: Shared documentation refresh skill for specialist agents. Uses Ref MCP first, then updates local doc-source metadata and refresh reports.
---

# Tech Spec Wrangler

## Purpose

Provides a shared documentation-refresh workflow for specialist agents and Marcus. The skill uses Ref MCP as the primary retrieval mechanism for authoritative documentation, changelogs, and working examples, then uses local scripts to update `doc-sources.yaml`, generate a structured refresh report, and optionally append discoveries to the requesting sidecar.

## Workflow

1. Load the target tool's `doc-sources.yaml`
2. Read the listed changelog/doc URLs via Ref MCP or fallback fetch tools
3. Summarize what changed, what is new, and what may break
4. Update `last_refreshed` and `refresh_notes`
5. Optionally append durable findings to the requesting `patterns.md`

## Invocation Contract

- Required input: path to `doc-sources.yaml`
- Optional input: tool name override, refresh summary text, findings JSON, sidecar `patterns.md` path

## Rules

- Prefer Ref MCP for documentation lookups
- Use fallback web reads only when MCP is unavailable
- Do not fabricate changelog findings
- Keep refresh notes concise and dated
