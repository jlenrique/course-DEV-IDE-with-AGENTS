---
name: source-wrangler
description: Pull course sources from Notion and Box Drive, fetch or ingest web and Playwright-captured HTML, extract text from local PDFs, and emit agent-ready source bundles (extracted.md + metadata) for Marcus and specialists.
---

# Source Wrangler (DEPRECATED)

> **DEPRECATED:** This skill has been superseded by **Texas** (`skills/bmad-agent-texas/`),
> a full memory agent with extraction validation, cross-validation, fallback chains,
> and a Marcus delegation contract. The scripts in this directory are retained for
> backward compatibility but will be removed once all callers are migrated to Texas.

## Purpose

Consolidates **reference material** into a **single consumable bundle** so Irene, Gary, and other agents do not depend on copy-paste or stale context. Supports:

- **Notion** — pages via `NotionClient` (`NOTION_API_KEY`)
- **Box Drive** — local sync folder (`BOX_DRIVE_PATH`) file listing and text reads
- **HTTP URLs** — fetch + HTML-to-text (simple sites; auth-walled pages need Playwright capture)
- **Local PDFs** — `extract_pdf_text()` / `wrangle_local_pdf()` via **pypdf** (text-native PDFs; scanned/OCR out of scope unless added later)
- **Playwright MCP captures** — user/session saves HTML to disk; skill **processes** the file into clean text and provenance

### Gamma hosted docs (critical)

- **Do not** call `fetch_url` / `summarize_url_for_envelope` on `https://gamma.app/docs/...` links. They return Cloudflare interstitials and are the wrong integration surface.
- **Do** obtain exemplar content through **Gary** (`bmad-agent-gamma` + `gamma-api-mastery` / Gamma MCP): export PDF or PNG, then `wrangle_local_pdf()` on the export, **or** Playwright save + `wrangle_playwright_saved_html()`.
- Attempting a blocked URL raises `GammaDocsURLNotSupportedError` with remediation text.

### Preflight

- Before building a bundle, call `require_local_source_files([...])` or check `verify_local_source_paths()` so missing SME PDFs fail loudly (no silent empty bundles).
- Assemble bundles only through this skill’s APIs — **no one-off builder scripts** in `course-content/`.

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
| `./scripts/source_wrangler_operations.py` | HTML + PDF text extraction, URL fetch (with Gamma guard), bundle IO, Box listing, local preflight |
| `scripts/api_clients/notion_client.py` | Notion API |

## Operating Rules

- Never commit secrets; `.env` holds `NOTION_API_KEY`, `BOX_DRIVE_PATH`
- Cap URL fetch size (default 5MB) and prefer **saved HTML** for heavy/JS pages
- **Bundle output path (align with Marcus run mode):**
  - **Default mode:** `course-content/staging/source-bundles/{run_or_slug}/`
  - **Ad-hoc mode:** `course-content/staging/ad-hoc/source-bundles/{run_or_slug}/` so ingest artifacts stay in the scratch tree (`bmad-agent-marcus` → `references/mode-management.md`)
- This skill does **not** read `mode_state.json` itself — **Marcus** (or the invoking agent) chooses `output_dir` for `write_source_bundle()` from the active modality
- Register durable patterns under `resources/exemplars/` only when human promotes a capture to a **named exemplar**

## Downstream

Marcus adds to context envelopes:

- `source_bundle_path` or explicit path to `extracted.md`
- `provenance` summary from `metadata.json` for transparency

Irene/Gary use content as **supplemental** `input_text` / `user_constraints` / `additionalInstructions` — not a substitute for the slide brief contract.
