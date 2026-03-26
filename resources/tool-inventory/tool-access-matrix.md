# Tool Universe — Access Matrix

**Last Updated:** March 26, 2026
**Purpose:** Comprehensive inventory of all tools in the collaborative intelligence ecosystem, classifying each by programmatic access method (REST API, MCP server, manual-only).

## Access Classification Summary

| Tool | Category | REST API | MCP Server | Manual Only | Notes |
|------|----------|:--------:|:----------:|:-----------:|-------|
| **Gamma** | Slide Generation | YES | YES (official) | — | API v1.0, Pro+ plans. MCP via `@raydeck/gamma-app-mcp` |
| **ElevenLabs** | Voice/Audio Synthesis | YES | YES (official) | — | REST + WebSocket. Free tier 10k credits/mo. API verified in this repo; MCP deferred because Cursor currently filters its surfaced tools. |
| **Canvas LMS** | LMS Platform | YES | YES (community) | — | REST API v1. MCP via `canvas-mcp-server` (54+ tools) |
| **Qualtrics** | Surveys/Assessments | YES | YES (community) | — | REST API v3. API verified in this repo; MCP exists on GitHub, but is not npm-published and is not active here. |
| **Canva** | Design/Graphics | YES | YES (official) | — | Connect API. Official remote MCP exists, but Cursor OAuth currently fails with invalid redirect URL in this setup. |
| **Botpress** | Chatbot | YES | — | — | REST API + Bot-as-Code SDK. PAT auth. |
| **Wondercraft** | Audio Podcasting | YES | — | — | REST API. Paid plans. 5 concurrent jobs. |
| **Vyond** | Video Animation | — | — | YES | API requires Enterprise plan. Zapier/Slack integrations are notification-only, not editing. |
| **Kling** | Video Generation | YES | — | — | REST API. Multiple models (O1, 2.6, 3.0). SDKs for Python/Node. |
| **Panopto** | Video Platform | YES | — | — | REST API. Python examples on GitHub. |
| **Descript** | Video/Audio Editing | EARLY ACCESS | — | Partial | API limited to partner import/export workflows. Full editing is manual. |
| **Midjourney** | Image Generation | THIRD-PARTY | — | Partial | No official REST API. Third-party wrappers available (Crazyrouter, Legnext). |
| **CapCut** | Video Editing | UNCLEAR | — | Partial | OpenAPI spec for ChatGPT plugin. Third-party Python wrappers. Official API status unclear. |
| **CourseArc** | Interactive Content/LMS | — | — | YES | LTI 1.3 + SCORM only. No REST API. Contact for API access. |
| **Articulate** | Interactive Authoring | — | — | YES | No content creation API. Desktop app (Storyline) and web app (Rise). JS API for Storyline runtime only. |

## Tier Classification

### Tier 1 — Full Programmatic Access (API + MCP)

These tools have both REST APIs and published MCP servers, enabling the richest agent integration.

#### Gamma
- **API:** REST API v1.0 at `developers.gamma.app`
- **Auth:** `X-API-KEY` header, generated from Settings > API Keys
- **Plan Requirement:** Pro, Ultra, Teams, or Business
- **Key Endpoints:** `POST /v1.0/generations`, `GET /v1.0/generations/{id}`, `GET /v1.0/themes`
- **Rate Limit:** 50 generations/hour (beta)
- **MCP Server:** `npx @raydeck/gamma-app-mcp` (community, well-maintained)
- **MCP Tools:** Generate content, browse themes, organize to folders
- **Billing:** Credit-based per generation

