# Project Context: Multi-Agent Course Content Production System

**Project Name:** course-DEV-IDE-with-AGENTS  
**Phase:** 4-Implementation (PRD + Architecture COMPLETE, Epic 1 DONE, Epic 2 DONE, Epic 3 IN PROGRESS)
**Architecture Status:** 10 Epics, 80 FRs, Complete Architecture - Recast for BMad Agent + Cursor Plugin Approach
**Implementation Status:** Epic 1 complete (11/11 stories, 117 tests). Epic 2 complete (6/6 stories, 55 tests). Epic 3 in progress (Story 3.1 DONE — Gary, Gamma specialist, 29 new tests).

## Purpose

Build a persistent collaborative intelligence infrastructure for systematically scaling creative expertise in online course content production. A custom master orchestrator agent (created via `bmad-agent-builder`) provides a conversational interface ("general contractor" experience) coordinating specialist agents that manipulate professional media tools through skills backed by Python scripts for API calls, while systematically capturing creative decision-making patterns in BMad memory sidecars for iterative refinement and reuse.

## Critical Implementation Model

**Agents are .md files** created through `bmad-agent-builder` six-phase conversational discovery process, following BMad SKILL.md standard. They live in `agents/` directory and are auto-discovered by Cursor's plugin system.

**Skills are SKILL.md directories** providing tool-specific capabilities with progressive disclosure (`references/`), Python code execution (`scripts/`), and output templates (`assets/`).

**Python infrastructure** provides supporting code for API clients, state management, and file operations - invoked from agent skills when code execution is required.

**Cursor plugin packaging** via `.cursor-plugin/plugin.json` enables native IDE integration with auto-discovery of agents, skills, rules, commands, hooks, and MCP servers.

**BMad memory sidecars** provide persistent agent learning through `_bmad/memory/{skillName}-sidecar/` with index.md (context), patterns.md (learned preferences), chronology.md (history), and access-boundaries.md (scope control).

## Key Decisions From Planning

### Agent Architecture (Confirmed)
- **Custom Master Orchestrator agent** (.md file created via `bmad-agent-builder`) as single conversational point of contact
- **Custom specialist agents** (.md files created via `bmad-agent-builder`) for tool mastery (Gamma, ElevenLabs, Canvas, etc.)
- **Custom skills** (SKILL.md + references/ + scripts/) for tool expertise, parameter intelligence, coordination
- **Reuse existing BMad agents** for writing, editing, review, documentation
- **Python infrastructure** in scripts/ for API clients, state management, file operations

### Cursor Plugin Architecture (Confirmed)
- `.cursor-plugin/plugin.json` manifest with auto-discovery of agents/, skills/, rules/
- `.mcp.json` for tool server definitions bundled in plugin
- `hooks/hooks.json` for event-driven automation (sessionStart → pre-flight, afterFileEdit → quality, sessionEnd → reporting)
- `rules/*.mdc` for persistent agent behavior guidance
- `commands/*.md` for agent-executable actions

### BMad Memory System (Confirmed)
- Agent memory sidecars at `_bmad/memory/{skillName}-sidecar/`
- `index.md` for essential context loaded on activation
- `patterns.md` for systematic expertise crystallization (append-only, periodically condensed)
- `chronology.md` for session and production run history
- `access-boundaries.md` for agent scope control (read/write/deny zones)

### Operational Model (Confirmed)
- **Run presets**: `explore`, `draft`, `production`, `regulated` with parameter overrides
- **Asset-lesson pairing invariant**: every educational artifact paired with instructional context
- **Tool parameter mastery**: Specialty agents master complete API parameter spaces, preferences stored in style guide YAML
- **Exemplar-driven development**: Each specialist agent proves competence by reproducing real exemplar artifacts programmatically via API/MCP, scored against a structured rubric. Exemplars serve as both design aids and acceptance tests. See `resources/exemplars/_shared/woodshed-workflow.md`
- **Woodshed skill**: Shared skill (`skills/woodshed/`) provides study → reproduce → compare → reflect → register workflow with detailed run logging, downloaded artifact retention for every attempt (pass/fail), mandatory reflection between failed attempts, and circuit breaker give-up protocol (3/session, 7 total)
- **Two woodshed modes**: Faithful (exact reproduction proving tool control) must be mastered before Creative (enhanced reproduction proving creative judgment) is unlocked per exemplar
- **Progressive mastery**: L1-L4 single artifacts → L5 multi-artifact sets. L-levels with dot extensions. Levels provisional — agents may propose changes. Regression runs ensure mastered exemplars stay mastered
- **Export and download**: All reproductions must download production-quality artifacts (PNG for production, PDF for review, PPTX for editing, MP3 for audio) — screenshots supplementary only
- **Evaluator design requirements** (from Story 3.1): Guide the tool's intelligence (never suppress), extract and compare actual output (not just process compliance), score on content coverage (not exact match), use cheap quality signals per medium, separate woodshed training from production QA, capture know-how from user checkpoint reviews. See `skills/woodshed/SKILL.md` for full reference
- **HIL gates**: human checkpoints at every stage with rubrics and signoff tracking
- **Pre-flight checks**: Hook-driven MCP/API connectivity verification + tool documentation scanning
- **Production run reporting**: Comprehensive effectiveness analysis with learning capture in agent memory

