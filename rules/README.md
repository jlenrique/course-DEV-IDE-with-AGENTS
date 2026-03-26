# Rules

Cursor `.mdc` and `.md` rule files for persistent agent behavior guidance. Cursor auto-discovers rule files placed in this directory as part of the plugin system.

**Note:** Cursor also loads rules from `.cursor/rules/` (the IDE's built-in rules location). This directory provides plugin-level rules that are auto-discovered alongside those built-in rules.

## Current Rules

| Rule | Purpose | Location |
|------|---------|----------|
| `course-content-agents.mdc` | Course content authoring with human-in-the-loop and LMS delivery context | `.cursor/rules/` (built-in) |
