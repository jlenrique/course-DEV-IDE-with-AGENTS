# Playwright-assisted exemplar capture

## Why

Many exemplar sites (e.g. rich Gamma presentations) rely on **client-rendered** content. A plain `requests` fetch may return shells. **Playwright MCP** in Cursor can render the page, then **save HTML** (or MHTML / print) to the project.

## Recommended workflow

1. User asks the Cursor session to open the URL with **Playwright MCP** and **save** the DOM HTML to e.g. `course-content/staging/source-captures/my-exemplar.html`.
2. Invoke `source_wrangler_operations.wrangle_playwright_saved_html(path, source_url="https://...")` to get **title**, **extracted text**, and a **SourceRecord**.
3. Merge into `build_extracted_markdown` + `write_source_bundle` with other sources (Notion, Box).
4. Marcus passes **`extracted.md`** to Irene/Gary with a short note: “Web exemplar distilled from {url} on {date}; verify accuracy.”

## Limits

- Dynamic lazy content may still be missing if not loaded before save.
- Login-walled pages: user must be authenticated in the browser context Playwright uses.
