# First-Run Setup for Marcus

Welcome! Setting up the production orchestrator workspace.

## Memory Location

Creating `{project-root}/_bmad/memory/bmad-agent-marcus-sidecar/` for persistent memory.

## Initial Discovery

Before creating the memory structure, gather essential context:

1. **User name** — How should Marcus address you?
2. **Course context** — Is there an existing `state/config/course_context.yaml`? If so, load and confirm the course hierarchy. If not, ask what courses and modules are in scope.
3. **Style bible** — Does `resources/style-bible/` exist? If so, acknowledge. If not, note that production planning will proceed without established brand standards until one is created.
4. **Exemplar library** — Does `resources/exemplars/` exist? If so, scan for available allocation policies and patterns. If not, note that Marcus will build the exemplar library as production runs complete.
5. **Tool availability** — Offer to run `pre-flight-check` to verify which specialist agents and API connections are operational.

## Initial Structure

Creating:
- `index.md` — active production context, user preferences, current mode (defaults to default mode)
- `access-boundaries.md` — read/write/deny zones per `./references/memory-system.md`
- `patterns.md` — empty, will grow as production runs complete
- `chronology.md` — empty, will grow as production history accumulates

## Ready

Setup complete! Marcus is ready to produce. Present the user with a summary of what was found (course context, style bible status, tool availability) and ask what they'd like to produce first.
