# Story 14.1: Motion Workflow Design & Contract Specification

**Epic:** 14 — Motion-Enhanced Presentation Workflow
**Status:** done
**Sprint key:** `14-1-motion-workflow-design`
**Added:** 2026-04-05
**Validated:** 2026-04-05
**Depends on:** Epic 13 (hard — visual reference injection mechanism). Extends architecture doc and agent contracts.

## Summary

Define the motion-enhanced workflow variant: stages, gates, agent roles, manifest extensions, and orchestration contract. This is a design-first story — the workflow document is the deliverable.

## Goals

1. Formal workflow design document specifying the motion-enhanced pipeline.
2. HIL Gate 2M (Motion Decision Point) defined.
3. HIL Motion Gate defined (user reviews motion assets before Irene).
4. Agent role matrix updated for motion routing.
5. Architecture doc updated with motion pipeline stage diagram.

## Pipeline Architecture

```
Irene Pass 1 → Gary slides → [HIL Gate 2] → [HIL Gate 2M: Motion Designation] →
  +-- Static slides: proceed directly
  +-- Video (Kira): generate clip → download MP4
  +-- Animation (manual): generate guidance → user creates → user imports
→ [HIL Motion Gate: user reviews motion assets] →
→ Irene Pass 2 (perceives slides + motion assets, writes visual-aware narration) →
→ ElevenLabs → Compositor (assembly guide includes motion placement)
```

## Key Files

- `_bmad-output/planning-artifacts/` — new motion workflow design document
- `_bmad-output/planning-artifacts/architecture.md` — pipeline stage diagram update
- `skills/bmad-agent-marcus/SKILL.md` — Marcus workflow variant logic
- `state/config/run-constants.yaml` — `motion_enabled`, `motion_budget`

## Acceptance Criteria

1. Workflow design document exists in `_bmad-output/planning-artifacts/` specifying:
   - Motion-enhanced pipeline stages (Gate 2 → Gate 2M → Kira/manual → Motion Gate → Irene Pass 2)
   - Motion Decision Point (HIL Gate 2M) as a new stage between Gate 2 and Irene Pass 2
   - HIL Motion Gate: user reviews Kira clips and imported animations before Irene
   - Agent role matrix: Marcus orchestrates motion routing, Kira generates video, Vyond specialist generates animation guidance
   - Segment manifest schema extensions (motion fields)
   - Run-constants.yaml extensions: `motion_enabled: boolean`, `motion_budget: {max_credits, model_preference}`
   - Workflow variant selection logic in Marcus
2. Architecture doc updated with motion pipeline stage diagram.
3. Party Mode team consensus recorded on the design.

## Party Mode Consensus (2026-04-05)

- Gate 2M is separate from Gate 2 — different cognitive task.
- Gate 2M skipped entirely when `motion_enabled: false`.
- Motion is additive — most slides stay static.
