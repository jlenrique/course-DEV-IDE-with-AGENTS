# Transform Registry

Extraction method hierarchy per source type. For each format, methods are listed in priority order — try the default first, fall back in sequence.

## PDF

| Priority | Method | When to Use | Known Limitations |
|----------|--------|-------------|-------------------|
| 1 | `pypdf` (text extraction) | Default for all PDFs | Fails on scanned/image PDFs; can produce stubs on complex layouts |
| 2 | `pdfplumber` | Fallback when pypdf output is thin | Better with tables and complex layouts; slower |
| 3 | Notion MCP cross-pull | When PDF is a known Notion export | Requires Notion page ID; operator must declare provenance |
| 4 | Playwright PDF render + re-extract | When PDF is a web-generated export | Requires the original URL |
| 5 | HIL escalation | All automated methods failed | Operator provides content manually or via alternative format |

**Stub detection heuristic**: If pypdf extracts < 50% of expected words (page_count × 200), immediately try the next method before reporting.

## DOCX

| Priority | Method | When to Use | Known Limitations |
|----------|--------|-------------|-------------------|
| 1 | `python-docx` text extraction | Default | Style/formatting loss beyond headings H1-H6 — bold, italic, colors, fonts, paragraph spacing not preserved; table-layout loss — cells flattened to pipe-rows, no cell-merge or vertical-align preservation; inline images ignored; footnotes, comments, and tracked-changes not extracted |
| 2 | LibreOffice CLI → plain text | Fallback for complex layouts | Requires LibreOffice installed; currently not wired (Priority-1 failure produces FAILED `SourceOutcome`; operator reroutes) |
| 3 | Read as ZIP + extract XML | Last resort for corrupted files | Produces raw XML, needs cleanup; currently not wired |

> **Implementation cross-reference** (Story 27-1): Priority-1 method is wired via `wrangle_local_docx()` in `skills/bmad-agent-texas/scripts/source_wrangler_operations.py` and the `.docx` branch inside `run_wrangler._fetch_source()`. Malformed-DOCX inputs surface `python-docx` `PackageNotFoundError`, which `_classify_fetch_error()` maps to `error_kind="docx_extraction_failed"` with `known_losses=["docx_open_failed"]` — no fall-through to `read_text_file()` (which would re-introduce the binary-garbage defect 27-1 fixes). This footnote is human-facing documentation only; the `test_transform_registry_lockstep` contract test encodes the method→extractor mapping as Python constants in the test file, not by parsing this prose.

## Markdown (.md)

| Priority | Method | When to Use | Known Limitations |
|----------|--------|-------------|-------------------|
| 1 | Direct file read | Always | Escaped markdown (backslash-prefixed) needs cleanup |

**Note**: MD files with escaped formatting (e.g., `\#` instead of `#`, `\*\*` instead of `**`) should be normalized during extraction. This is common with content exported from rich text editors.

## Notion

| Priority | Method | When to Use | Known Limitations |
|----------|--------|-------------|-------------------|
| 1 | Notion MCP / REST API | Default | Requires NOTION_API_KEY; page must be shared with integration |
| 2 | Playwright page save | When API access fails | Requires browser automation |
| 3 | Exported PDF/HTML | When operator provides a manual export | May lose database/embedded content |

## HTML / URL

| Priority | Method | When to Use | Known Limitations |
|----------|--------|-------------|-------------------|
| 1 | `requests` + HTML-to-text | Simple static pages | Fails on JS-rendered SPAs |
| 2 | Playwright MCP | Dynamic/JS-heavy pages | Slower; requires browser context |
| 3 | Playwright save + offline extract | Auth-walled pages | Operator must authenticate first |

## Box (fetch layer)

| Priority | Method | When to Use | Known Limitations |
|----------|--------|-------------|-------------------|
| 1 | `boxsdk` developer-token fetch → local file → format extractor | Default for Box-hosted content | Requires `BOX_DEVELOPER_TOKEN` env var; developer tokens expire after 60 minutes; folder-level fetch is deferred to a follow-on story (file-level only in v1); OAuth2 refresh / JWT auth are future work |

> **Implementation cross-reference** (Story 27-6): Box is a **fetch-layer** provider, not a format handler — it resolves a Box file ID or shared-link URL to a local file via `wrangle_box_file()` in `skills/bmad-agent-texas/scripts/source_wrangler_operations.py`, then dispatches the downloaded file through the existing suffix-based extractors (`wrangle_local_pdf` for `.pdf`, `wrangle_local_docx` for `.docx`, `wrangle_local_md` for `.md`, `read_text_file` for plain text). The `box` provider branch in `run_wrangler._fetch_source` calls `wrangle_box_file(locator)` and returns its `(title, body, SourceRecord)` tuple. Auth failures (missing or expired `BOX_DEVELOPER_TOKEN`, 401/403 from Box) raise `BoxAuthError` with operator-facing remediation text that names the env var, the Box developer-console URL, and the re-run step. Rate-limit (429), not-found (404), and permission (403-class resolvable-but-unauthorized) failures surface as typed `BoxRateLimitError` / `BoxNotFoundError` / `BoxPermissionError` — each distinct so downstream error classification can act on the auth-vs-availability axis. Since Box itself does not produce extraction output (the underlying PDF/DOCX/MD does), the transform-registry lockstep test exempts Box via `LOCKSTEP_EXEMPTIONS`; end-to-end routing is proved separately by `tests/test_box_provider.py`.

## Future (Placeholder)

These formats are not yet supported but are anticipated:

- **PPTX**: Slide-by-slide text + speaker notes extraction
- **XLSX/CSV**: Tabular data → structured markdown tables
- **Video transcripts (SRT/VTT)**: Timestamp-aware text extraction
- **Scanned PDFs**: OCR pipeline (Tesseract or cloud vision API)
- **Images**: Vision API → structured description
