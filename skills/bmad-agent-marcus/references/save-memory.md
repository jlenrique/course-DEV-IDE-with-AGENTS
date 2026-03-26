# Save Memory

Immediately persist the current session context to the memory sidecar at `{project-root}/_bmad/memory/bmad-agent-marcus-sidecar/`.

## Process

Update `index.md` with current session context: active production run, progress state, outstanding tasks, user preferences, and next steps. Checkpoint `patterns.md` and `chronology.md` if significant changes occurred during this session.

**Mode-aware:** In ad-hoc mode, only update the transient ad-hoc session section of `index.md`. Do not write to `patterns.md` or `chronology.md`.

## Output

Confirm save with brief summary: "Memory saved. [brief summary of what was updated]"
