# Agent environment (Cursor + Claude Code)

## Repository layout

| Path | Purpose |
|------|---------|
| `course-content/courses/` | Versioned **source** per course (modules, lessons, slide decks as Markdown/Marp/reveal notes, scripts). |
| `course-content/staging/` | **Human-in-the-loop queue**: agent drafts awaiting your approval before promotion to `courses/` or export. |
| `course-content/_templates/` | Reusable outlines (lesson, module, rubric, slide deck skeleton). |
| `config/content-standards.yaml` | Voice, audience, accessibility defaults for agents. |
| `config/platforms.example.yaml` | Template for Canvas/CourseArc endpoints; copy and adapt locally if needed. |
| `integrations/canvas/` | Scripts, small clients, or notes for Canvas REST usage. |
| `integrations/coursearc/` | LTI/SCORM notes, export checklists, any vendor-specific helpers. |
| `scripts/` | One-off or repeatable deploy/publish commands. |
| `docs/` | Workflow and integration reference (this file, `workflow/`). |
| `_bmad/` + `_bmad-output/` | BMad Method artifacts (PRD, architecture, sprint planning) when you use that track. |
| `.cursor/skills/` | Installed agent skills (BMad, CIS, etc.). |
| `skills/` | Custom project skills (woodshed, mastery skills, production-coordination, pre-flight-check). |
| `resources/exemplars/` | Per-tool exemplar libraries for agent skill development and validation. |

## MCPs (project and user-level)

| MCP | Level | Role for this project | Health Check |
|-----|-------|------------------------|--------------|
| **Gamma** | project | Slide/presentation generation (`generate`, `get_themes`, `get_folders`) | Pre-flight: MCP config + API heartbeat |
| **Canvas LMS** | project | Course/module/assignment management (54 tools) | Pre-flight: MCP config + API heartbeat |
| **Notion** | project | Source wrangling — pull course development notes (22 tools) | Pre-flight: API `/v1/users/me` |
| **Ref** | user | `ref_search_documentation` + `ref_read_url` — primary tool for tech-spec-wrangler doc refresh. Critical for woodshed doc refresh cycles before exemplar reproduction. | Pre-flight: verify callable |
| **Playwright** | user | Browser automation — preview slides, render JS-heavy docs, smoke-test pages | Pre-flight: verify responsive |
| **Perplexity (future)** | user | Deep research, working examples, community patterns — extends tech-spec-wrangler | Deferred until API key configured |

There is no universal "Canvas MCP" in the wild; treat **Canvas as HTTPS + token** via small scripts in `integrations/canvas/` or your existing Python tooling. CourseArc is primarily **LTI 1.3 / SCORM** for delivery into Canvas, not a substitute for Canvas's content APIs.

## Shared Skills (available to all agents)

| Skill | Path | Purpose | Status |
|-------|------|---------|--------|
| **Pre-flight check** | `skills/pre-flight-check/` | MCP/API/doc-sources connectivity verification before production runs | Active |
| **Woodshed** | `skills/woodshed/` | Exemplar-driven agent skill development — study, reproduce, compare, reflect, regress (faithful + creative modes) | Active |
| **Production coordination** | `skills/production-coordination/` | Workflow stages, delegation, mode management, style guide | Active |
| **Tech spec wrangler** | `skills/tech-spec-wrangler/` | Tool API doc refresh, research, validation via Ref MCP; ensures agents always have current API knowledge | Planned (Story 3.8) |

## APIs and credentials

- **Canvas**: REST API with access token; store `CANVAS_API_URL` and `CANVAS_ACCESS_TOKEN` in `.env` (see `docs/admin-guide.md`). Use scoped tokens and institution API policies.
- **Gamma**: REST API with X-API-KEY header; store `GAMMA_API_KEY` in `.env`. Pro/Ultra/Teams/Business plan required.
- **ElevenLabs**: REST API with xi-api-key header; store `ELEVENLABS_API_KEY` in `.env`.
- **Qualtrics**: REST API with X-API-TOKEN header; store `QUALTRICS_API_TOKEN` and `QUALTRICS_DATACENTER` in `.env`.
- **CourseArc**: Confirm with your account team whether any **content export or REST** access exists beyond the UI; plan on **LTI embedding in Canvas** and/or **SCORM** for delivery workflows.

Secrets stay in `.env` or your password manager; never commit tokens.

## BMad alignment

- **Ideation / requirements**: CIS skills (`bmad-product-brief`, `bmad-brainstorming`, design thinking) or full BMM **PRD → UX → Architecture → Epics**.
- **Build content**: `bmad-quick-dev` or story-driven `bmad-dev-story` once you add sprint artifacts under `_bmad-output/`.
- **Review**: `bmad-editorial-review-prose`, `bmad-review-adversarial-general`, CIS **Presentation** agent for slide narratives.
- **Agent creation**: `bmad-agent-builder` with Party Mode coaching for specialist agents; `woodshed` skill for exemplar-driven mastery validation.

Use a **fresh chat** per major skill run, as BMad recommends.
