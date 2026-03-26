# Master Orchestrator — Memory Sidecar

**Agent**: `agents/master-orchestrator.md` (Epic 2)
**Purpose**: Persistent learning context for the conversational orchestrator.

## Planned Files

- `patterns.md` — Learned production patterns, successful workflows, parameter preferences
- `chronology.md` — Production run history and session log
- `access-boundaries.md` — Read: entire project. Write: `state/`, `_bmad/memory/`, `agents/`, `skills/`. Deny: `.env`, `.cursor-plugin/plugin.json`

## Active Context

No production runs yet. This sidecar will be populated when the master orchestrator agent is created in Story 2.1.
