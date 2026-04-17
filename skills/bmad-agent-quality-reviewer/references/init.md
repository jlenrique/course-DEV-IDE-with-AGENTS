# First-Run Setup for Quinn-R

Welcome! Setting up the Quality Guardian workspace.

## Memory Location

Creating `{project-root}/_bmad/memory/quinn-r-sidecar/` for persistent memory.

## Initial Structure

Creating:
- `index.md` — active review context, calibration summary, recurring issue patterns
- `patterns.md` — specialist quality patterns, human calibration, effective feedback, accessibility catalog
- `chronology.md` — review history, human review outcomes, calibration events
- `access-boundaries.md` — read/write/deny zones for Quinn-R

## Environment Check

Verify these paths exist and are accessible:
- `resources/style-bible/` — primary quality rubric (brand, voice, accessibility)
- `state/config/course_context.yaml` — learning objectives for alignment checks
- `state/config/tool_policies.yaml` — quality thresholds and enforcement rules
- `state/runtime/coordination.db` — SQLite database for quality_gates logging
- `skills/quality-control/` — companion skill with automated checking scripts

If any reference is missing, Quinn-R operates in partial review mode — available dimensions are reviewed, unavailable dimensions are flagged as SKIPPED.

## Ready

Setup complete! Quinn-R is ready to validate production outputs.
