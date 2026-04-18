# Story 27-6: Box Provider

**Epic:** 27 — Texas Intake Surface Expansion
**Status:** ratified-stub
**Sprint key:** `27-6-box-provider`
**Added:** 2026-04-17
**Points:** 2
**Depends on:** 27-2 (atomic-write + lockstep patterns).
**Blocks:** nothing.

## Story

As the Texas wrangler,
I want to fetch files from a Box location (folder ID or file ID) specified at directive time,
So that operator-stored primary and supporting materials in Box become first-class Texas sources without manual download.

## Background

Unlike Notion, there is no Box MCP currently loaded in the environment. This story either (a) adds a Box MCP server + wires it like 27-5, or (b) uses the Box Python SDK directly with OAuth token. Architecture decision at create-story time.

Box's distinguishing trait over generic file-store access is its versioning, granular permission model, and link-shared folder semantics. For Texas's purposes, the surface is simpler: authenticate → list/fetch a specified file or folder's contents → normalize via the same extraction logic Texas uses for `local_file` (PDF, DOCX from 27-1, plain text, etc.).

## Acceptance Criteria (Stub Level)

- **AC-1:** `provider: box` registered in `transform-registry.md` and dispatched in `run_wrangler.py`.
- **AC-2:** Directive accepts Box file ID, folder ID, or shared link. Folder mode recurses with a configurable depth cap.
- **AC-3:** Downloaded files route through Texas's existing format-specific extractors (PDF, DOCX from 27-1, text, future image from 27-3, etc.) — Box is a fetch layer, not a new extraction format.
- **AC-4:** Auth handled via Box OAuth (token stored in env var `BOX_ACCESS_TOKEN`); refresh-token flow documented if refresh is needed beyond single-session.
- **AC-5:** `provider_metadata.box`: `item_id`, `item_type`, `size_bytes`, `modified_at`, `created_by`, `path` (folder hierarchy).
- **AC-6:** Rate-limit + permission-denied failures emit controlled FAILED outcomes with actionable guidance.
- **AC-7:** Cassette-backed tests via mocked API responses.
- **AC-8:** Lockstep check passes. Epic 27 spine satisfied.
- **AC-9:** No pytest regressions.

## File Impact (Preliminary)

- `skills/bmad-agent-texas/scripts/providers/box_provider.py` — new
- `skills/bmad-agent-texas/scripts/run_wrangler.py` — box branch
- `skills/bmad-agent-texas/references/transform-registry.md` — add box row
- `tests/test_box_provider.py` — new
- `tests/cassettes/texas/box/*.yaml` — cassette library
- `.env.example` — document `BOX_ACCESS_TOKEN`
- `requirements.txt` — `boxsdk` or equivalent

## Notes for Create-Story

- Direct SDK vs. MCP — decide at create-story with Winston input. If a Box MCP becomes available in the environment before this story lands, prefer MCP for consistency with 27-5.
- Folder recursion depth cap needs operator confirmation (default 3 levels, configurable).

## Party Input Captured
- **Amelia (Dev, Round 3):** 2 points (smallest of the new providers — fetch layer only, extraction delegated).
- **Operator (Round 3 NN1):** Box intake is a committed new capability.
