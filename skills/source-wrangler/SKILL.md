---
name: source-wrangler
description: Pull course sources from Notion and Box Drive, fetch or ingest web and Playwright-captured HTML, and emit agent-ready source bundles (extracted.md + metadata) for Marcus and specialists.
---

# Source Wrangler

## Purpose

Consolidates **reference material** into a **single consumable bundle** so Irene, Gary, and other agents do not depend on copy-paste or stale context. Supports:

- **Notion** — pages via `NotionClient` (`NOTION_API_KEY`)
- **Box Drive** — local sync folder (`BOX_DRIVE_PATH`) file listing and text reads
- **HTTP URLs** — fetch + HTML-to-text (simple sites; auth-walled pages need Playwright capture)
- **Playwright MCP captures** — user/session saves HTML to disk; skill **processes** the file into clean text and provenance

This is a **skill**, not a dedicated agent. **Marcus** invokes it early in a run; specialists receive **`extracted.md`** paths in their envelopes.

## When to Invoke

- Before Pass 1 when user has Notion notes, Box references, or a **web exemplar** to mirror
- When user says “pull my Notion page,” “scan Box for this module,” “I saved the Gamma page from Playwright—ingest it”
- Optional: append short **feedback paragraphs** back to a Notion page via `NotionClient.append_paragraphs`

## Key Paths

| Path | Purpose |
|------|---------|
| `./references/bundle-format.md` | Output layout (`extracted.md`, `metadata.json`, `raw/`) |
| `./references/playwright-assisted-capture.md` | MCP → save HTML → `wrangle_playwright_saved_html` |
| `./references/notion-and-box.md` | Env vars and conventions |
| `./scripts/source_wrangler_operations.py` | HTML text extraction, URL fetch, bundle IO, Box listing |
| `scripts/api_clients/notion_client.py` | Notion API |

## Operating Rules

- Never commit secrets; `.env` holds `NOTION_API_KEY`, `BOX_DRIVE_PATH`
- Cap URL fetch size (default 5MB) and prefer **saved HTML** for heavy/JS pages
- Write bundles under `course-content/staging/source-bundles/{run_or_slug}/` unless user specifies another path
- Register durable patterns under `resources/exemplars/` only when human promotes a capture to a **named exemplar**

## Downstream

Marcus adds to context envelopes:

- `source_bundle_path` or explicit path to `extracted.md`
- `provenance` summary from `metadata.json` for transparency

Irene/Gary use content as **supplemental** `input_text` / `user_constraints` / `additionalInstructions` — not a substitute for the slide brief contract.
