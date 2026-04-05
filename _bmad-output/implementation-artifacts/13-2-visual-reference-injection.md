# Story 13.2: Visual Reference Injection in Narration Scripts

**Epic:** 13 — Visual-Aware Irene Pass 2 Scripting
**Status:** backlog
**Sprint key:** `13-2-visual-reference-injection`
**Added:** 2026-04-05
**Depends on:** Story 13.1 (mandatory perception contract)

## Summary

Irene's narration templates produce scripts that explicitly reference specific visual elements perceived on each slide, with a configurable reference count. References are natural language, integrated into narration flow — not bolted-on annotations.

## Goals

1. Add `visual_references_per_slide` parameter to run-constants.yaml (default: 2).
2. Narration explicitly references perceived visual elements (±1 tolerance on count).
3. References are traceable to specific perception artifact entries.
4. Natural language integration — references guide the learner's eye, not annotate.

## Key Files

- `skills/bmad-agent-content-creator/SKILL.md` — Irene narration writing logic
- `skills/bmad-agent-content-creator/references/template-narration-script.md` — narration template
- `state/config/run-constants.yaml` — `visual_references_per_slide` parameter

## Acceptance Criteria

1. `run-constants.yaml` parameter `visual_references_per_slide: int` (default: 2) controls reference count.
2. Narration includes exactly `visual_references_per_slide` explicit references to perceived visual elements (±1 tolerance).
3. References are natural language integrated into narration flow ("As you can see in the comparison chart on the right..." not "Reference 1: comparison chart").
4. Each reference is grounded in a specific element from `perception_artifacts` — traceable.
5. References complement (not duplicate) slide content — narrate the insight, reference the visual.
6. Narration script template updated with `visual_references[]` metadata per segment.
7. Unit tests validate reference count compliance and traceability to perception artifacts.

## Party Mode Consensus (2026-04-05)

- Natural language flow is critical — references should feel like a good lecturer pointing at the screen.
- Default of 2 references per slide balances specificity with narration flow.
