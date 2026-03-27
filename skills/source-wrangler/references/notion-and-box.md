# Notion and Box Drive

## Environment

| Variable | Role |
|----------|------|
| `NOTION_API_KEY` | Internal integration secret |
| `NOTION_ROOT_PAGE_ID` | Default hub page (optional anchor for searches) |
| `BOX_DRIVE_PATH` | Root of Box **sync** folder on disk |

Pre-flight already checks Notion `users/me` and Box path readability (`skills/pre-flight-check`).

## Notion usage

- `NotionClient.page_to_markdown(page_id)` — full page text for bundles
- `NotionClient.search_pages(query)` — discover page IDs by title keywords
- `NotionClient.append_paragraphs(block_id, paragraphs)` — post-run feedback (keep concise)

## Box usage

- `list_box_files(root, glob_pattern, max_files)` — bounded discovery
- Read `.md`/`.txt` directly; `.pdf`/`.docx` are listed but **not** text-extracted in v1 (ingest manually or convert offline)
