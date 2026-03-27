# Source bundle format

Each bundle is a directory written by `write_source_bundle()`.

## Files

| File | Purpose |
|------|---------|
| `extracted.md` | **Primary agent consumption** — merged sections (title + bodies) |
| `metadata.json` | `title`, `generated_at`, `provenance[]`, `primary_consumption_path` |
| `raw/` | Optional originals (e.g. saved HTML, fetched snippet) for audit |

## Provenance entries

Each item: `kind` (`url` | `notion_page` | `box_file` | `playwright_html` | `local_pdf`), `ref`, `note`, `fetched_at` (ISO-8601).

For PDFs ingested via `wrangle_local_pdf()`, `note` typically includes `pypdf` and pages scanned (e.g. `pypdf scanned=10/24`).

Agents should cite `ref` when summarizing where a claim came from.
