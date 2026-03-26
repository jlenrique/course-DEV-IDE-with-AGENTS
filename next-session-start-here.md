# Next Session Start Here

## Immediate Next Action

**Complete story creation for Epic 1-4 (MVP)** using `bmad-create-epics-and-stories` step-03.

```
# Priority sequence:
1. Complete story creation for Epic 1-4 with acceptance criteria
2. Run sprint planning (bmad-sprint-planning)
3. Begin Epic 1: Create Cursor plugin structure + Python infrastructure
4. Begin Epic 2: Create master orchestrator agent via bmad-agent-builder
```

## Current Status - ALL DOCS RECAST AND HARMONIZED

- **PRD**: ✅ COMPLETE & RECAST (70 FRs, agent .md approach)
- **Architecture**: ✅ COMPLETE & RECAST (BMad Agent + Cursor Plugin patterns)
- **Epic Structure**: ✅ APPROVED & RECAST (10 epics, bmad-agent-builder approach)
- **Strategic Decisions**: ✅ RECAST (BMB module + Cursor plugin development)
- **Project Context**: ✅ HARMONIZED (all docs aligned)
- **Stories**: ⏳ IN PROGRESS (requirements extracted, epic structure approved, story creation next)
- **Sprint Planning**: Not started

## Implementation Approach (Recast & Harmonized)

### Agents
- **Created via**: `bmad-agent-builder` six-phase conversational discovery process
- **Format**: .md files in `agents/` directory following BMad SKILL.md standard
- **Memory**: BMad sidecar pattern at `_bmad/memory/{skillName}-sidecar/`
- **Integration**: Cursor plugin auto-discovery via `.cursor-plugin/plugin.json`

### Skills
- **Format**: SKILL.md directories under `skills/` with `references/` + `scripts/`
- **Purpose**: Tool-specific capabilities bridging agent intelligence to code execution
- **Integration**: Cursor plugin auto-discovery

### Python Infrastructure
- **Purpose**: Supporting code for API clients, state management, file operations
- **Location**: `scripts/` for shared code, `skills/*/scripts/` for tool-specific code
- **Pattern**: Following canvas_api_tools patterns with .env, .venv, requirements.txt

### Cursor Plugin
- **Manifest**: `.cursor-plugin/plugin.json` with auto-discovery configuration
- **MCP**: `.mcp.json` bundled in plugin for tool server definitions
- **Hooks**: `hooks/hooks.json` for event-driven automation
- **Rules**: `rules/*.mdc` for persistent agent behavior guidance

## Hot-Start Context

### Key File Paths
- PRD: `_bmad-output/planning-artifacts/prd.md`
- Architecture: `_bmad-output/planning-artifacts/architecture.md`
- Epics: `_bmad-output/planning-artifacts/epics.md`
- Strategic Decisions: `_bmad-output/strategic-decisions-collaborative-intelligence.md`
- Workflow Status: `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml`
- Sprint Status: `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Key Tools
- `bmad-agent-builder` - Creates custom agents through conversational discovery
- `bmad-create-epics-and-stories` - Story creation workflow (step-03 next)
- `bmad-sprint-planning` - Sprint planning after stories complete

## Branch
- **master** branch

## Next Phase Sequence
1. **Complete story creation** (bmad-create-epics-and-stories step-03)
2. **Sprint planning** (bmad-sprint-planning)
3. **Epic 1**: Cursor plugin structure + Python infrastructure setup
4. **Epic 2**: Master orchestrator agent creation via bmad-agent-builder
5. **Epic 3**: Tool specialist agent creation via bmad-agent-builder
6. **C1M1 MVP validation** through complete production run
