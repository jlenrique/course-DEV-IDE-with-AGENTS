# Next Session Start Here

## Immediate Next Action

**Complete Story 1.1 code review**, then **create and implement Story 1.2** (Python Infrastructure).

```
# In a FRESH Cursor chat session:
1. Run bmad-code-review on Story 1.1 (status: review) — or mark done if satisfied
2. Run bmad-create-story (auto-discovers Story 1.2 from sprint-status.yaml)
3. Run bmad-dev-story to implement Story 1.2
4. Repeat for remaining Epic 1 stories
```

## Current Status — IMPLEMENTATION PHASE STARTED

- **Story 1.1 (Cursor Plugin Foundation)**: REVIEW — all tasks complete, validated, post-review cleanup applied
- **Story 1.2 (Python Infrastructure)**: BACKLOG — next to create
- **Epic 1**: IN-PROGRESS
- **Tool Universe**: 15 tools audited and classified
- **Live MCPs**: Gamma (2 tools), Canvas LMS (54 tools) verified in Cursor
- **API-verified**: ElevenLabs (45 voices), Qualtrics (authenticated), Wondercraft, Kling

## What's Working Right Now

### MCP Servers (in Cursor agent chat)
- **Gamma**: 2 tools — generate content, browse themes
- **Canvas LMS**: 54 tools — full course/module/assignment management
- **Playwright**: 22 tools — browser automation (user-level)
- **Ref**: 2 tools — doc search and URL reading (user-level)

### API Access (via scripts, not MCP)
- **ElevenLabs**: `node scripts/smoke_elevenlabs.mjs` — 45 voices
- **Qualtrics**: `node scripts/smoke_qualtrics.mjs` — surveys, questions, distributions
- **All tools**: `node scripts/heartbeat_check.mjs` — full heartbeat

### Known MCP Limitations (deferred)
- ElevenLabs MCP: Cursor filters tools due to name length >60 chars
- Qualtrics MCP: Not on npm, needs local build
- Canva MCP: OAuth redirect rejected by Cursor
- Fetch MCP: No usable tools surfaced

## Hot-Start Context

### Key File Paths
- Story 1.1: `_bmad-output/implementation-artifacts/1-1-cursor-plugin-foundation.md`
- Sprint Status: `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Epics: `_bmad-output/planning-artifacts/epics.md`
- Tool Matrix: `resources/tool-inventory/tool-access-matrix.md`
- MCP Config (live): `.cursor/mcp.json`
- MCP Config (template): `.mcp.json`
- MCP Wrapper: `scripts/run_mcp_from_env.cjs`
- Project Context: `docs/project-context.md`

### Key Tools for Next Session
- `bmad-code-review` — finish Story 1.1 review
- `bmad-create-story` — create Story 1.2
- `bmad-dev-story` — implement stories

### API Keys
- `.env` has live keys for: Gamma, ElevenLabs, Canvas, Qualtrics, Botpress, Wondercraft, Kling
- `.env` is gitignored; `.env.example` is the safe template
- `.cursor/mcp.json` uses `scripts/run_mcp_from_env.cjs` to load keys at runtime (no literal secrets in config)

### Gotchas
- PowerShell doesn't support `&&` chaining — use `;` instead
- `python` defaults to 3.13 via pyenv, but some packages were installed in 3.10 — Story 1.2 will set up a proper .venv
- Cursor MCP `env` field does NOT resolve `${VAR}` from .env files — that's why the wrapper script exists
- Rotate any API keys visible in chat history (Gamma, ElevenLabs, Canvas, Qualtrics were exposed during this session)
