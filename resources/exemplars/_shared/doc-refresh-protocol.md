# Documentation Refresh Protocol

Every specialist agent must have current, authoritative knowledge of its tool's API. Stale docs lead to wrong parameters, missed capabilities, and failed reproductions. This protocol ensures agents stay current.

## Doc Sources Registry

Each mastery skill maintains a `references/doc-sources.yaml` listing all authoritative documentation sources for its tool. This file is the single source of truth for where to find current docs.

### Schema

```yaml
tool: gamma                       # tool identifier
doc_sources:
  - name: "Gamma Developer Docs"
    url: "https://developers.gamma.app/"
    type: developer-docs           # developer-docs | help-center | changelog | api-reference
    llm_optimized: "https://developers.gamma.app/llms.txt"      # if available
    llm_full: "https://developers.gamma.app/llms-full.txt"       # if available
    md_suffix: true                # append .md to any page URL for markdown version
  - name: "Gamma Help Center"
    url: "https://help.gamma.app/en/"
    type: help-center
  - name: "Gamma API Changelog"
    url: "https://developers.gamma.app/changelog/readme.md"
    type: changelog

refresh_protocol:
  on_woodshed_start: true          # MANDATORY: check for doc updates before every woodshed cycle
  on_story_start: true             # check when a new story involving this tool begins
  on_regression: false             # skip for regression runs (speed)
  method: ref_mcp                  # primary: use Ref MCP (ref_search_documentation + ref_read_url)
  fallback: web_fetch              # secondary: use WebFetch if Ref MCP unavailable

last_refreshed: null               # timestamp of last refresh
refresh_notes: null                # any changes discovered during last refresh
```

## When to Refresh

| Trigger | Action | Depth |
|---------|--------|-------|
| **Woodshed start** | Mandatory. Check changelog + LLM-optimized docs for any changes since last refresh | Full: read changelog, scan for new/changed parameters |
| **New story** | Recommended. Quick check of changelog for breaking changes | Light: read changelog only |
| **Regression run** | Skip unless a regression failure suggests API change | Only on failure investigation |
| **User request** | "Update your docs" or "Check for API changes" | Full refresh |

## How to Refresh

### Step 1: Check Changelog

Use Ref MCP to read the tool's changelog URL:

```
ref_read_url({ url: "{changelog_url}" })
```

Compare against `last_refreshed` date. If new entries exist, flag them.

### Step 2: Scan LLM-Optimized Docs

If the tool provides `llm_optimized` or `llm_full` URLs (like Gamma's `llms.txt`):

```
ref_read_url({ url: "{llm_optimized_url}" })
```

Compare the page index against the baseline `api-docs.md` in `references/`. Flag any new pages or changed page titles.

### Step 3: Deep Read (if changes detected)

For any changed or new doc pages:

```
ref_read_url({ url: "{specific_page_url}.md" })
```

Extract new parameters, changed behaviors, deprecations. Update the baseline `api-docs.md` and `parameter-catalog.md` if needed.

### Step 4: Update Refresh Metadata

Update `doc-sources.yaml`:
```yaml
last_refreshed: "2026-03-28T14:30:00"
refresh_notes: "New cardOptions.dimensions value 'widescreen' added. exportAs now supports 'svg'."
```

### Step 5: Log to Memory Sidecar

Append discovered changes to the agent's `patterns.md`:
```
## Doc Refresh — 2026-03-28
- New parameter: cardOptions.dimensions supports 'widescreen'
- exportAs now supports 'svg' format
- No breaking changes
```

## MCP Tools Available

The **Ref MCP** (user-level, always available in Cursor) provides:

| Tool | Purpose |
|------|---------|
| `ref_search_documentation` | Search for documentation by query (e.g., "Gamma API generate parameters") |
| `ref_read_url` | Read a specific URL as markdown (use exact URLs from search results or doc-sources.yaml) |

## Tool-Specific Doc Patterns

Different tools provide docs in different ways. The `doc-sources.yaml` captures these differences:

| Tool | LLM-Optimized Docs | Changelog | Notes |
|------|---------------------|-----------|-------|
| **Gamma** | `llms.txt` + `llms-full.txt` + `.md` suffix on any page | Yes (developer docs) | Best-in-class LLM support |
| **ElevenLabs** | Check for `/llms.txt` | Check developer docs | May need `ref_search_documentation` |
| **Canvas** | Official REST API docs | Check community changelog | Large API surface — focus on endpoints used |
| **Qualtrics** | Developer portal | Check release notes | Enterprise API — may need specific scoping |
| **Canva** | MCP-based — check MCP tool descriptors | Check MCP changelog | OAuth-based access |

## Anti-Patterns

- Never assume cached docs are current — always check before woodshed cycles
- Never hardcode API parameters from memory — always verify against current docs
- Never skip the changelog check — even minor API changes can break reproductions
- Never update `parameter-catalog.md` without citing the source doc URL
