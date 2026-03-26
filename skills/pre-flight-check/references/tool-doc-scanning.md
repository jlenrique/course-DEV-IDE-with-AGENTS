# Tool Documentation Scanning

Patterns for using the Ref MCP to scan tool documentation for capability changes, deprecations, or new features.

## How It Works

The pre-flight check can optionally scan tool documentation for changes since the last check. This uses the **Ref MCP** (`ref_search_documentation` and `ref_read_url` tools) available at user level in Cursor.

The Python `doc_scanner.py` prepares scan instructions. The agent executes them using Ref MCP during the pre-flight run.

## Scan Targets

| Tool | Documentation URL | What to Look For |
|---|---|---|
| Gamma | `developers.gamma.app` | New API endpoints, rate limit changes, new LLM options |
| ElevenLabs | `elevenlabs.io/docs/api-reference` | New voice models, parameter changes, pricing updates |
| Canvas LMS | `canvas.instructure.com/doc/api` | Deprecated endpoints, new API versions, auth changes |
| Qualtrics | `api.qualtrics.com` | New question types, API version changes |
| Canva | `canva.dev/docs/connect` | MCP updates, OAuth flow changes, new design tools |

## Scan Patterns

### API Changelog Check
```
Search: "{tool_name} API changelog 2026"
Purpose: Detect breaking changes or new capabilities
```

### Deprecation Notice Check
```
Search: "{tool_name} API deprecation notice"
Purpose: Identify endpoints being removed or replaced
```

### New Feature Detection
```
Search: "{tool_name} API new features release notes"
Purpose: Discover capabilities not yet in our parameter catalogs
```

## Integration with Readiness Report

Doc scanning findings appear in the readiness report under a "Documentation Changes" section when relevant changes are detected. The agent summarizes findings conversationally:

> "ElevenLabs added new voice options since last check — consider updating the voice catalog."

## Scan Frequency

- **Every session**: Not recommended (slow, consumes context)
- **Weekly or on-demand**: Recommended — invoke explicitly with "scan tool docs" or on schedule
- **After failures**: Useful to check if a failure is due to a known API change