#### ElevenLabs
- **API:** REST API at `api.elevenlabs.io/v1` + WebSocket for streaming
- **Auth:** `xi-api-key` header
- **Plan Requirement:** Free tier available (10k credits/month)
- **Key Endpoints:** `POST /v1/text-to-speech/{voice_id}`, voice listing, voice cloning
- **Models:** Eleven v3 (70+ languages), Multilingual v2, Flash v2.5 (~75ms), Turbo v2.5
- **Output Formats:** MP3, WAV, PCM, Opus, μ-law, A-law
- **MCP Server:** `npx elevenlabs-mcp` (official, by ElevenLabs)
- **MCP Tools:** 24 tools including TTS, music composition, agent creation, audio processing
- **Alternative Install:** `pip install elevenlabs-mcp`
- **Cursor Status in This Repo:** API verified via `scripts/smoke_elevenlabs.mjs`; MCP connects but Cursor filters out surfaced tools because combined server/tool names exceed Cursor's 60-character limit.
- **Recommended Integration Path Here:** Use the REST API / future Python client as the primary programmatic path.

#### Canvas LMS
- **API:** REST API at `{institution}.instructure.com/api/v1`
- **Auth:** OAuth2 access token via Authorization header
- **Docs Migration:** Moving to `developerdocs.instructure.com` (redirects after July 2026)
- **Key Resources:** Courses, modules, pages, assignments, quizzes, enrollments, grades
- **MCP Server:** `npx canvas-mcp-server` (community, 54+ tools, v2.3.0)
- **MCP Alternatives:** `@canvas-mcp/server` (npm), `vishalsachdev/canvas-mcp` (90+ tools, Python)
- **Auth for MCP:** `CANVAS_API_TOKEN` + `CANVAS_DOMAIN` env vars

#### Qualtrics
- **API:** REST API v3 at `api.qualtrics.com`
- **Auth:** `X-API-TOKEN` header
- **Key Endpoints:** Survey CRUD, question management, distribution, response export
- **SDKs:** Python and Java code snippets available
- **MCP Server:** `yrvelez/qualtrics-mcp-server` (community, TypeScript, 53 tools)
- **MCP Domains:** Surveys, questions, blocks, flow, responses, contacts, distributions, webhooks
- **Cursor Status in This Repo:** REST API verified via `scripts/smoke_qualtrics.mjs`; MCP not active because the server is GitHub-only and needs a local build step instead of direct npm execution.
- **Recommended Integration Path Here:** Use the REST API / future Python client as the primary programmatic path.

#### Canva
- **API:** Connect API at `api.canva.com/rest/v1`
- **Auth:** OAuth2 with `design:content:write` scope
- **Key Endpoints:** Create/get/list/export designs, asset management
- **Rate Limit:** 20 requests/minute per user
- **MCP Server:** Remote at `https://mcp.canva.com/mcp` (official, by Canva)
- **MCP Tools:** `create_design`, `export_design`, `get_design`, `list_designs`
- **Note:** Some features require paid Canva plan
- **Cursor Status in This Repo:** Connect API remains available, but the remote MCP is not active because Cursor's OAuth redirect URL is rejected by Canva in this setup.

### Tier 2 — API Access Only (No Published MCP)

These tools have REST APIs but no published MCP servers. Agent integration works through Python API clients in `scripts/api_clients/` invoked by skills.

#### Botpress
- **API:** REST API at `api.botpress.cloud`
- **Auth:** Bearer token (Personal Access Token, Bot Token, or Integration Token)
- **Key Endpoints:** `POST /v1/admin/bots` (create), Chat API for messaging
- **SDK:** `@botpress/cli` for bot-as-code development (TypeScript)
- **Note:** Strong developer ecosystem. Could build custom MCP if needed.

#### Wondercraft
- **API:** REST API at `api.wondercraft.ai/v1`
- **Auth:** `X-API-KEY` header
- **Plan Requirement:** Paid plan required
- **Key Endpoints:** `/podcast` (AI-scripted), `/podcast/scripted` (custom), `/podcast/convo-mode/user-scripted`
- **Limits:** 5 concurrent jobs (contact support to increase), ~10 credits/min generated
- **Note:** Async job-based — submit, poll for completion.

#### Kling
- **API:** REST API at `klingapi.com`
- **Auth:** API key (Bearer token)
- **Models:** Kling O1, 2.6 Pro/Standard, 2.5 Turbo, 3.0
- **SDKs:** `kling-api` (Python), `@kling-api/sdk` (Node.js)
- **Features:** Text-to-video, image-to-video, lip-sync, motion control
- **Free Tier:** $1 in free credits on signup

