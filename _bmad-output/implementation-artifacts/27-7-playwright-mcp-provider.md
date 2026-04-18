# Story 27-7: Playwright MCP Provider

**Epic:** 27 — Texas Intake Surface Expansion
**Status:** ratified-stub
**Sprint key:** `27-7-playwright-mcp-provider`
**Added:** 2026-04-17
**Points:** 3
**Depends on:** 27-2 (atomic-write + lockstep patterns).
**Blocks:** nothing.

## Story

As the Texas wrangler,
I want a `provider: playwright_mcp` that performs live headless-browser scripted capture of a URL via a Playwright MCP server — including dynamic-content rendering (JavaScript-rendered pages, authenticated sessions, cookie-gated content),
So that web content Texas's existing `playwright_html` local-scraper path cannot reach becomes first-class via MCP-mediated browser automation.

## Background

Texas already has a `playwright_html` provider (local scraper, static HTML). A Playwright MCP server exposes browser automation as a tool — enabling Texas to fetch JS-rendered content, navigate multi-step flows (click through a cookie banner, log in, wait for lazy content), and capture full-fidelity DOM + screenshots.

This is **additive** to the existing `playwright_html` — not a replacement. Use cases differ:
- `playwright_html` = static HTML, fast, no browser cost
- `playwright_mcp` = dynamic rendering, slower, supports auth + interaction

MCP pathway means the harness owns browser lifecycle; Texas invokes capture actions via MCP tools. Confirm MCP availability in environment at create-story time.

## Acceptance Criteria (Stub Level)

- **AC-1:** `provider: playwright_mcp` registered in `transform-registry.md` and dispatched in `run_wrangler.py` alongside existing `playwright_html`.
- **AC-2:** Directive accepts URL + optional interaction script (YAML-declarative: wait for selector, click selector, fill form, accept cookies).
- **AC-3:** Captures: rendered HTML + full-page screenshot + console log + network log (last optional, gated by verbose flag).
- **AC-4:** Timeout + retry policy: configurable per-directive, defaults to 45s page-load, 1 retry on transient failure.
- **AC-5:** `provider_metadata.playwright_mcp`: `final_url` (after redirects), `render_time_ms`, `screenshot_path`, `interaction_script_used`, `browser_version`.
- **AC-6:** Auth-required pages: interaction script supports form-based login; credentials from env vars only (never from directive) with explicit env-var-name reference in directive.
- **AC-7:** Cassette-backed + fixture-HTML tests for extraction logic; live browser tests gated behind env var and quarantined.
- **AC-8:** Lockstep check passes. Epic 27 spine satisfied.
- **AC-9:** No pytest regressions.

## File Impact (Preliminary)

- `skills/bmad-agent-texas/scripts/providers/playwright_mcp_provider.py` — new
- `skills/bmad-agent-texas/scripts/run_wrangler.py` — playwright_mcp branch
- `skills/bmad-agent-texas/references/transform-registry.md` — add playwright_mcp row (alongside existing playwright_html)
- `skills/bmad-agent-texas/references/playwright-interaction-dsl.md` — new doc for the YAML interaction script schema
- `tests/test_playwright_mcp_provider.py` — new
- `tests/fixtures/texas/playwright_mcp/` — captured HTML + screenshots

## Notes for Create-Story

- Confirm Playwright MCP server availability in the environment at create-story time. If absent, story converts to "wire Texas assuming MCP is added; document prerequisite."
- Interaction-script DSL scope can creep — keep initial DSL small (wait, click, fill, accept-cookies). More complex flows wait for evidence of need.
- Sensitive-content handling: screenshots may capture sensitive data; documentation should note that `tests/fixtures/texas/playwright_mcp/` must not contain captures of authenticated sessions.

## Party Input Captured
- **Amelia (Dev, Round 3):** 3 points.
- **John (PM, Round 3):** grouped originally with image as "active-providers batch"; split for clarity since MCP-vs-SDK decisions differ.
- **Operator (Round 3 NN1):** Playwright MCP provider is a committed new capability distinct from existing `playwright_html`.
