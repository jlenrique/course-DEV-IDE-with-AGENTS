# First-Run Setup for Cora

Welcome. Setting up Cora's dev-session orchestration workspace.

## Memory Location

Creating `{project-root}/_bmad/memory/cora-sidecar/` for persistent memory.

## Initial Discovery

Before creating the memory structure, gather essential context:

1. **Operator name** — How should Cora address you? (Likely already in `_bmad/config.user.yaml` as `user_name`; confirm.)
2. **Current branch** — `git branch --show-current`; confirm this is the active dev branch.
3. **Hot-start pair presence** — Do `SESSION-HANDOFF.md` and `next-session-start-here.md` exist at project root? If not, note that Cora will create them at the next session WRAPUP.
4. **Sprint-status snapshot** — Read `_bmad-output/implementation-artifacts/sprint-status.yaml`; confirm Cora can see the current story state.
5. **Structural walk availability** — Confirm `python -m scripts.utilities.structural_walk --workflow standard` runs without error; this is the foundation of Audra's L1 sweep.
6. **Operator preferences** — Ask the operator one time:
   - Preferred harmonization scope default? (full repo / since-handoff / directory-scoped)
   - Pre-closure hook preference? (warn / silent). Default: warn.
   - Paige-routing threshold for prose drift? (paragraph / section / doc). Default: paragraph.

## Initial Structure

Create the four sidecar files per the memory-system.md layout:

- `index.md` — seeded with operator preferences and current session context
- `patterns.md` — empty header; populates as patterns crystallize
- `chronology.md` — first entry: `YYYY-MM-DD HH:MM — Cora initialized.`
- `access-boundaries.md` — copied from template (see `_bmad/memory/cora-sidecar/access-boundaries.md` template content)

Confirm completion with: "Sidecar initialized. Ready when you are."
