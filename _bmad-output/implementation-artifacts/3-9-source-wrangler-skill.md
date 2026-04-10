# Story 3.9: Source Wrangler — Implementation Record

**Status:** done (2026-03-28)  
**Form:** Shared **skill** (`skills/source-wrangler/`), not a standalone agent.  
**Scope expansion:** Original Notion + Box scope **plus** HTTP URL fetch, HTML-to-text, and **Playwright MCP-assisted** capture (saved HTML processed into agent bundles).

## Delivered

- `scripts/api_clients/notion_client.py` — Notion API v1, page markdown export, search, append paragraphs
- `skills/source-wrangler/SKILL.md` + references (bundle format, Notion/Box, Playwright path)
- `skills/source-wrangler/scripts/source_wrangler_operations.py` — bundles, URL fetch, Box listing, HTML ingest
- Unit tests: `skills/source-wrangler/scripts/tests/`, `tests/test_notion_client.py`
- Marcus: `source-wrangler` external skill **active**; `source-prompting.md` updated
- Docs: `project-context.md`, `agent-environment.md`, `user-guide.md`

## Invocation

Marcus (or any specialist session) loads the skill when pulling sources; outputs land under `course-content/staging/source-bundles/{slug}/` with `extracted.md` + `metadata.json`.

## Follow-ups (non-blocking)

- PDF/DOCX text extraction for Box files
- Deeper Notion block types (tables, databases)
- Optional promotion of captures to `resources/exemplars/{id}/` via human gate