#### Panopto
- **API:** REST API at `{instance}/api/v1/`
- **Auth:** OAuth2
- **Features:** Video import, search, metadata, recording control, user/group management, analytics
- **Resources:** Python examples on GitHub (`Panopto/panopto-api-python-examples`)
- **Limitation:** Quiz results and detailed viewing events not available via API

### Tier 3 — Limited/Early Access API

These tools have partial programmatic access. Integration may be possible but with significant constraints.

#### Descript
- **API:** Early Access Public API at `docs.descriptapi.com`
- **Auth:** Bearer token from Descript Settings
- **Scope:** Limited to partner import/export workflows — NOT full editing control
- **Key Endpoints:** Import media, AI agent edits, job management
- **Reality:** Best used for "handoff" workflows — send media in, get edited media out
- **Recommendation:** Treat as semi-manual; use API for import/export, manual for editing

#### Midjourney
- **API:** NO official REST API (Discord-based interface)
- **Third-Party Options:** Crazyrouter, Legnext, ImagineAPI.dev provide REST wrappers
- **Auth:** Varies by third-party provider (Bearer tokens)
- **Features via Third-Party:** Text-to-image, upscale, variations, image-to-image
- **Recommendation:** Evaluate third-party options for reliability; plan for possible manual fallback

#### CapCut
- **API:** Official status unclear. OpenAPI spec exists for ChatGPT plugin.
- **Third-Party:** Community Python wrappers exist for batch editing via draft file parsing
- **Recommendation:** Treat as manual-primary; explore ChatGPT plugin integration as alternative

### Tier 4 — Manual Only

These tools have no programmatic access. Agent interaction must be through conversational guidance and manual user execution.

#### Vyond
- **Integration:** Zapier, Slack, Google Workspace (notification/sharing only — no editing control)
- **API:** REST API exists but requires Enterprise plan (not available on paid non-Enterprise plans)
- **Agent Strategy:** Agent provides detailed animation storyboards, scene descriptions, character specifications, and timing; user builds in Vyond's web editor. Agent can coordinate the exported video with other production assets downstream.

#### CourseArc
- **Integration:** LTI 1.3 for Canvas embedding, SCORM 1.2 for export
- **API:** None publicly available. Contact CourseArc for enterprise API access.
- **Agent Strategy:** Agent provides content structure and instructions; user manually creates in CourseArc web interface. Agent can validate LTI embed URLs after manual creation.

#### Articulate (Storyline 360 / Rise 360)
- **Integration:** SCORM/xAPI export for LMS delivery
- **API:** No content creation API. Advanced JavaScript API (early access) for Storyline runtime interactions only.
- **Agent Strategy:** Agent provides detailed interaction specifications and storyboards; user builds in Storyline/Rise. Agent can review exported SCORM packages.

## MCP Configuration Reference

### Ready-to-Use MCP Configurations for `.mcp.json`

**Live repo default:** this repository currently keeps the active MCP set conservative and only enables the servers verified to work well in Cursor for this setup: `gamma` and `canvas-lms`. Additional MCP-capable platforms remain documented here but are deferred until their Cursor-specific issues are resolved.

```json
{
  "mcpServers": {
    "gamma": {
      "command": "node",
      "args": ["scripts/run_mcp_from_env.cjs", "gamma"]
    },
    "canvas-lms": {
      "command": "node",
      "args": ["scripts/run_mcp_from_env.cjs", "canvas-lms"]
    }
  }
}
```

**Why the wrapper?** `scripts/run_mcp_from_env.cjs` reads local secrets from `.env` at runtime so `.cursor/mcp.json` and `.mcp.json` can stay safe and versionable without embedding literal API keys.

## Environment Variables Reference

### Required for Tier 1 Tools (API + MCP)

