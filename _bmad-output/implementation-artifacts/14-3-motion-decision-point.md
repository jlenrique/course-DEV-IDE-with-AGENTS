# Story 14.3: Motion Decision Point & Designation UI

**Epic:** 14 — Motion-Enhanced Presentation Workflow
**Status:** backlog
**Sprint key:** `14-3-motion-decision-point`
**Added:** 2026-04-05
**Depends on:** Story 14.2 (segment manifest motion extensions)

## Summary

After Gary's slides are approved (HIL Gate 2), present a motion designation interface (HIL Gate 2M) where the user marks each slide as static, video (Kira), or animation (manual). Designations drive downstream routing by Marcus.

## Goals

1. New HIL Gate 2M between Gate 2 and Irene Pass 2.
2. Per-slide motion designation with cost estimates.
3. Designations written to segment manifest `motion_type` fields.
4. Marcus routes slides to appropriate downstream handlers.

## Key Files

- Storyboard infrastructure (extension for motion designation controls)
- `skills/bmad-agent-marcus/SKILL.md` — Marcus motion routing logic
- `state/config/run-constants.yaml` — `motion_budget` cost estimation

## Acceptance Criteria

1. Storyboard view shows all approved slides with motion designation controls when `motion_enabled: true`.
2. Per-slide options: Static (default), Video (Kira), Animation (manual).
3. Video designation allows optional motion brief (what should the video depict).
4. Animation designation allows optional guidance notes.
5. Designation summary displayed: "12 slides: 8 static, 3 video (Kira), 1 animation (manual)."
6. Cost estimate shown for Kira video designations (based on model/mode/duration defaults from `motion_budget`).
7. Designations written to segment manifest `motion_type` fields.
8. Marcus routes: static slides proceed directly, video slides to Kira, animation slides to guidance skill.

## Party Mode Consensus (2026-04-05)

- Gate 2M is separate from Gate 2 — "are the slides good?" vs "what do we do with them?"
- Skipped entirely when `motion_enabled: false`.
