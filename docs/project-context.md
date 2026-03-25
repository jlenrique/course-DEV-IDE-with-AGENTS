# Project Context: Multi-Agent Course Content Production System

**Project Name:** course-DEV-IDE-with-AGENTS  
**Phase:** Ideation → Planning (BMad Method Phase 1-analysis completed)  
**Architecture Status:** Conceptual  
**Implementation Status:** Environment scaffolded, awaiting PRD/Architecture

## Purpose

Build a repository and workflow system optimized for **multi-agent, human-in-the-loop creation** of online course content, supporting branching content paths (presentations, assessments, discussions, modules) with explicit checkpoints, governance, and delivery to platforms like Canvas and CourseArc.

## Key Decisions From Brainstorming

### Agent Architecture (Confirmed)
- **One custom Producer/Orchestrator agent** (BMad Builder v1 when stable)
- **Custom specialist skills** for bootstrap, preflight, compliance gates, path routing, tool-specific prompts, publishing
- **Reuse default BMad agents** for writing, editing, review, documentation (CIS, Core, BMM)

### Operational Model (Confirmed)  
- **Run presets**: `explore`, `draft`, `production`, `regulated` with parameter overrides (P9-P13)
- **Asset-lesson pairing invariant**: every educational artifact paired with instructional context/lesson plan
- **Tool capability registry**: structured inventory drives routing and prompt generation per tool
- **HIL gates**: human checkpoints at every stage, with rubrics and signoff tracking

### Repository Contract (Confirmed)
```
orchestrator/     # Producer agent + run presets + schemas
skills/           # Custom route/generate/publish/compliance skills  
resources/        # source materials, exemplars, policies, rubrics, tool-inventory, templates
workflows/        # master-workflow.md + paths/ (presentation.md, assessment.md, etc.)
runs/             # YYYY/run-<id>/ with manifests, checkpoints, artifacts, approvals, logs
releases/         # <course-slug>/<asset-id>/ with release manifests + final artifacts
```

## Current State

- [x] Repository scaffolded with directory structure, .env.example, content standards  
- [x] BMad Method installed (BMM, Core, CIS modules)
- [x] Brainstorming session completed through morphological analysis (5 high-priority parameter combinations identified from real course content)
- [ ] Complete brainstorming (Phases 2-4): pattern recognition, requirement refinement, action planning
- [ ] Generate PRD (bmad-create-prd) incorporating brainstorming outputs
- [ ] Create architecture (bmad-create-architecture) 
- [ ] Generate epics/stories (bmad-create-epics-and-stories)
- [ ] Sprint planning and implementation

## Next Session Priority

Continue brainstorming progression: **Phase 2 (Mind Mapping)** to cluster requirements into epic boundaries, then complete remaining phases before transitioning to formal BMad Method planning artifacts.

## Key Files

- `_bmad-output/brainstorming/brainstorming-session-20260325-150802.md` - Current brainstorming session state
- `docs/agent-environment.md` - Agent/MCP guidance  
- `docs/workflow/human-in-the-loop.md` - HIL procedure
- `.cursor/rules/course-content-agents.mdc` - Cursor agent rules