### State Management (Confirmed)
- **YAML files**: Course context, style guides, policies (human-readable, git-versioned) in `state/config/`
- **SQLite database**: Runtime coordination state, production run tracking in `state/runtime/`
- **BMad memory sidecars**: Agent learning, expertise patterns, session history in `_bmad/memory/`

### Repository Contract (Confirmed)
```
.cursor-plugin/   # Cursor plugin manifest
agents/           # Custom agent .md files (auto-discovered)
skills/           # SKILL.md directories with references/ + scripts/ (auto-discovered)
  woodshed/       # Shared exemplar mastery skill (study, reproduce, compare, regress)
rules/            # .mdc rules files for agent guidance
hooks/            # Event-driven automation triggers
commands/         # Agent-executable command files
state/            # YAML configs + SQLite runtime
_bmad/memory/     # Agent memory sidecars for persistent learning
scripts/          # Shared Python infrastructure (API clients, utilities)
tests/            # Unit + integration tests
docs/             # Architecture + agent guides + troubleshooting
resources/
  exemplars/      # Per-tool exemplar libraries with _catalog.yaml, briefs, source, reproductions
    _shared/      # Comparison rubric template, woodshed workflow protocol
    gamma/        # Gamma exemplars (slides/presentations)
    elevenlabs/   # ElevenLabs exemplars (audio/voiceover)
    canvas/       # Canvas exemplars (LMS deployment)
    qualtrics/    # Qualtrics exemplars (surveys/assessments)
    canva/        # Canva exemplars (visual design)
  style-bible/    # Authoritative brand reference
  tool-inventory/ # Tool access matrix
```

## Tool Universe (Researched March 26, 2026)

17 tools classified by programmatic access. Full details in `resources/tool-inventory/tool-access-matrix.md`.

| Tier | Tools | Access |
|------|-------|--------|
| **Tier 1: API + MCP** | Gamma, ElevenLabs, Canvas LMS, Qualtrics, Canva, Notion | Platform capability: REST API and published MCP server |
| **Tier 2: API Only** | Botpress, Wondercraft, Kling, Panopto | REST API, no MCP server |
| **Tier 3: Limited API** | Descript, Midjourney, CapCut | Early access / third-party only |
| **Tier 4: Manual Only** | Vyond, CourseArc, Articulate (Storyline/Rise) | No usable programmatic access for this repo setup |
| **Local FS** | Box Drive | Local filesystem via desktop sync client, no API needed |

- **Live Cursor-verified MCP servers** in `.mcp.json` / `.cursor/mcp.json`: Gamma, Canvas LMS
- **API-verified but MCP-deferred platforms**: ElevenLabs, Qualtrics
- **Documented but currently deferred MCPs**: ElevenLabs (Cursor tool-name filtering), Canva (OAuth redirect rejection), Qualtrics (GitHub-only build step), Fetch (no usable surfaced tools in this setup), Brave Search (not enabled by default)
- **User-level MCPs** already available: Playwright (browser automation), Ref (doc search/reading)
- **API keys templated** in `.env.example`: All Tier 1-3 tools with documentation links
- **Manual tools** require agent-guided workflows where agents provide specs and users execute in tool UI

## Current State

