# Source bundle format

Each bundle is a directory written by `write_source_bundle()`.

## Files

| File | Purpose |
|------|---------|
| `extracted.md` | **Primary agent consumption** — merged sections (title + bodies) |
| `metadata.json` | `title`, `generated_at`, `provenance[]`, `primary_consumption_path` |
| `raw/` | Optional originals (e.g. saved HTML, fetched snippet) for audit |

## Provenance entries

Each item: `kind` (`url` | `notion_page` | `box_file` | `playwright_html`), `ref`, `note`, `fetched_at` (ISO-8601).

Agents should cite `ref` when summarizing where a claim came from.