```bash
# Gamma — Slide Generation (Pro+ plan required)
GAMMA_API_KEY=

# ElevenLabs — Voice/Audio Synthesis (free tier available)
ELEVENLABS_API_KEY=

# Canvas LMS — Learning Management System
CANVAS_API_URL=https://your-institution.instructure.com
CANVAS_ACCESS_TOKEN=
CANVAS_DOMAIN=your-institution.instructure.com
CANVAS_SUBACCOUNT_ID=

# Qualtrics — Surveys/Assessments
QUALTRICS_API_TOKEN=
QUALTRICS_BASE_URL=https://yourdatacenter.qualtrics.com
QUALTRICS_DATA_CENTER_ID=
QUALTRICS_OWNER_ID=
QUALTRICS_ORGANIZATION_ID=
QUALTRICS_USERNAME=

# Canva — Design/Graphics (OAuth — handled by MCP server)
# No API key needed; Canva MCP uses OAuth via browser
```

### Required for Tier 2 Tools (API Only)

```bash
# Botpress — Chatbot
BOTPRESS_API_KEY=
BOTPRESS_BOT_ID=

# Wondercraft — Audio Podcasting (paid plan required)
WONDERCRAFT_API_KEY=

# Kling — Video Generation
KLING_ACCESS_KEY=
KLING_SECRET_KEY=

# Panopto — Video Platform
PANOPTO_BASE_URL=https://your-instance.hosted.panopto.com
PANOPTO_CLIENT_ID=
PANOPTO_CLIENT_SECRET=
```

### Optional for Tier 3 Tools (Limited API)

```bash
# Descript — Video/Audio Editing (early access API)
DESCRIPT_API_KEY=

# Midjourney — Image Generation (third-party wrapper)
MIDJOURNEY_API_KEY=

# CapCut — Video Editing (official API status unclear)
CAPCUT_API_KEY=
```

### No API Keys Needed (Tier 4 — Manual Only)

```
# CourseArc — LTI 1.3 / SCORM only (no API)
# Articulate — Desktop/web authoring (no API)
```

## Utility MCPs (Agent Infrastructure)

These MCPs are not tool-specific but provide cross-cutting capabilities that benefit all agents.

### Configured at Project Level (`.mcp.json`)

| MCP | Package | Purpose |
|-----|---------|---------|
| **Fetch** | `mcp-fetch-server` | Documented utility MCP, but not currently active in the live repo config because the Cursor integration surfaced no usable tools in this setup. |
| **Brave Search** | `npx @modelcontextprotocol/server-brave-search` | Useful optional search MCP. Documented, but not active by default until a key is added and verified in this setup. |

### Configured at User Level (Already Available)

| MCP | Purpose |
|-----|---------|
| **Playwright** | Browser automation — navigate, click, fill forms, screenshot. Useful for testing CourseArc/Articulate manual workflows and web-based tool validation. |
| **Ref** | Documentation search and URL reading. Search library/framework docs and read web pages for reference. |

### Utility MCP Environment Variables

```bash
# Brave Search (free tier: 2,000 queries/month)
# Get key at: https://api.search.brave.com/app/keys
BRAVE_API_KEY=

# Fetch MCP — no API key needed when re-enabled
```

## Pre-Flight Check Guidance

Future Story 1.4 should use this repo's current validation hierarchy:

| Tool State | Preferred Pre-Flight Method |
|------------|-----------------------------|
| **Cursor-verified MCP** | Check MCP connectivity and tool discovery first |
| **API-verified, MCP-deferred** | Run focused smoke scripts or read-only API probes |
| **Manual-only** | Report as manual workflow, not failure |
| **Blocked/deferred MCP** | Report blocker and route to API or manual path |

### Current Recommended Mapping

| Tool | Pre-Flight Method |
|------|-------------------|
| Gamma | MCP check + optional API heartbeat |
| Canvas LMS | MCP check + optional API heartbeat |
| ElevenLabs | `scripts/smoke_elevenlabs.mjs` |
| Qualtrics | `scripts/smoke_qualtrics.mjs` |
| Wondercraft | `scripts/heartbeat_check.mjs` |
| Kling | config presence + future JWT client check |
| Canva | report OAuth redirect blocker in current Cursor setup |
| Vyond / CourseArc / Articulate | report manual workflow |