- [x] Repository scaffolded with directory structure, .env.example, content standards  
- [x] BMad Method installed (BMM, Core, CIS modules)
- [x] **BRAINSTORMING COMPLETED**: 10 comprehensive epics defined
- [x] **PRD COMPLETED**: 70 FRs across 11 capability domains (recast for agent .md approach)
- [x] **ARCHITECTURE COMPLETED**: BMad Agent + Cursor Plugin architecture validated (recast)
- [x] **EPICS RECAST**: All 10 epics updated to reflect bmad-agent-builder creation approach
- [x] **Strategic Decisions**: Party Mode team validated and recast for agent .md patterns
- [x] **STORY CREATION COMPLETED**: 31 stories across 10 epics, 100% FR coverage validated
- [x] **API-FIRST SEQUENCING**: API/MCP clients (Gamma, ElevenLabs, Canvas) built in Epic 1 before agent creation
- [x] **TOOL UNIVERSE AUDIT**: 15 tools researched and classified (Tier 1-4), MCP servers configured, .env.example expanded
- [x] **EPIC 1 COMPLETE**: All 11 stories implemented, tested with live APIs, validated by Party Mode review team
- [x] **STORY 1.1**: Cursor plugin foundation — plugin.json, .mcp.json, hooks, directory structure
- [x] **STORY 1.2**: Python infrastructure — BaseAPIClient with retry/pagination/binary, utilities, venv
- [x] **STORY 1.3**: State management — SQLite (3 tables), YAML configs (3 files), BMad memory sidecars (5 agents)
- [x] **STORY 1.4**: Pre-flight check skill — SKILL.md + Python runner + doc scanner + 3 reference docs
- [x] **STORIES 1.5-1.11**: Testing framework + 5 full-featured API clients (Gamma, ElevenLabs, Canvas, Qualtrics, Panopto) + Canva MCP config
- [x] **LIVE API VALIDATION**: 117 tests pass against real services (Gamma, ElevenLabs, Canvas, Qualtrics), 3 skipped (Panopto — no creds)
- [x] **FR EXPANSION (Party Mode)**: 10 new FRs (FR71-FR80) added for Source Wrangling + Run Mode Management
- [x] **TOOLS EXPANSION**: Notion (API + MCP, source wrangling) and Box Drive (local FS) added to tool universe (17 tools total)
- [x] **SOURCE WRANGLER**: New architectural component for pulling reference materials from Notion/Box into production context; agent vs. skill design decision deferred to story creation
- [x] **AD-HOC MODE**: Binary ad-hoc/default mode switch for Master Orchestrator; ad-hoc routes assets to scratch/staging, suppresses state tracking; QA always runs; future per-level modality matrix deferred
- [x] **STORY 2.1 (Marcus Orchestrator)**: Agent built via bmad-agent-builder (6-phase discovery with Party Mode coaching), quality scan passed (0 critical), 12 interaction test scenarios passed, Party Mode team validation complete. 13 files: SKILL.md + 8 references + 2 scripts + 2 test files. Memory sidecar active with 4 files. First production plan staged (C1-M1-P2S1-VID-001).
- [x] **EPIC 2 COMPLETE**: Stories 2.2–2.6 all done. Production-coordination skill (4 scripts, 4 refs, 40 tests). Marcus references updated for workflow management, delegation, parameter intelligence, pre-flight, and mode management.
- [x] **EXEMPLAR-DRIVEN DEVELOPMENT**: Woodshed skill created (`skills/woodshed/`), exemplar library scaffolded (`resources/exemplars/` per tool), comparison rubric, run logging, reflection protocol, circuit breaker, two-mode woodshed (faithful + creative), doc refresh protocol, and L-level difficulty system all in place. 5 Gamma exemplars provided (L1-L4.2). Smoke test validated: Gamma API produces single-card output, PDF export/download works (205KB), 5 credits/card. GammaClient needs parameter name updates (inputText, textMode, exportAs). Epic 3 stories updated with exemplar reproduction as acceptance criteria.
- [ ] Epic 3: Core Tool Specialist Agents & Mastery Skills (8 stories — Story 3.1 Gary/Gamma DONE, Story 3.8 Tech Spec Wrangler added)

## Key Files

- `_bmad-output/planning-artifacts/prd.md` - Complete PRD (70 FRs, recast)
- `_bmad-output/planning-artifacts/architecture.md` - Complete architecture (recast)
- `_bmad-output/planning-artifacts/epics.md` - Epic breakdown with requirements (recast)
- `_bmad-output/strategic-decisions-collaborative-intelligence.md` - Strategic decisions
- `_bmad-output/brainstorming/brainstorming-session-20260325-150802.md` - Brainstorming session
- `_bmad-output/brainstorming/party-mode-coaching-marcus-orchestrator.md` - Marcus coaching doc
- `skills/bmad-agent-marcus/SKILL.md` - **Marcus orchestrator agent (Story 2.1 DONE)**
- `skills/reports/bmad-agent-marcus/quality-scan/2026-03-26_152243/quality-report.md` - Marcus quality scan
- `tests/agents/bmad-agent-marcus/interaction-test-guide.md` - Marcus interaction tests
- `resources/tool-inventory/tool-access-matrix.md` - **Tool universe access matrix (17 tools)**
- `scripts/heartbeat_check.mjs` - Baseline read-only API heartbeat across configured tools
- `scripts/smoke_elevenlabs.mjs` - Focused ElevenLabs API smoke check
- `scripts/smoke_qualtrics.mjs` - Focused Qualtrics API smoke check
- `skills/woodshed/SKILL.md` - **Shared exemplar mastery skill (study, reproduce, compare, regress)**
- `resources/exemplars/_shared/woodshed-workflow.md` - **Complete woodshed workflow protocol (logging, reflection, circuit breaker)**
- `resources/exemplars/_shared/comparison-rubric-template.md` - **Rubric for scoring exemplar reproductions**
- `resources/exemplars/gamma/_catalog.yaml` - **Gamma exemplar registry**
- `docs/agent-environment.md` - Agent/MCP guidance  
- `docs/workflow/human-in-the-loop.md` - HIL procedure
- `.cursor/rules/course-content-agents.mdc` - Cursor agent rules
