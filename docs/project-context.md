# Project Context: Multi-Agent Course Content Production System

**Project Name:** course-DEV-IDE-with-AGENTS  
**Phase:** 3-Solutioning (PRD + Architecture COMPLETE, Story Creation IN PROGRESS)  
**Architecture Status:** 10 Epics, 70 FRs, Complete Architecture - Recast for BMad Agent + Cursor Plugin Approach  
**Implementation Status:** Ready for story creation and sprint planning

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
rules/            # .mdc rules files for agent guidance
hooks/            # Event-driven automation triggers
commands/         # Agent-executable command files
state/            # YAML configs + SQLite runtime
_bmad/memory/     # Agent memory sidecars for persistent learning
scripts/          # Shared Python infrastructure (API clients, utilities)
tests/            # Unit + integration tests
docs/             # Architecture + agent guides + troubleshooting
resources/        # Exemplars, style bible, tool inventory
```

## Current State

- [x] Repository scaffolded with directory structure, .env.example, content standards  
- [x] BMad Method installed (BMM, Core, CIS modules)
- [x] **BRAINSTORMING COMPLETED**: 10 comprehensive epics defined
- [x] **PRD COMPLETED**: 70 FRs across 11 capability domains (recast for agent .md approach)
- [x] **ARCHITECTURE COMPLETED**: BMad Agent + Cursor Plugin architecture validated (recast)
- [x] **EPICS RECAST**: All 10 epics updated to reflect bmad-agent-builder creation approach
- [x] **Strategic Decisions**: Party Mode team validated and recast for agent .md patterns
- [ ] **Story Creation**: In progress - requirements extracted, epic structure approved
- [ ] Sprint planning and development execution

## Key Files

- `_bmad-output/planning-artifacts/prd.md` - Complete PRD (70 FRs, recast)
- `_bmad-output/planning-artifacts/architecture.md` - Complete architecture (recast)
- `_bmad-output/planning-artifacts/epics.md` - Epic breakdown with requirements (recast)
- `_bmad-output/strategic-decisions-collaborative-intelligence.md` - Strategic decisions
- `_bmad-output/brainstorming/brainstorming-session-20260325-150802.md` - Brainstorming session
- `docs/agent-environment.md` - Agent/MCP guidance  
- `docs/workflow/human-in-the-loop.md` - HIL procedure
- `.cursor/rules/course-content-agents.mdc` - Cursor agent rules
