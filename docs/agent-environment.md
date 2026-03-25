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

## MCPs (recommended)

Enable in **Cursor Settings → MCP** (and mirror in Claude Code if you use MCP there).

| MCP | Role for this project |
|-----|------------------------|
| **Filesystem / workspace** | Default; agents read and edit under `course-content/`, `config/`, `integrations/`. |
| **Documentation / Ref** (e.g. Ref, built-in fetch) | Look up **Canvas REST** endpoint shapes and CourseArc LTI docs without hallucinating URLs. |
| **Browser automation** (e.g. Playwright) | Optional: preview HTML slides, smoke-test public Canvas pages (respect login and institution policies). |
| **Git** (if available) | Branch per module or per course; PRs as review gates. |

There is no universal “Canvas MCP” in the wild; treat **Canvas as HTTPS + token** via small scripts in `integrations/canvas/` or your existing Python tooling. CourseArc is primarily **LTI 1.3 / SCORM** for delivery into Canvas, not a substitute for Canvas’s content APIs.

## APIs and credentials

- **Canvas**: REST API with access token; store `CANVAS_API_URL` and `CANVAS_ACCESS_TOKEN` in `.env` (see `.env.example`). Use scoped tokens and institution API policies.
- **CourseArc**: Confirm with your account team whether any **content export or REST** access exists beyond the UI; plan on **LTI embedding in Canvas** and/or **SCORM** for delivery workflows.

Secrets stay in `.env` or your password manager; never commit tokens.

## BMad alignment

- **Ideation / requirements**: CIS skills (`bmad-product-brief`, `bmad-brainstorming`, design thinking) or full BMM **PRD → UX → Architecture → Epics**.
- **Build content**: `bmad-quick-dev` or story-driven `bmad-dev-story` once you add sprint artifacts under `_bmad-output/`.
- **Review**: `bmad-editorial-review-prose`, `bmad-review-adversarial-general`, CIS **Presentation** agent for slide narratives.

Use a **fresh chat** per major skill run, as BMad recommends.
