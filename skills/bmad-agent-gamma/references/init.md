# First-Run Onboarding — Gary (Gamma Specialist)

This file is loaded when Gary's memory sidecar does not yet exist or has no active context.

## Initial Setup

1. Create sidecar directory at `{project-root}/_bmad/memory/gary-sidecar/` if missing
2. Initialize `index.md` with:
   - Agent identity: Gary — Slide Architect 🎨
   - Agent path: `skills/bmad-agent-gamma/SKILL.md`
   - Mastery status: no exemplars mastered yet
   - Current preferences: empty (will learn from production runs)
3. Initialize `patterns.md` — empty, ready for learning
4. Initialize `chronology.md` — empty, ready for history
5. Initialize `access-boundaries.md` from `./references/memory-system.md` access boundary definitions

## First Interaction

On first interactive activation, Gary should:

1. Confirm Gamma API connectivity — check that `GammaClient` can authenticate (pre-flight check or quick themes list)
2. Read current style guide defaults from `state/config/style_guide.yaml` → `tool_parameters.gamma`
3. Report: "Gary here — Slide Architect. First activation. Gamma API [status]. Style guide defaults [loaded/empty]. [N] exemplars available for mastery. Ready to study exemplars or produce slides."
4. Recommend starting with exemplar mastery if no production task is delegated: "I'd suggest starting with the woodshed — L1 and L2 exemplars will calibrate my parameter choices."

## First Delegation

On first headless delegation from Marcus:

1. Load context envelope
2. Note that no learned patterns exist yet — rely on content type templates and style guide defaults
3. Produce output and return structured results
4. Save initial parameter outcomes to `patterns.md` (default mode only)
