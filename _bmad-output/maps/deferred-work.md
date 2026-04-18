# Deferred Work

- ~~2026-04-02: Build function to save downloaded literal visuals from Gamma into the existing Git site destination. Status: implemented on `dev/storyboarding-feature` with preintegration publish helper, mode-aware fail-closed behavior, URL substitution wiring, and regression/live integration test coverage.~~ **Closed 2026-04-02.**

## Stashed for Story 27-5 (Notion provider) — 2026-04-17

Cursor loads TWO Notion MCP servers in parallel (non-conflicting keys):

**User-scope** `C:\Users\juanl\.cursor\mcp.json` → `"Notion"` → hosted HTTP MCP at `https://mcp.notion.com/mcp`
- Tools: `notion-*` curated surface (~12-14 tools: `notion-search`, `notion-fetch`, `notion-create-pages`, etc.)
- Auth: Notion's hosted flow (typically OAuth / session)
- Designed for agent-UX (Tracy, IDE sessions)

**Project-scope** `.cursor/mcp.json` + `.mcp.json` → `"notion"` → local stdio via `scripts/run_mcp_from_env.cjs notion` → `npx -y @notionhq/notion-mcp-server`
- Tools: `API-*` wrappers (~22 tools: `API-post-search`, `API-retrieve-a-page`, etc.)
- Auth: integration token (`NOTION_API_KEY` in `.env`, mapped to `NOTION_TOKEN`)
- Designed for API-key automation (headless Python, CI)

**For Story 27-5 (Texas Notion adapter, locator-shape)**: use **project-scope stdio version**. Rationale:
1. Token-auth matches `run_mcp_from_env.cjs` pattern already established for canvas-lms, gamma, and this notion entry.
2. Texas runs headless in CI — OAuth-style user-session auth doesn't fit.
3. Granular `API-*` tools map cleanly onto locator-shape dispatch (operator provides Notion page-id → Texas fetches via `API-retrieve-a-page` / `API-get-block-children`).
4. Deterministic for testing — stdio subprocess can be mocked; hosted HTTP requires live auth flow.

**For Tracy's IDE-agent exploratory research (Epic 28)**: user-scope hosted version is better. Curated `notion-*` tools are designed for agent reasoning; OAuth session matches Cursor's session auth; fewer tools = less prompt bloat.

**Recommendation**: keep both — they serve different consumers. When 27-5 reshapes post-27-0, spec notes that Texas's Notion adapter uses project-scope stdio; Tracy may use either in IDE sessions at her discretion.

## Deferred from: code review of story-27-1 (2026-04-17)

- Sibling Office-ZIP suffixes `.docm` / `.dotx` / `.dotm` still fall through to `read_text_file()` in Texas's `local_file` dispatch, re-introducing the binary-garbage defect 27-1 fixes for slightly rarer suffixes. Real-world-shape robustness was explicitly deferred to a follow-on Epic 27 story per Murat's implementation-review note (candidate name: "Texas intake robustness" — password-protected, macros, Google Docs / Pages exports, corrupted-ZIP-valid).
- DOCX body-order iteration silently drops `<w:sdt>` (content controls / structured document tags) and `<w:altChunk>` (embedded sub-document) elements. Form-control DOCX files produce empty extraction with no `known_loss` sentinel. Same follow-on story as the sibling-suffix gap.
- `extract_docx_text` docstring only documents `PackageNotFoundError`, but python-docx can raise `BadZipFile`, `KeyError` (missing style reference), or `AttributeError` under unusual inputs. Either expand the classifier's case table or broaden the docstring's Raises clause. Low-priority doc accuracy.
- Integration test `provenance[0]["ref"] == str(docx_path)` could theoretically flake on Windows short-path resolution (`JUANLE~1` format). Not observed in practice; switch to `Path(...).samefile(...)` comparison if observed.
- Negative-control fixture for Tejal cross-validator — a DOCX/PDF pair from unrelated source docs that should cross-validate as DIFFERENT. Without it, the 100% key-term coverage result cannot be distinguished from "heuristic is loose." Murat implementation-review follow-on.
- Collapse `_EXTRACTOR_LABELS` + `_EXTRACTOR_LABELS_BY_KIND` to a single kind-keyed source of truth with provider-derived default kind. Winston implementation-review architectural polish pass (~20 min).
