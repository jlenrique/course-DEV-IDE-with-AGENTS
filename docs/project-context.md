# Project Context: Multi-Agent Course Content Production System

**Project Name:** course-DEV-IDE-with-AGENTS  
**Phase:** 3-Solutioning (PRD + Architecture COMPLETE, Story Creation IN PROGRESS)  
**Architecture Status:** 10 Comprehensive Epics, 70 FRs, Complete Architecture Document  
**Implementation Status:** Ready for story creation and sprint planning

## Purpose

Build a persistent collaborative intelligence infrastructure for systematically scaling creative expertise in online course content production. A custom master orchestrator agent provides a conversational interface ("general contractor" experience) coordinating specialist agents that manipulate professional media tools through APIs and MCPs while systematically capturing creative decision-making patterns for iterative refinement and reuse.

## Critical Architectural Insight

**Agents are .md files** following BMad patterns - NOT traditional software classes. They are invoked like BMad agents and use skills for tool mastery and code execution. Python code supports agents by providing API clients, state management, file operations, and other capabilities that require programmatic execution.

## Key Decisions From Planning

### Agent Architecture (Confirmed)
- **Custom Master Orchestrator agent** (.md file) as single conversational point of contact
- **Custom specialist agents** (.md files) for tool mastery (Gamma, ElevenLabs, Canvas, etc.)
- **Custom skills** (.md files + supporting code) for tool expertise, parameter intelligence, coordination
- **Reuse existing BMad agents** for writing, editing, review, documentation
- **Python infrastructure** for API clients, state management, MCP integration, file operations

### Conversational Interface (Confirmed)
- Users interact ONLY through conversation with master orchestrator
- Orchestrator manages all system complexity behind conversational abstraction
- Parameter elicitation through conversation with intelligent defaults from style guides
- Human review checkpoints at key creative and quality decision points

### Operational Model (Confirmed)
- **Run presets**: `explore`, `draft`, `production`, `regulated` with parameter overrides
- **Asset-lesson pairing invariant**: every educational artifact paired with instructional context
- **Tool capability registry**: structured inventory drives routing and prompt generation
- **HIL gates**: human checkpoints at every stage with rubrics and signoff tracking
- **Pre-flight checks**: MCP/API connectivity verification + tool documentation scanning
- **Production run reporting**: comprehensive effectiveness analysis with learning capture

### State Management (Confirmed)
- **YAML files**: Course context, style guides, policies (human-readable, git-versioned)
- **SQLite database**: Runtime coordination state, production run tracking (ACID transactions)
- **Learning databases**: Expertise patterns, optimization insights (systematic capture)

### Repository Contract (Confirmed)
```
orchestrator/     # Master orchestrator agent + conversation management
agents/           # Specialist agent .md files
skills/           # Tool mastery skills with supporting code
state/            # YAML configs + SQLite runtime + learning databases
integrations/     # API clients, MCP patterns, tool adapters
quality/          # Automated review + compliance + brand validation
reporting/        # Production intelligence + troubleshooting
tests/            # Unit + integration + orchestration tests
docs/             # Architecture + agent guides + troubleshooting
```

## Current State

- [x] Repository scaffolded with directory structure, .env.example, content standards  
- [x] BMad Method installed (BMM, Core, CIS modules)
- [x] **BRAINSTORMING COMPLETED**: 10 comprehensive epics defined
- [x] **PRD COMPLETED**: 70 FRs across 11 capability domains with enhanced conversational interface
- [x] **ARCHITECTURE COMPLETED**: Hybrid multi-agent + conversational framework validated
- [x] **Strategic Decisions**: Party Mode team review validated approach
- [ ] **Story Creation**: In progress - requirements extracted, epic structure approved
- [ ] Sprint planning and development execution

## Key Files

- `_bmad-output/planning-artifacts/prd.md` - Complete PRD (70 FRs)
- `_bmad-output/planning-artifacts/architecture.md` - Complete architecture document
- `_bmad-output/planning-artifacts/epics.md` - Epic breakdown with requirements inventory
- `_bmad-output/strategic-decisions-collaborative-intelligence.md` - Strategic decisions
- `_bmad-output/brainstorming/brainstorming-session-20260325-150802.md` - Brainstorming session
- `docs/agent-environment.md` - Agent/MCP guidance  
- `docs/workflow/human-in-the-loop.md` - HIL procedure
- `.cursor/rules/course-content-agents.mdc` - Cursor agent rules
