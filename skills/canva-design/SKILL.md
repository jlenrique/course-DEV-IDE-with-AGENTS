---
name: canva-design
description: Canva design guidance skill for manual-tool execution. Use when producing Canva-ready design specifications and editor instructions without API automation.
---

# Canva Design

## Purpose

Provides knowledge-only Canva design guidance for the Canva specialist. This skill documents what Canva can contribute to a production cycle and converts design intent into executable step-by-step instructions for human execution.

## Manual-Tool Contract

- Knowledge-only skill layer.
- No scripts directory and no direct API calls.
- Outputs instruction packs, template recommendations, and import/export checklists.
- Reads style defaults from `state/config/style_guide.yaml` and visual standards from `resources/style-bible/`.
- Configuration precedence: Marcus envelope values override local defaults when both are provided.

## Key Paths

| Path | Purpose |
|---|---|
| ./references/capability-catalog.md | Capability matrix by use case and plan constraints |
| ./references/template-catalog.md | Educational template recommendations and selection heuristics |
| ./references/pptx-import-workflow.md | Gamma PPTX handoff workflow for Canva enhancement |

## Output Contract

Return a structured guidance payload with:
- status: planned | guidance-ready | blocked
- recommended_workflow
- template_recommendations
- step_by_step_instructions
- accessibility_checks
- warnings and blockers

Example payload:

```yaml
status: planned
recommended_workflow: "Template-first infographic build with manual iconography tuning"
template_recommendations:
  - "Learning Objective One-Pager"
step_by_step_instructions:
  - "Select the recommended template family in Canva"
  - "Apply brand palette and typography from style sources"
  - "Populate structured copy and run accessibility checks"
accessibility_checks:
  - "Contrast >= WCAG AA"
  - "Body text >= 16px"
warnings: []
blockers: []
estimated_effort_minutes: 25
proceed_recommendation: proceed
```

## Polling Contract (Marcus)

When Marcus polls Canva contribution options, return:

1. What Canva can contribute for the requested asset.
2. What cannot be automated in this runtime.
3. Recommended manual workflow and expected export set.
