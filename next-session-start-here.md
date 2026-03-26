# Next Session Start Here

## Immediate Next Action

**Create Story 2.1 file, then build the Master Orchestrator agent.**

Discovery answers for Story 2.1 have been refined by Party Mode coaching (March 26, 2026 session). The answers now include run mode management (ad-hoc/default switch), source wrangling coordination (Notion + Box Drive), and medical education domain sharpening.

```
# In a FRESH Cursor chat session:
1. Run bmad-create-story for Story 2.1 (Master Orchestrator Agent Creation)
   - Discovery answers are ready in epics.md (refined by Party Mode team)
2. In a FRESH session: Run bmad-agent-builder with the refined discovery answers
   - Six-phase process produces agents/master-orchestrator.md
3. In a FRESH session: Run bmad-dev-story to implement Story 2.1
   - Memory sidecars, test invocation, validation
4. In a FRESH session: Party Mode team validates the completed agent
```

**Before starting**: Set up Notion internal integration (notion.so/my-integrations), add token to `.env` as `NOTION_API_KEY`. Notion API is free on all plans including free educator accounts.

## Current Status — EPIC 1 COMPLETE

- **Story 1.1 (Cursor Plugin Foundation)**: DONE
- **Story 1.2 (Python Infrastructure)**: DONE — BaseAPIClient with retry, pagination, binary support
- **Story 1.3 (State Management)**: DONE — SQLite + YAML + BMad memory sidecars
- **Story 1.4 (Pre-Flight Check Skill)**: DONE — SKILL.md + Python runner + doc scanner
- **Story 1.5 (Testing Framework)**: DONE — Live API tests, dev mode, conftest
- **Story 1.6 (Gamma API)**: DONE — GammaClient with themes, generation, polling
- **Story 1.7 (ElevenLabs API)**: DONE — ElevenLabsClient with TTS, voice listing, file output
- **Story 1.8 (Canvas API)**: DONE — CanvasClient with pagination, modules, pages, assignments
- **Story 1.9 (Qualtrics API)**: DONE — QualtricsClient with surveys, questions, response export
- **Story 1.10 (Canva MCP)**: DONE — Config validation, blocker documented
- **Story 1.11 (Panopto API)**: DONE — PanoptoClient with OAuth2, folders, sessions
- **Epic 1**: COMPLETE (11/11 stories done, 117 tests pass, 3 skipped)
- **Tool Universe**: 17 tools audited and classified (added Notion + Box Drive)
- **Live MCPs**: Gamma (2 tools), Canvas LMS (54 tools) verified in Cursor
- **API-verified**: ElevenLabs (45 voices), Qualtrics (authenticated), Wondercraft, Kling
- **PRD expanded**: 80 FRs (was 70). Added FR71-FR80 for Source Wrangling + Run Mode Management
- **New stories**: Story 2.6 (Run Mode Management), Story 3.7 (Source Wrangler — Notion + Box)

### Party Mode Decisions (March 26, 2026 — Pre-Story 2.1 Session)

**Three new capabilities agreed upon:**

1. **Notion + Box Drive Integration** — Notion added as Tier 1 tool (API + MCP). Box Drive added as local filesystem source. Both feed a "source wrangler" capability for pulling course development notes into production context. Notion also supports write-back (feedback, readiness assessments). Story 3.7 created.

2. **Run Mode Management (Ad-Hoc / Default)** — Binary ad-hoc/default mode switch for the Master Orchestrator. Ad-hoc mode suppresses state tracking and routes assets to scratch/staging. QA always runs. Future evolution to per-level modality matrix (course/module/lesson/asset × default/write-only/read-only/ad-hoc) deferred until ad-hoc is reliable. Story 2.6 created.

3. **Source Wrangler** — New architectural component. Start as a skill (SKILL.md), may evolve to dedicated agent. Pulls from Notion API + Box Drive local path. The orchestrator delegates to it for production context enrichment. Includes NotionClient in `scripts/api_clients/`.

**Architecture decision**: Ad-hoc switch is a gate on the state management layer, not on agents. Agents behave identically in both modes. The infrastructure handles routing (assets → scratch, state writes → suppressed).

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
- `bmad-create-story` — create Story 2.1 (Master Orchestrator Agent)
- `bmad-agent-builder` — six-phase discovery for master orchestrator .md
- `bmad-dev-story` — implement Story 2.1

### API Keys
- `.env` has live keys for: Gamma, ElevenLabs, Canvas, Qualtrics, Botpress, Wondercraft, Kling
- `.env` is gitignored; `.env.example` is the safe template
- `.cursor/mcp.json` uses `scripts/run_mcp_from_env.cjs` to load keys at runtime (no literal secrets in config)

### Agent Creation Process (Epic 2+ pattern)
For every story that creates a custom agent via `bmad-agent-builder`:
1. **Party Mode coaching** — team (Winston, Mary, John, Sally, Quinn) refines discovery answers with the user
2. **bmad-agent-builder** — six-phase discovery using the refined answers
3. **Skill co-creation** — agent's mastery skill (SKILL.md + references/ + scripts/) built in the same story
4. **Party Mode validation** — team reviews completed agent + skill for accuracy and completeness

**Why coaching matters**: Agent definitions and skill reference docs (parameter catalogs, context optimization templates) require the user's domain expertise (medical education, physician audience) combined with architectural and tool knowledge. The Party Mode team provides the rigor; the user provides the instructional vision.

**Three-layer architecture** (each independently updatable):
- **API clients** (`scripts/api_clients/`) — connectivity, retry, auth (Epic 1, DONE)
- **Skills** (`skills/{tool}/`) — tool expertise, parameter templates, execution code (Epic 3)
- **Agents** (`agents/*.md`) — judgment, decision-making, personality, memory (Epics 2-3)

**Full agent roster**: 13 custom agents planned across Epics 2-9 (see SESSION-HANDOFF.md for complete map).

### Gotchas
- PowerShell doesn't support `&&` chaining — use `;` instead
- `.venv` is set up with Python 3.13 — activate with `.venv\Scripts\activate`
- Run tests with `.venv\Scripts\python -m pytest tests/ -v`
- Cursor MCP `env` field does NOT resolve `${VAR}` from .env files — that's why the wrapper script exists
